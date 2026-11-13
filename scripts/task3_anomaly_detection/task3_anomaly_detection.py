"""Task 3: Anomaly detection. Run from any working directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_six_tasks import run_task

if __name__ == "__main__":
    run_task(3)
