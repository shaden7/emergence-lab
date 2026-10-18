"""CI-only abnormal-exit probe: never constructs an S1b graph or draws its RNG.

The real engineering runner and Linux ResourceGuard execute. We replace only
the graph construction entry point, *after* the runner fsyncs STARTED and
updates the manifest, with a controlled SIGKILL or cgroup memory exhaustion.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import sys

from emergence_lab import spectral_s1 as s1
from emergence_lab import spectral_s1b as s1b


def main() -> None:
    mode, output = sys.argv[1], Path(sys.argv[2])
    if mode not in {"sigkill", "oom"}:
        raise ValueError("test-only fault must be sigkill or oom")
    if s1.S1B_RUN_AUTHORIZED:
        raise AssertionError("S1b scientific seeds must remain locked")

    def interrupt_before_rng(*_args, **_kwargs):
        # The real production runner already wrote these checkpoints and
        # passed its cgroup-v2 preflight. Never touch any random generator.
        events = [json.loads(line) for line in (output / "attempts.jsonl").read_text().splitlines()]
        manifest = json.loads((output / "manifest.json").read_text())
        assert len(events) == 1 and events[0]["status"] == "STARTED"
        assert manifest["mode"] == "engineering"
        assert manifest["seed_tuples_attempted"] == [events[0]["seed"]]
        assert events[0]["seed"][0] == s1b.ENGINEERING_SEED
        assert not (output / "report.json").exists()
        if mode == "sigkill":
            os.kill(os.getpid(), signal.SIGKILL)
        # Touch real anonymous pages until a deliberately small Docker
        # cgroup memory limit kills this process; not a Python MemoryError
        # simulation and not an allocation on the shared Lightsail host.
        pages: list[bytearray] = []
        while True:
            pages.append(bytearray(8 * 1024 * 1024))

    s1.build_instance = interrupt_before_rng
    s1b.main(["--mode", "engineering", "--contained-engineering",
              "--no-controls", "--output", str(output)])
    raise AssertionError("fault injection unexpectedly completed")


if __name__ == "__main__":
    main()
