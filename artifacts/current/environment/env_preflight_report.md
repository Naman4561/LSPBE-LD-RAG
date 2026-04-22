# Environment Preflight

- repo_root: `.`
- python_executable: `python`
- python_version: `[3, 9, 5]`
- requires_python: `>=3.10`
- requires_python_satisfied: `False`
- platform: `Windows 10 AMD64`
- repo_healthy_for_long_runs: `False`
- pytest_cli_ok: `False`
- pytest_module_ok: `False`
- git_status_ok: `True`
- HF_HOME: `None`
- TRANSFORMERS_CACHE: `None`
- disk_free_bytes: `17454813184`

## Packages

- `pytest`: installed `False`, version `None`
- `numpy`: installed `True`, version `2.0.2`
- `torch`: installed `True`, version `2.8.0`
- `transformers`: installed `True`, version `4.57.6`
- `datasets`: installed `True`, version `3.6.0`
- `sentence-transformers`: installed `True`, version `5.1.2`
- `scikit-learn`: installed `True`, version `1.6.1`

## Dataset Files

- `train_fast50`: exists `True` at `data/qasper_train_fast50.json`
- `validation`: exists `True` at `data/qasper_validation_full.json`
- `test`: exists `True` at `data/qasper_test_full.json`
- `train_dev`: exists `True` at `data/qasper_train_dev.json`
- `train_lockbox`: exists `True` at `data/qasper_train_lockbox.json`

## Notes

- `pytest` is not runnable in this runtime. Use direct Python smoke checks until it is installed into the active interpreter.
- The active interpreter is Python 3.9, but `pyproject.toml` requires `>=3.10`.
- The environment is not fully healthy for long runs. Inspect the failing checks before starting a heavy job.
