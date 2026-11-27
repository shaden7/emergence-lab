"""Regression tests for real-valued Minkowski coordinate inputs."""
import numpy as np
import pytest

from emergence_lab.causal_set_slab import (
    minkowski_slab_causal_relation,
    side_boundary_censor_mask,
)


@pytest.mark.parametrize("dtype", [np.complex128, object])
def test_minkowski_relation_rejects_complex_coordinates(dtype):
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0 + 2.0j, 0.0, 0.0]],
        dtype=dtype,
    )
    with pytest.raises(TypeError, match="complex values are not supported"):
        minkowski_slab_causal_relation(points)


@pytest.mark.parametrize("dtype", [np.complex128, object])
def test_side_boundary_censor_rejects_complex_coordinates(dtype):
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0 + 2.0j, 0.0, 0.0]],
        dtype=dtype,
    )
    relation = np.zeros((2, 2), dtype=np.bool_)
    with pytest.raises(TypeError, match="complex values are not supported"):
        side_boundary_censor_mask(
            points,
            relation,
            time_extent=4.0,
            x_extent=4.0,
            y_extent=4.0,
        )
