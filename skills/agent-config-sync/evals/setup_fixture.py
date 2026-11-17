#!/usr/bin/env python3
"""Prepare one isolated evaluation project from checked-in manifests (Python 3.9+)."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


EVAL_DIR = Path(__file__).resolve().parent


def child(root, name):
    path = root / name
    if Path(name).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Fixture paths must remain inside their designated directory.")
    return path


def write_files(root, files, binary=False):
    for name, content in files.items():
        path = child(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes.fromhex(content) if binary else content.encode("utf-8"))


def snapshot(root):
    """Hash regular files and record links without reading through them."""
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(set(dirs + files)):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[relative] = {"symlink": os.readlink(path)}
            elif path.is_file():
                result[relative] = {
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "executable": bool(path.stat().st_mode & stat.S_IXUSR),
                }
    return result


def prepare(eval_id, workspace):
    definitions = json.loads((EVAL_DIR / "evals.json").read_text(encoding="utf-8"))
    case = next((case for case in definitions["evals"] if case["id"] == eval_id), None)
    if case is None:
        raise ValueError("Unknown evaluation ID.")
    fixture_path = child(EVAL_DIR, case["fixture"])
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=f"eval-{eval_id}-", dir=workspace))
    project, external = run / "project", run / "external-skill"
    try:
        project.mkdir()
        write_files(project, fixture["project_files"])
        write_files(project, fixture.get("binary_files", {}), binary=True)
        write_files(external, fixture.get("external_files", {}))
        for name in fixture.get("executable_files", []):
            path = child(project, name)
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        # Git supplies a real repository boundary, without commits or network.
        # Ignore inherited Git overrides and user template directories.
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        subprocess.run(["git", "init", "--quiet", "--template=", str(project)],
                       check=True, capture_output=True, env=env)
        for name, target in fixture.get("symlinks", {}).items():
            path = child(project, name)
            if Path(target).is_absolute() or not (path.parent / target).resolve().is_relative_to(run):
                raise ValueError("Fixture symlink targets must remain inside this run.")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(target, target_is_directory=True)
        launch = child(project, fixture.get("launch_directory", "."))
        if not launch.is_dir():
            raise ValueError("Fixture launch directory does not exist.")
        outputs = run / "outputs"
        outputs.mkdir()
        initial = run / "initial-state.json"
        initial.write_text(json.dumps({"project": snapshot(project), "external": snapshot(external)},
                                      indent=2) + "\n", encoding="utf-8")
        metadata = {
            "eval_id": eval_id,
            "eval_name": fixture_path.stem,
            "prompt": case["prompt"].replace("{{project}}", str(project)),
            "assertions": case["assertions"],
            "files": [str(project)],
            "project": str(project),
            "working_directory": str(launch),
            "outputs": str(outputs),
            "initial_state_file": str(initial),
            "run_directory": str(run),
        }
        metadata_path = run / "eval_metadata.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
        return {**metadata, "metadata_file": str(metadata_path)}
    except Exception:
        # Only remove the fresh directory this invocation just allocated.
        shutil.rmtree(run)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-id", type=int, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata = prepare(args.eval_id, args.workspace)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"Fixture setup failed ({type(error).__name__}). Requires Git; "
                       "evaluation 3 also requires directory symlink support.\n")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
