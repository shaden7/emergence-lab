"""D2-E0 endpoint-conditioned exact MM reference and fixed-writer (NOT frozen).

Design: docs/CS0_D2_ENDPOINT_CONTROL_PROPOSAL.md (r3). This module is the pure
computation plus the bounded fixed-writer artifact layer. It does **not**
provide aggregate process-tree CPU/RSS/wall containment, does not authorize a
D2-E0 run, and importing it evaluates nothing. ``generate_reference`` is the
explicit evaluation; unit tests use small ``sizes`` fixtures only.

Model (analytical, see design): fixed input D=2 diamond with both interval
endpoints included and m=N-2 uniform interior events. R=2N-3+R_inner, the
multiplicity of R=2N-3+k is the Mahonian number M(m,k), denominator m!.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
from fractions import Fraction
from pathlib import Path
import platform
import time

SIZES = tuple(range(2, 33))
SPOT_CHECK_SIZES = (2, 3, 4, 8, 32)
DIGITS = 80
NEWTON_STOP = '1e-75'
NEWTON_MAX_ITERATIONS = 12
SIGN_DELTA = '1e-62'
RESIDUAL_GATE = '1e-60'
BISECTION_WIDTH = '1e-65'
BISECTION_AGREEMENT = '1e-60'
BINARY64_GATE = 1e-11
INVERSE_BRACKET = (1, 10)

# Fixed-writer slots (design r3). Temporaries are separate counted slots.
REFERENCE_NAME, MANIFEST_NAME, LOG_NAME = 'reference.json.gz', 'manifest.json', 'diagnostic.log'
REFERENCE_BYTES, MANIFEST_BYTES, LOG_BYTES = 800_000, 16_384, 131_072
TOTAL_CONTENT_BYTES = 2_000_000
SLOTS = {
    REFERENCE_NAME: REFERENCE_BYTES, REFERENCE_NAME + '.tmp': REFERENCE_BYTES,
    MANIFEST_NAME: MANIFEST_BYTES, MANIFEST_NAME + '.tmp': MANIFEST_BYTES,
    LOG_NAME: LOG_BYTES,
}
SLOT_SUM = sum(SLOTS.values())
assert SLOT_SUM == 1_763_840 <= TOTAL_CONTENT_BYTES


class ReferenceDependencyError(RuntimeError):
    """Missing reviewed reference dependency: a setup failure, not a finding."""


class WriterRefusal(ValueError):
    """The fixed writer refused an operation before exceeding its bound."""


# ---------------------------------------------------------------- exact layer

def mahonian(m: int) -> tuple[int, ...]:
    """Inversion-count multiplicities M(m,k), k=0..m(m-1)/2, by convolution."""
    if type(m) is not int or m < 0:
        raise ValueError('m must be a nonnegative integer')
    weights = [1]
    for j in range(2, m + 1):  # multiply by 1+q+...+q^(j-1)
        new = [0] * (len(weights) + j - 1)
        for i, a in enumerate(weights):
            for s in range(j):
                new[i + s] += a
        weights = new
    return tuple(weights)


def _validate_n(n):
    if type(n) is not int or not 2 <= n <= 32:
        raise ValueError('N must be an integer in 2..32')


def endpoint_weights(n: int) -> dict:
    """Exact endpoint-ensemble law: R=offset+k has weight M(N-2,k)/(N-2)!."""
    _validate_n(n)
    m = n - 2
    counts = list(mahonian(m)[::-1])  # R_inner=K_m-I; symmetric anyway.
    return dict(N=n, m=m, offset=2 * n - 3, pairs=n * (n - 1) // 2,
                denominator=math.factorial(m), counts=counts)


def exact_controls(weights: dict) -> tuple[dict, dict]:
    """Rational moments and design identities; returns (values, checks)."""
    n, m, offset, pairs = weights['N'], weights['m'], weights['offset'], weights['pairs']
    counts, denominator = weights['counts'], weights['denominator']
    k_max = m * (m - 1) // 2
    mean = sum((Fraction((offset + k) * w, pairs * denominator)
                for k, w in enumerate(counts)), Fraction())
    variance = sum((Fraction(w, denominator) * (Fraction(offset + k, pairs) - mean) ** 2
                    for k, w in enumerate(counts)), Fraction())
    checks = dict(
        support_length=len(counts) == k_max + 1,
        positive_integer_weights=all(type(w) is int and w > 0 for w in counts),
        normalization=sum(counts) == denominator,
        symmetry=counts == counts[::-1],
        min_R=offset == 2 * n - 3,
        max_R=offset + k_max == pairs,
        no_zero_R=offset > 0,
        mean=mean == Fraction(n * n + 3 * n - 6, 2 * n * (n - 1)),
        mean_above_half=mean > Fraction(1, 2),
        variance=variance == Fraction(m * (m - 1) * (2 * m + 5), 72 * pairs * pairs),
    )
    return dict(mean_r=mean, variance_r=variance), checks


def support_fraction(weights: dict, k: int) -> Fraction:
    return Fraction(weights['offset'] + k, weights['pairs'])


# ------------------------------------------------------------ numerical layer

def _mp_context():
    try:
        import mpmath
    except ImportError as error:
        raise ReferenceDependencyError('D2-E0 requires mpmath==1.3.0') from error
    context = mpmath.mp.clone()
    context.dps = DIGITS
    return context


def _as_mp(ctx, r: Fraction):
    # Exact rational, never routed through binary64.
    return ctx.mpf(r.numerator) / ctx.mpf(r.denominator)


def _forward(ctx, d):
    return ctx.gamma(d + 1) * ctx.gamma(d / 2) / (2 * ctx.gamma(3 * d / 2))


def _derivative(ctx, d):
    return _forward(ctx, d) * (ctx.digamma(d + 1) + ctx.digamma(d / 2) / 2
                               - ctx.mpf(3) / 2 * ctx.digamma(3 * d / 2))


def _text(ctx, value) -> str:
    return ctx.nstr(value, DIGITS, strip_zeros=False)


def _binary64_dimension(r: Fraction) -> float:
    from emergence_lab.causal_set_mm import myrheim_meyer_dimension
    return myrheim_meyer_dimension(float(r))


def newton_inverse(r: Fraction, seed: float) -> dict:
    """80-digit seeded Newton inverse with a finite-precision sign check.

    r == 1 returns d=1 exactly with no iteration. The target is built from the
    exact rational; only the starting point is binary64. A sign check
    f(d-delta) > r > f(d+delta) (f decreasing) is numerical, not an interval
    certificate. Failures are reported in the returned record, never raised.
    """
    if type(r) is not Fraction or not 0 < r <= 1:
        raise ValueError('inverse requires an exact Fraction in (0,1]')
    ctx = _mp_context()
    if r == 1:
        return dict(d=_text(ctx, ctx.mpf(1)), residual='0', residual_ok=True,
                    iterations=0, sign_check=True, converged=True, error=None)
    target = _as_mp(ctx, r)
    record = dict(d=None, residual=None, residual_ok=False, iterations=0, sign_check=False,
                  converged=False, error=None)
    try:
        if not (type(seed) is float and math.isfinite(seed)
                and INVERSE_BRACKET[0] < seed < INVERSE_BRACKET[1]):
            raise ValueError('binary64 seed is not finite inside the inverse bracket')
        d, stop = ctx.mpf(seed), ctx.mpf(NEWTON_STOP)
        for iteration in range(1, NEWTON_MAX_ITERATIONS + 1):
            step = (_forward(ctx, d) - target) / _derivative(ctx, d)
            d -= step
            record['iterations'] = iteration
            if not (INVERSE_BRACKET[0] < d < INVERSE_BRACKET[1]):
                raise ValueError('Newton iterate left the inverse bracket')
            if abs(step) < stop:
                record['converged'] = True
                break
        delta = ctx.mpf(SIGN_DELTA)
        residual = abs(_forward(ctx, d) - target)
        record.update(d=_text(ctx, d), residual=ctx.nstr(residual, 6),
                      residual_ok=bool(residual <= ctx.mpf(RESIDUAL_GATE)),
                      sign_check=bool(_forward(ctx, d - delta) > target > _forward(ctx, d + delta)))
    except (ValueError, ArithmeticError, ZeroDivisionError) as error:
        record['error'] = f'{type(error).__name__}: {error}'[:256]
    return record


def bisection_inverse(r: Fraction) -> str:
    """Independent unseeded 80-digit bisection on [1,10] (spot cross-check)."""
    if type(r) is not Fraction or not 0 < r <= 1:
        raise ValueError('inverse requires an exact Fraction in (0,1]')
    ctx = _mp_context()
    if r == 1:
        return _text(ctx, ctx.mpf(1))
    target = _as_mp(ctx, r)
    low, high = ctx.mpf(INVERSE_BRACKET[0]), ctx.mpf(INVERSE_BRACKET[1])
    if target < _forward(ctx, high):
        raise ValueError('fraction below the [1,10] inverse bracket')
    width = ctx.mpf(BISECTION_WIDTH)
    while high - low > width:
        middle = (low + high) / 2
        if _forward(ctx, middle) > target:
            low = middle
        else:
            high = middle
    return _text(ctx, (low + high) / 2)


def _independent_forward_check(ctx, r: Fraction, d_text) -> tuple[bool, object]:
    """Recompute residual and sign check from the stored 80-digit text and the
    exact rational, independent of the solver's self-report."""
    if type(d_text) is not str:
        return False, None
    d = ctx.mpf(d_text)
    if not (ctx.isfinite(d) and d >= 1):
        return False, None
    if r == 1:
        return bool(d == 1), ctx.mpf(0) if d == 1 else None
    if not d < INVERSE_BRACKET[1]:
        return False, None
    target, delta = _as_mp(ctx, r), ctx.mpf(SIGN_DELTA)
    residual = abs(_forward(ctx, d) - target)
    sign = _forward(ctx, d - delta) > target > _forward(ctx, d + delta)
    return bool(sign and residual <= ctx.mpf(RESIDUAL_GATE)), residual


def _b64(value: float) -> str:
    return format(value, '.17g')


def _rational(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def protocol_config(sizes=SIZES) -> dict:
    return dict(diagnostic='D2-E0', design='docs/CS0_D2_ENDPOINT_CONTROL_PROPOSAL.md r3',
                frozen=False, sizes=list(sizes), ambient_dimension=2,
                mandatory_interval_endpoints=True, decimal_digits=DIGITS,
                newton_stop=NEWTON_STOP, newton_max_iterations=NEWTON_MAX_ITERATIONS,
                sign_delta=SIGN_DELTA, residual_gate=RESIDUAL_GATE,
                bisection_width=BISECTION_WIDTH, bisection_agreement=BISECTION_AGREEMENT,
                binary64_gate=BINARY64_GATE, inverse_bracket=list(INVERSE_BRACKET),
                spot_check_sizes=[n for n in SPOT_CHECK_SIZES if n in sizes],
                stochastic=False, cs0_acceptance=False)


def generate_reference(sizes=SIZES, *, _inverse=newton_inverse,
                       _binary64=_binary64_dimension) -> dict:
    """Explicitly evaluate the D2-E0 reference for ``sizes``; never on import.

    All occupancies and all distinct fractions are retained, including failed
    ones. ``_inverse``/``_binary64`` exist only for manufactured-failure tests.
    """
    sizes = tuple(sizes)
    if not sizes or list(sizes) != sorted(set(sizes)):
        raise ValueError('sizes must be strictly increasing')
    for n in sizes:
        _validate_n(n)
    ctx = _mp_context()
    import mpmath
    started = time.process_time()
    weights = [endpoint_weights(n) for n in sizes]
    exact = [exact_controls(w) for w in weights]

    # Distinct reduced support fractions with auditable per-N coverage.
    distinct = sorted({support_fraction(w, k) for w in weights
                       for k in range(len(w['counts']))})
    index = {r: i for i, r in enumerate(distinct)}
    coverage = [dict(N=w['N'], fraction_index=[index[support_fraction(w, k)]
                                              for k in range(len(w['counts']))])
                for w in weights]

    fractions, failures = [], []
    gate_b64 = ctx.mpf(BINARY64_GATE)
    hp_values, residuals = {}, []
    for r in distinct:
        b64 = _binary64(r)
        b64_finite = type(b64) is float and math.isfinite(b64)
        inv = _inverse(r, b64 if b64_finite else math.nan)
        row = dict(r=_rational(r), binary64=_b64(b64) if b64_finite else 'nonfinite',
                   d_hp=inv['d'], residual=inv['residual'], iterations=inv['iterations'],
                   sign_check=inv['sign_check'], converged=inv['converged'],
                   error=inv['error'], discrepancy=None)
        ok = (b64_finite and inv['error'] is None and inv['converged']
              and inv['sign_check'] and inv['d'] is not None)
        if ok:
            d = ctx.mpf(inv['d'])
            independent, residual = _independent_forward_check(ctx, r, inv['d'])
            row['independent_residual'] = None if residual is None else ctx.nstr(residual, 6)
            row['independent_check'] = independent
            ok = bool(independent and inv['residual_ok'] is True)
            if residual is not None:
                residuals.append((residual, r))
            discrepancy = ctx.mpf(b64) - d
            row['discrepancy'] = ctx.nstr(discrepancy, 6)
            ok = ok and bool(abs(discrepancy) <= gate_b64)
            if r == 1:
                ok = ok and inv['d'] == _text(ctx, ctx.mpf(1)) and b64 == 1.0
            hp_values[r] = d
        row['passed'] = bool(ok)
        if not ok:
            failures.append(f'fraction {r}')
        fractions.append(row)
    monotone = all(hp_values[a] >= hp_values[b]
                   for a, b in zip(distinct, distinct[1:]) if a in hp_values and b in hp_values)
    if not monotone:
        failures.append('dimension not nonincreasing in r')

    summaries = []
    for w, (values, checks) in zip(weights, exact):
        n, mean = w['N'], values['mean_r']
        row = dict(N=n, m=w['m'], denominator=w['denominator'],
                   min_R=w['offset'], max_R=w['offset'] + len(w['counts']) - 1,
                   mean_r=_rational(mean), variance_r=_rational(values['variance_r']),
                   exact_checks=checks)
        ok = all(checks.values())
        rows = [fractions[i] for i in coverage[sizes.index(n)]['fraction_index']]
        if all(f['passed'] for f in rows):
            dem_b64 = _binary64(mean)
            dem = _inverse(mean, dem_b64 if math.isfinite(dem_b64) else math.nan)
            edr_b64 = math.fsum(c / w['denominator'] * float(f['binary64'])
                                for c, f in zip(w['counts'], rows))
            edr_hp = ctx.fsum(_as_mp(ctx, Fraction(c, w['denominator'])) * ctx.mpf(f['d_hp'])
                              for c, f in zip(w['counts'], rows))
            dem_ok = (dem['error'] is None and dem['converged'] and dem['sign_check']
                      and math.isfinite(dem_b64) and dem['residual_ok'] is True
                      and _independent_forward_check(ctx, mean, dem['d'])[0])
            disc_dem = (ctx.mpf(dem_b64) - ctx.mpf(dem['d'])) if dem_ok else None
            disc_edr = ctx.mpf(edr_b64) - edr_hp
            ok = ok and dem_ok and abs(disc_dem) <= gate_b64 and abs(disc_edr) <= gate_b64
            ok = ok and 1 <= ctx.mpf(dem['d']) < 2 and ctx.isfinite(edr_hp) and edr_hp >= 1
            if n in (2, 3):
                ok = ok and dem_b64 == 1.0 and edr_b64 == 1.0 and mean == 1
            row.update(dimension_of_mean_r=_b64(dem_b64), dimension_of_mean_r_hp=dem['d'],
                       dimension_of_mean_r_residual=dem['residual'],
                       mean_dimension=_b64(edr_b64), mean_dimension_hp=_text(ctx, edr_hp),
                       nonlinear_gap=_b64(edr_b64 - dem_b64),
                       nonlinear_gap_hp=_text(ctx, edr_hp - ctx.mpf(dem['d'])) if dem_ok else None,
                       discrepancy_dimension_of_mean=ctx.nstr(disc_dem, 6) if dem_ok else None,
                       discrepancy_mean_dimension=ctx.nstr(disc_edr, 6))
        else:
            ok = False
            row['error'] = 'support fraction failed; summaries not evaluated'
        row['checks_passed'] = bool(ok)
        if not ok:
            failures.append(f'N={n} summary')
        summaries.append(row)

    spot = []
    agreement = ctx.mpf(BISECTION_AGREEMENT)
    for n in SPOT_CHECK_SIZES:
        if n not in sizes:
            continue
        w = weights[sizes.index(n)]
        for label, r in (('min_r', support_fraction(w, 0)),
                         ('max_r', support_fraction(w, len(w['counts']) - 1)),
                         ('mean_r', exact[sizes.index(n)][0]['mean_r'])):
            reference = bisection_inverse(r)
            newton = fractions[index[r]]['d_hp'] if r in index else None
            if newton is None:
                for s in summaries:
                    if s['N'] == n:
                        newton = s.get('dimension_of_mean_r_hp')
            passed = newton is not None and abs(ctx.mpf(newton) - ctx.mpf(reference)) <= agreement
            spot.append(dict(N=n, label=label, r=_rational(r), bisection=reference,
                             newton=newton, passed=bool(passed)))
            if not passed:
                failures.append(f'N={n} {label} bisection spot check')

    worst = max((f for f in fractions if f['discrepancy'] is not None),
                key=lambda f: abs(ctx.mpf(f['discrepancy'])), default=None)
    worst_residual = max(residuals, key=lambda item: item[0], default=None)
    outcome = 'REFERENCE_COMPLETE' if not failures else 'NUMERICAL_CHECK_FAILED'
    return dict(schema=1, diagnostic='D2-E0', config=protocol_config(sizes), outcome=outcome,
                cs0_acceptance=False, stochastic=False, failures=failures,
                weights=weights, coverage=coverage, fractions=fractions,
                summaries=summaries, spot_checks=spot, monotone=bool(monotone),
                counts=dict(sizes=len(sizes), support_rows=sum(len(c['fraction_index']) for c in coverage),
                            distinct_fractions=len(distinct)),
                worst_binary64=None if worst is None else dict(r=worst['r'], discrepancy=worst['discrepancy']),
                worst_independent_residual=None if worst_residual is None else dict(
                    r=_rational(worst_residual[1]), residual=ctx.nstr(worst_residual[0], 6)),
                worst_summary_discrepancy=max(
                    (dict(N=s['N'], name=name, discrepancy=s[name]) for s in summaries
                     for name in ('discrepancy_dimension_of_mean', 'discrepancy_mean_dimension')
                     if s.get(name) is not None),
                    key=lambda item: abs(ctx.mpf(item['discrepancy'])), default=None),
                versions=dict(python=platform.python_version(), mpmath=mpmath.__version__),
                compute_cpu_seconds=round(time.process_time() - started, 6),
                limitation=('Fixed input D=2 with mandatory endpoints; exact estimator '
                            'control, not physical dimensional reduction. Sign checks are '
                            'finite-precision, not interval certificates.'))


# --------------------------------------------------------------- fixed writer

def _json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')) + '\n').encode()


def _fsync_dir(path: Path):
    fd = os.open(path, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class FixedWriter:
    """Writes only the design-r3 slots; every size is checked before opening.

    Trusted fixed-writer content bound (1,763,840 bytes incl. temporaries),
    not a filesystem quota and no protection from other writers.
    """

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self._log_used = 0

    def audit(self) -> dict:
        present = {}
        for entry in os.scandir(self.directory):
            if entry.name not in SLOTS or not entry.is_file(follow_symlinks=False):
                raise WriterRefusal(f'unexpected directory entry {entry.name!r}')
            size = entry.stat(follow_symlinks=False).st_size
            if size > SLOTS[entry.name]:
                raise WriterRefusal(f'{entry.name} exceeds its slot')
            present[entry.name] = size
        if sum(present.values()) > TOTAL_CONTENT_BYTES:
            raise WriterRefusal('total content bound exceeded')
        return present

    def replace(self, name: str, data: bytes):
        if name not in (REFERENCE_NAME, MANIFEST_NAME):
            raise WriterRefusal(f'{name!r} is not an atomic slot')
        if type(data) is not bytes or len(data) > SLOTS[name]:
            raise WriterRefusal(f'{name} payload exceeds {SLOTS[name]} bytes')
        self.audit()
        temporary = self.directory / (name + '.tmp')
        if temporary.exists():  # stale copy from an interrupted replacement
            temporary.unlink()
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.directory / name)
        _fsync_dir(self.directory)

    def log(self, message: str):
        """Append to the single bounded log; truncates rather than overflowing."""
        data = (str(message).replace('\n', ' ') + '\n').encode('utf-8', 'replace')
        remaining = LOG_BYTES - self._log_used
        marker = b'[log truncated]\n'
        if len(data) > remaining:
            if remaining <= 0:
                return
            data = (data[:max(0, remaining - len(marker))] + marker)[:remaining]
        with open(self.directory / LOG_NAME, 'ab') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        self._log_used += len(data)


def _minimal_manifest(base: dict, stage: str, reason: str) -> bytes:
    record = dict(schema=1, diagnostic='D2-E0', outcome='INCOMPLETE', stage=stage,
                  reason=str(reason)[:1024], cs0_acceptance=False, stochastic=False,
                  commit=str(base.get('commit', ''))[:64],
                  versions={k: str(v)[:32] for k, v in dict(base.get('versions') or {}).items()
                            if isinstance(k, str)} if isinstance(base.get('versions'), dict) else {})
    return _json(record)


def write_reference(directory: Path, payload: dict, base: dict, *,
                    _compress=lambda data: gzip.compress(data, 9, mtime=0)) -> dict:
    """Persist a computed payload through the fixed writer; never re-evaluates.

    Returns the final manifest record. Any refusal/failure leaves a minimal
    INCOMPLETE manifest if that write itself succeeds.
    """
    writer = FixedWriter(directory)
    stage = 'setup'
    try:
        writer.replace(MANIFEST_NAME, _minimal_manifest(base, stage, 'started'))
        stage = 'serialize'
        if type(payload) is not dict or payload.get('outcome') not in (
                'REFERENCE_COMPLETE', 'NUMERICAL_CHECK_FAILED'):
            raise WriterRefusal('payload outcome is not a reference outcome')
        if (payload['outcome'] == 'REFERENCE_COMPLETE') != (payload.get('failures') == []):
            raise WriterRefusal('payload outcome inconsistent with its failure list')
        raw = _json(payload)
        stage = 'compress'
        compressed = _compress(raw)
        if type(compressed) is not bytes or gzip.decompress(compressed) != raw:
            raise WriterRefusal('compression did not round-trip')
        stage = 'reference'
        writer.replace(REFERENCE_NAME, compressed)
        stage = 'manifest'
        record = dict(base, schema=1, diagnostic='D2-E0', stage='finished',
                      outcome=payload.get('outcome', 'INCOMPLETE'), cs0_acceptance=False,
                      stochastic=False, raw_bytes=len(raw),
                      raw_sha256=hashlib.sha256(raw).hexdigest(),
                      reference_bytes=len(compressed),
                      reference_sha256=hashlib.sha256(compressed).hexdigest(),
                      failures=list(payload.get('failures', []))[:32])
        # Log first: the finished manifest is the last write, so nothing after
        # it can fail and leave a finished manifest without its reference.
        writer.log(f'finished outcome={record["outcome"]}')
        writer.replace(MANIFEST_NAME, _json(record))
        record['present'] = writer.audit()
        return record
    except Exception as error:  # preserve minimal evidence, never a result
        reason = f'{type(error).__name__}: {error}'
        try:
            # A reference without a matching finished manifest is never left
            # looking complete: remove it (deletion only lowers content bytes).
            for name in (REFERENCE_NAME, REFERENCE_NAME + '.tmp'):
                if (writer.directory / name).exists():
                    (writer.directory / name).unlink()
            writer.replace(MANIFEST_NAME, _minimal_manifest(base, stage, reason))
        except Exception as nested:
            return dict(outcome='INCOMPLETE', stage=stage, reason=reason,
                        manifest_persisted=False, nested=f'{type(nested).__name__}: {nested}'[:256])
        try:
            writer.log(f'stage={stage} {reason}')
        except Exception:
            pass  # the INCOMPLETE manifest above is the authoritative record
        return dict(json.loads(_minimal_manifest(base, stage, reason)), manifest_persisted=True)
