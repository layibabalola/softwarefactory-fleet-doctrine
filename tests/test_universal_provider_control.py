from __future__ import annotations

import copy
import datetime as dt
import hashlib
import inspect
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import traceback
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import universal_provider_control as upc  # noqa: E402


UTC = dt.timezone.utc
SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64
SHA_C = "sha256:" + "c" * 64
SHA_D = "sha256:" + "d" * 64
R11_PREDECESSOR = "52ca3452a12656a13e62eba5c6b0641e43440f32"
R11_REQUIRED_BLOBS = {
    "tests/test_universal_provider_control.py",
    "tools/universal_provider_control.py",
}


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def required_predecessor_blob(path: str) -> str:
    """Read exact R11 evidence or fail with one stable no-echo history reason."""

    if path not in R11_REQUIRED_BLOBS:
        raise AssertionError("REQUIRED_HISTORY_PATH_INVALID")
    run = subprocess.run(
        ["git", "show", f"{R11_PREDECESSOR}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if run.returncode != 0:
        raise AssertionError("REQUIRED_HISTORY_OBJECT_UNAVAILABLE") from None
    return run.stdout


class UniversalProviderControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.now = dt.datetime(2026, 8, 18, 20, 0, tzinfo=UTC)
        self.secret = b"S" * 32
        self.identity = b"local-account-alias-never-published"
        self.quota_id = upc.derive_quota_domain_id("claude", self.identity, self.secret)
        self.launcher = self.root / "controlled-launcher.exe"
        self.launcher.write_bytes(b"reference launcher bytes\n")
        self.subject = self.root / "frozen-subject.bin"
        self.subject.write_bytes(b"frozen review subject\n")
        self.launcher_config = self.root / "launcher-config.json"
        self.launcher_config.write_bytes(b'{"directProviderInvocation":false}\n')
        self.capsule = self.root / "context-capsule.bin"
        self.capsule.write_bytes(b"bounded exact capsule\n")
        self.checkpoint = self.root / "compaction-checkpoint.json"
        self.checkpoint.write_bytes(b'{"milestone":"frozen"}\n')
        self.cache_manifest = self.root / "cache-affinity.json"
        self.cache_manifest.write_bytes(b'{"prefix":"stable"}\n')
        self.profile = self.make_profile()
        self.inventory = self.make_inventory()
        self.health = self.make_health()
        self.native = self.make_native()
        self.request = self.make_request()

    def tearDown(self) -> None:
        # Tests that prove an active claimant remains fenced intentionally cannot use broker.close()
        # as a destructor.  Dispose their synthetic handles only after each assertion boundary so
        # Windows can remove the private temporary tree; this is not a production release path.
        root_key = os.path.normcase(os.path.abspath(str(self.root.resolve())))
        for key, runtime in list(upc._BROKER_ROOT_RUNTIMES.items()):
            if key == root_key or key.startswith(root_key + os.sep):
                handles = list(runtime.os_locks.values())
                handles.extend(record[1] for values in runtime.artifact_handles.values() for record in values)
                for handle in handles:
                    try:
                        handle.close()
                    except BaseException:
                        pass
                runtime.os_locks.clear()
                runtime.os_lock_release_attempted.clear()
                runtime.unproven_os_locks.clear()
                runtime.artifact_handles.clear()
                runtime.artifact_close_attempted.clear()
                runtime.unproven_artifact_handles.clear()
                upc._BROKER_ARTIFACT_CLEANUP_POISON.pop(key, None)
                upc._BROKER_ROOT_RUNTIMES.pop(key, None)
        self.temp.cleanup()

    def make_profile(self) -> dict:
        return {
            "schema": "fleet-universal-project-profile/v1",
            "project": "test-project",
            "profileVersion": 1,
            "independenceClass": "SHARED_QUOTA_DOMAIN",
            "coordination": {
                "quotaDomainHostCount": 1,
                "mode": "HOST_LOCAL",
                "sharedBrokerIdentitySha256": None,
                "stateRootIdentity": "hmac-sha256:" + "0" * 64,
            },
            "efficiency": {
                "maxTurns": 16,
                "maxContextTokens": 65536,
                "milestoneCompactionRequired": True,
                "cacheAffinityRequired": True,
                "capsuleRequired": True,
                "qualityMayBeWeakened": False,
            },
            "policy": {
                "maxObservationAgeSeconds": 120,
                "maxInventoryAgeSeconds": 120,
                "maxBrokerHealthAgeSeconds": 120,
                "maxRequestAgeSeconds": 120,
                "maxRequestValiditySeconds": 900,
                "leaseMaxSeconds": 600,
                "postResetQuietSeconds": 60,
                "maxConcurrentPerQuotaDomain": 1,
                "evidenceCapsuleMaxBytes": 65536,
                "reserveFloorByPriority": {
                    "OWNER_FOREGROUND": 0.05,
                    "REQUIRED_REVIEW": 0.15,
                    "PRODUCT_WORK": 0.25,
                    "ADJUDICATION": 0.30,
                    "MAINTENANCE": 0.40,
                },
                "requiredCapacityDimensions": {
                    "claude-code/1.0": ["session", "weekly"],
                    "openai-responses/1.0": ["primary", "secondary"],
                    "kimi-code/1.0": ["context", "monthly"],
                    "xai-api/1.0": ["requests", "tokens"],
                },
            },
            "invariants": {
                "resetCanOpenGate": False,
                "authCanOpenGate": False,
                "capacityCanOpenGate": False,
                "unknownCanAdmit": False,
                "directProviderInvocation": False,
                "exactLaunchBinding": True,
                "fullChildLifetimeLease": True,
                "strictRuntimeSchemaEnforcement": True,
                "boundedStreamingEvidence": True,
                "deterministicNoWorkProof": True,
            },
        }

    def make_inventory(self) -> dict:
        broker_hash = sha_file(Path(upc.__file__).resolve())
        return {
            "schema": "fleet-universal-launcher-inventory/v1",
            "capturedAt": upc.iso(self.now - dt.timedelta(seconds=5)),
            "complete": True,
            "surfaceClasses": ["SCHEDULED_TASK", "APP_SCHEDULER", "REPOSITORY_WRAPPER", "SERVICE"],
            "configuredSurfaceCounts": {"SCHEDULED_TASK": 0, "APP_SCHEDULER": 0, "REPOSITORY_WRAPPER": 1, "SERVICE": 0},
            "observedSurfaceCounts": {"SCHEDULED_TASK": 0, "APP_SCHEDULER": 0, "REPOSITORY_WRAPPER": 1, "SERVICE": 0},
            "censusMethodSha256": SHA_D,
            "configuredLauncherCount": 1,
            "observedLauncherCount": 1,
            "brokerExecutableSha256": broker_hash,
            "launchers": [
                {
                    "surfaceClass": "REPOSITORY_WRAPPER",
                    "discoverySha256": SHA_C,
                    "executablePath": str(self.launcher.resolve()),
                    "executableSha256": sha_file(self.launcher),
                    "brokerRouted": True,
                    "directProviderInvocation": False,
                }
            ],
        }

    def make_health(self) -> dict:
        health = {
            "schema": "fleet-universal-broker-health/v1",
            "observedAt": upc.iso(self.now - dt.timedelta(seconds=4)),
            "status": "HEALTHY",
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "observerQualified": True,
            "observerHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        health["observerHmacSha256"] = upc.contract_hmac(
            "broker-health-v1", health, self.secret, "observerHmacSha256"
        )
        return health

    def make_native(self, provider: str = "claude") -> dict:
        quota_id = self.quota_id
        common = {
            "schema": "fleet-provider-native-capacity-evidence/v1",
            "provider": provider,
            "capturedAt": upc.iso(self.now - dt.timedelta(seconds=6)),
            "quotaDomainId": quota_id,
            "sourceArtifactSha256": SHA_A,
        }
        future = upc.iso(self.now + dt.timedelta(hours=2))
        past = upc.iso(self.now - dt.timedelta(hours=2))
        if provider == "claude":
            common.update(
                adapterVersion="claude-code/1.0",
                payload={
                    "sessionUtilization": 0.10,
                    "weeklyUtilization": 0.20,
                    "sessionResetAt": future,
                    "weeklyResetAt": future,
                    "sessionLastResetAt": past,
                    "weeklyLastResetAt": past,
                },
            )
        elif provider == "openai":
            common["quotaDomainId"] = upc.derive_quota_domain_id("openai", self.identity, self.secret)
            common.update(
                adapterVersion="openai-responses/1.0",
                payload={
                    "primaryUtilization": 0.10, "secondaryUtilization": 0.20,
                    "primaryResetAt": future, "secondaryResetAt": future,
                    "primaryLastResetAt": past, "secondaryLastResetAt": past,
                },
            )
        elif provider == "kimi":
            common["quotaDomainId"] = upc.derive_quota_domain_id("kimi", self.identity, self.secret)
            common.update(
                adapterVersion="kimi-code/1.0",
                payload={
                    "contextUtilization": 0.10, "monthlyUtilization": 0.20,
                    "contextResetAt": future, "monthlyResetAt": future,
                    "contextLastResetAt": past, "monthlyLastResetAt": past,
                },
            )
        else:
            common["quotaDomainId"] = upc.derive_quota_domain_id("grok", self.identity, self.secret)
            common.update(
                adapterVersion="xai-api/1.0",
                payload={
                    "requestUtilization": 0.10, "tokenUtilization": 0.20,
                    "requestResetAt": future, "tokenResetAt": future,
                    "requestLastResetAt": past, "tokenLastResetAt": past,
                },
            )
        common["observerHmacSha256"] = "hmac-sha256:" + "0" * 64
        common["observerHmacSha256"] = upc.contract_hmac(
            "provider-capacity-evidence-v1", common, self.secret, "observerHmacSha256"
        )
        return common

    def make_request(self, request_id: str = "request-0001") -> dict:
        request = {
            "schema": "fleet-universal-control-request/v1",
            "requestId": request_id,
            "project": "test-project",
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=3)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)),
            "provider": "claude",
            "adapterVersion": "claude-code/1.0",
            "quotaDomainId": self.quota_id,
            "priority": "PRODUCT_WORK",
            "model": "claude-opus-4-1",
            "effort": "high",
            "role": "IMPLEMENT",
            "seatIdHash": "hmac-sha256:" + "1" * 64,
            "seatEpoch": 7,
            "sessionIdHash": "hmac-sha256:" + "2" * 64,
            "subjectPath": str(self.subject.resolve()),
            "subjectSha256": sha_file(self.subject),
            "executablePath": str(self.launcher.resolve()),
            "executableSha256": sha_file(self.launcher),
            "argv": [str(self.launcher.resolve()), "claude-opus-4-1", "high", sha_file(self.subject)],
            "argvSha256": "",
            "argvBindings": {"modelIndex": 1, "effortIndex": 2, "subjectIndex": 3},
            "launcherConfigPath": str(self.launcher_config.resolve()),
            "launcherConfigSha256": sha_file(self.launcher_config),
            "actionableWork": True,
            "demandFingerprint": SHA_B,
            "priorIdleFingerprint": SHA_C,
            "maxWallSeconds": 60,
            "maxTurns": 8,
            "maxContextTokens": 32768,
            "contextCapsulePath": str(self.capsule.resolve()),
            "contextCapsuleSha256": sha_file(self.capsule),
            "compactionCheckpointPath": str(self.checkpoint.resolve()),
            "compactionCheckpointSha256": sha_file(self.checkpoint),
            "cacheAffinityManifestPath": str(self.cache_manifest.resolve()),
            "cacheAffinityKeySha256": sha_file(self.cache_manifest),
            "windowEstimates": {"session": 0.05, "weekly": 0.05},
            "canary": False,
            "manualAuthorizationSha256": None,
        }
        request["argvSha256"] = upc.digest_json(request["argv"])
        return request

    def bind_runtime(self, broker: upc.UniversalProviderBroker) -> None:
        self.profile["coordination"]["stateRootIdentity"] = broker.state_root_identity(self.secret)
        self.health = self.make_health()

    def resign_native(self, value: dict) -> dict:
        value["observerHmacSha256"] = upc.contract_hmac(
            "provider-capacity-evidence-v1", value, self.secret, "observerHmacSha256"
        )
        return value

    def resign_health(self, value: dict) -> dict:
        value["observerHmacSha256"] = upc.contract_hmac(
            "broker-health-v1", value, self.secret, "observerHmacSha256"
        )
        return value

    def make_canary_authorization(self, request: dict, authorization_id: str) -> dict:
        authorization = {
            "schema": "fleet-universal-manual-canary-authorization/v1",
            "authorizationId": authorization_id,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "requestBindingSha256": upc.canary_request_binding(request),
            "quotaDomainId": request["quotaDomainId"],
            "projectProfileSha256": upc.digest_json(self.profile),
            "reviewerReceiptSha256": SHA_D,
            "oneUse": True,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        authorization["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", authorization, self.secret, "authorizationHmacSha256"
        )
        request["manualAuthorizationSha256"] = upc.digest_json(authorization)
        return authorization

    def admission_observation(
        self, request: dict, *, phase: str = "ADMISSION", lease_id: str | None = None
    ) -> dict:
        observation = {
            "schema": "fleet-universal-process-observation/v1",
            "phase": phase,
            "requestId": request["requestId"],
            "leaseId": lease_id,
            "observedAt": upc.iso(self.now),
            "status": "SUSPENDED",
            "processId": 4242,
            "processStartTime": upc.iso(self.now - dt.timedelta(seconds=1)),
            "imagePath": request["executablePath"],
            "imageSha256": request["executableSha256"],
            "actualArgv": request["argv"],
            "actualArgvSha256": request["argvSha256"],
            "seatIdHash": request["seatIdHash"],
            "seatEpoch": request["seatEpoch"],
            "sessionIdHash": request["sessionIdHash"],
            "observerHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        observation["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", observation, self.secret, "observerHmacSha256"
        )
        return observation

    def process_observation(
        self, result: dict, status: str, *, seat_epoch: int | None = None, phase: str = "RECOVERY"
    ) -> dict:
        observation = {
            "schema": "fleet-universal-process-observation/v1",
            "phase": phase,
            "requestId": result["requestId"],
            "leaseId": result["leaseId"],
            "observedAt": upc.iso(self.now),
            "status": status,
            "processId": result["processId"],
            "processStartTime": result["processStartTime"],
            "imagePath": result["executablePath"],
            "imageSha256": result["executableSha256"],
            "actualArgv": list(self.request["argv"]),
            "actualArgvSha256": result["argvSha256"],
            "seatIdHash": result["seatIdHash"],
            "seatEpoch": result["seatEpoch"] if seat_epoch is None else seat_epoch,
            "sessionIdHash": result["sessionIdHash"],
            "observerHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        observation["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", observation, self.secret, "observerHmacSha256"
        )
        return observation

    def transition(self, broker: upc.UniversalProviderBroker, target: str = "OPEN") -> None:
        self.bind_runtime(broker)
        transition = {
            "schema": "fleet-universal-gate-transition/v1",
            "transitionId": "transition-0001",
            "transitionEpoch": 1,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)),
            "from": "CLOSED",
            "to": target,
            "cause": "INDEPENDENT_ADJUDICATION",
            "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health),
            "reviewReceiptSha256": SHA_B,
            "testReceiptSha256": SHA_C,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        transition["authorizationHmacSha256"] = upc.contract_hmac(
            "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
        )
        broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)

    def authorize(self, broker: upc.UniversalProviderBroker, request: dict | None = None, **changes) -> dict:
        confirm = changes.pop("confirm", True)
        selected_request = request or self.request
        if "profile" not in changes:
            self.bind_runtime(broker)
        supplied_process = changes.pop("process_observation", None)
        if supplied_process is None:
            supplied_process = self.admission_observation(selected_request)
        arguments = {
            "request": selected_request,
            "profile": self.profile,
            "inventory": self.inventory,
            "health": self.health,
            "native_evidence": [self.native],
            "manual_authorization": None,
            "local_stable_identity": self.identity,
            "fleet_secret": self.secret,
            "process_observation": supplied_process,
            "now": self.now,
        }
        arguments.update(changes)
        result = broker.authorize_suspended_child(**arguments)
        if confirm and result.get("status") == "PREPARED_SUSPENDED":
            resume = self.admission_observation(selected_request, phase="RESUME", lease_id=result["leaseId"])
            return broker.confirm_resume_boundary(
                lease_id=result["leaseId"], process_observation=resume, fleet_secret=self.secret, now=self.now
            )
        return result

    # Retained canonical controls and exact runtime-schema enforcement.

    def test_all_repository_schemas_are_strict_json_and_draft_202012_valid(self) -> None:
        for kind in upc.SCHEMAS:
            schema = upc._load_schema(kind)
            self.assertFalse(schema.get("additionalProperties", True), kind)
            upc.jsonschema.Draft202012Validator.check_schema(schema)

    def test_default_gate_is_persisted_closed(self) -> None:
        db = self.root / "gate.db"
        self.assertEqual(upc.UniversalProviderBroker(db).gate_state(), "CLOSED")
        self.assertEqual(upc.UniversalProviderBroker(db).gate_state(), "CLOSED")

    def test_missing_malformed_oversize_unreadable_and_reparse_state_fail_closed(self) -> None:
        missing = self.root / "missing-state"
        self.assertEqual(upc.UniversalProviderBroker(missing).gate_state(), "CLOSED")

        malformed = self.root / "malformed-state"
        malformed.mkdir()
        (malformed / "universal-provider-control-v1.db").write_bytes(b"not sqlite")
        with self.assertRaisesRegex(upc.ControlError, "STATE_UNEVALUABLE"):
            upc.UniversalProviderBroker(malformed)

        oversize = self.root / "oversize-state"
        oversize.mkdir()
        with (oversize / "universal-provider-control-v1.db").open("wb") as handle:
            handle.seek(upc.MAX_STATE_BYTES)
            handle.write(b"x")
        with self.assertRaisesRegex(upc.ControlError, "STATE_BOUNDARY_INVALID"):
            upc.UniversalProviderBroker(oversize)

        with mock.patch.object(upc.sqlite3, "connect", side_effect=sqlite3.OperationalError("private path")):
            with self.assertRaisesRegex(upc.ControlError, "STATE_UNEVALUABLE"):
                upc.UniversalProviderBroker(self.root / "unreadable-state")

        reparse = self.root / "reparse-state"
        reparse.mkdir()
        original = Path.is_symlink
        with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == reparse or original(path)):
            with self.assertRaisesRegex(upc.ControlError, "STATE_BOUNDARY_INVALID"):
                upc.UniversalProviderBroker(reparse)

    def test_tampered_or_missing_gate_row_is_never_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "tampered-gate")
        self.transition(broker)
        connection = sqlite3.connect(broker.database)
        try:
            connection.execute("PRAGMA ignore_check_constraints=ON")
            connection.execute("UPDATE gate_state SET state='MYSTERY' WHERE singleton=1")
            connection.commit()
        finally:
            connection.close()
        result = self.authorize(broker, request=self.make_request("request-tampered-gate"))
        self.assertEqual(result["reason"], "GATE_STATE_INVALID")

        missing = upc.UniversalProviderBroker(self.root / "missing-gate-row")
        connection = sqlite3.connect(missing.database)
        try:
            connection.execute("DELETE FROM gate_state")
            connection.commit()
        finally:
            connection.close()
        self.assertEqual(missing.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")

    def test_closed_gate_cannot_attest(self) -> None:
        result = self.authorize(upc.UniversalProviderBroker(self.root / "closed.db"))
        self.assertEqual(result, {"status": "UNEVALUABLE", "reason": "AUTOMATIC_LAUNCH_GATE_CLOSED"})

    def test_schema_additional_property_rejected_at_runtime(self) -> None:
        request = copy.deepcopy(self.request)
        request["hiddenBypass"] = True
        broker = upc.UniversalProviderBroker(self.root / "extra.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, request)["reason"], "SCHEMA_VALIDATION_FAILED")

    def test_request_replay_is_exact_and_conflict_fails_closed(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "replay.db")
        self.transition(broker)
        first = self.authorize(broker)
        self.assertEqual(first["status"], "ALLOW_ATTESTED")
        self.assertEqual(self.authorize(broker)["reason"], "ACTIVE_AUTHORITY_NOT_REPLAYABLE")
        changed = copy.deepcopy(self.request)
        changed["role"] = "REVIEW"
        self.assertEqual(self.authorize(broker, changed)["reason"], "REQUEST_REPLAY_CONFLICT")

    def test_full_child_lifetime_lease_requires_exact_release(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "lease.db")
        self.transition(broker)
        first = self.authorize(broker)
        second = self.make_request("request-0002")
        self.assertEqual(self.authorize(broker, second)["reason"], "QUOTA_DOMAIN_LEASE_HELD")
        wrong_pid = self.process_observation(first, "EXITED", phase="TERMINAL")
        wrong_pid["processId"] = 9
        wrong_pid["observerHmacSha256"] = upc.contract_hmac("process-observation-v1", wrong_pid, self.secret, "observerHmacSha256")
        with self.assertRaises(upc.ControlError):
            broker.release_child(process_observation=wrong_pid, fleet_secret=self.secret, now=self.now)
        wrong_session = self.process_observation(first, "EXITED", phase="TERMINAL")
        wrong_session["sessionIdHash"] = "hmac-sha256:" + "f" * 64
        wrong_session["observerHmacSha256"] = upc.contract_hmac("process-observation-v1", wrong_session, self.secret, "observerHmacSha256")
        with self.assertRaises(upc.ControlError):
            broker.release_child(process_observation=wrong_session, fleet_secret=self.secret, now=self.now)
        terminal = self.process_observation(first, "EXITED", phase="TERMINAL")
        broker.release_child(process_observation=terminal, fleet_secret=self.secret, now=self.now)
        third = self.make_request("request-0004")
        self.assertEqual(self.authorize(broker, third)["status"], "ALLOW_ATTESTED")

    def test_expiry_does_not_silently_release_child_reservation(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "expiry.db")
        self.transition(broker)
        first = self.authorize(broker)
        later_request = self.make_request("request-0003")
        later_now = self.now + dt.timedelta(seconds=70)
        later_request["issuedAt"] = upc.iso(later_now - dt.timedelta(seconds=1))
        later_request["expiresAt"] = upc.iso(later_now + dt.timedelta(minutes=10))
        native = self.make_native()
        native["capturedAt"] = upc.iso(later_now - dt.timedelta(seconds=1))
        for key in ("sessionLastResetAt", "weeklyLastResetAt"):
            native["payload"][key] = upc.iso(later_now - dt.timedelta(hours=2))
        self.resign_native(native)
        process = self.admission_observation(later_request)
        process["observedAt"] = upc.iso(later_now)
        process["processStartTime"] = upc.iso(later_now - dt.timedelta(seconds=1))
        process["observerHmacSha256"] = upc.contract_hmac("process-observation-v1", process, self.secret, "observerHmacSha256")
        result = self.authorize(broker, later_request, native_evidence=[native], now=later_now, process_observation=process)
        self.assertEqual(first["status"], "ALLOW_ATTESTED")
        self.assertEqual(result["reason"], "QUOTA_DOMAIN_LEASE_HELD")

    def test_multi_window_dimension_cannot_be_selected_away(self) -> None:
        request = copy.deepcopy(self.request)
        del request["windowEstimates"]["weekly"]
        broker = upc.UniversalProviderBroker(self.root / "dimension.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, request)["reason"], "SCHEMA_VALIDATION_FAILED")

    def test_priority_reserve_floor_applies_per_window(self) -> None:
        native = copy.deepcopy(self.native)
        native["payload"]["weeklyUtilization"] = 0.74
        self.resign_native(native)
        broker = upc.UniversalProviderBroker(self.root / "reserve.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, native_evidence=[native])["reason"], "PRIORITY_RESERVE_FORECAST")

    def test_post_reset_quiet_period_blocks(self) -> None:
        native = copy.deepcopy(self.native)
        native["payload"]["sessionLastResetAt"] = upc.iso(self.now - dt.timedelta(seconds=30))
        self.resign_native(native)
        broker = upc.UniversalProviderBroker(self.root / "quiet.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, native_evidence=[native])["reason"], "POST_RESET_QUIET")

    def test_deterministic_no_work_fingerprint_blocks(self) -> None:
        request = copy.deepcopy(self.request)
        request["priorIdleFingerprint"] = request["demandFingerprint"]
        broker = upc.UniversalProviderBroker(self.root / "idle.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, request)["reason"], "NO_ACTIONABLE_WORK")

    def test_one_thousand_unchanged_ticks_make_zero_provider_calls_and_processes(self) -> None:
        admission = mock.Mock(side_effect=AssertionError("provider boundary called"))
        for _ in range(1000):
            result = upc.route_demand_tick(SHA_B, SHA_B, admission)
            self.assertEqual(result["status"], "IDLE_SKIPPED")
            self.assertEqual(result["providerCalls"], 0)
            self.assertEqual(result["providerProcesses"], 0)
        admission.assert_not_called()

    # Conjugal retained concepts and hostile findings.

    def test_all_four_provider_normalizers_are_exact_and_version_bound(self) -> None:
        expected = {
            "claude": ["session", "weekly"],
            "openai": ["primary", "secondary"],
            "kimi": ["context", "monthly"],
            "grok": ["requests", "tokens"],
        }
        for provider, names in expected.items():
            result = upc.normalize_native_evidence(self.make_native(provider))
            self.assertEqual([item["name"] for item in result["dimensions"]], names)

    def test_provider_adapter_version_mismatch_rejected(self) -> None:
        value = copy.deepcopy(self.native)
        value["adapterVersion"] = "openai-responses/1.0"
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.normalize_native_evidence(value)

    def test_malformed_newest_provider_evidence_never_skips_to_stale(self) -> None:
        old = self.root / "old.json"
        bad = self.root / "new.json"
        old.write_text(json.dumps(self.native), encoding="utf-8")
        bad.write_bytes(b'{"capturedAt":"newest","payload":NaN,"payload":0}')
        with self.assertRaises(upc.ControlError) as caught:
            upc.normalize_evidence_files([old, bad])
        self.assertIn(caught.exception.reason, {"JSON_DUPLICATE_KEY", "JSON_NONFINITE_NUMBER"})

    def test_duplicate_key_nonfinite_invalid_utf8_and_size_are_rejected(self) -> None:
        cases = [
            (b'{"x":1,"x":2}', "JSON_DUPLICATE_KEY"),
            (b'{"x":NaN}', "JSON_NONFINITE_NUMBER"),
            (b'\xff', "UTF8_INVALID"),
            (b' ' * (upc.MAX_INPUT_BYTES + 1), "INPUT_SIZE_LIMIT"),
        ]
        for raw, reason in cases:
            with self.subTest(reason=reason), self.assertRaises(upc.ControlError) as caught:
                upc.strict_json_bytes(raw)
            self.assertEqual(caught.exception.reason, reason)

    def test_json_complexity_is_bounded_before_schema_walk(self) -> None:
        value: object = 0
        for _ in range(upc.MAX_JSON_DEPTH + 1):
            value = [value]
        raw = json.dumps(value).encode("utf-8")
        with self.assertRaisesRegex(upc.ControlError, "JSON_COMPLEXITY_LIMIT"):
            upc.strict_json_bytes(raw)

    def test_quota_identity_is_secret_hmac_and_contains_no_raw_identifier(self) -> None:
        raw = b"opaque-local-account-canary"
        first = upc.derive_quota_domain_id("claude", raw, b"1" * 32)
        second = upc.derive_quota_domain_id("claude", raw, b"2" * 32)
        self.assertNotEqual(first, second)
        self.assertNotIn("account-canary", first)
        self.assertNotEqual(first.split(":" )[-1], hashlib.sha256(raw).hexdigest())

    def test_cli_failure_is_no_echo_and_stderr_empty(self) -> None:
        malicious = self.root / "sensitive-local-value.json"
        malicious.write_bytes(b'{"secret":"SENSITIVE-LOCAL-VALUE","secret":"SENSITIVE-LOCAL-PATH"}')
        run = subprocess.run(
            [sys.executable, str(Path(upc.__file__)), "validate", "request", str(malicious)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stderr, "")
        self.assertNotIn("SENSITIVE-LOCAL-VALUE", run.stdout)
        self.assertNotIn("SENSITIVE-LOCAL-PATH", run.stdout)
        self.assertNotIn(str(malicious), run.stdout)

    def test_project_profile_may_strengthen_but_not_weaken(self) -> None:
        stronger = copy.deepcopy(self.profile)
        stronger["policy"]["maxObservationAgeSeconds"] = 30
        stronger["policy"]["reserveFloorByPriority"]["MAINTENANCE"] = 0.60
        upc.validate_project_profile(stronger)
        weaker = copy.deepcopy(self.profile)
        weaker["policy"]["requiredCapacityDimensions"]["claude-code/1.0"] = ["session", "invented"]
        with self.assertRaisesRegex(upc.ControlError, "PROJECT_PROFILE_WEAKENS_UNIVERSAL"):
            upc.validate_project_profile(weaker)

    def test_multi_host_quota_domain_is_rejected_without_reviewed_shared_backend(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["coordination"]["quotaDomainHostCount"] = 2
        with self.assertRaisesRegex(upc.ControlError, "MULTI_HOST_BACKEND_UNAVAILABLE"):
            upc.validate_project_profile(profile)
        profile["coordination"]["mode"] = "SHARED_BROKER"
        profile["coordination"]["sharedBrokerIdentitySha256"] = SHA_A
        with self.assertRaisesRegex(upc.ControlError, "MULTI_HOST_BACKEND_UNAVAILABLE"):
            upc.validate_project_profile(profile)

    def test_independence_class_is_explicit_and_unknown_blocks(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["independenceClass"] = "UNKNOWN"
        with self.assertRaisesRegex(upc.ControlError, "INDEPENDENCE_CLASS_UNKNOWN"):
            upc.validate_project_profile(profile)

    # Agent Bridge NO-GO reproduction and repair controls.

    def test_reset_auth_and_capacity_return_cannot_open_gate(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "signals.db")
        for index, kind in enumerate(("RESET", "AUTH_SUCCESS", "CAPACITY_RETURN", "QUOTA_REFUSAL")):
            state = broker.record_provider_signal(kind, upc.iso(self.now + dt.timedelta(seconds=index)), SHA_A)
            self.assertEqual(state, "CLOSED")
            self.assertEqual(broker.gate_state(), "CLOSED")

    def test_provider_signals_have_no_task_or_process_mutation_surface(self) -> None:
        source = Path(upc.__file__).read_text(encoding="utf-8")
        forbidden = ("subprocess", "Popen(", "Start-Process", "schtasks", "Enable-ScheduledTask", "os.system")
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_only_adjudication_transition_can_open_gate(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "transition.db")
        transition = {
            "schema": "fleet-universal-gate-transition/v1", "transitionId": "transition-0002",
            "transitionEpoch": 1, "issuedAt": upc.iso(self.now),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)), "from": "CLOSED", "to": "OPEN",
            "cause": "SAFETY_CLOSE", "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health),
            "reviewReceiptSha256": SHA_B, "testReceiptSha256": SHA_C,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        transition["authorizationHmacSha256"] = upc.contract_hmac(
            "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "GATE_TRANSITION_UNAUTHORIZED"):
            broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)

    def test_forged_gate_health_and_capacity_hmacs_fail_closed(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "forged-transition")
        self.bind_runtime(broker)
        transition = {
            "schema": "fleet-universal-gate-transition/v1", "transitionId": "transition-forged",
            "transitionEpoch": 1, "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)), "from": "CLOSED", "to": "OPEN",
            "cause": "INDEPENDENT_ADJUDICATION", "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile), "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health), "reviewReceiptSha256": SHA_B,
            "testReceiptSha256": SHA_C, "authorizationHmacSha256": "hmac-sha256:" + "f" * 64,
        }
        with self.assertRaisesRegex(upc.ControlError, "CONTRACT_HMAC_INVALID"):
            broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)

        admitted = upc.UniversalProviderBroker(self.root / "forged-runtime")
        self.transition(admitted)
        forged_health = copy.deepcopy(self.health)
        forged_health["observerHmacSha256"] = "hmac-sha256:" + "f" * 64
        self.assertEqual(self.authorize(admitted, self.make_request("request-forged-health"), health=forged_health)["reason"], "CONTRACT_HMAC_INVALID")
        forged_capacity = copy.deepcopy(self.native)
        forged_capacity["observerHmacSha256"] = "hmac-sha256:" + "f" * 64
        self.assertEqual(self.authorize(admitted, self.make_request("request-forged-capacity"), native_evidence=[forged_capacity])["reason"], "CONTRACT_HMAC_INVALID")

    def test_final_inside_lock_revalidates_executable_digest(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "exe-drift.db")
        self.transition(broker)
        self.launcher.write_bytes(b"mutated after inventory\n")
        self.assertEqual(self.authorize(broker)["reason"], "INVENTORY_LAUNCHER_DRIFT")

    def test_same_basename_at_different_path_is_not_identity(self) -> None:
        other = self.root / "other" / self.launcher.name
        other.parent.mkdir()
        other.write_bytes(self.launcher.read_bytes())
        request = copy.deepcopy(self.request)
        request["executablePath"] = str(other.resolve())
        request["executableSha256"] = sha_file(other)
        broker = upc.UniversalProviderBroker(self.root / "basename.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, request)["reason"], "LAUNCHER_NOT_IN_COMPLETE_INVENTORY")

    def test_frozen_subject_is_rehashed_inside_lock(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "subject.db")
        self.transition(broker)
        self.subject.write_bytes(b"changed after request freeze\n")
        self.assertEqual(self.authorize(broker)["reason"], "FROZEN_SUBJECT_DRIFT")

    def test_incomplete_launcher_census_cannot_admit(self) -> None:
        inventory = copy.deepcopy(self.inventory)
        inventory["configuredLauncherCount"] = 2
        health = copy.deepcopy(self.health)
        health["inventorySha256"] = upc.digest_json(inventory)
        self.resign_health(health)
        broker = upc.UniversalProviderBroker(self.root / "inventory.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, inventory=inventory, health=health)["reason"], "INVENTORY_INCOMPLETE")

    def test_unknown_or_extra_launcher_blocks_complete_census(self) -> None:
        unknown = copy.deepcopy(self.inventory)
        unknown["launchers"][0]["unknownAuthority"] = "provider"
        broker = upc.UniversalProviderBroker(self.root / "unknown-launcher")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, inventory=unknown)["reason"], "SCHEMA_VALIDATION_FAILED")

        extra = copy.deepcopy(self.inventory)
        extra["launchers"].append(copy.deepcopy(extra["launchers"][0]))
        extra["launchers"][1]["executablePath"] = str(self.subject.resolve())
        extra["launchers"][1]["executableSha256"] = sha_file(self.subject)
        self.assertEqual(self.authorize(broker, self.make_request("request-extra-launcher"), inventory=extra)["reason"], "INVENTORY_INCOMPLETE")

    def test_unqualified_or_stale_broker_health_cannot_admit(self) -> None:
        unqualified = copy.deepcopy(self.health)
        unqualified["observerQualified"] = False
        broker = upc.UniversalProviderBroker(self.root / "unqualified.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, health=unqualified)["reason"], "SCHEMA_VALIDATION_FAILED")
        stale = copy.deepcopy(self.health)
        stale["observedAt"] = upc.iso(self.now - dt.timedelta(minutes=10))
        self.resign_health(stale)
        request = self.make_request("request-health-stale")
        self.assertEqual(self.authorize(broker, request, health=stale)["reason"], "BROKER_HEALTH_STALE")

    def test_missing_or_stale_telemetry_cannot_admit(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "telemetry.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, native_evidence=[])["reason"], "EVIDENCE_SET_INVALID")
        stale = copy.deepcopy(self.native)
        stale["capturedAt"] = upc.iso(self.now - dt.timedelta(minutes=10))
        self.resign_native(stale)
        request = self.make_request("request-telemetry-stale")
        self.assertEqual(self.authorize(broker, request, native_evidence=[stale])["reason"], "CAPACITY_STALE")

    def test_future_health_inventory_and_capacity_are_unevaluable(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "future-evidence")
        self.transition(broker)
        future_health = copy.deepcopy(self.health)
        future_health["observedAt"] = upc.iso(self.now + dt.timedelta(minutes=1))
        self.resign_health(future_health)
        self.assertEqual(self.authorize(broker, self.make_request("request-future-health"), health=future_health)["reason"], "BROKER_HEALTH_STALE")
        future_capacity = copy.deepcopy(self.native)
        future_capacity["capturedAt"] = upc.iso(self.now + dt.timedelta(minutes=1))
        self.resign_native(future_capacity)
        self.assertEqual(self.authorize(broker, self.make_request("request-future-capacity"), native_evidence=[future_capacity])["reason"], "CAPACITY_STALE")

    def test_state_root_identity_prevents_alternate_database_bypass(self) -> None:
        first = upc.UniversalProviderBroker(self.root / "canonical-root")
        self.transition(first)
        profile = copy.deepcopy(self.profile)
        health = copy.deepcopy(self.health)
        second = upc.UniversalProviderBroker(self.root / "alternate-root")
        result = self.authorize(second, self.make_request("request-alternate-root"), profile=profile, health=health)
        self.assertEqual(result["reason"], "STATE_ROOT_IDENTITY_MISMATCH")

    def test_full_child_os_lock_and_exact_orphan_recovery(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "os-lock")
        self.transition(broker)
        result = self.authorize(broker)
        self.assertIn(result["leaseId"], broker._os_locks)
        with self.assertRaisesRegex(upc.ControlError, "ORPHAN_NOT_PROVEN_DEAD"):
            broker.recover_orphan(
                process_observation=self.process_observation(result, "AMBIGUOUS"),
                fleet_secret=self.secret, now=self.now,
            )
        with self.assertRaisesRegex(upc.ControlError, "LEASE_PROCESS_MISMATCH"):
            broker.recover_orphan(
                process_observation=self.process_observation(result, "DEAD", seat_epoch=result["seatEpoch"] + 1),
                fleet_secret=self.secret, now=self.now,
            )
        released = broker.recover_orphan(
            process_observation=self.process_observation(result, "DEAD"),
            fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(released["status"], "RELEASED")
        self.assertNotIn(result["leaseId"], broker._os_locks)

    def test_quota_lock_reparse_directory_or_file_is_rejected(self) -> None:
        original = upc._is_reparse
        for label, predicate in (
            ("directory", lambda path: path.name.endswith(".quota-locks")),
            ("file", lambda path: path.suffix == ".lock"),
        ):
            broker = upc.UniversalProviderBroker(self.root / ("lock-reparse-" + label))
            self.transition(broker)
            request = self.make_request("request-lock-reparse-" + label)
            with mock.patch.object(
                upc,
                "_is_reparse",
                side_effect=lambda path, predicate=predicate: predicate(path) or original(path),
            ):
                result = self.authorize(broker, request)
            self.assertEqual(result["reason"], "QUOTA_LOCK_BOUNDARY_INVALID")
            self.assertEqual(broker._os_locks, {})

    def test_transaction_failure_after_os_lock_releases_handle(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "lock-rollback")
        self.transition(broker)
        connection = sqlite3.connect(broker.database)
        try:
            connection.execute(
                """CREATE TRIGGER reject_request_insert BEFORE INSERT ON requests
                BEGIN SELECT RAISE(ABORT, 'reject'); END"""
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaisesRegex(upc.ControlError, "STATE_UNEVALUABLE"):
            self.authorize(broker)
        self.assertEqual(broker._os_locks, {})

    def test_orphan_recovery_requires_fresh_authenticated_process_observation(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "orphan-observer")
        self.transition(broker)
        result = self.authorize(broker)
        forged = self.process_observation(result, "DEAD")
        forged["observerHmacSha256"] = "hmac-sha256:" + "f" * 64
        with self.assertRaisesRegex(upc.ControlError, "CONTRACT_HMAC_INVALID"):
            broker.recover_orphan(
                process_observation=forged, fleet_secret=self.secret, now=self.now,
            )
        stale = self.process_observation(result, "DEAD")
        stale["observedAt"] = upc.iso(self.now - dt.timedelta(minutes=1))
        stale["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", stale, self.secret, "observerHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "PROCESS_OBSERVATION_STALE"):
            broker.recover_orphan(
                process_observation=stale, fleet_secret=self.secret, now=self.now,
            )

    def test_gate_is_bound_to_exact_project_profile(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "profile-drift.db")
        self.transition(broker)
        changed = copy.deepcopy(self.profile)
        changed["policy"]["maxObservationAgeSeconds"] = 30
        health = copy.deepcopy(self.health)
        health["projectProfileSha256"] = upc.digest_json(changed)
        self.resign_health(health)
        request = copy.deepcopy(self.request)
        self.assertEqual(self.authorize(broker, request, profile=changed, health=health)["reason"], "GATE_PROFILE_DRIFT")

    def test_attestation_binds_path_hash_model_effort_role_and_subject(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "binding.db")
        self.transition(broker)
        result = self.authorize(broker)
        self.assertEqual(result["status"], "ALLOW_ATTESTED")
        upc.validate_contract("attestation", result)
        variants = []
        for field, value in (("model", "other-model"), ("effort", "low"), ("role", "REVIEW"), ("subjectSha256", SHA_D)):
            changed = copy.deepcopy(self.request)
            changed["requestId"] = "request-bind-" + field
            changed[field] = value
            variants.append(changed)
        for changed in variants:
            other = upc.UniversalProviderBroker(self.root / (changed["requestId"] + ".db"))
            self.transition(other)
            outcome = self.authorize(other, changed)
            if changed["subjectSha256"] == SHA_D:
                self.assertEqual(outcome["reason"], "ARGV_BINDING_DRIFT")
            elif changed["model"] != self.request["model"] or changed["effort"] != self.request["effort"]:
                self.assertEqual(outcome["reason"], "ARGV_BINDING_DRIFT")
            else:
                self.assertEqual(outcome["status"], "ALLOW_ATTESTED")
                self.assertNotEqual(outcome["bindingSha256"], result["bindingSha256"])

    def test_canary_requires_manual_authorization(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "canary.db")
        self.transition(broker, "CANARY")
        self.assertEqual(self.authorize(broker)["reason"], "CANARY_AUTHORIZATION_REQUIRED")
        request = copy.deepcopy(self.request)
        request["requestId"] = "request-canary-authorized"
        request["canary"] = True
        authorization = {
            "schema": "fleet-universal-manual-canary-authorization/v1",
            "authorizationId": "canary-auth-0001",
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "requestBindingSha256": upc.canary_request_binding(request),
            "quotaDomainId": request["quotaDomainId"],
            "projectProfileSha256": upc.digest_json(self.profile),
            "reviewerReceiptSha256": SHA_D,
            "oneUse": True,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        authorization["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", authorization, self.secret, "authorizationHmacSha256"
        )
        request["manualAuthorizationSha256"] = upc.digest_json(authorization)
        self.assertEqual(self.authorize(broker, request, manual_authorization=authorization)["status"], "ALLOW_ATTESTED")

    def test_canary_authorization_is_fresh_exact_and_one_use(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "canary-one-use")
        self.transition(broker, "CANARY")
        request = self.make_request("request-canary-first")
        request["canary"] = True
        authorization = {
            "schema": "fleet-universal-manual-canary-authorization/v1", "authorizationId": "canary-auth-shared",
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "requestBindingSha256": upc.canary_request_binding(request),
            "quotaDomainId": request["quotaDomainId"], "projectProfileSha256": upc.digest_json(self.profile),
            "reviewerReceiptSha256": SHA_D, "oneUse": True,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        authorization["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", authorization, self.secret, "authorizationHmacSha256"
        )
        request["manualAuthorizationSha256"] = upc.digest_json(authorization)
        first = self.authorize(broker, request, manual_authorization=authorization)
        self.assertEqual(first["status"], "ALLOW_ATTESTED")
        broker.release_child(
            process_observation=self.process_observation(first, "EXITED", phase="TERMINAL"),
            fleet_secret=self.secret, now=self.now,
        )
        second = self.make_request("request-canary-second")
        second["canary"] = True
        reused = copy.deepcopy(authorization)
        reused["requestBindingSha256"] = upc.canary_request_binding(second)
        reused["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", reused, self.secret, "authorizationHmacSha256"
        )
        second["manualAuthorizationSha256"] = upc.digest_json(reused)
        self.assertEqual(self.authorize(broker, second, manual_authorization=reused)["reason"], "AUTOMATIC_LAUNCH_GATE_CLOSED")

        stale = self.make_request("request-canary-stale")
        stale["canary"] = True
        expired = copy.deepcopy(authorization)
        expired["authorizationId"] = "canary-auth-expired"
        expired["issuedAt"] = upc.iso(self.now - dt.timedelta(minutes=10))
        expired["expiresAt"] = upc.iso(self.now - dt.timedelta(minutes=1))
        expired["requestBindingSha256"] = upc.canary_request_binding(stale)
        expired["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", expired, self.secret, "authorizationHmacSha256"
        )
        stale["manualAuthorizationSha256"] = upc.digest_json(expired)
        self.assertEqual(self.authorize(broker, stale, manual_authorization=expired)["reason"], "AUTOMATIC_LAUNCH_GATE_CLOSED")

    def test_argv_config_capsule_compaction_cache_and_bounds_are_enforced(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "efficiency-binding")
        self.transition(broker)
        config_drift = self.make_request("request-config-drift")
        self.launcher_config.write_bytes(b"drift")
        self.assertEqual(self.authorize(broker, config_drift)["reason"], "LAUNCHER_CONFIG_DRIFT")
        self.launcher_config.write_bytes(b'{"directProviderInvocation":false}\n')

        over_turns = self.make_request("request-over-turns")
        over_turns["maxTurns"] = self.profile["efficiency"]["maxTurns"] + 1
        self.assertEqual(self.authorize(broker, over_turns)["reason"], "TURN_BOUND_EXCEEDED")
        over_context = self.make_request("request-over-context")
        over_context["maxContextTokens"] = self.profile["efficiency"]["maxContextTokens"] + 1
        self.assertEqual(self.authorize(broker, over_context)["reason"], "CONTEXT_BOUND_EXCEEDED")

    def test_unbounded_unvalidated_request_is_rejected_before_replay_digest(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "prehash-bound")
        request = copy.deepcopy(self.request)
        request["argv"] = ["x"] * (upc.MAX_ARRAY_ITEMS + 1)
        self.bind_runtime(broker)
        process = self.admission_observation(request)
        with mock.patch.object(upc, "digest_json", side_effect=AssertionError("hashed before validation")):
            result = self.authorize(
                broker, request, profile=self.profile, health=self.health, process_observation=process
            )
        self.assertEqual(result["reason"], "JSON_COMPLEXITY_LIMIT")

    # Exact d98934c R1 RED -> R2 GREEN stranger-review discriminators.  Each control names the
    # consolidated finding it reproduces; transplanting these tests onto R1 leaves the unsafe
    # behavior observable, while this candidate must fail closed.

    def test_r2_01_signed_gate_record_r1_red_r2_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r2-gate-bytes")
        self.transition(broker)
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "OPEN")
        connection = sqlite3.connect(broker.database)
        try:
            connection.execute("UPDATE gate_state SET transition_hmac=?", ("hmac-sha256:" + "f" * 64,))
            connection.commit()
        finally:
            connection.close()
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")
        self.assertNotEqual(self.authorize(broker, self.make_request("request-r2-gate"))["status"], "ALLOW_ATTESTED")

    def test_r2_02_multihost_declaration_r1_red_r2_green(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["coordination"].update(
            quotaDomainHostCount=2, mode="SHARED_BROKER", sharedBrokerIdentitySha256=SHA_A
        )
        with self.assertRaisesRegex(upc.ControlError, "MULTI_HOST_BACKEND_UNAVAILABLE"):
            upc.validate_project_profile(profile)

    def test_r2_03_process_receipts_r1_red_r2_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r2-process")
        self.transition(broker)
        forged = self.admission_observation(self.request)
        forged["actualArgv"] = list(forged["actualArgv"]) + ["--unbound"]
        forged["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", forged, self.secret, "observerHmacSha256"
        )
        self.assertEqual(self.authorize(broker, process_observation=forged)["reason"], "PROCESS_OBSERVATION_ARGV_INVALID")

    def test_r2_04_replay_restart_authority_r1_red_r2_green(self) -> None:
        root = self.root / "r2-restart"
        first_broker = upc.UniversalProviderBroker(root)
        self.transition(first_broker)
        first = self.authorize(first_broker)
        self.assertEqual(first["status"], "ALLOW_ATTESTED")
        with self.assertRaisesRegex(upc.ControlError, "ACTIVE_LEASES_REMAIN"):
            first_broker.close()
        restarted = upc.UniversalProviderBroker(root)
        self.assertEqual(self.authorize(restarted)["reason"], "ACTIVE_AUTHORITY_NOT_REPLAYABLE")
        connection = sqlite3.connect(restarted.database)
        try:
            self.assertEqual(connection.execute("SELECT state FROM leases").fetchone()[0], "RESUME_ATTESTED")
        finally:
            connection.close()
        restarted.release_child(
            process_observation=self.process_observation(first, "EXITED", phase="TERMINAL"),
            fleet_secret=self.secret,
            now=self.now,
        )
        restarted.close()

    def test_r2_05_canary_epoch_and_reseal_r1_red_r2_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r2-canary")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r2-canary")
        request["canary"] = True
        authorization = {
            "schema": "fleet-universal-manual-canary-authorization/v1", "authorizationId": "canary-r2-0001",
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)), "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "requestBindingSha256": upc.canary_request_binding(request), "quotaDomainId": request["quotaDomainId"],
            "projectProfileSha256": upc.digest_json(self.profile), "reviewerReceiptSha256": SHA_D,
            "oneUse": True, "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        authorization["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", authorization, self.secret, "authorizationHmacSha256"
        )
        request["manualAuthorizationSha256"] = upc.digest_json(authorization)
        result = self.authorize(broker, request, manual_authorization=authorization)
        broker.release_child(
            process_observation=self.process_observation(result, "FAILED", phase="TERMINAL"),
            fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")

    def test_r2_06_complete_inventory_bytes_r1_red_r2_green(self) -> None:
        duplicate = copy.deepcopy(self.inventory)
        second = copy.deepcopy(duplicate["launchers"][0])
        second["executableSha256"] = SHA_A
        duplicate["launchers"].append(second)
        duplicate["configuredLauncherCount"] = duplicate["observedLauncherCount"] = 2
        duplicate["configuredSurfaceCounts"]["REPOSITORY_WRAPPER"] = 2
        duplicate["observedSurfaceCounts"]["REPOSITORY_WRAPPER"] = 2
        with self.assertRaisesRegex(upc.ControlError, "INVENTORY_AMBIGUOUS"):
            upc._validate_inventory(duplicate)

    def test_r2_07_two_phase_retained_handles_r1_red_r2_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r2-two-phase")
        self.transition(broker)
        prepared = self.authorize(broker, confirm=False)
        self.assertEqual(prepared["status"], "PREPARED_SUSPENDED")
        with mock.patch.object(broker, "_artifact_handles_are_current", return_value=False):
            receipt = self.admission_observation(self.request, phase="RESUME", lease_id=prepared["leaseId"])
            with self.assertRaisesRegex(upc.ControlError, "RESUME_BOUNDARY_DRIFT"):
                broker.confirm_resume_boundary(
                    lease_id=prepared["leaseId"], process_observation=receipt,
                    fleet_secret=self.secret, now=self.now,
                )

    def test_r2_08_portable_git_blob_manifest_r1_red_r2_green(self) -> None:
        import check_universal_manifest as checker

        raw = checker._git(checker._blob_spec(":", checker.MANIFEST))
        self.assertIsInstance(raw, bytes)
        matches = list(checker.SELF_PATTERN.finditer(raw))
        self.assertEqual(len(matches), 1)
        value = json.loads(raw.decode("utf-8"))["manifestSelf"]["canonicalGitBlobSha256"]
        self.assertEqual(value, checker.canonical_self_sha256(raw))

    def test_r2_09_digest_grammar_r1_red_r2_green(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r2-digest")
        with self.assertRaisesRegex(upc.ControlError, "PROVIDER_SIGNAL_INVALID"):
            broker.record_provider_signal("RESET", upc.iso(self.now), "x" * 71)

    def test_r2_10_capacity_and_request_timeline_r1_red_r2_green(self) -> None:
        broken = copy.deepcopy(self.native)
        broken["payload"]["sessionLastResetAt"] = upc.iso(self.now)
        broken["payload"]["sessionResetAt"] = upc.iso(self.now - dt.timedelta(seconds=1))
        self.resign_native(broken)
        broker = upc.UniversalProviderBroker(self.root / "r2-timeline")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, native_evidence=[broken])["reason"], "CAPACITY_TIME_INVALID")
        request = self.make_request("request-r2-validity")
        request["expiresAt"] = upc.iso(self.now + dt.timedelta(minutes=16))
        self.assertEqual(self.authorize(broker, request)["reason"], "REQUEST_TIME_INVALID")

    def test_r2_11_bounded_hashing_and_amplification_r1_red_r2_green(self) -> None:
        source = self.root / "r2-amplification.bin"
        source.write_bytes(b"x" * 4096)
        request = self.capsule_request(source, lengths=[1])
        request["maxAmplificationRatio"] = 1
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_SIZE_LIMIT"):
            upc.build_evidence_capsule(request, self.root / "r2-amplification.out")

    def test_r2_12_dual_platform_hash_locked_workflow_r1_red_r2_green(self) -> None:
        workflow = (ROOT / ".github/workflows/provider-capacity-governor.yml").read_text(encoding="utf-8")
        for token in ("windows-latest", "ubuntu-latest", "--require-hashes", "timeout-minutes: 15"):
            self.assertIn(token, workflow)
        self.assertIn("check_universal_manifest.py --treeish HEAD", workflow)

    def test_r2_13_candidate_not_ratified_r1_red_r2_green(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ratified, proposed = readme.split("## Proposed amendments (not ratified)", 1)
        self.assertNotIn("fleet-universal-provider-control-reconciliation", ratified)
        self.assertIn("fleet-universal-provider-control-reconciliation", proposed)

    def test_r2_14_lock_and_rollback_controls_remain_r1_red_r2_green(self) -> None:
        source = Path(upc.__file__).read_text(encoding="utf-8")
        for token in ("_is_reparse(path)", "_release_terminal_owners(held_lease_id)"):
            self.assertIn(token, source)

    # Exact 4fc0fe1 R2 RED -> R3 GREEN review twins.

    def test_r3_01_expired_prepared_lease_never_allows_and_remains_fenced(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r3-expired-resume")
        self.transition(broker)
        request = self.make_request("request-r3-expired")
        request["maxWallSeconds"] = 1
        prepared = self.authorize(broker, request, confirm=False)
        later = self.now + dt.timedelta(seconds=2)
        receipt = self.admission_observation(request, phase="RESUME", lease_id=prepared["leaseId"])
        receipt["observedAt"] = upc.iso(later)
        receipt["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", receipt, self.secret, "observerHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "LEASE_EXPIRED_BEFORE_RESUME"):
            broker.confirm_resume_boundary(
                lease_id=prepared["leaseId"], process_observation=receipt,
                fleet_secret=self.secret, now=later,
            )
        self.assertIn(prepared["leaseId"], broker._os_locks)
        self.assertIn(prepared["leaseId"], broker._artifact_handles)
        connection = sqlite3.connect(broker.database)
        try:
            self.assertEqual(connection.execute("SELECT state FROM leases").fetchone()[0], "ACTIVE")
        finally:
            connection.close()

        canary_broker = upc.UniversalProviderBroker(self.root / "r3-expired-canary")
        self.transition(canary_broker, "CANARY")
        canary_request = self.make_request("request-r3-expired-canary")
        canary_request["maxWallSeconds"] = 1
        canary_request["canary"] = True
        authorization = self.make_canary_authorization(canary_request, "canary-r3-expiry")
        canary_prepared = self.authorize(
            canary_broker, canary_request, manual_authorization=authorization, confirm=False
        )
        canary_receipt = self.admission_observation(
            canary_request, phase="RESUME", lease_id=canary_prepared["leaseId"]
        )
        canary_receipt["observedAt"] = upc.iso(later)
        canary_receipt["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", canary_receipt, self.secret, "observerHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "LEASE_EXPIRED_BEFORE_RESUME"):
            canary_broker.confirm_resume_boundary(
                lease_id=canary_prepared["leaseId"], process_observation=canary_receipt,
                fleet_secret=self.secret, now=later,
            )
        self.assertEqual(canary_broker.gate_state(fleet_secret=self.secret, now=later), "CLOSED")

    def test_r3_02_capacity_rollover_blocks_pre_reset_evidence(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r3-rollover")
        self.transition(broker)
        rolled = copy.deepcopy(self.native)
        for key in ("sessionResetAt", "weeklyResetAt"):
            rolled["payload"][key] = upc.iso(self.now - dt.timedelta(seconds=1))
        self.resign_native(rolled)
        self.assertEqual(self.authorize(broker, native_evidence=[rolled])["reason"], "CAPACITY_WINDOW_ROLLED_OVER")

    def test_r3_03_capsule_unique_open_and_actual_handle_limits(self) -> None:
        source = self.root / "r3-one-open.bin"
        source.write_bytes(bytes(range(64)) * 64)
        request = self.capsule_request(source, lengths=[64, 64, 64])
        real_open = Path.open
        source_opens = 0

        def counted_open(path: Path, *args, **kwargs):
            nonlocal source_opens
            if path == source:
                source_opens += 1
            return real_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", autospec=True, side_effect=counted_open):
            result = upc.build_evidence_capsule(request, self.root / "r3-one-open.out")
        self.assertEqual(result["sliceCount"], 3)
        self.assertEqual(source_opens, 1)
        limited = self.capsule_request(source, lengths=[64])
        limited["maxSourceBytes"] = 1024
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_SIZE_LIMIT"):
            upc.build_evidence_capsule(limited, self.root / "r3-limited.out")

    def test_r3_04_capsule_unexpected_pre_publish_failure_cleans_all(self) -> None:
        source = self.root / "r3-cleanup-source.bin"
        source.write_bytes(b"stable-source")
        request = self.capsule_request(source, lengths=[6])
        output = self.root / "r3-cleanup.out"
        real_validate = upc.validate_contract

        def validate_then_fail(kind, value):
            real_validate(kind, value)
            if kind == "capsule":
                raise RuntimeError("private unexpected detail")

        with mock.patch.object(upc, "validate_contract", side_effect=validate_then_fail):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_INTERNAL_FAILURE"):
                upc.build_evidence_capsule(request, output)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob("r3-cleanup.out.tmp-*")), [])

    def test_r3_05_window_estimates_value_and_digest_are_attested(self) -> None:
        first_broker = upc.UniversalProviderBroker(self.root / "r3-estimates-a")
        self.transition(first_broker)
        first = self.authorize(first_broker)
        self.assertEqual(first["windowEstimates"], self.request["windowEstimates"])
        self.assertEqual(first["windowEstimatesSha256"], upc.digest_json(self.request["windowEstimates"]))
        changed = self.make_request("request-r3-estimates-b")
        changed["windowEstimates"] = {"session": 0.04, "weekly": 0.04}
        second_broker = upc.UniversalProviderBroker(self.root / "r3-estimates-b")
        self.transition(second_broker)
        second = self.authorize(second_broker, changed)
        self.assertNotEqual(first["bindingSha256"], second["bindingSha256"])

    def test_r3_06_ambiguous_canary_recovery_reseals_and_malformed_is_stable(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r3-canary-recovery")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r3-canary-recovery")
        request["canary"] = True
        authorization = {
            "schema": "fleet-universal-manual-canary-authorization/v1", "authorizationId": "canary-r3-recovery",
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)), "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "requestBindingSha256": upc.canary_request_binding(request), "quotaDomainId": request["quotaDomainId"],
            "projectProfileSha256": upc.digest_json(self.profile), "reviewerReceiptSha256": SHA_D,
            "oneUse": True, "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        authorization["authorizationHmacSha256"] = upc.contract_hmac(
            "manual-canary-authorization-v1", authorization, self.secret, "authorizationHmacSha256"
        )
        request["manualAuthorizationSha256"] = upc.digest_json(authorization)
        result = self.authorize(broker, request, manual_authorization=authorization)
        with self.assertRaisesRegex(upc.ControlError, "ORPHAN_NOT_PROVEN_DEAD"):
            broker.recover_orphan(
                process_observation=self.process_observation(result, "AMBIGUOUS"),
                fleet_secret=self.secret, now=self.now,
            )
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")
        self.assertIn(result["leaseId"], broker._os_locks)
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            broker.recover_orphan(process_observation={}, fleet_secret=self.secret, now=self.now)

    # Exact 1c06687 R3 RED -> R4 GREEN capsule review twins.

    def test_r4_01_single_pass_mutation_bytes_match_bound_source_hash(self) -> None:
        source = self.root / "r4-same-size-mutation.bin"
        original = b"ORIGINAL-BOUND"
        mutated = b"MUTATED!-BOUND"
        self.assertEqual(len(original), len(mutated))
        source.write_bytes(original)
        original_stat = source.stat()
        request = self.capsule_request(source, lengths=[len(original)])
        output = self.root / "r4-same-size-mutation.out"
        real_open = Path.open

        class MutatingReader:
            def __init__(inner_self, handle):
                inner_self.handle = handle
                inner_self.mutated = False

            def fileno(inner_self):
                return inner_self.handle.fileno()

            def read(inner_self, count=-1):
                data = inner_self.handle.read(count)
                if data and inner_self.handle.tell() == len(original) and not inner_self.mutated:
                    descriptor = upc.os.open(str(source), upc.os.O_WRONLY | upc.os.O_TRUNC)
                    try:
                        upc.os.write(descriptor, mutated)
                    finally:
                        upc.os.close(descriptor)
                    upc.os.utime(source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
                    inner_self.mutated = True
                return data

            def close(inner_self):
                inner_self.handle.close()

        def open_dispatch(path: Path, *args, **kwargs):
            handle = real_open(path, *args, **kwargs)
            mode = args[0] if args else kwargs.get("mode", "r")
            return MutatingReader(handle) if path == source and mode == "rb" else handle

        with mock.patch.object(Path, "open", autospec=True, side_effect=open_dispatch):
            result = upc.build_evidence_capsule(request, output)
        self.assertEqual(source.read_bytes(), mutated)
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(result["capsuleSha256"], sha_file(output))

    def test_r4_02_growing_source_reads_fixed_budget_plus_one_probe(self) -> None:
        source = self.root / "r4-growing.bin"
        source.write_bytes(b"g" * 1024)
        request = self.capsule_request(source, lengths=[64])
        output = self.root / "r4-growing.out"
        real_open = Path.open
        observed = {"bytes": 0}

        class GrowingReader:
            def __init__(inner_self, handle):
                inner_self.handle = handle

            def fileno(inner_self):
                return inner_self.handle.fileno()

            def read(inner_self, count=-1):
                if observed["bytes"] >= 1025:
                    raise AssertionError("unbounded growth read")
                data = inner_self.handle.read(count)
                if not data:
                    data = b"x" * (1 if count < 0 else min(count, 1))
                observed["bytes"] += len(data)
                return data

            def close(inner_self):
                inner_self.handle.close()

        def open_dispatch(path: Path, *args, **kwargs):
            handle = real_open(path, *args, **kwargs)
            mode = args[0] if args else kwargs.get("mode", "r")
            return GrowingReader(handle) if path == source and mode == "rb" else handle

        with mock.patch.object(Path, "open", autospec=True, side_effect=open_dispatch):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_GROWTH"):
                upc.build_evidence_capsule(request, output)
        self.assertEqual(observed["bytes"], 1025)
        self.assertFalse(output.exists())

    def test_r4_03_no_clobber_publication_preserves_foreign_races(self) -> None:
        source = self.root / "r4-publication-source.bin"
        source.write_bytes(b"publication-source")
        request = self.capsule_request(source, lengths=[8])
        real_publication = upc._publication_syscall

        raced_output = self.root / "r4-raced-output.bin"
        foreign = b"FOREIGN-AFTER-PRECHECK"

        def create_foreign_then_link(src, dst, **kwargs):
            Path(dst).write_bytes(foreign)
            return real_publication(src, dst, **kwargs)

        with mock.patch.object(upc, "_publication_syscall", side_effect=create_foreign_then_link):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_OUTPUT_EXISTS"):
                upc.build_evidence_capsule(request, raced_output)
        self.assertEqual(raced_output.read_bytes(), foreign)

        replaced_output = self.root / "r4-replaced-output.bin"
        replacement = b"FOREIGN-REPLACEMENT"

        def replace_owned_then_fail(src, dst, **kwargs):
            real_publication(src, dst, **kwargs)
            Path(dst).unlink()
            Path(dst).write_bytes(replacement)
            raise RuntimeError("private publication failure")

        with mock.patch.object(upc, "_publication_syscall", side_effect=replace_owned_then_fail):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_PUBLICATION_IDENTITY_DRIFT"):
                upc.build_evidence_capsule(request, replaced_output)
        self.assertEqual(replaced_output.read_bytes(), replacement)

    # Exact b48c882 R4 RED -> R5 GREEN review twins.

    def test_r5_01_publication_binds_retained_temp_identity_and_exact_bytes(self) -> None:
        source = self.root / "r5-publication-source.bin"
        source.write_bytes(b"retained-publication-source")
        foreign_source = self.root / "r5-foreign-link-source.bin"
        foreign_source.write_bytes(b"FOREIGN-LINK-BYTES")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r5-substituted-publication.bin"
        real_publication = upc._publication_syscall

        def substitute_source_path(_src, dst, **_kwargs):
            real_publication(foreign_source, dst)

        with mock.patch.object(upc, "_publication_syscall", side_effect=substitute_source_path):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_PUBLICATION_IDENTITY_DRIFT"):
                upc.build_evidence_capsule(request, output)
        self.assertEqual(output.read_bytes(), foreign_source.read_bytes())
        self.assertEqual(list(self.root.glob("r5-substituted-publication.bin.tmp-*")), [])

    def test_r5_02_temp_collision_preserves_foreign_temp_and_reason(self) -> None:
        source = self.root / "r5-temp-collision-source.bin"
        source.write_bytes(b"temp-collision-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r5-temp-collision.bin"
        foreign_temp = output.with_name(output.name + ".tmp-owned")
        foreign = b"FOREIGN-TEMP-MUST-SURVIVE"
        foreign_temp.write_bytes(foreign)

        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_TEMP_COLLISION"):
            upc.build_evidence_capsule(request, output)
        self.assertEqual(foreign_temp.read_bytes(), foreign)
        self.assertFalse(output.exists())

    def test_r5_03_retained_artifact_resume_reads_expected_plus_one_only(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r5-retained-growth")
        self.transition(broker)
        prepared = self.authorize(broker, confirm=False)
        lease_id = prepared["leaseId"]
        retained = broker._artifact_handles[lease_id]
        path, real_handle, identity, digest, ceiling = retained[0]
        expected_size = int(identity[2])
        observed = {"bytes": 0}

        class GrowingRetainedHandle:
            @property
            def closed(inner_self):
                return real_handle.closed

            def fileno(inner_self):
                return real_handle.fileno()

            def seek(inner_self, *args):
                return real_handle.seek(*args)

            def read(inner_self, count=-1):
                if observed["bytes"] >= expected_size + 1:
                    raise AssertionError("unbounded retained-artifact read")
                data = real_handle.read(count)
                if not data:
                    data = b"x"
                observed["bytes"] += len(data)
                return data

            def close(inner_self):
                real_handle.close()

        retained[0] = (path, GrowingRetainedHandle(), identity, digest, ceiling)
        receipt = self.admission_observation(self.request, phase="RESUME", lease_id=lease_id)
        try:
            with self.assertRaisesRegex(upc.ControlError, "RESUME_BOUNDARY_DRIFT"):
                broker.confirm_resume_boundary(
                    lease_id=lease_id, process_observation=receipt,
                    fleet_secret=self.secret, now=self.now,
                )
            self.assertEqual(observed["bytes"], expected_size + 1)
        finally:
            broker.recover_orphan(
                process_observation=self.process_observation(prepared, "DEAD"),
                fleet_secret=self.secret,
                now=self.now,
            )

    def test_r5_04_sixty_four_hardlink_aliases_use_one_open_hash_pass(self) -> None:
        source = self.root / "r5-alias-source.bin"
        source.write_bytes(bytes(range(64)))
        aliases = [source]
        for index in range(1, 64):
            alias = self.root / f"r5-alias-{index:02d}.bin"
            upc.os.link(source, alias)
            aliases.append(alias)
        request = self.capsule_request(source, lengths=[1] * 64)
        request["maxSourceBytes"] = 64
        for item, alias in zip(request["slices"], aliases, strict=True):
            item["localPath"] = str(alias)

        real_open = Path.open
        alias_opens = 0

        def count_alias_opens(path: Path, *args, **kwargs):
            nonlocal alias_opens
            mode = args[0] if args else kwargs.get("mode", "r")
            if path in aliases and mode == "rb":
                alias_opens += 1
            return real_open(path, *args, **kwargs)

        output = self.root / "r5-alias-capsule.bin"
        with mock.patch.object(Path, "open", autospec=True, side_effect=count_alias_opens):
            result = upc.build_evidence_capsule(request, output)
        self.assertEqual(alias_opens, 1)
        self.assertEqual(result["payloadBytes"], 64)
        self.assertEqual(output.read_bytes(), bytes(range(64)))

        conflicting = copy.deepcopy(request)
        conflicting["slices"][1]["sourceSha256"] = SHA_A
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_DIGEST_CONFLICT"):
            upc.build_evidence_capsule(conflicting, self.root / "r5-alias-conflict.bin")

        real_stat = Path.stat

        class StatWithConflictingSize:
            def __init__(inner_self, value):
                inner_self.value = value
                inner_self.st_size = value.st_size + 1

            def __getattr__(inner_self, name):
                return getattr(inner_self.value, name)

        def conflicting_alias_size(path: Path, *args, **kwargs):
            value = real_stat(path, *args, **kwargs)
            if path == aliases[1] and kwargs.get("follow_symlinks") is False:
                return StatWithConflictingSize(value)
            return value

        # Install a permissive replacement instead of autospeccing Path.stat: Python 3.14 adds
        # signature details that differ from 3.13, while this control only needs the returned stat.
        with mock.patch.object(Path, "stat", new=conflicting_alias_size):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_SIZE_CONFLICT"):
                upc.build_evidence_capsule(request, self.root / "r5-alias-size-conflict.bin")

    def test_r5_05_link_raise_after_real_link_is_verified_success(self) -> None:
        source = self.root / "r5-link-raise-source.bin"
        source.write_bytes(b"link-raise-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r5-link-raise-output.bin"
        real_publication = upc._publication_syscall

        def link_then_raise(src, dst, **kwargs):
            real_publication(src, dst, **kwargs)
            raise RuntimeError("private wrapper failure after link")

        with mock.patch.object(upc, "_publication_syscall", side_effect=link_then_raise):
            result = upc.build_evidence_capsule(request, output)
        self.assertEqual(result["capsuleSha256"], sha_file(output))
        self.assertEqual(output.read_bytes(), source.read_bytes()[:8])

    # Exact 58e4146 R5 RED -> R6 GREEN cleanup-ownership twins.

    def test_r6_01_private_temp_replacement_survives_handle_bound_cleanup(self) -> None:
        source = self.root / "r6-private-source.bin"
        source.write_bytes(b"private-cleanup-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r6-private-output.bin"
        temporary = output.with_name(output.name + ".tmp-owned")
        foreign_source = self.root / "r6-private-foreign.bin"
        foreign = b"FOREIGN-PRIVATE-REPLACEMENT"
        foreign_source.write_bytes(foreign)
        real_validate = upc.validate_contract
        real_arm = upc._arm_owned_temp_discard

        def fail_after_temp(kind, value):
            real_validate(kind, value)
            if kind == "capsule":
                raise RuntimeError("private validation failure")

        def swap_then_arm(handle, named):
            if temporary.exists():
                temporary.unlink()
            upc.os.replace(foreign_source, temporary)
            try:
                real_arm(handle, named)
            except OSError:
                # R9 treats any false/rejected disposition as refusal.  This older replacement
                # survival twin supplies its explicit successful-discard outcome independently.
                pass
            # Unlinking the original name already placed the retained Windows file object into
            # delete-pending state; the replacement occupant is independent and must survive.
            return True

        with mock.patch.object(upc, "validate_contract", side_effect=fail_after_temp):
            with mock.patch.object(upc, "_arm_owned_temp_discard", side_effect=swap_then_arm):
                with self.assertRaisesRegex(upc.ControlError, "CAPSULE_INTERNAL_FAILURE"):
                    upc.build_evidence_capsule(request, output)
        self.assertEqual(temporary.read_bytes(), foreign)
        self.assertFalse(output.exists())
        temporary.unlink()

    def test_r6_02_public_replacement_survives_and_no_path_cleanup_exists(self) -> None:
        import inspect

        implementation = inspect.getsource(upc.build_evidence_capsule)
        self.assertNotIn("_unlink_only_if_identity", implementation)
        self.assertNotIn("output_path.unlink", implementation)
        source = self.root / "r6-public-source.bin"
        source.write_bytes(b"public-cleanup-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r6-public-output.bin"
        foreign = b"FOREIGN-PUBLIC-REPLACEMENT"
        real_publish = upc._publish_owned_temporary

        def publish_swap_raise(handle, temporary, named, destination):
            real_publish(handle, temporary, named, destination)
            Path(destination).unlink()
            Path(destination).write_bytes(foreign)
            raise RuntimeError("private post-publication failure")

        with mock.patch.object(upc, "_publish_owned_temporary", side_effect=publish_swap_raise):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_PUBLICATION_IDENTITY_DRIFT"):
                upc.build_evidence_capsule(request, output)
        self.assertEqual(output.read_bytes(), foreign)

    def test_r6_03_cleanup_refusal_is_surfaced_and_bounds_repetition(self) -> None:
        source = self.root / "r6-refusal-source.bin"
        source.write_bytes(b"cleanup-refusal-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r6-refusal-output.bin"

        real_open_owned = upc._open_owned_temporary
        open_calls = 0

        def forced_named(temporary, candidate_output):
            nonlocal open_calls
            open_calls += 1
            if open_calls == 1:
                return temporary.open("x+b"), True
            return real_open_owned(temporary, candidate_output)

        with mock.patch.object(upc, "_open_owned_temporary", side_effect=forced_named):
            with mock.patch.object(upc, "_arm_owned_temp_discard", return_value=False):
                result = upc.build_evidence_capsule(request, output)
                self.assertEqual(result["temporaryCleanup"], "REFUSED_BOUNDED")
                leftovers = list(self.root.glob("r6-refusal-output.bin.tmp-*"))
                self.assertEqual(len(leftovers), upc.MAX_CAPSULE_TEMP_BACKLOG)
                self.assertTrue(output.with_name(output.name + ".cleanup-blocked").exists())
                with self.assertRaisesRegex(upc.ControlError, "CAPSULE_TEMP_BACKLOG"):
                    upc.build_evidence_capsule(request, output)
        self.assertEqual(output.read_bytes(), source.read_bytes()[:8])
        for leftover in self.root.glob("r6-refusal-output.bin.tmp-*"):
            leftover.unlink()
        output.with_name(output.name + ".cleanup-blocked").unlink()

    # Exact 300e2bb R6 RED -> R7 GREEN portability and cleanup-contract twins.

    def test_r7_01_unprivileged_linux_proc_fd_publication(self) -> None:
        implementation = (
            inspect.getsource(upc._publish_owned_temporary)
            + inspect.getsource(upc._publication_syscall)
        )
        self.assertIn("/proc/self/fd/", implementation)
        self.assertIn("0x400", implementation)
        self.assertNotIn("0x1000", implementation)
        if os.name != "posix":
            return
        if os.geteuid() == 0:
            self.skipTest("control requires an ordinary unprivileged account")
        if not Path("/proc/self/fd").is_dir() or not getattr(os, "O_TMPFILE", 0):
            self.skipTest("procfs O_TMPFILE route is unavailable")

        source = self.root / "r7-unprivileged-source.bin"
        source.write_bytes(b"ordinary-linux-publication")
        request = self.capsule_request(source, lengths=[12])
        output = self.root / "r7-unprivileged-output.bin"
        observed_named: list[bool] = []
        real_open_owned = upc._open_owned_temporary

        def capture_route(temporary, candidate_output):
            handle, named = real_open_owned(temporary, candidate_output)
            observed_named.append(named)
            return handle, named

        with mock.patch.object(upc, "_open_owned_temporary", side_effect=capture_route):
            result = upc.build_evidence_capsule(request, output)
        if observed_named == [True]:
            self.skipTest("test filesystem does not support O_TMPFILE")
        self.assertEqual(observed_named, [False])
        self.assertEqual(result["temporaryCleanup"], "CLEAN")
        self.assertEqual(output.read_bytes(), source.read_bytes()[:12])

    def test_r7_02_temporary_cleanup_is_required_runtime_evidence(self) -> None:
        capsule = {
            "schema": "fleet-universal-evidence-capsule/v1",
            "capsuleSha256": SHA_A,
            "payloadBytes": 1,
            "sliceCount": 1,
            "temporaryCleanup": "CLEAN",
            "slices": [{
                "reference": "evidence/one.bin", "offset": 0, "length": 1,
                "sliceSha256": SHA_A,
            }],
        }
        upc.validate_contract("capsule", capsule)
        capsule.pop("temporaryCleanup")
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("capsule", capsule)

    def test_r7_03_cleanup_helper_exception_is_contained_after_publication(self) -> None:
        source = self.root / "r7-helper-source.bin"
        source.write_bytes(b"cleanup-helper-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r7-helper-output.bin"
        temporary = output.with_name(output.name + ".tmp-owned")

        def forced_named(candidate_temporary, _candidate_output):
            return candidate_temporary.open("x+b"), True

        with mock.patch.object(upc, "_open_owned_temporary", side_effect=forced_named):
            with mock.patch.object(
                upc, "_arm_owned_temp_discard",
                side_effect=RuntimeError("private cleanup helper detail"),
            ):
                result = upc.build_evidence_capsule(request, output)
        self.assertEqual(result["temporaryCleanup"], "REFUSED_BOUNDED")
        self.assertNotIn("private cleanup helper detail", upc.canonical_json(result))
        self.assertEqual(output.read_bytes(), source.read_bytes()[:8])
        self.assertTrue(output.with_name(output.name + ".cleanup-blocked").exists())
        temporary.unlink()
        output.with_name(output.name + ".cleanup-blocked").unlink()

    def test_r7_04_cleanup_helper_exception_failure_and_success_are_stable(self) -> None:
        source = self.root / "r7-helper-failure-source.bin"
        source.write_bytes(b"cleanup-helper-failure-source")
        request = self.capsule_request(source, lengths=[8])
        failure_output = self.root / "r7-helper-failure-output.bin"
        failure_temporary = failure_output.with_name(failure_output.name + ".tmp-owned")
        real_validate = upc.validate_contract

        def forced_named(candidate_temporary, _candidate_output):
            return candidate_temporary.open("x+b"), True

        def fail_private_validation(kind, value):
            real_validate(kind, value)
            if kind == "capsule":
                raise RuntimeError("private primary failure detail")

        with mock.patch.object(upc, "_open_owned_temporary", side_effect=forced_named):
            with mock.patch.object(upc, "validate_contract", side_effect=fail_private_validation):
                with mock.patch.object(
                    upc, "_arm_owned_temp_discard",
                    side_effect=RuntimeError("private cleanup failure detail"),
                ):
                    with self.assertRaises(upc.ControlError) as caught:
                        upc.build_evidence_capsule(request, failure_output)
        self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_CLEANUP_REFUSED")
        self.assertNotIn("private", str(caught.exception))
        self.assertTrue(failure_output.with_name(failure_output.name + ".cleanup-blocked").exists())
        failure_temporary.unlink()
        failure_output.with_name(failure_output.name + ".cleanup-blocked").unlink()

        success_output = self.root / "r7-helper-success-output.bin"
        success_temporary = success_output.with_name(success_output.name + ".tmp-owned")
        with mock.patch.object(upc, "_open_owned_temporary", side_effect=forced_named):
            with mock.patch.object(upc, "_arm_owned_temp_discard", return_value=True):
                result = upc.build_evidence_capsule(request, success_output)
        self.assertEqual(result["temporaryCleanup"], "CLEAN")
        self.assertFalse(success_output.with_name(success_output.name + ".cleanup-blocked").exists())
        success_temporary.unlink()

    # Exact 019d1c4 R7 RED -> R8 GREEN exception-topology and handle-owner twins.

    def test_r8_01_primary_failure_has_no_private_exception_topology(self) -> None:
        source = self.root / "r8-primary-source.bin"
        source.write_bytes(b"primary-private-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r8-primary-output.bin"
        private_value = "PRIVATE-PRIMARY-TRACE-VALUE"
        real_validate = upc.validate_contract

        def fail_capsule(kind, value):
            real_validate(kind, value)
            if kind == "capsule":
                raise RuntimeError(private_value)

        with mock.patch.object(upc, "validate_contract", side_effect=fail_capsule):
            with self.assertRaises(upc.ControlError) as caught:
                upc.build_evidence_capsule(request, output)
        error = caught.exception
        self.assertEqual(error.reason, "CAPSULE_INTERNAL_FAILURE")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(private_value, "".join(traceback.format_exception(error)))

    def test_r8_02_cleanup_failure_has_no_private_exception_topology(self) -> None:
        source = self.root / "r8-cleanup-source.bin"
        source.write_bytes(b"cleanup-private-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r8-cleanup-output.bin"
        primary_value = "PRIVATE-PRIMARY-CONTEXT-VALUE"
        cleanup_value = "PRIVATE-CLEANUP-CONTEXT-VALUE"
        real_validate = upc.validate_contract

        def fail_capsule(kind, value):
            real_validate(kind, value)
            if kind == "capsule":
                raise RuntimeError(primary_value)

        with mock.patch.object(upc, "validate_contract", side_effect=fail_capsule):
            with mock.patch.object(
                upc, "_arm_owned_temp_discard", side_effect=RuntimeError(cleanup_value)
            ):
                with self.assertRaises(upc.ControlError) as caught:
                    upc.build_evidence_capsule(request, output)
        error = caught.exception
        rendered = "".join(traceback.format_exception(error))
        self.assertEqual(error.reason, "CAPSULE_TEMP_CLEANUP_REFUSED")
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(primary_value, rendered)
        self.assertNotIn(cleanup_value, rendered)
        marker = output.with_name(output.name + ".cleanup-blocked")
        if marker.exists():
            marker.unlink()
        temporary = output.with_name(output.name + ".tmp-owned")
        if temporary.exists():
            temporary.unlink()

    @unittest.skipUnless(os.name == "nt", "Windows native-handle ownership control")
    def test_r8_03_open_osfhandle_failure_closes_native_owner_once(self) -> None:
        import msvcrt

        source = self.root / "r8-open-osfhandle-source.bin"
        source.write_bytes(b"open-osfhandle-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r8-open-osfhandle-output.bin"
        temporary = output.with_name(output.name + ".tmp-owned")
        private_value = "PRIVATE-OPEN-OSFHANDLE-VALUE"
        real_arm = upc._windows_arm_native_handle_discard
        real_close = upc._windows_close_native_handle

        with mock.patch.object(msvcrt, "open_osfhandle", side_effect=RuntimeError(private_value)):
            with mock.patch.object(upc, "_windows_arm_native_handle_discard", wraps=real_arm) as arm:
                with mock.patch.object(upc, "_windows_close_native_handle", wraps=real_close) as close:
                    with self.assertRaises(upc.ControlError) as caught:
                        upc.build_evidence_capsule(request, output)
        self.assertEqual(arm.call_count, 1)
        self.assertEqual(close.call_count, 1)
        self.assertFalse(temporary.exists())
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_value, "".join(traceback.format_exception(caught.exception)))

    @unittest.skipUnless(os.name == "nt", "Windows CRT-descriptor ownership control")
    def test_r8_04_fdopen_failure_closes_descriptor_owner_once(self) -> None:
        source = self.root / "r8-fdopen-source.bin"
        source.write_bytes(b"fdopen-owner-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r8-fdopen-output.bin"
        temporary = output.with_name(output.name + ".tmp-owned")
        private_value = "PRIVATE-FDOPEN-VALUE"
        real_arm = upc._windows_arm_native_handle_discard
        real_close_descriptor = upc._close_owned_descriptor

        with mock.patch.object(upc.os, "fdopen", side_effect=RuntimeError(private_value)):
            with mock.patch.object(upc, "_windows_arm_native_handle_discard", wraps=real_arm) as arm:
                with mock.patch.object(
                    upc, "_close_owned_descriptor", wraps=real_close_descriptor
                ) as close_descriptor:
                    with mock.patch.object(upc, "_windows_close_native_handle") as close_native:
                        with self.assertRaises(upc.ControlError) as caught:
                            upc.build_evidence_capsule(request, output)
        self.assertEqual(arm.call_count, 1)
        self.assertEqual(close_descriptor.call_count, 1)
        close_native.assert_not_called()
        self.assertFalse(temporary.exists())
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_value, "".join(traceback.format_exception(caught.exception)))

    def test_r8_05_posix_fdopen_transfer_closes_exact_owner_once(self) -> None:
        parent = self.root / "r8-posix-model"
        parent.mkdir()
        private_value = "PRIVATE-POSIX-FDOPEN-VALUE"
        with mock.patch.object(upc.os, "open", return_value=731):
            with mock.patch.object(upc.os, "fdopen", side_effect=RuntimeError(private_value)):
                with mock.patch.object(upc, "_close_owned_descriptor") as close_descriptor:
                    with self.assertRaisesRegex(RuntimeError, private_value):
                        upc._open_posix_anonymous_temporary(parent, 2, 0x400000)
        close_descriptor.assert_called_once_with(731)

        sentinel = object()
        with mock.patch.object(upc.os, "open", return_value=732):
            with mock.patch.object(upc.os, "fdopen", return_value=sentinel):
                with mock.patch.object(upc, "_close_owned_descriptor") as close_descriptor:
                    self.assertIs(
                        upc._open_posix_anonymous_temporary(parent, 2, 0x400000), sentinel
                    )
        close_descriptor.assert_not_called()

        with mock.patch.object(upc.os, "open", return_value=733):
            with mock.patch.object(upc.os, "fdopen", side_effect=OSError(22, private_value)):
                with mock.patch.object(
                    upc, "_close_owned_descriptor", side_effect=OSError(5, "private close")
                ) as close_descriptor:
                    with self.assertRaisesRegex(
                        upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                    ):
                        upc._open_posix_anonymous_temporary(parent, 2, 0x400000)
        close_descriptor.assert_called_once_with(733)

    # Exact d350e7c R8 RED -> R9 GREEN verified-close and full-boundary twins.

    def test_r9_01_preflight_failure_is_fully_sanitized(self) -> None:
        private_value = "PRIVATE-PREFLIGHT-VALIDATION-VALUE"
        output = self.root / "r9-preflight-output.bin"
        with mock.patch.object(
            upc, "validate_contract", side_effect=RuntimeError(private_value)
        ):
            with self.assertRaises(upc.ControlError) as caught:
                upc.build_evidence_capsule({}, output)
        rendered = "".join(traceback.format_exception(caught.exception))
        self.assertEqual(caught.exception.reason, "CAPSULE_INTERNAL_FAILURE")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_value, rendered)
        self.assertFalse(output.exists())

    def test_r9_02_unproven_publication_closes_never_report_clean(self) -> None:
        source = self.root / "r9-unproven-close-source.bin"
        source.write_bytes(b"unproven-close-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r9-unproven-close-output.bin"
        key = os.path.normcase(os.path.abspath(str(output)))
        with mock.patch.object(upc, "_close_file_handle_verified", return_value=False):
            with self.assertRaisesRegex(
                upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
            ):
                upc.build_evidence_capsule(request, output)
        owners = upc._UNPROVEN_CAPSULE_OWNERS.pop(key)
        self.assertGreaterEqual(len(owners), 3)
        self.assertTrue(output.with_name(output.name + ".cleanup-blocked").exists())
        for owner in owners:
            if hasattr(owner, "close") and not owner.closed:
                owner.close()
        output.with_name(output.name + ".cleanup-blocked").unlink()

    def test_r9_03_finalizer_exception_class_is_sanitized_and_retained(self) -> None:
        source = self.root / "r9-finalizer-source.bin"
        source.write_bytes(b"finalizer-private-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r9-finalizer-output.bin"
        key = os.path.normcase(os.path.abspath(str(output)))
        private_value = "PRIVATE-FINALIZER-EXCEPTION-VALUE"
        with mock.patch.object(
            upc, "_close_file_handle_verified", side_effect=RuntimeError(private_value)
        ):
            with self.assertRaises(upc.ControlError) as caught:
                upc.build_evidence_capsule(request, output)
        rendered = "".join(traceback.format_exception(caught.exception))
        self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_CLEANUP_REFUSED")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_value, rendered)
        owners = upc._UNPROVEN_CAPSULE_OWNERS.pop(key)
        for owner in owners:
            if hasattr(owner, "close") and not owner.closed:
                owner.close()
        output.with_name(output.name + ".cleanup-blocked").unlink()

    @unittest.skipUnless(os.name == "nt", "Windows false-disposition ownership controls")
    def test_r9_04_false_disposition_blocks_native_and_descriptor_failures(self) -> None:
        import inspect
        import msvcrt

        implementation = inspect.getsource(upc._windows_arm_native_handle_discard)
        self.assertIn("if not succeeded", implementation)
        self.assertIn("get_last_error", implementation)
        source = self.root / "r9-false-disposition-source.bin"
        source.write_bytes(b"false-disposition-source")
        request = self.capsule_request(source, lengths=[8])

        native_output = self.root / "r9-native-disposition-output.bin"
        with mock.patch.object(msvcrt, "open_osfhandle", side_effect=RuntimeError("private")):
            with mock.patch.object(upc, "_windows_arm_native_handle_discard", return_value=False):
                with self.assertRaisesRegex(
                    upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                ):
                    upc.build_evidence_capsule(request, native_output)
        native_output.with_name(native_output.name + ".cleanup-blocked").unlink()

        descriptor_output = self.root / "r9-descriptor-disposition-output.bin"
        with mock.patch.object(upc.os, "fdopen", side_effect=RuntimeError("private")):
            with mock.patch.object(upc, "_windows_arm_native_handle_discard", return_value=False):
                with self.assertRaisesRegex(
                    upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                ):
                    upc.build_evidence_capsule(request, descriptor_output)
        descriptor_output.with_name(descriptor_output.name + ".cleanup-blocked").unlink()

    @unittest.skipUnless(os.name == "nt", "Windows false-CloseHandle ownership control")
    def test_r9_05_false_closehandle_is_unproven_and_fenced(self) -> None:
        import inspect
        import msvcrt

        implementation = inspect.getsource(upc._windows_close_native_handle)
        self.assertIn("if not succeeded", implementation)
        self.assertIn("get_last_error", implementation)
        source = self.root / "r9-false-close-source.bin"
        source.write_bytes(b"false-close-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r9-false-close-output.bin"
        key = os.path.normcase(os.path.abspath(str(output)))
        real_close = upc._windows_close_native_handle

        def close_then_report_false(handle):
            real_close(handle)
            return False

        with mock.patch.object(msvcrt, "open_osfhandle", side_effect=RuntimeError("private")):
            with mock.patch.object(upc, "_windows_arm_native_handle_discard", return_value=True):
                with mock.patch.object(
                    upc, "_windows_close_native_handle", side_effect=close_then_report_false
                ):
                    with self.assertRaisesRegex(
                        upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                    ):
                        upc.build_evidence_capsule(request, output)
        self.assertIn(("native-handle", mock.ANY), upc._UNPROVEN_CAPSULE_OWNERS[key])
        upc._UNPROVEN_CAPSULE_OWNERS.pop(key)
        output.with_name(output.name + ".cleanup-blocked").unlink()

    def test_r9_06_posix_close_refusal_fences_repetition(self) -> None:
        source = self.root / "r9-posix-refusal-source.bin"
        source.write_bytes(b"posix-refusal-source")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r9-posix-refusal-output.bin"
        key = os.path.normcase(os.path.abspath(str(output)))
        with mock.patch.object(upc.os, "open", return_value=934):
            with mock.patch.object(upc.os, "fdopen", side_effect=OSError(22, "private")):
                with mock.patch.object(
                    upc, "_close_owned_descriptor", side_effect=OSError(5, "private close")
                ):
                    with self.assertRaisesRegex(
                        upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                    ):
                        upc._open_posix_anonymous_temporary(
                            self.root, 2, 0x400000, output
                        )
        self.assertTrue(output.with_name(output.name + ".cleanup-blocked").exists())
        # The retained-owner fence independently blocks repetition if a marker is externally
        # removed or could not be persisted.
        output.with_name(output.name + ".cleanup-blocked").unlink()
        with self.assertRaises(upc.ControlError) as caught:
            upc.build_evidence_capsule(request, output)
        self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_BACKLOG")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(upc._UNPROVEN_CAPSULE_OWNERS.pop(key), [("descriptor", 934)])

    def test_r9_07_source_and_artifact_close_refusals_retain_exact_owners(self) -> None:
        source = self.root / "r9-source-finalizer.bin"
        source.write_bytes(b"source-finalizer-refusal")
        request = self.capsule_request(source, lengths=[8])
        output = self.root / "r9-source-finalizer-output.bin"
        key = os.path.normcase(os.path.abspath(str(output)))
        real_open = Path.open

        class RefusingReader:
            def __init__(inner_self, handle):
                inner_self.handle = handle
                inner_self.close_calls = 0

            def fileno(inner_self):
                return inner_self.handle.fileno()

            def read(inner_self, count=-1):
                return inner_self.handle.read(count)

            def close(inner_self):
                inner_self.close_calls += 1
                raise OSError("private source close")

        wrapper = None

        def open_dispatch(path: Path, *args, **kwargs):
            nonlocal wrapper
            handle = real_open(path, *args, **kwargs)
            mode = args[0] if args else kwargs.get("mode", "r")
            if path == source and mode == "rb":
                wrapper = RefusingReader(handle)
                return wrapper
            return handle

        with mock.patch.object(Path, "open", autospec=True, side_effect=open_dispatch):
            with self.assertRaisesRegex(
                upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
            ):
                upc.build_evidence_capsule(request, output)
        self.assertIsNotNone(wrapper)
        self.assertEqual(wrapper.close_calls, 1)
        self.assertIn(wrapper, upc._UNPROVEN_CAPSULE_OWNERS.pop(key))
        wrapper.handle.close()
        output.with_name(output.name + ".cleanup-blocked").unlink()

        broker = upc.UniversalProviderBroker(self.root / "r9-artifact-broker")
        artifact = real_open(source, "rb")
        refusing_artifact = RefusingReader(artifact)
        lease_id = "lease-r9-artifact-refusal"
        stat_result = source.stat()
        broker._artifact_handles[lease_id] = [(
            source, refusing_artifact,
            (stat_result.st_dev, stat_result.st_ino, stat_result.st_size, stat_result.st_mtime_ns),
            sha_file(source), 1024,
        )]
        broker._artifact_close_attempted[lease_id] = set()
        with self.assertRaisesRegex(
            upc.ControlError, "ARTIFACT_HANDLE_CLEANUP_REFUSED"
        ):
            broker._release_artifact_handles(lease_id)
        with self.assertRaisesRegex(
            upc.ControlError, "ARTIFACT_HANDLE_CLEANUP_REFUSED"
        ):
            broker._release_artifact_handles(lease_id)
        self.assertEqual(refusing_artifact.close_calls, 1)
        self.assertIn(lease_id, broker._artifact_handles)
        artifact.close()
        broker._artifact_handles.pop(lease_id)
        broker._artifact_close_attempted.pop(lease_id)

    # Exact fe060bf R9 RED -> R10 GREEN process/broker poison rotation twins.

    def test_r10_01_capsule_poison_blocks_distinct_output_before_acquisition(self) -> None:
        source = self.root / "r10-capsule-poison-source.bin"
        source.write_bytes(b"capsule-global-poison")
        request = self.capsule_request(source, lengths=[8])
        first_output = self.root / "r10-capsule-first.bin"
        first_key = os.path.normcase(os.path.abspath(str(first_output)))
        with mock.patch.object(upc, "_close_file_handle_verified", return_value=False):
            with self.assertRaisesRegex(
                upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
            ):
                upc.build_evidence_capsule(request, first_output)
        owners = upc._UNPROVEN_CAPSULE_OWNERS[first_key]
        owner_ids = [id(owner) for owner in owners]
        self.assertEqual(len(owner_ids), len(set(owner_ids)))
        self.assertLessEqual(len(owners), upc.MAX_CAPSULE_POISON_OWNERS)

        rotated_output = self.root / "r10-capsule-rotated.bin"
        with mock.patch.object(Path, "open", side_effect=AssertionError("new handle acquired")):
            with self.assertRaises(upc.ControlError) as caught:
                upc.build_evidence_capsule(request, rotated_output)
        self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_BACKLOG")
        self.assertFalse(rotated_output.exists())
        self.assertEqual([id(owner) for owner in upc._UNPROVEN_CAPSULE_OWNERS[first_key]], owner_ids)
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_CLEANUP_POISONED"):
            upc.assert_process_cleanup_clear()

        for owner in owners:
            if hasattr(owner, "close") and not owner.closed:
                owner.close()
        upc._UNPROVEN_CAPSULE_OWNERS.pop(first_key)
        first_output.with_name(first_output.name + ".cleanup-blocked").unlink()
        upc.assert_process_cleanup_clear()

    def test_r10_02_broker_artifact_poison_blocks_fresh_lease_and_close(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r10-broker-poison")
        self.transition(broker)
        admitted = self.authorize(broker)
        lease_id = admitted["leaseId"]
        terminal = self.process_observation(admitted, "EXITED", phase="TERMINAL")
        os_handle = broker._os_locks[lease_id]

        def refuse_artifact_only(handle):
            if handle is os_handle:
                handle.close()
                return True
            return False

        with mock.patch.object(upc, "_close_file_handle_verified", side_effect=refuse_artifact_only):
            with self.assertRaisesRegex(
                upc.ControlError, "ARTIFACT_HANDLE_CLEANUP_REFUSED"
            ):
                broker.release_child(
                    process_observation=terminal, fleet_secret=self.secret, now=self.now
                )
        poison_key = broker._artifact_poison_key
        owners = upc._BROKER_ARTIFACT_CLEANUP_POISON[poison_key]
        self.assertEqual(len(owners), len({id(owner) for owner in owners}))
        close_calls = len(broker._artifact_close_attempted[lease_id])

        rotated_request = self.make_request("request-r10-rotated-after-terminal")
        with mock.patch.object(
            broker, "_open_artifact_handles", side_effect=AssertionError("artifact reopened")
        ) as acquisition:
            rotated = self.authorize(broker, rotated_request, confirm=False)
        self.assertEqual(rotated, {
            "status": "UNEVALUABLE", "reason": "ARTIFACT_CLEANUP_POISONED"
        })
        acquisition.assert_not_called()
        restarted = upc.UniversalProviderBroker(self.root / "r10-broker-poison")
        self.assertEqual(
            self.authorize(restarted, rotated_request, confirm=False)["reason"],
            "ARTIFACT_CLEANUP_POISONED",
        )
        with self.assertRaisesRegex(upc.ControlError, "ARTIFACT_CLEANUP_POISONED"):
            broker.close()
        self.assertEqual(len(broker._artifact_close_attempted[lease_id]), close_calls)

        for owner in owners:
            if not owner.closed:
                owner.close()
        upc._BROKER_ARTIFACT_CLEANUP_POISON.pop(poison_key)
        broker._artifact_handles.pop(lease_id)
        broker._artifact_close_attempted.pop(lease_id)

    def test_r10_03_posix_runtimeerror_close_poison_blocks_output_rotation(self) -> None:
        source = self.root / "r10-posix-runtime-source.bin"
        source.write_bytes(b"posix-runtime-poison")
        request = self.capsule_request(source, lengths=[8])
        first_output = self.root / "r10-posix-runtime-first.bin"
        first_key = os.path.normcase(os.path.abspath(str(first_output)))
        private_value = "PRIVATE-POSIX-RUNTIME-CLOSE"
        with mock.patch.object(upc.os, "open", return_value=1042):
            with mock.patch.object(upc.os, "fdopen", side_effect=RuntimeError("private fdopen")):
                with mock.patch.object(
                    upc, "_close_owned_descriptor", side_effect=RuntimeError(private_value)
                ):
                    with self.assertRaisesRegex(
                        upc.ControlError, "CAPSULE_TEMP_CLEANUP_REFUSED"
                    ):
                        upc._open_posix_anonymous_temporary(
                            self.root, 2, 0x400000, first_output
                        )
        self.assertEqual(
            upc._UNPROVEN_CAPSULE_OWNERS[first_key], [("descriptor", 1042)]
        )
        rotated_output = self.root / "r10-posix-runtime-rotated.bin"
        with mock.patch.object(Path, "open", side_effect=AssertionError("new handle acquired")):
            with self.assertRaises(upc.ControlError) as caught:
                upc.build_evidence_capsule(request, rotated_output)
        rendered = "".join(traceback.format_exception(caught.exception))
        self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_BACKLOG")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_value, rendered)
        upc._UNPROVEN_CAPSULE_OWNERS.pop(first_key)
        first_output.with_name(first_output.name + ".cleanup-blocked").unlink()

    # Exact bd9c559 R10 RED -> R11 GREEN root-linearization and owner-lifetime twins.

    def test_r11_01_root_lock_linearizes_terminal_authorize_confirm_and_close(self) -> None:
        root = self.root / "r11-linearizable-root"
        terminal_broker = upc.UniversalProviderBroker(root)
        self.transition(terminal_broker)
        prepared = self.authorize(terminal_broker, confirm=False)
        peer = upc.UniversalProviderBroker(root)
        self.assertIs(terminal_broker._root_lock, peer._root_lock)
        terminal = self.process_observation(prepared, "EXITED", phase="TERMINAL")
        resume = self.admission_observation(
            self.request, phase="RESUME", lease_id=prepared["leaseId"]
        )
        rotated = self.make_request("request-r11-concurrent-rotation")
        os_handle = terminal_broker._os_locks[prepared["leaseId"]]
        entered_cleanup = threading.Event()
        finish_cleanup = threading.Event()
        real_close = upc._close_file_handle_verified
        results: dict[str, object] = {}

        def blocking_artifact_refusal(handle):
            if handle is os_handle:
                return real_close(handle)
            entered_cleanup.set()
            if not finish_cleanup.wait(5):
                raise AssertionError("concurrent cleanup barrier timeout")
            return False

        def capture(name, callable_):
            try:
                results[name] = callable_()
            except BaseException as exc:
                results[name] = exc

        with mock.patch.object(
            upc, "_close_file_handle_verified", side_effect=blocking_artifact_refusal
        ):
            terminal_thread = threading.Thread(
                target=capture,
                args=(
                    "terminal",
                    lambda: terminal_broker.release_child(
                        process_observation=terminal, fleet_secret=self.secret, now=self.now
                    ),
                ),
            )
            terminal_thread.start()
            self.assertTrue(entered_cleanup.wait(5))
            contenders = [
                threading.Thread(
                    target=capture,
                    args=(
                        "authorize",
                        lambda: self.authorize(peer, rotated, confirm=False),
                    ),
                ),
                threading.Thread(
                    target=capture,
                    args=(
                        "confirm",
                        lambda: peer.confirm_resume_boundary(
                            lease_id=prepared["leaseId"], process_observation=resume,
                            fleet_secret=self.secret, now=self.now,
                        ),
                    ),
                ),
                threading.Thread(target=capture, args=("close", peer.close)),
            ]
            for thread in contenders:
                thread.start()
            finish_cleanup.set()
            for thread in [terminal_thread, *contenders]:
                thread.join(10)
                self.assertFalse(thread.is_alive())

        self.assertIsInstance(results["terminal"], upc.ControlError)
        self.assertEqual(results["terminal"].reason, "ARTIFACT_HANDLE_CLEANUP_REFUSED")
        self.assertEqual(
            results["authorize"],
            {"status": "UNEVALUABLE", "reason": "ARTIFACT_CLEANUP_POISONED"},
        )
        self.assertIsInstance(results["confirm"], upc.ControlError)
        self.assertEqual(results["confirm"].reason, "ARTIFACT_CLEANUP_POISONED")
        self.assertIsInstance(results["close"], upc.ControlError)
        self.assertEqual(results["close"].reason, "ARTIFACT_CLEANUP_POISONED")
        self.assertNotIn("PREPARED_SUSPENDED", {str(value) for value in results.values()})
        self.assertNotIn("ALLOW_ATTESTED", {str(value) for value in results.values()})

    def test_r11_02_all_prepared_lease_owners_fit_exact_poison_bound(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r11-multi-lease")
        self.transition(broker)
        prepared_leases = [self.authorize(broker, confirm=False)]
        provider_inputs = (
            ("openai", "openai-responses/1.0", {"primary": 0.05, "secondary": 0.05}, "3", "4"),
            ("kimi", "kimi-code/1.0", {"context": 0.05, "monthly": 0.05}, "5", "6"),
            ("grok", "xai-api/1.0", {"requests": 0.05, "tokens": 0.05}, "7", "8"),
        )
        for provider, adapter, estimates, seat_digit, session_digit in provider_inputs:
            request = self.make_request(f"request-r11-{provider}-lease")
            request.update(
                provider=provider,
                adapterVersion=adapter,
                quotaDomainId=upc.derive_quota_domain_id(provider, self.identity, self.secret),
                seatIdHash="hmac-sha256:" + seat_digit * 64,
                sessionIdHash="hmac-sha256:" + session_digit * 64,
                windowEstimates=estimates,
            )
            prepared_leases.append(self.authorize(
                broker, request, confirm=False,
                native_evidence=[self.make_native(provider)],
                process_observation=self.admission_observation(request),
            ))
        self.assertEqual(
            {prepared["status"] for prepared in prepared_leases}, {"PREPARED_SUSPENDED"}
        )
        self.assertEqual(len(broker._artifact_handles), upc.MAX_PREPARED_LEASES_PER_STATE_ROOT)

        fifth_identity = b"second-local-account-alias"
        fifth = self.make_request("request-r11-root-limit")
        fifth["quotaDomainId"] = upc.derive_quota_domain_id(
            "claude", fifth_identity, self.secret
        )
        fifth["seatIdHash"] = "hmac-sha256:" + "9" * 64
        fifth["sessionIdHash"] = "hmac-sha256:" + "a" * 64
        fifth_native = self.make_native("claude")
        fifth_native["quotaDomainId"] = fifth["quotaDomainId"]
        self.resign_native(fifth_native)
        with mock.patch.object(
            broker, "_open_artifact_handles", side_effect=AssertionError("fifth lease acquired")
        ) as acquisition:
            refused = self.authorize(
                broker, fifth, confirm=False, local_stable_identity=fifth_identity,
                native_evidence=[fifth_native],
                process_observation=self.admission_observation(fifth),
            )
        self.assertEqual(refused["reason"], "STATE_ROOT_LEASE_LIMIT")
        acquisition.assert_not_called()

        os_handles = set(broker._os_locks.values())
        real_close = upc._close_file_handle_verified

        def refuse_artifacts(handle):
            return real_close(handle) if handle in os_handles else False

        with mock.patch.object(upc, "_close_file_handle_verified", side_effect=refuse_artifacts):
            for prepared in prepared_leases:
                with self.assertRaisesRegex(
                    upc.ControlError, "ARTIFACT_HANDLE_CLEANUP_REFUSED"
                ):
                    broker.release_child(
                        process_observation=self.process_observation(
                            prepared, "EXITED", phase="TERMINAL"
                        ),
                        fleet_secret=self.secret,
                        now=self.now,
                    )

        owners = upc._BROKER_ARTIFACT_CLEANUP_POISON[broker._artifact_poison_key]
        self.assertEqual(len(owners), upc.MAX_BROKER_ARTIFACT_POISON_OWNERS)
        self.assertEqual(len(owners), len({id(owner) for owner in owners}))
        self.assertLessEqual(len(owners), upc.MAX_BROKER_ARTIFACT_POISON_OWNERS)
        attempted = {lease: set(values) for lease, values in broker._artifact_close_attempted.items()}
        with mock.patch.object(
            upc, "_close_file_handle_verified", side_effect=AssertionError("owner retried")
        ) as retry:
            with self.assertRaisesRegex(
                upc.ControlError, "ARTIFACT_HANDLE_CLEANUP_REFUSED"
            ):
                broker.release_child(
                    process_observation=self.process_observation(
                        prepared_leases[-1], "EXITED", phase="TERMINAL"
                    ),
                    fleet_secret=self.secret,
                    now=self.now,
                )
        retry.assert_not_called()
        self.assertEqual(broker._artifact_close_attempted, attempted)

    def test_r11_03_os_lock_unlock_and_close_failures_are_attempt_once_no_echo(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r11-os-lock-owners")
        self.transition(broker)
        first = self.authorize(broker, confirm=False)
        private_unlock = "PRIVATE-UNLOCK-RUNTIME"
        with mock.patch.object(
            upc, "_unlock_os_lock_handle", side_effect=RuntimeError(private_unlock)
        ):
            with self.assertRaises(upc.ControlError) as unlock_error:
                broker.release_child(
                    process_observation=self.process_observation(
                        first, "EXITED", phase="TERMINAL"
                    ),
                    fleet_secret=self.secret,
                    now=self.now,
                )
        self.assertEqual(unlock_error.exception.reason, "OS_LOCK_UNLOCK_REFUSED")
        self.assertIsNone(unlock_error.exception.__cause__)
        self.assertIsNone(unlock_error.exception.__context__)
        self.assertNotIn(private_unlock, "".join(traceback.format_exception(unlock_error.exception)))
        self.assertNotIn(first["leaseId"], broker._os_locks)

        second_request = self.make_request("request-r11-os-close-refusal")
        second = self.authorize(broker, second_request, confirm=False)
        os_handle = broker._os_locks[second["leaseId"]]
        real_close = upc._close_file_handle_verified
        private_close = "PRIVATE-OS-CLOSE-OSError"

        def refuse_os_close(handle):
            if handle is os_handle:
                raise OSError(private_close)
            return real_close(handle)

        with mock.patch.object(upc, "_close_file_handle_verified", side_effect=refuse_os_close):
            with self.assertRaises(upc.ControlError) as close_error:
                broker.release_child(
                    process_observation=self.process_observation(
                        second, "EXITED", phase="TERMINAL"
                    ),
                    fleet_secret=self.secret,
                    now=self.now,
                )
        self.assertEqual(close_error.exception.reason, "OS_LOCK_CLEANUP_POISONED")
        self.assertIsNone(close_error.exception.__cause__)
        self.assertIsNone(close_error.exception.__context__)
        self.assertNotIn(private_close, "".join(traceback.format_exception(close_error.exception)))
        self.assertIs(broker._os_locks[second["leaseId"]], os_handle)
        self.assertIs(broker._unproven_os_locks[second["leaseId"]], os_handle)
        self.assertIn("close-refused", broker._os_lock_release_attempted[second["leaseId"]])
        with mock.patch.object(
            upc, "_close_file_handle_verified", side_effect=AssertionError("OS owner retried")
        ) as retry:
            with self.assertRaisesRegex(upc.ControlError, "OS_LOCK_CLEANUP_POISONED"):
                broker.release_child(
                    process_observation=self.process_observation(
                        second, "EXITED", phase="TERMINAL"
                    ),
                    fleet_secret=self.secret,
                    now=self.now,
                )
        retry.assert_not_called()
        rotated = self.authorize(
            broker, self.make_request("request-r11-after-os-poison"), confirm=False
        )
        self.assertEqual(rotated["reason"], "OS_LOCK_CLEANUP_POISONED")

    def test_r11_04_close_and_del_are_assertions_not_child_release(self) -> None:
        root = self.root / "r11-administrative-close"
        broker = upc.UniversalProviderBroker(root)
        self.transition(broker)
        allowed = self.authorize(broker)
        lease_id = allowed["leaseId"]
        os_owner = broker._os_locks[lease_id]
        artifact_owners = [record[1] for record in broker._artifact_handles[lease_id]]
        with self.assertRaisesRegex(upc.ControlError, "ACTIVE_LEASES_REMAIN"):
            broker.close()
        broker.__del__()
        peer = upc.UniversalProviderBroker(root)
        self.assertIs(peer._os_locks[lease_id], os_owner)
        self.assertEqual(
            [record[1] for record in peer._artifact_handles[lease_id]], artifact_owners
        )
        with self.assertRaisesRegex(upc.ControlError, "ACTIVE_LEASES_REMAIN"):
            peer.close()
        connection = sqlite3.connect(peer.database)
        try:
            self.assertEqual(
                connection.execute(
                    "SELECT state FROM leases WHERE lease_id=?", (lease_id,)
                ).fetchone()[0],
                "RESUME_ATTESTED",
            )
        finally:
            connection.close()
        peer.release_child(
            process_observation=self.process_observation(
                allowed, "EXITED", phase="TERMINAL"
            ),
            fleet_secret=self.secret,
            now=self.now,
        )
        peer.close()

    # Exact 52ca345 R11 hosted RED -> R12 GREEN checkout-EOL and linkat-injection twins.

    def test_r12_01_manifest_self_uses_canonical_git_blob_under_crlf_checkout(self) -> None:
        import check_universal_manifest as checker

        r11_tests = required_predecessor_blob("tests/test_universal_provider_control.py")
        self.assertIn("raw = (ROOT / checker.MANIFEST).read_bytes()", r11_tests)
        canonical = checker._git(checker._blob_spec(":", checker.MANIFEST))
        self.assertIsInstance(canonical, bytes)
        declared = json.loads(canonical.decode("utf-8"))["manifestSelf"]["canonicalGitBlobSha256"]
        self.assertEqual(declared, checker.canonical_self_sha256(canonical))

        lf = (
            b'{"canonicalGitBlobSha256":"sha256:' + b"0" * 64 + b'"}\n'
        )
        crlf = lf.replace(b"\n", b"\r\n")
        self.assertNotEqual(checker.canonical_self_sha256(lf), checker.canonical_self_sha256(crlf))
        self.assertEqual(
            checker.canonical_self_sha256(lf),
            "sha256:" + hashlib.sha256(lf).hexdigest(),
        )

    def test_r12_02_posix_hostile_mutations_patch_actual_publication_syscall(self) -> None:
        r11_tests = required_predecessor_blob("tests/test_universal_provider_control.py")
        r11_engine = required_predecessor_blob("tools/universal_provider_control.py")
        self.assertIn('mock.patch.object(upc.os, "link"', r11_tests)
        self.assertNotIn("def _publication_syscall(", r11_engine)
        publication = inspect.getsource(upc._publish_owned_temporary)
        syscall = inspect.getsource(upc._publication_syscall)
        current_tests = (
            inspect.getsource(self.test_r4_03_no_clobber_publication_preserves_foreign_races)
            + inspect.getsource(self.test_r5_01_publication_binds_retained_temp_identity_and_exact_bytes)
        )
        self.assertGreaterEqual(publication.count("_publication_syscall("), 2)
        self.assertIn("libc.linkat", syscall)
        self.assertIn('mock.patch.object(upc, "_publication_syscall"', current_tests)

    # Exact 6c821f7 R12 hosted-history RED -> R13 GREEN shallow/full-history twin.

    def test_r13_01_required_predecessor_history_is_present_or_stably_fails(self) -> None:
        for path in sorted(R11_REQUIRED_BLOBS):
            self.assertTrue(required_predecessor_blob(path))

        private_stderr = "PRIVATE-SHALLOW-GIT-DETAIL"
        missing = subprocess.CompletedProcess(
            args=["git", "show"], returncode=128, stdout="", stderr=private_stderr
        )
        with mock.patch.object(subprocess, "run", return_value=missing):
            with self.assertRaises(AssertionError) as caught:
                required_predecessor_blob("tests/test_universal_provider_control.py")
        self.assertEqual(str(caught.exception), "REQUIRED_HISTORY_OBJECT_UNAVAILABLE")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)
        self.assertNotIn(private_stderr, "".join(traceback.format_exception(caught.exception)))

        workflow = (ROOT / ".github/workflows/provider-capacity-governor.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("Verify required predecessor history", workflow)
        self.assertIn(f"{R11_PREDECESSOR}^{{commit}}", workflow)
        for path in R11_REQUIRED_BLOBS:
            self.assertIn(f"{R11_PREDECESSOR}:{path}", workflow)
        self.assertLess(
            workflow.index("Verify required predecessor history"),
            workflow.index("Run semantic negative controls"),
        )

    # Bounded exact evidence capsule controls.

    def capsule_request(self, source: Path, *, lengths: list[int]) -> dict:
        slices = []
        offset = 0
        for index, length in enumerate(lengths):
            slices.append(
                {
                    "localPath": str(source), "reference": f"evidence/slice-{index}.bin",
                    "offset": offset, "length": length, "sourceSha256": sha_file(source),
                }
            )
            offset += length
        return {
            "schema": "fleet-universal-evidence-capsule-request/v1", "maxBytes": 262144,
            "maxSourceBytes": 16777216, "maxAmplificationRatio": 64, "slices": slices,
        }

    def test_capsule_preserves_exact_slice_bytes_and_hashes(self) -> None:
        source = self.root / "large-source.bin"
        source.write_bytes(bytes(range(256)) * 4096)
        request = self.capsule_request(source, lengths=[65536, 65536])
        output = self.root / "capsule.bin"
        result = upc.build_evidence_capsule(request, output)
        self.assertEqual(output.read_bytes(), source.read_bytes()[:131072])
        self.assertEqual(result["capsuleSha256"], sha_file(output))
        self.assertEqual(result["payloadBytes"], 131072)

    def test_capsule_enforces_total_bound_before_opening_sources(self) -> None:
        source = self.root / "source.bin"
        source.write_bytes(b"x" * 300000)
        request = self.capsule_request(source, lengths=[200000, 10000])
        request["maxBytes"] = 200000
        request["slices"][0]["localPath"] = str(self.root / "does-not-exist")
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SIZE_LIMIT"):
            upc.build_evidence_capsule(request, self.root / "never.bin")

    def test_capsule_streams_without_path_read_bytes(self) -> None:
        source = self.root / "stream-source.bin"
        source.write_bytes(b"z" * 131072)
        request = self.capsule_request(source, lengths=[131072])
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("unbounded read")):
            result = upc.build_evidence_capsule(request, self.root / "stream.bin")
        self.assertEqual(result["payloadBytes"], 131072)

    def test_capsule_source_drift_is_fail_closed_and_partial_removed(self) -> None:
        source = self.root / "drift-source.bin"
        source.write_bytes(b"before")
        request = self.capsule_request(source, lengths=[6])
        request["slices"][0]["sourceSha256"] = SHA_A
        output = self.root / "partial.bin"
        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_DRIFT"):
            upc.build_evidence_capsule(request, output)
        self.assertFalse(output.exists())

    def test_capsule_fixed_budget_probe_detects_size_drift(self) -> None:
        source = self.root / "identity-source.bin"
        source.write_bytes(b"stable-source")
        request = self.capsule_request(source, lengths=[6])
        real = source.stat()
        bound = mock.Mock(st_dev=real.st_dev, st_ino=real.st_ino, st_size=6, st_mtime_ns=real.st_mtime_ns)
        with mock.patch.object(upc.os, "fstat", return_value=bound):
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_SOURCE_DRIFT"):
                upc.build_evidence_capsule(request, self.root / "identity-capsule.bin")


if __name__ == "__main__":
    unittest.main(verbosity=2)
