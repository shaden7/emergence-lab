import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mixing_diagnostics import split_rhat


def test_classic_split_rhat_detects_intentionally_discordant_chains():
    rng = np.random.default_rng(9021)
    independent = rng.normal(size=(10, 200))
    assert split_rhat(independent) < 1.05
    divergent = independent.copy()
    divergent[:5] += 4.0
    assert split_rhat(divergent) > 1.4


def test_split_rhat_rejects_inadequate_or_frozen_traces():
    assert split_rhat(np.ones((10, 200))) is None
    with pytest.raises(ValueError):split_rhat(np.ones((3, 200)))
    with pytest.raises(ValueError):split_rhat(np.full((10, 200), np.nan))
