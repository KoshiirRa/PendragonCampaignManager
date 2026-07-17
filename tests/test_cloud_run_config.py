from pathlib import Path

import yaml


def test_cloud_build_migrates_before_deploying_service() -> None:
    config = yaml.safe_load(Path("cloudbuild.yaml").read_text(encoding="utf-8"))
    commands = [step.get("args", []) for step in config["steps"]]
    migrate_at = next(
        index
        for index, args in enumerate(commands)
        if "execute" in args and "${_SERVICE}-migrate" in args
    )
    deploy_at = next(
        index for index, args in enumerate(commands) if "deploy" in args and "${_SERVICE}" in args
    )
    assert migrate_at < deploy_at


def test_dockerfile_uses_cloud_run_port_and_non_root_user() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "0.0.0.0" in dockerfile
    assert "${PORT:-8080}" in dockerfile
    assert "USER app" in dockerfile
