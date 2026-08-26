from pathlib import Path
import shutil
import time


def limpiar_runs_viejos(
    runs_dir="runs",
    max_age_hours=24
):
    base = Path(runs_dir)

    if not base.exists():
        return

    limite = time.time() - (max_age_hours * 3600)

    for run_dir in base.iterdir():
        if not run_dir.is_dir():
            continue

        modified = run_dir.stat().st_mtime

        if modified < limite:
            shutil.rmtree(
                run_dir,
                ignore_errors=True
            )
