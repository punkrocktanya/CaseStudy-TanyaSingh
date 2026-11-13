"""Checks that task entry points run their implementation from task folders."""
import unittest
from unittest.mock import patch
import run_six_tasks as runner


class TaskEntryPointTests(unittest.TestCase):
    def test_task_runs_implementation_files_in_its_folder(self):
        with patch.object(runner.subprocess, 'run') as run, patch.object(runner, 'sync_outputs') as sync:
            runner.run_task(2)
        self.assertEqual(run.call_count, len(runner.TASKS[2]))
        for call, name in zip(run.call_args_list, runner.TASKS[2]):
            self.assertEqual(call.args[0][-1], str(runner.ROOT / 'scripts' / runner.TASK_FOLDERS[2] / name))
            self.assertTrue(call.kwargs['check'])
        sync.assert_called_once_with(2)


if __name__ == '__main__':
    unittest.main()
