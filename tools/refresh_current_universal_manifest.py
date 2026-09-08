#!/usr/bin/env python3
"""Print a reviewable active R45 snapshot; never modify the repository.

Only exact Git-blob bindings and the canonical self-binding may change. This
does not ratify the resulting candidate or grant provider/runtime authority.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ORIGINAL_PROOF = "0da4a20f9e62a47414f42a8780c695865f1633a0"
MANIFEST_PATH = "manifests/universal-provider-control-reconciliation-r45.json"
PREFIX = "manifests/universal-provider-control-reconciliation-r"
SELF = re.compile(rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")')
OBJECT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
              "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE",
              "GIT_SHALLOW_FILE", "GIT_GRAFT_FILE")


class RefreshError(ValueError):
    pass


def git(repo, *args):
    result = subprocess.run(
        ["git", "--no-replace-objects", "--no-optional-locks", "-c", "core.fsmonitor=false",
         "-C", str(repo), *args], capture_output=True, timeout=60,
    )
    if result.returncode:
        raise RefreshError("GIT_OBJECT_OR_COMMAND_UNAVAILABLE")
    return result.stdout


def render(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def parse(raw):
    try:
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict) or render(value) != raw:
            raise RefreshError("NONCANONICAL_MANIFEST")
        return value
    except (UnicodeError, ValueError, TypeError) as exc:
        raise RefreshError("NONCANONICAL_MANIFEST") from exc


def self_digest(raw):
    if len(SELF.findall(raw)) != 1:
        raise RefreshError("SELF_BINDING_INVALID")
    return "sha256:" + hashlib.sha256(
        SELF.sub(lambda match: match.group(1) + b"0" * 64 + match.group(3), raw)
    ).hexdigest()


def claims(value):
    """Remove only refreshable values; keep every key, path, order and claim."""
    value = copy.deepcopy(value)
    try:
        if not isinstance(value["subjectFiles"], list):
            raise RefreshError("MANIFEST_CLAIMS_CHANGED")
        for row in value["subjectFiles"]:
            if (not isinstance(row, dict)
                    or set(row) != {"path", "gitBlobOid", "sha256", "bytes"}
                    or not isinstance(row["path"], str)
                    or not isinstance(row["gitBlobOid"], str)
                    or not isinstance(row["sha256"], str)
                    or not re.fullmatch(r"[0-9a-f]{40}", row["gitBlobOid"])
                    or not re.fullmatch(r"sha256:[0-9a-f]{64}", row["sha256"])
                    or type(row["bytes"]) is not int or row["bytes"] < 0):
                raise RefreshError("MANIFEST_CLAIMS_CHANGED")
            for key in ("gitBlobOid", "sha256", "bytes"):
                row[key] = None
        if (set(value["manifestSelf"]) != {"path", "bytes", "canonicalGitBlobSha256"}
                or not isinstance(value["manifestSelf"]["path"], str)
                or type(value["manifestSelf"]["bytes"]) is not int
                or value["manifestSelf"]["bytes"] < 0):
            raise RefreshError("MANIFEST_CLAIMS_CHANGED")
        for key in ("bytes", "canonicalGitBlobSha256"):
            value["manifestSelf"][key] = None
    except (KeyError, TypeError) as exc:
        raise RefreshError("MANIFEST_CLAIMS_CHANGED") from exc
    return value


def binding(repo, candidate, path):
    raw = git(repo, "show", f"{candidate}:{path}")
    return {"path": path,
            "gitBlobOid": git(repo, "rev-parse", f"{candidate}:{path}").decode().strip(),
            "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def verify_input(repo, candidate):
    if not re.fullmatch(r"[0-9a-f]{40}", candidate):
        raise RefreshError("EXPLICIT_COMMIT_REQUIRED")
    if any(os.environ.get(key) for key in OBJECT_ENV):
        raise RefreshError("GIT_OBJECT_ENV_REFUSED")
    repo = Path(repo).resolve()
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
    if any((common / name).exists() for name in ("info/grafts", "objects/info/alternates")):
        raise RefreshError("GIT_OBJECT_INDIRECTION_REFUSED")
    if git(repo, "for-each-ref", "--format=%(refname)", "refs/replace").strip():
        raise RefreshError("GIT_OBJECT_INDIRECTION_REFUSED")
    if git(repo, "rev-parse", "HEAD").decode().strip() != candidate:
        raise RefreshError("CANDIDATE_NOT_CURRENT_HEAD")
    if git(repo, "status", "--porcelain=v1", "--untracked-files=all").strip():
        raise RefreshError("DIRTY_OR_AMBIGUOUS_INPUT")
    git(repo, "cat-file", "-e", f"{candidate}^{{commit}}")
    return repo


def refreshed_snapshot(repo, candidate):
    repo = verify_input(repo, candidate)
    original_raw = git(repo, "show", f"{ORIGINAL_PROOF}:{MANIFEST_PATH}")
    original = parse(original_raw)
    if (original["manifestSelf"]["bytes"] != len(original_raw)
            or original["manifestSelf"]["canonicalGitBlobSha256"] != self_digest(original_raw)):
        raise RefreshError("ORIGINAL_PROOF_INVALID")
    for row in original["subjectFiles"]:
        if binding(repo, ORIGINAL_PROOF, row["path"]) != row:
            raise RefreshError("ORIGINAL_PROOF_INVALID")
    git(repo, "merge-base", "--is-ancestor", original["candidateBase"]["commit"], candidate)
    # R45 is the supported active layer. Any changed frozen layer or new layer
    # needs its own reviewed tool update; this command cannot absorb it.
    def frozen(ref):
        paths = git(repo, "ls-tree", "-r", "--name-only", ref, "--", "manifests").decode().splitlines()
        return {p: git(repo, "rev-parse", f"{ref}:{p}").decode().strip()
                for p in paths if p.startswith(PREFIX) and p.endswith(".json") and p != MANIFEST_PATH}
    if frozen(candidate) != frozen(ORIGINAL_PROOF):
        raise RefreshError("FROZEN_LAYER_CHANGED")
    raw = git(repo, "show", f"{candidate}:{MANIFEST_PATH}")
    value = parse(raw)
    if claims(value) != claims(original):
        raise RefreshError("MANIFEST_CLAIMS_CHANGED")
    # Require a valid input self-binding even when its subject bindings are stale.
    if (value["manifestSelf"]["bytes"] != len(raw)
            or value["manifestSelf"]["canonicalGitBlobSha256"] != self_digest(raw)):
        raise RefreshError("SELF_BINDING_INVALID")
    result = copy.deepcopy(value)
    changed = []
    for index, row in enumerate(value["subjectFiles"]):
        current = binding(repo, candidate, row["path"])
        if current != row:
            changed.append(row["path"])
        result["subjectFiles"][index] = current
    result["manifestSelf"]["canonicalGitBlobSha256"] = "sha256:" + "0" * 64
    for _ in range(10):
        encoded = render(result)
        if result["manifestSelf"]["bytes"] == len(encoded):
            break
        result["manifestSelf"]["bytes"] = len(encoded)
    else:
        raise RefreshError("SELF_SIZE_UNSTABLE")
    result["manifestSelf"]["canonicalGitBlobSha256"] = self_digest(render(result))
    assert claims(result) == claims(value)
    verify_input(repo, candidate)  # Refuse a moving HEAD or concurrent dirty edit.
    return {"schema": "active-universal-manifest-refresh/v1", "candidateCommit": candidate,
            "candidateTree": git(repo, "rev-parse", f"{candidate}^{{tree}}").decode().strip(),
            "originalProofCommit": ORIGINAL_PROOF, "manifestPath": MANIFEST_PATH,
            "previousManifestGitBlobOid": git(repo, "rev-parse", f"{candidate}:{MANIFEST_PATH}").decode().strip(),
            "proposedManifestSha256": hashlib.sha256(render(result)).hexdigest(),
            "changedBindings": changed, "authorityGranted": False, "manifest": result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--candidate", required=True, help="Exact clean HEAD commit; no symbolic ref")
    args = parser.parse_args(argv)
    try:
        value = refreshed_snapshot(args.repo, args.candidate)
    except (RefreshError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"REFRESH REFUSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
