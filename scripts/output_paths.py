"""Resolve output groups to the task folder that owns them."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
GROUPS = {
    **dict.fromkeys(['01_data_cleaning','02_silver_phase_data','03_gold_cycle_features','validation_baseline_20261111'], 'task1_data_engineering'),
    **dict.fromkeys(['04_capacity_fade','05_capacity_model_comparison','06_differential_voltage'], 'task2_degradation_modeling'),
    **dict.fromkeys(['07_anomaly_detection','scientific_review'], 'task3_anomaly_detection'),
    **dict.fromkeys(['08_rul_individual_curves','09_rul_xgboost','10_rul_lstm','11_rul_model_comparison','12_rul_validation'], 'task4_rul_estimation'),
    '13_pack_scaling': 'task5_pack_scaling',
    '14_reporting_visualization': 'task6_reporting',
    '15_consistency_validation': 'task6_reporting',
    'execution_reports': 'utilities',
}
class TaskOutputs:
    """Map a group name (optionally with a relative suffix) to its owning task."""
    def __truediv__(self, relative):
        parts = Path(relative).parts
        if not parts or parts[0] not in GROUPS:
            raise KeyError(f'Unknown task output group: {relative}')
        return ROOT.joinpath('scripts', GROUPS[parts[0]], 'outputs', *parts)
