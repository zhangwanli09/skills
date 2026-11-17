# Reproducible evaluation projects

The `files` entries in `evals.json` point to checked-in fixture manifests and this
setup code. They are inputs, not pre-existing projects. Prepare a fresh project
before every run; never hand an unresolved `{{project}}` prompt to the executor.
If a runner stages only the declared inputs, preserve their paths relative to
the skill directory so setup can find `evals.json` and the selected manifest.
All six target clients and version/surface assumptions are listed in each
generated project's `CLIENTS.md`.

Requirements: Python 3.9+ and Git. Setup runs only local `git init`, with user
templates disabled; it does not install clients, authenticate, or start servers.
Evaluation 3 requires directory symlink support. On Windows, enable Developer
Mode or use an environment that supports symlinks. Setup fails explicitly and
removes its partial run if it cannot create the real links; it does not replace
the scenario with ordinary files.

From the skill directory, prepare one evaluation:

```bash
python3 evals/setup_fixture.py --eval-id 1 --workspace /tmp/agent-config-sync-evals
```

The workspace may be any writable directory; it need not be under `/tmp`. Each
invocation allocates a unique `eval-<id>-<random>/` directory, even for the same
evaluation ID. The returned JSON includes:

- `project`: the isolated, locally initialized Git repository to inspect or sync.
- `working_directory`: the normal launch path (`project/packages/api` for eval 3).
- `metadata_file`: `eval_metadata.json` with the fully resolved prompt, assertions,
  target directory, and output directory.
- `initial_state_file`: SHA256/executable-bit snapshots and link metadata for
  preservation checks; `.git` internals are excluded.
- `outputs`: where to save `report.md`, actual validation results, and other output.

Read `metadata_file` and execute its resolved `prompt` in `working_directory`.
The project is the modification boundary; metadata, outputs, and the external
sentinel are sibling directories, so the sentinel is genuinely outside the
project. All service endpoints use `.invalid`; credentials are variable
references. Fixture programs deliberately fail if executed and must not be run.

Repeat with `--eval-id 2` and `--eval-id 3` for the other cases. For comparisons,
invoke setup separately for the with-skill and baseline runs, under separate
workspace directories. Do not share or reuse a modified project between runs.
Keep each run's metadata with its outputs when feeding a review viewer.

| ID | Fixture | Behavior exercised |
| --- | --- | --- |
| 1 | `fixtures/read-only.json` | Existing Claude instructions/MCP and complete skill package with executable script, references, and a binary asset; check must leave it unchanged. |
| 2 | `fixtures/windows-conflict.json` | Divergent colleague copy, Gemini context, editor input/sandbox restrictions, and disabled OpenCode V1 service; sync must preserve conflicts and unsupported behavior. |
| 3 | `fixtures/nested-drift.json` | Real broken/external links, nested instructions, JSONC comments/trailing commas, spaced arguments, separate HTTP/SSE entries, and disabled V1 service. |

The manifests contain the source fixture data; edit them to change a scenario.
Generated projects and results belong in the chosen workspace, not in the skill
package. A rerun always creates another isolated copy; it never overwrites an
earlier run. Remove only the run directories you no longer need after review.

Verify the setup itself from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/agent-config-sync/evals -p 'test_*.py' -v
```

These tests verify fixture availability, actual scenario contents, repository
boundaries, per-run isolation, and setup failure behavior. They do not execute
the agent evaluations or establish real-client compatibility.
