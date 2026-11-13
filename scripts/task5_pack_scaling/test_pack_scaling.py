
# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

import unittest
import numpy as np
from stage_13_scale_module_pack import envelope


class TopologyChecks(unittest.TestCase):
    def test_identical_cells_and_limiting_group(self):
        q=np.full((1,3,4,2),2.)
        modules,pack=envelope(q,np.ones_like(q))
        np.testing.assert_allclose(modules,4.)
        self.assertEqual(pack[0],4.)
        q[0,1,2,:]=1.
        modules,pack=envelope(q,np.ones_like(q))
        self.assertEqual(pack[0],2.)
        np.testing.assert_allclose(modules,[[4,2,4]])

    def test_soc_accessibility(self):
        q=np.full((1,1,2,2),2.)
        _,pack=envelope(q,np.full_like(q,.8))
        self.assertAlmostEqual(pack[0],3.2)


if __name__=='__main__':unittest.main()
