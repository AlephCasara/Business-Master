from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict
from uuid import uuid4

import typer

from business_master.controllers.reconciler import ReconcilePolicy, ReconcileSnapshot
from business_master.settings import Settings

app = typer.Typer(no_args_is_help=True, help="Business Master operator/debug CLI.")


def _command_version(command: str, args: list[str]) -> str | None:
    path = shutil.which(command)
    if path is None:
        return None
    try:
        result = subprocess.run(
            [path, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return path
    output = (result.stdout or result.stderr).strip().splitlines()
    return output[0][:240] if output else path


@app.command()
def doctor() -> None:
    """Inspect local capabilities without changing machine state."""
    tools = {
        "ffmpeg": _command_version("ffmpeg", ["-version"]),
        "psql": _command_version("psql", ["--version"]),
        "docker": _command_version("docker", ["--version"]),
        "podman": _command_version("podman", ["--version"]),
        "nvidia-smi": _command_version("nvidia-smi", ["--query-gpu=name,memory.total", "--format=csv,noheader"]),
        "rocminfo": _command_version("rocminfo", ["--version"]),
        "adb": _command_version("adb", ["version"]),
        "git": _command_version("git", ["--version"]),
    }
    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "tools": tools,
    }
    typer.echo(json.dumps(report, indent=2, ensure_ascii=False))


@app.command()
def policy() -> None:
    """Print bootstrap financial/resource policy."""
    settings = Settings()
    data = {
        "environment": settings.environment,
        "paid_ads_budget_daily": settings.paid_ads_budget_daily,
        "external_ai_api_budget_daily": settings.external_ai_api_budget_daily,
        "cloud_gpu_budget_daily": settings.cloud_gpu_budget_daily,
        "paid_saas_budget_daily": settings.paid_saas_budget_daily,
        "exploration_fraction": settings.exploration_fraction,
        "max_candidate_allocation_fraction": settings.max_candidate_allocation_fraction,
    }
    typer.echo(json.dumps(data, indent=2))


@app.command("reconcile-demo")
def reconcile_demo() -> None:
    """Show that liveness can create work without an operator scheduling a task."""
    hypothesis_id = uuid4()
    snapshot = ReconcileSnapshot(
        hypotheses_without_live_experiment=(hypothesis_id,),
        available_probe_slots=1,
    )
    actions = ReconcilePolicy().plan(snapshot)
    typer.echo(json.dumps([asdict(action) for action in actions], default=str, indent=2))


if __name__ == "__main__":
    app()
