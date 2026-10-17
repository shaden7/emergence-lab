"""Fail-closed Linux cgroup-v2 preflight/watchdog for a future reviewed S1b run.

The container must be dedicated, CPU quota <= one core, memory+swap <= 2 GiB,
network disabled, one process group. CPU watchdog stops TWO CPU seconds before
the budget, including subprocess and analysis CPU; the kernel enforces CPU rate
and memory. Abrupt stops preserve the attempts ledger, never a reusable seed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import threading


def preflight(cgroup: Path, memory_bytes: int) -> dict:
    quota, period = (cgroup/"cpu.max").read_text().split()
    memory = (cgroup/"memory.max").read_text().strip()
    swap = (cgroup/"memory.swap.max").read_text().strip()
    if quota == "max" or int(quota) <= 0 or int(period) <= 0 or int(quota) > int(period):
        raise PermissionError("S1b requires externally enforced <=1 CPU quota")
    if memory == "max" or not 0 < int(memory) <= memory_bytes or swap != "0":
        raise PermissionError("S1b requires bounded memory and zero additional swap")
    if {name for _, name in socket.if_nameindex()} != {"lo"}:
        raise PermissionError("S1b requires an isolated network namespace (loopback only)")
    if os.environ.get("S1B_HOST_CLASS") != "non-lightsail":
        raise PermissionError("operator must verify this is not the shared Lightsail host")
    if any(os.environ.get(k) != "1" for k in
           ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")):
        raise PermissionError("S1b requires explicitly single-threaded numerical libraries")
    return {"cpu.max": [quota, period], "memory.max": memory, "memory.swap.max": swap,
            "network_interfaces": ["lo"], "host_class_operator_attestation": "non-lightsail"}


def cgroup_cpu(cgroup: Path) -> float:
    fields = dict(line.split() for line in (cgroup/"cpu.stat").read_text().splitlines())
    return int(fields["usage_usec"]) / 1e6


class ResourceGuard:
    def __init__(self, outdir: Path, total_cpu_s: float, memory_bytes: int,
                 cgroup: Path = Path("/sys/fs/cgroup")):
        self.outdir, self.total, self.memory, self.cgroup = outdir, total_cpu_s, memory_bytes, cgroup
        self.done = threading.Event()
        self.failure = None

    def __enter__(self):
        if os.name != "posix" or not Path("/proc/self").exists():
            raise PermissionError("full S1b requires Linux cgroup-v2 containment")
        if self.outdir.exists():
            raise FileExistsError(self.outdir)
        self.evidence = preflight(self.cgroup, self.memory)
        if os.getsid(0) != os.getpid():
            os.setsid()
        if os.getpgrp() != os.getpid():
            raise PermissionError("S1b must own its isolated process group")
        self.start = cgroup_cpu(self.cgroup)
        self.thread = threading.Thread(target=self.watch, daemon=True)
        self.thread.start()
        return self

    def stop(self, reason):
        self.failure = reason
        # _run creates the output directory only after this guard has passed.
        try:
            if self.outdir.exists():
                with (self.outdir/"resource_stop.json").open("w") as fh:
                    json.dump({"status": "BLOCKED", "reason": reason,
                               "seed_reuse_forbidden": True}, fh)
                    fh.flush()
                    os.fsync(fh.fileno())
        finally:
            os.killpg(os.getpgrp(), signal.SIGKILL)

    def watch(self):
        while not self.done.wait(.05):
            try:
                if cgroup_cpu(self.cgroup) - self.start >= self.total - 2.:
                    self.stop("cgroup CPU reserve reached; stop before total budget")
                    return
            except (OSError, ValueError, KeyError) as exc:
                self.stop("resource accounting unavailable: " + type(exc).__name__)
                return

    def __exit__(self, typ, value, trace):
        self.done.set()
        self.thread.join()
        elapsed = cgroup_cpu(self.cgroup) - self.start
        if elapsed >= self.total - 2.:
            self.stop("CPU reserve reached on final output")
        if self.outdir.exists():
            (self.outdir/"resource_evidence.json").write_text(json.dumps({
                "preflight": self.evidence, "cgroup_cpu_s": elapsed,
                "cpu_limit_s": self.total, "reserve_cpu_s": 2.,
                "watchdog_poll_wall_s": .05, "watchdog_failure": self.failure,
                "clean_exit": typ is None}, sort_keys=True, indent=2) + "\n")
