"""Unit tests for the topology-aware capacity envelope."""
import unittest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_13_scale_module_pack import envelope


class TopologyChecks(unittest.TestCase):

    def test_identical_cells_limiting_group(self):
        """All cells identical → pack capacity = 2 × q (2 parallel cells)."""
        q = np.full((1, 3, 4, 2), 2.0)
        modules, pack = envelope(q, np.ones_like(q))
        # Each group sums 2 parallel cells of 2.0 Ah → 4.0 Ah per group.
        # Min over groups within module = 4.0; min over modules = 4.0.
        np.testing.assert_allclose(modules, 4.0)
        self.assertAlmostEqual(float(pack[0]), 4.0)

    def test_weakest_group_limits_module(self):
        """One weak group drives the whole module below the others."""
        q = np.full((1, 3, 4, 2), 2.0)
        q[0, 1, 2, :] = 1.0           # module 1, group 2 degraded to 1.0 Ah
        modules, pack = envelope(q, np.ones_like(q))
        # Degraded group sums to 2.0 Ah; others sum to 4.0 Ah.
        # Module 1 capacity = min(4, 4, 2, 4) = 2.0.
        # Pack = min(4, 2, 4) = 2.0.
        self.assertAlmostEqual(float(pack[0]), 2.0)
        np.testing.assert_allclose(modules[0], [4.0, 2.0, 4.0])

    def test_pack_is_not_min_cell(self):
        """Pack capacity is NOT simply the minimum individual cell capacity.

        In a 2-parallel group the weak cell is supplemented by its partner;
        the group still contributes its combined Ah.
        """
        q = np.ones((1, 1, 1, 2))
        q[0, 0, 0, 0] = 0.5           # one cell at 0.5 Ah, partner at 1.0 Ah
        _, pack = envelope(q, np.ones_like(q))
        # Group capacity = 0.5 + 1.0 = 1.5 (not the min cell 0.5).
        self.assertAlmostEqual(float(pack[0]), 1.5)

    def test_soc_scales_accessible_capacity(self):
        """Usable SOC < 1 reduces accessible capacity proportionally."""
        q = np.full((1, 1, 2, 2), 2.0)
        _, pack = envelope(q, np.full_like(q, 0.8))
        # Each group: (2.0 × 0.8) + (2.0 × 0.8) = 3.2 Ah.
        self.assertAlmostEqual(float(pack[0]), 3.2)

    def test_soc_zero_one_cell_in_group(self):
        """A cell at SOC=0 halves its group capacity (partner still contributes)."""
        q = np.ones((1, 1, 1, 2))
        soc = np.ones((1, 1, 1, 2))
        soc[0, 0, 0, 0] = 0.0
        _, pack = envelope(q, soc)
        # Group = 1.0×0 + 1.0×1 = 1.0 Ah (not 0).
        self.assertAlmostEqual(float(pack[0]), 1.0)


if __name__ == "__main__":
    unittest.main()
