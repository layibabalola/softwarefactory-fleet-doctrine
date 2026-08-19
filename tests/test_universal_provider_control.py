from __future__ import annotations

import copy
import datetime as dt
import hashlib
import inspect
import json
import os
from pathlib import Path
import sqlite3
import stat
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
R13_DIRECTORY_CLOSE_FIXTURE = "os.close(directory)"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class UniversalProviderControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        # Ordinary test discovery must never touch the persistent OS-account quota authority.
        # Override both module paths before constructing any broker, using a deterministic child of
        # this test's private temporary root.  The production resolver remains covered separately.
        self.default_quota_trusted_base = upc._CANONICAL_QUOTA_TRUSTED_BASE
        self.default_quota_authority_root = upc._CANONICAL_QUOTA_AUTHORITY_ROOT
        self.default_quota_ledger_root = upc._CANONICAL_QUOTA_LEDGER_ROOT
        upc._CANONICAL_QUOTA_TRUSTED_BASE = self.root
        upc._CANONICAL_QUOTA_AUTHORITY_ROOT = self.root / "test-account-authority"
        upc._CANONICAL_QUOTA_LEDGER_ROOT = (
            upc._CANONICAL_QUOTA_AUTHORITY_ROOT / "quota-ledger"
        )
        self.now = dt.datetime(2026, 8, 18, 20, 0, tzinfo=UTC)
        self.default_clock_patch = mock.patch.object(
            upc, "_default_broker_clock", side_effect=lambda: self.now
        )
        self.default_clock_patch.start()
        self.secret = b"S" * 32
        self.termination_secret = b"T" * 32
        self.quality_secret = b"Q" * 32
        self.receipt_signer_secrets = {
            "process-tree-observer": self.termination_secret,
            "output-quality-observer": self.quality_secret,
        }
        # The production quota ledger is deliberately canonical across state roots.  Give every
        # isolated test a distinct synthetic account so intentional active leases cannot leak
        # authority into a later case.
        self.identity = b"local-account-" + str(self.root).encode("utf-8")
        self.quota_id = upc.derive_quota_domain_id("claude", self.identity, self.secret)
        self.launcher = self.root / "controlled-launcher.exe"
        self.launcher.write_bytes(b"reference launcher bytes\n")
        self.provider_executable = self.root / "pinned-provider.exe"
        self.provider_executable.write_bytes(b"pinned provider adapter bytes\n")
        self.termination_evidence = self.root / "termination-evidence.json"
        self.termination_evidence.write_bytes(b'{"rootExited":true,"descendants":0}\n')
        self.output_artifact = self.root / "retained-output.bin"
        self.output_artifact.write_bytes(b"candidate output bytes\n")
        self.reference_output = self.root / "retained-reference.bin"
        self.reference_output.write_bytes(b"reference output bytes\n")
        self.output_review = self.root / "retained-output-review.json"
        self.output_review.write_bytes(b'{"nonInferior":true}\n')
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
        self.addressed_work = self.root / "addressed-work.json"
        self.addressed_work.write_bytes(b'{"work":["issue-4"]}\n')
        self.cursor = self.root / "cursor.json"
        self.cursor.write_bytes(b'{"cursor":"current"}\n')
        self.prior_idle_work = self.root / "prior-idle-work.json"
        self.prior_idle_work.write_bytes(b'{"work":[]}\n')
        self.prior_idle_cursor = self.root / "prior-idle-cursor.json"
        self.prior_idle_cursor.write_bytes(b'{"cursor":"prior"}\n')
        self.demand_snapshot = {
            "schema": "fleet-universal-demand-snapshot/v1", "project": "test-project",
            "addressedWork": [
                {"kind": "ISSUE", "id": "issue-4", "state": "READY",
                 "subjectSha256": sha_file(self.subject)}
            ],
            "cursor": {"stream": "issues", "sequence": 4, "checkpointSha256": SHA_C},
        }
        self.prior_idle_snapshot = {
            "schema": "fleet-universal-demand-snapshot/v1", "project": "test-project",
            "addressedWork": [],
            "cursor": {"stream": "issues", "sequence": 3, "checkpointSha256": SHA_D},
        }
        self.prior_idle_authority = self.root / "broker-observed-prior-idle.json"
        self.prior_idle_authority.write_bytes(
            upc.canonical_json(self.prior_idle_snapshot).encode("utf-8")
        )
        self.demand_authority = self.root / "broker-observed-demand.json"
        self.demand_authority.write_bytes(upc.canonical_json(self.demand_snapshot).encode("utf-8"))
        self.request = self.make_request()
        self.profile = self.make_profile()
        self.inventory = self.make_inventory()
        self.health = self.make_health()
        self.native = self.make_native()
        self.permits: dict[str, dict] = {}
        self.brokers: dict[str, upc.UniversalProviderBroker] = {}
        self.prior_receipts: dict[tuple[int, str], dict] = {}
        self.prior_receipt_pools: dict[tuple[int, str], dict[str, dict]] = {}
        self.prior_receipt_lock = threading.Lock()
        self.terminal_artifacts: dict[str, dict] = {}

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
        upc._QUOTA_AUTHORITY_POISON = {
            key for key in upc._QUOTA_AUTHORITY_POISON
            if not key.startswith(os.path.normcase(os.path.abspath(str(self.root))))
        }
        self.default_clock_patch.stop()
        upc._CANONICAL_QUOTA_TRUSTED_BASE = self.default_quota_trusted_base
        upc._CANONICAL_QUOTA_AUTHORITY_ROOT = self.default_quota_authority_root
        upc._CANONICAL_QUOTA_LEDGER_ROOT = self.default_quota_ledger_root
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
            "demandAuthority": {
                "snapshotPath": str(self.demand_authority.resolve()),
                "snapshotSha256": sha_file(self.demand_authority),
                "brokerObserved": True,
            },
            "efficiency": {
                "maxTurns": 16,
                "maxContextTokens": 65536,
                "maxCumulativeTokenCeilings": {
                    "inputTokens": 100000,
                    "cacheReadTokens": 1000000,
                    "cacheWriteTokens": 100000,
                    "reasoningTokens": 100000,
                    "outputTokens": 50000,
                },
                "maxReservedTokenCeilings": {
                    "inputTokens": 100000,
                    "cacheReadTokens": 1000000,
                    "cacheWriteTokens": 100000,
                    "reasoningTokens": 100000,
                    "outputTokens": 50000,
                },
                "milestoneCompactionRequired": True,
                "cacheAffinityRequired": True,
                "capsuleRequired": True,
                "qualityMayBeWeakened": False,
            },
            "launchAllowlist": [
                {
                    "provider": provider,
                    "adapterVersion": adapter,
                    "model": "claude-opus-4-1",
                    "effort": "high",
                    "role": "IMPLEMENT",
                    "qualityTier": "FRONTIER_HIGH",
                    "qualityEquivalenceReceiptSha256": self.request["qualityEquivalenceReceiptSha256"],
                    "executableSha256": sha_file(self.launcher),
                    "launcherConfigSha256": sha_file(self.launcher_config),
                    "argvContractSha256": upc.canonical_argv_contract(
                        [str(self.launcher.resolve()), "claude-opus-4-1", "high", sha_file(self.subject),
                         "IMPLEMENT", "8", "32768", "50000", "500000", "50000", "50000", "25000"],
                        {"modelIndex": 1, "effortIndex": 2, "subjectIndex": 3, "roleIndex": 4,
                         "maxTurnsIndex": 5, "maxContextTokensIndex": 6, "maxInputTokensIndex": 7,
                         "maxCacheReadTokensIndex": 8, "maxCacheWriteTokensIndex": 9,
                         "maxReasoningTokensIndex": 10, "maxOutputTokensIndex": 11},
                    ),
                    "requestBoundaryMode": "SINGLE_REQUEST_PROCESS",
                    "boundaryCertificationSha256": self.request["boundaryCertificationSha256"],
                    "runtimeWatchdogCertified": True,
                }
                for provider, adapter in (
                    ("claude", "claude-code/1.0"),
                    ("openai", "openai-responses/1.0"),
                    ("kimi", "kimi-code/1.0"),
                    ("grok", "xai-api/1.0"),
                )
            ],
            "policy": {
                "maxObservationAgeSeconds": 120,
                "maxInventoryAgeSeconds": 120,
                "maxBrokerHealthAgeSeconds": 120,
                "maxRequestAgeSeconds": 120,
                "maxRequestValiditySeconds": 900,
                "maxPriorIdleAgeSeconds": 60,
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
                "capacityTokenBudgets": {
                    "claude-code/1.0": 10000000,
                    "openai-responses/1.0": 10000000,
                    "kimi-code/1.0": 10000000,
                    "xai-api/1.0": 10000000,
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
        state_root_identity = getattr(self, "current_state_root_identity", "hmac-sha256:" + "0" * 64)
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
            "qualityTier": "FRONTIER_HIGH",
            "qualityEquivalenceReceipt": {},
            "qualityEquivalenceReceiptSha256": SHA_A,
            "seatIdHash": "hmac-sha256:" + "1" * 64,
            "seatEpoch": 7,
            "sessionIdHash": "hmac-sha256:" + "2" * 64,
            "subjectPath": str(self.subject.resolve()),
            "subjectSha256": sha_file(self.subject),
            "executablePath": str(self.launcher.resolve()),
            "executableSha256": sha_file(self.launcher),
            "providerExecutablePath": str(self.provider_executable.resolve()),
            "providerExecutableSha256": sha_file(self.provider_executable),
            "argv": [
                str(self.launcher.resolve()), "claude-opus-4-1", "high", sha_file(self.subject),
                "IMPLEMENT", "8", "32768", "50000", "500000", "50000", "50000", "25000",
            ],
            "argvSha256": "",
            "argvBindings": {
                "modelIndex": 1, "effortIndex": 2, "subjectIndex": 3, "roleIndex": 4,
                "maxTurnsIndex": 5, "maxContextTokensIndex": 6, "maxInputTokensIndex": 7,
                "maxCacheReadTokensIndex": 8, "maxCacheWriteTokensIndex": 9,
                "maxReasoningTokensIndex": 10, "maxOutputTokensIndex": 11,
            },
            "launcherConfigPath": str(self.launcher_config.resolve()),
            "launcherConfigSha256": sha_file(self.launcher_config),
            "argvContractSha256": "",
            "requestBoundaryMode": "SINGLE_REQUEST_PROCESS",
            "boundaryCertification": {},
            "boundaryCertificationSha256": SHA_B,
            "actionableWork": True,
            "demandSnapshot": copy.deepcopy(self.demand_snapshot),
            "demandFingerprint": "",
            "priorIdleReceipt": {
                "schema": "fleet-universal-prior-idle-receipt/v1", "receiptId": "idle-" + "1" * 32,
                "project": "test-project", "recordedAt": upc.iso(self.now - dt.timedelta(seconds=10)),
                "expiresAt": upc.iso(self.now + dt.timedelta(seconds=50)), "sequence": 1,
                "authorityPath": str(self.prior_idle_authority.resolve()),
                "authoritySha256": sha_file(self.prior_idle_authority),
                "demandSnapshot": copy.deepcopy(self.prior_idle_snapshot),
                "demandFingerprint": upc.digest_json(upc.canonical_demand_snapshot(self.prior_idle_snapshot)),
                "demandAuthorityPinEpoch": 1,
                "demandAuthorityPinHmacSha256": "hmac-sha256:" + "3" * 64,
                "stateRootIdentity": state_root_identity,
                "receiptHmacSha256": "hmac-sha256:" + "0" * 64,
            },
            "maxWallSeconds": 60,
            "maxTurns": 8,
            "maxContextTokens": 32768,
            "cumulativeTokenCeilings": {
                "inputTokens": 50000,
                "cacheReadTokens": 500000,
                "cacheWriteTokens": 50000,
                "reasoningTokens": 50000,
                "outputTokens": 25000,
            },
            "inputEnvelopeTokens": 600000,
            "generatedEnvelopeTokens": 75000,
            "terminalReserveTokens": 5000,
            "contextCapsulePath": str(self.capsule.resolve()),
            "contextCapsuleSha256": sha_file(self.capsule),
            "compactionCheckpointPath": str(self.checkpoint.resolve()),
            "compactionCheckpointSha256": sha_file(self.checkpoint),
            "cacheAffinityManifestPath": str(self.cache_manifest.resolve()),
            "cacheAffinityKeySha256": sha_file(self.cache_manifest),
            "canary": False,
            "manualAuthorizationSha256": None,
        }
        request["demandFingerprint"] = upc.canonical_demand_fingerprint(request["demandSnapshot"])
        request["argvSha256"] = upc.digest_json(request["argv"])
        request["argvContractSha256"] = upc.canonical_argv_contract(request["argv"], request["argvBindings"])
        quality = {
            "schema": "fleet-universal-quality-equivalence-receipt/v1",
            "receiptId": "quality-" + "1" * 32,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=2)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)),
            "provider": request["provider"], "model": request["model"],
            "effort": request["effort"], "role": request["role"],
            "referenceSubjectSha256": request["subjectSha256"],
            "candidateSubjectSha256": request["subjectSha256"],
            "nonInferior": True, "independentReviewSha256": SHA_B,
            "receiptHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        quality["receiptHmacSha256"] = upc.contract_hmac(
            "quality-equivalence-receipt-v1", quality, self.secret, "receiptHmacSha256"
        )
        request["qualityEquivalenceReceipt"] = quality
        request["qualityEquivalenceReceiptSha256"] = upc.digest_json(quality)
        boundary = {
            "schema": "fleet-universal-wrapper-boundary-certification/v1",
            "certificationId": "boundary-" + "2" * 32,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=2)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)),
            "wrapperExecutableSha256": request["executableSha256"],
            "providerExecutableSha256": request["providerExecutableSha256"],
            "launcherConfigSha256": request["launcherConfigSha256"],
            "argvContractSha256": request["argvContractSha256"],
            "requestBoundaryMode": "SINGLE_REQUEST_PROCESS",
            "brokerPermitCommand": "reference-only-no-execution",
            "directInvocationImpossible": False,
            "processTreeTerminationRequired": True,
            "terminationObserverId": "process-tree-observer",
            "terminationObserverKeySha256": upc.signer_key_sha256(self.termination_secret),
            "qualityObserverId": "output-quality-observer",
            "qualityObserverKeySha256": upc.signer_key_sha256(self.quality_secret),
            "independentReviewSha256": SHA_C,
            "certificationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        boundary["certificationHmacSha256"] = upc.contract_hmac(
            "wrapper-boundary-certification-v1", boundary, self.secret,
            "certificationHmacSha256",
        )
        request["boundaryCertification"] = boundary
        request["boundaryCertificationSha256"] = upc.digest_json(boundary)
        if state_root_identity != "hmac-sha256:" + "0" * 64:
            request["priorIdleReceipt"]["receiptHmacSha256"] = upc.contract_hmac(
                "prior-idle-receipt-v1", request["priorIdleReceipt"], self.secret, "receiptHmacSha256"
            )
        return request

    def bind_runtime(self, broker: upc.UniversalProviderBroker) -> None:
        self.current_state_root_identity = broker.state_root_identity(self.secret)
        self.profile["coordination"]["stateRootIdentity"] = self.current_state_root_identity
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
        if phase == "TERMINAL":
            permit = self.permits.get(result["leaseId"])
            artifacts = self.terminal_artifacts.get(result["leaseId"])
            if artifacts is None:
                termination = {
                    "schema": "fleet-universal-process-tree-termination-receipt/v1",
                    "receiptId": "termination-" + "3" * 32,
                    "leaseId": result["leaseId"], "observedAt": upc.iso(self.now),
                    "expiresAt": upc.iso(self.now + dt.timedelta(minutes=1)),
                    "bindingSha256": result["bindingSha256"],
                    "rootProcessId": result["processId"],
                    "rootProcessStartTime": result["processStartTime"],
                    "rootExited": True, "liveDescendantCount": 0,
                    "observerQualified": True,
                    "observerId": "process-tree-observer",
                    "observerKeySha256": upc.signer_key_sha256(self.termination_secret),
                    "evidencePath": str(self.termination_evidence.resolve()),
                    "evidenceSha256": sha_file(self.termination_evidence),
                    "retainedEvidenceBytes": self.termination_evidence.stat().st_size,
                    "receiptHmacSha256": "hmac-sha256:" + "0" * 64,
                }
                termination["receiptHmacSha256"] = upc.contract_hmac(
                    "process-tree-termination-receipt-v1", termination, self.termination_secret,
                    "receiptHmacSha256",
                )
                usage = {
                    "inputTokens": 100, "cacheReadTokens": 1000, "cacheWriteTokens": 10,
                    "reasoningTokens": 100, "outputTokens": 100,
                } if permit is not None else {
                    "inputTokens": 0, "cacheReadTokens": 0, "cacheWriteTokens": 0,
                    "reasoningTokens": 0, "outputTokens": 0,
                }
                checkpoint_digest = None
                terminal_permit_digest = None
                output_quality = None
                if permit is not None:
                    broker = self.brokers[result["leaseId"]]
                    broker._checkpoint_provider_usage(
                        lease_id=result["leaseId"], phase="PRE_TURN", turn_count=1,
                        current_context_tokens=1000, peak_context_tokens=1000,
                        token_usage=usage, fleet_secret=self.secret, now=self.now,
                    )
                    terminal_permit = broker._issue_terminal_request_permit(
                        lease_id=result["leaseId"], fleet_secret=self.secret, now=self.now
                    )
                    checkpoint = broker._checkpoint_provider_usage(
                        lease_id=result["leaseId"], phase="TERMINAL", turn_count=1,
                        current_context_tokens=1000, peak_context_tokens=1000,
                        token_usage=usage, fleet_secret=self.secret, now=self.now,
                    )
                    checkpoint_digest = upc.digest_json(checkpoint)
                    terminal_permit_digest = upc.digest_json(terminal_permit)
                    output_quality = {
                        "schema": "fleet-universal-output-quality-receipt/v1",
                        "receiptId": "output-quality-" + "4" * 32,
                        "leaseId": result["leaseId"], "requestId": result["requestId"],
                        "bindingSha256": result["bindingSha256"],
                        "completedAt": upc.iso(self.now),
                        "expiresAt": upc.iso(self.now + dt.timedelta(minutes=1)),
                        "outputPath": str(self.output_artifact.resolve()),
                        "outputSha256": sha_file(self.output_artifact),
                        "retainedOutputBytes": self.output_artifact.stat().st_size,
                        "referenceOutputPath": str(self.reference_output.resolve()),
                        "referenceOutputSha256": sha_file(self.reference_output),
                        "retainedReferenceBytes": self.reference_output.stat().st_size,
                        "qualitySubjectSha256": self.request["subjectSha256"],
                        "providerUsageCheckpointSha256": checkpoint_digest,
                        "nonInferior": True,
                        "observerId": "output-quality-observer",
                        "observerKeySha256": upc.signer_key_sha256(self.quality_secret),
                        "independentReviewPath": str(self.output_review.resolve()),
                        "independentReviewSha256": sha_file(self.output_review),
                        "retainedIndependentReviewBytes": self.output_review.stat().st_size,
                        "receiptHmacSha256": "hmac-sha256:" + "0" * 64,
                    }
                    output_quality["receiptHmacSha256"] = upc.contract_hmac(
                        "output-quality-receipt-v1", output_quality, self.quality_secret,
                        "receiptHmacSha256",
                    )
                artifacts = {
                    "usage": usage, "checkpoint": checkpoint_digest,
                    "terminalPermit": terminal_permit_digest,
                    "termination": termination, "outputQuality": output_quality,
                }
                self.terminal_artifacts[result["leaseId"]] = copy.deepcopy(artifacts)
            observation.update(
                providerRequestCount=1 if permit is not None else 0,
                providerRequestPermitSha256=upc.digest_json(permit) if permit is not None else None,
                tokenUsage=copy.deepcopy(artifacts["usage"]),
                providerUsageCheckpointSha256=artifacts["checkpoint"],
                terminalRequestPermitSha256=artifacts["terminalPermit"],
                processTreeTerminationReceipt=copy.deepcopy(artifacts["termination"]),
                outputQualityReceipt=copy.deepcopy(artifacts["outputQuality"]),
            )
        observation["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", observation, self.secret, "observerHmacSha256"
        )
        return observation

    def transition(self, broker: upc.UniversalProviderBroker, target: str = "OPEN") -> None:
        self.bind_runtime(broker)
        if target == "OPEN":
            stages = ["CLOSED", "SHADOW", "CONTAINMENT", "OPEN"]
        else:
            stages = ["CLOSED", "SHADOW", "CONTAINMENT", "CANARY"]
        prior_digest = None
        for epoch, (source, destination) in enumerate(zip(stages, stages[1:]), start=1):
            canary_receipt = None
            if destination == "OPEN":
                synthetic_receipt = {
                    "schema": "fleet-universal-canary-success-receipt/v1",
                    "receiptId": "canary-success-" + "f" * 32,
                    "leaseId": "lease-" + "e" * 32,
                    "requestId": "request-test-transition",
                    "completedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
                    "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
                    "gateEpoch": epoch - 1,
                    "gateTransitionSha256": prior_digest or SHA_A,
                    "projectProfileSha256": upc.digest_json(self.profile),
                    "inventorySha256": upc.digest_json(self.inventory),
                    "providerRequestPermitSha256": SHA_A,
                    "providerUsageCheckpointSha256": SHA_B,
                    "outputQualityReceiptSha256": SHA_C,
                    "tokenUsageSha256": SHA_D,
                    "success": True,
                    "receiptHmacSha256": "hmac-sha256:" + "0" * 64,
                }
                synthetic_receipt["receiptHmacSha256"] = upc.contract_hmac(
                    "canary-success-receipt-v1", synthetic_receipt, self.secret,
                    "receiptHmacSha256",
                )
                canary_receipt = upc.digest_json(synthetic_receipt)
                with broker._connect() as connection:
                    connection.execute(
                        """INSERT OR REPLACE INTO canary_success_receipts(
                            receipt_id, receipt_digest, receipt_bytes, gate_epoch,
                            profile_digest, inventory_digest, used_at
                        ) VALUES (?, ?, ?, ?, ?, ?, NULL)""",
                        (
                            synthetic_receipt["receiptId"], canary_receipt,
                            upc.canonical_json(synthetic_receipt).encode("utf-8"), epoch - 1,
                            upc.digest_json(self.profile), upc.digest_json(self.inventory),
                        ),
                    )
            proof_type = {
                "SHADOW": "SHADOW_VALIDATION", "CONTAINMENT": "CONTAINMENT_ENFORCEMENT",
                "CANARY": "CANARY_READINESS", "OPEN": "CANARY_SUCCESS_ADJUDICATION",
            }[destination]
            proof = {
                "schema": "fleet-universal-stage-proof/v1", "proofId": "stage-" + f"{epoch:032x}",
                "proofType": proof_type, "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
                "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)), "targetStage": destination,
                "priorTransitionSha256": prior_digest,
                "projectProfileSha256": upc.digest_json(self.profile),
                "inventorySha256": upc.digest_json(self.inventory),
                "hostedNegativeSuiteSha256": SHA_C, "independentReviewSha256": SHA_B,
                "canarySuccessReceiptSha256": canary_receipt, "oneUse": True,
                "proofHmacSha256": "hmac-sha256:" + "0" * 64,
            }
            proof["proofHmacSha256"] = upc.contract_hmac(
                "stage-proof-v1", proof, self.secret, "proofHmacSha256"
            )
            transition = {
                "schema": "fleet-universal-gate-transition/v1",
                "transitionId": f"transition-{epoch:04d}",
                "transitionEpoch": epoch,
                "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
                "expiresAt": upc.iso(self.now + dt.timedelta(minutes=10)),
                "from": source,
                "to": destination,
                "cause": "INDEPENDENT_ADJUDICATION",
                "doctrineCommitSha256": SHA_A,
                "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
                "projectProfileSha256": upc.digest_json(self.profile),
                "inventorySha256": upc.digest_json(self.inventory),
                "brokerHealthSha256": upc.digest_json(self.health),
                "reviewReceiptSha256": SHA_B,
                "testReceiptSha256": SHA_C,
                "stageProof": proof,
                "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
            }
            transition["authorizationHmacSha256"] = upc.contract_hmac(
                "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
            )
            broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)
            prior_digest = upc.digest_json(transition)
            if destination == target:
                return
        self.fail(f"unknown gate target {target}")

    def stage_proof(self, target: str, *, prior: str | None = None, receipt: str | None = None, serial: int = 99) -> dict:
        proof = {
            "schema": "fleet-universal-stage-proof/v1", "proofId": "stage-" + f"{serial:032x}",
            "proofType": {"CLOSED": "SAFETY_CLOSE", "SHADOW": "SHADOW_VALIDATION",
                          "CONTAINMENT": "CONTAINMENT_ENFORCEMENT", "CANARY": "CANARY_READINESS",
                          "OPEN": "CANARY_SUCCESS_ADJUDICATION"}[target],
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)), "targetStage": target,
            "priorTransitionSha256": prior, "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory), "hostedNegativeSuiteSha256": SHA_C,
            "independentReviewSha256": SHA_B, "canarySuccessReceiptSha256": receipt,
            "oneUse": True, "proofHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        proof["proofHmacSha256"] = upc.contract_hmac(
            "stage-proof-v1", proof, self.secret, "proofHmacSha256"
        )
        return proof

    def authorize(self, broker: upc.UniversalProviderBroker, request: dict | None = None, **changes) -> dict:
        broker.install_independent_receipt_signers(self.receipt_signer_secrets)
        confirm = changes.pop("confirm", True)
        begin_request = changes.pop("begin_request", True)
        preserve_prior_idle = changes.pop("preserve_prior_idle", False)
        selected_request = request or self.request
        if "profile" not in changes:
            self.bind_runtime(broker)
            if not preserve_prior_idle and isinstance(selected_request, dict):
                request_id = selected_request.get("requestId")
                project = selected_request.get("project")
                if isinstance(request_id, str) and isinstance(project, str):
                    key = (id(broker._root_runtime), request_id)
                    receipt = self.prior_receipts.get(key)
                    if receipt is None:
                        with self.prior_receipt_lock:
                            receipt = self.prior_receipts.get(key)
                            if receipt is None:
                                admission_now = changes.get("now", self.now)
                                pool_key = (id(broker._root_runtime), project)
                                pool = self.prior_receipt_pools.get(pool_key)
                                if pool is None:
                                    broker.pin_demand_authority(
                                        project=project,
                                        authority_path=self.prior_idle_authority,
                                        authority_sha256=sha_file(self.prior_idle_authority),
                                        fleet_secret=self.secret,
                                        now=admission_now - dt.timedelta(seconds=11),
                                    )
                                    values = [broker.record_prior_idle(
                                        project=project, fleet_secret=self.secret,
                                        now=admission_now - dt.timedelta(seconds=10),
                                        max_age_seconds=self.profile["policy"]["maxPriorIdleAgeSeconds"],
                                    ) for _ in range(16)]
                                    pool = {value["receiptId"]: value for value in values}
                                    self.prior_receipt_pools[pool_key] = pool
                                    broker.pin_demand_authority(
                                        project=project,
                                        authority_path=self.demand_authority,
                                        authority_sha256=sha_file(self.demand_authority),
                                        fleet_secret=self.secret,
                                        now=admission_now - dt.timedelta(seconds=1),
                                    )
                                with broker._connect() as pool_connection:
                                    newest = pool_connection.execute(
                                        """SELECT receipt_id FROM prior_idle_receipts
                                        WHERE project=? AND used_at IS NULL
                                        ORDER BY sequence DESC LIMIT 1""", (project,),
                                    ).fetchone()
                                if newest is None or newest["receipt_id"] not in pool:
                                    raise AssertionError("TEST_PRIOR_IDLE_POOL_EXHAUSTED")
                                receipt = pool[newest["receipt_id"]]
                                self.prior_receipts[key] = copy.deepcopy(receipt)
                    selected_request["priorIdleReceipt"] = copy.deepcopy(receipt)
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
        if result.get("status") == "PREPARED_SUSPENDED":
            self.brokers[result["leaseId"]] = broker
        if confirm and result.get("status") == "PREPARED_SUSPENDED":
            resume = self.admission_observation(selected_request, phase="RESUME", lease_id=result["leaseId"])
            confirmed = broker.confirm_resume_boundary(
                lease_id=result["leaseId"], process_observation=resume, fleet_secret=self.secret, now=self.now
            )
            self.brokers[result["leaseId"]] = broker
            if begin_request:
                self.permits[result["leaseId"]] = broker._begin_provider_request(
                    lease_id=result["leaseId"], fleet_secret=self.secret, now=self.now
                )
            return confirmed
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
        self.assertEqual(self.authorize(broker, third)["reason"], "PROCESS_IDENTITY_ALREADY_CLAIMED")

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
        broker._clock = lambda: later_now
        result = self.authorize(broker, later_request, native_evidence=[native], now=later_now, process_observation=process)
        self.assertEqual(first["status"], "ALLOW_ATTESTED")
        self.assertEqual(result["reason"], "PRIOR_IDLE_RECEIPT_INVALID")
        with broker._connect() as connection:
            self.assertEqual(connection.execute(
                "SELECT state FROM leases WHERE lease_id=?", (first["leaseId"],)
            ).fetchone()[0], "RESUME_ATTESTED")
        self.assertIn(first["leaseId"], broker._os_locks)

    def test_multi_window_dimension_cannot_be_selected_away(self) -> None:
        native = copy.deepcopy(self.native)
        del native["payload"]["weeklyUtilization"]
        self.resign_native(native)
        broker = upc.UniversalProviderBroker(self.root / "dimension.db")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, native_evidence=[native])["reason"], "SCHEMA_VALIDATION_FAILED")

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
        broker = upc.UniversalProviderBroker(self.root / "idle.db")
        self.transition(broker)
        broker.pin_demand_authority(
            project=request["project"], authority_path=self.demand_authority,
            authority_sha256=sha_file(self.demand_authority), fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=11),
        )
        with self.assertRaisesRegex(upc.ControlError, "PRIOR_IDLE_ACTIONABLE_WORK"):
            broker.record_prior_idle(
                project=request["project"], fleet_secret=self.secret,
                now=self.now - dt.timedelta(seconds=10),
            )

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
            "stageProof": self.stage_proof("OPEN", receipt=SHA_D, serial=97),
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
            "testReceiptSha256": SHA_C, "stageProof": self.stage_proof("OPEN", receipt=SHA_D, serial=98),
            "authorizationHmacSha256": "hmac-sha256:" + "f" * 64,
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
            ("directory", lambda path: path.name == "quota-locks"),
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
                self.assertIn(outcome["reason"], {"LAUNCH_PROFILE_NOT_REVIEWED", "UNIVERSAL_QUALITY_FLOOR_VIOLATION", "SCHEMA_VALIDATION_FAILED"})
            else:
                self.assertIn(outcome["reason"], {"LAUNCH_PROFILE_NOT_REVIEWED", "UNIVERSAL_QUALITY_FLOOR_VIOLATION"})

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
        broker._clock = lambda: later
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

        broker._clock = lambda: self.now
        canary_broker = upc.UniversalProviderBroker(self.root / "r3-expired-canary")
        self.transition(canary_broker, "CANARY")
        canary_request = self.make_request("request-r3-expired-canary")
        canary_identity = b"canary-expiry-" + str(self.root).encode("utf-8")
        canary_request["quotaDomainId"] = upc.derive_quota_domain_id("claude", canary_identity, self.secret)
        canary_request["maxWallSeconds"] = 1
        canary_request["canary"] = True
        authorization = self.make_canary_authorization(canary_request, "canary-r3-expiry")
        canary_prepared = self.authorize(
            canary_broker, canary_request, manual_authorization=authorization, confirm=False,
            local_stable_identity=canary_identity,
            native_evidence=[self.resign_native({**copy.deepcopy(self.native), "quotaDomainId": canary_request["quotaDomainId"]})],
        )
        canary_receipt = self.admission_observation(
            canary_request, phase="RESUME", lease_id=canary_prepared["leaseId"]
        )
        canary_receipt["observedAt"] = upc.iso(later)
        canary_receipt["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", canary_receipt, self.secret, "observerHmacSha256"
        )
        canary_broker._clock = lambda: later
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

    def test_r3_05_capacity_estimates_are_broker_derived_not_caller_selected(self) -> None:
        first_broker = upc.UniversalProviderBroker(self.root / "r3-estimates-a")
        self.transition(first_broker)
        first = self.authorize(first_broker)
        self.assertNotIn("windowEstimates", first)
        with first_broker._connect() as connection:
            derived = json.loads(connection.execute(
                "SELECT reservations_json FROM leases WHERE lease_id=?", (first["leaseId"],)
            ).fetchone()[0])
        self.assertEqual(set(derived), {"session", "weekly"})
        self.assertEqual(derived["session"], derived["weekly"])
        changed = self.make_request("request-r3-estimates-b")
        changed["windowEstimates"] = {"session": 0.04, "weekly": 0.04}
        second_broker = upc.UniversalProviderBroker(self.root / "r3-estimates-b")
        self.transition(second_broker)
        self.assertEqual(self.authorize(second_broker, changed)["reason"], "SCHEMA_VALIDATION_FAILED")

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
        terminal = self.process_observation(prepared, "FAILED", phase="TERMINAL")
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
        provider_inputs = (("3", "4"), ("5", "6"), ("7", "8"))
        for offset, (seat_digit, session_digit) in enumerate(provider_inputs, start=1):
            identity = f"independent-account-{offset}-".encode("ascii") + str(self.root).encode("utf-8")
            request = self.make_request(f"request-r11-claude-{offset}-lease")
            request.update(
                quotaDomainId=upc.derive_quota_domain_id("claude", identity, self.secret),
                seatIdHash="hmac-sha256:" + seat_digit * 64,
                sessionIdHash="hmac-sha256:" + session_digit * 64,
            )
            native = self.make_native("claude")
            native["quotaDomainId"] = request["quotaDomainId"]
            self.resign_native(native)
            process = self.admission_observation(request)
            process["processId"] += offset
            process["observerHmacSha256"] = upc.contract_hmac(
                "process-observation-v1", process, self.secret, "observerHmacSha256"
            )
            prepared_leases.append(self.authorize(
                broker, request, confirm=False,
                native_evidence=[native], local_stable_identity=identity,
                process_observation=process,
            ))
        self.assertEqual(
            {prepared["status"] for prepared in prepared_leases}, {"PREPARED_SUSPENDED"}
        )
        self.assertEqual(len(broker._artifact_handles), upc.MAX_PREPARED_LEASES_PER_STATE_ROOT)

        fifth_identity = b"second-local-account-" + str(self.root).encode("utf-8")
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
                            prepared, "FAILED", phase="TERMINAL"
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
                        prepared_leases[-1], "FAILED", phase="TERMINAL"
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
                        first, "FAILED", phase="TERMINAL"
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
        second_process = self.admission_observation(second_request)
        second_process["processId"] += 1
        second_process["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", second_process, self.secret, "observerHmacSha256"
        )
        second = self.authorize(
            broker, second_request, confirm=False, process_observation=second_process
        )
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
                        second, "FAILED", phase="TERMINAL"
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
                        second, "FAILED", phase="TERMINAL"
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

    # R12 hosted portability controls. These are self-contained because hosted checkouts are shallow.

    def test_r12_01_manifest_self_uses_canonical_git_blob_under_crlf_checkout(self) -> None:
        import check_universal_manifest as checker

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
        publication = inspect.getsource(upc._publish_owned_temporary)
        syscall = inspect.getsource(upc._publication_syscall)
        current_tests = (
            inspect.getsource(self.test_r4_03_no_clobber_publication_preserves_foreign_races)
            + inspect.getsource(self.test_r5_01_publication_binds_retained_temp_identity_and_exact_bytes)
        )
        self.assertGreaterEqual(publication.count("_publication_syscall("), 2)
        self.assertIn("libc.linkat", syscall)
        self.assertIn('mock.patch.object(upc, "_publication_syscall"', current_tests)

    def test_r13_01_prepare_before_reset_confirm_after_is_denied_and_fenced(self) -> None:
        native = copy.deepcopy(self.native)
        boundary = self.now + dt.timedelta(seconds=1)
        native["payload"]["sessionResetAt"] = upc.iso(boundary)
        native["payload"]["weeklyResetAt"] = upc.iso(self.now + dt.timedelta(seconds=5))
        self.resign_native(native)

        broker = upc.UniversalProviderBroker(self.root / "r12-rollover-resume")
        self.transition(broker)
        prepared = self.authorize(broker, native_evidence=[native], confirm=False)
        self.assertEqual(prepared["status"], "PREPARED_SUSPENDED")
        self.assertEqual(prepared["capacityValidUntil"], upc.iso(boundary))
        self.assertIn("capacityValidUntil", prepared)
        connection = sqlite3.connect(broker.database)
        try:
            row = connection.execute(
                "SELECT capacity_valid_until, state FROM leases WHERE lease_id=?",
                (prepared["leaseId"],),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(row, (upc.iso(boundary), "ACTIVE"))

        later = boundary + dt.timedelta(microseconds=1)
        resume = self.admission_observation(
            self.request, phase="RESUME", lease_id=prepared["leaseId"]
        )
        resume["observedAt"] = upc.iso(later)
        resume["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", resume, self.secret, "observerHmacSha256"
        )
        broker._clock = lambda: later
        with self.assertRaisesRegex(
            upc.ControlError, "LEASE_EXPIRED_BEFORE_RESUME"
        ):
            broker.confirm_resume_boundary(
                lease_id=prepared["leaseId"], process_observation=resume,
                fleet_secret=self.secret, now=later,
            )
        self.assertIn(prepared["leaseId"], broker._os_locks)
        self.assertIn(prepared["leaseId"], broker._artifact_handles)
        connection = sqlite3.connect(broker.database)
        try:
            self.assertEqual(
                connection.execute(
                    "SELECT state FROM leases WHERE lease_id=?", (prepared["leaseId"],)
                ).fetchone()[0],
                "ACTIVE",
            )
        finally:
            connection.close()

        broker._clock = lambda: self.now
        canary = upc.UniversalProviderBroker(self.root / "r12-rollover-canary")
        self.transition(canary, "CANARY")
        canary_request = self.make_request("request-r12-rollover-canary")
        canary_identity = b"rollover-canary-" + str(self.root).encode("utf-8")
        canary_request["quotaDomainId"] = upc.derive_quota_domain_id("claude", canary_identity, self.secret)
        canary_request["canary"] = True
        authorization = self.make_canary_authorization(
            canary_request, "canary-r12-rollover"
        )
        canary_prepared = self.authorize(
            canary, canary_request,
            native_evidence=[self.resign_native({**copy.deepcopy(native), "quotaDomainId": canary_request["quotaDomainId"]})],
            local_stable_identity=canary_identity,
            manual_authorization=authorization, confirm=False,
        )
        canary_resume = self.admission_observation(
            canary_request, phase="RESUME", lease_id=canary_prepared["leaseId"]
        )
        canary_resume["observedAt"] = upc.iso(later)
        canary_resume["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", canary_resume, self.secret, "observerHmacSha256"
        )
        canary._clock = lambda: later
        with self.assertRaisesRegex(
            upc.ControlError, "LEASE_EXPIRED_BEFORE_RESUME"
        ):
            canary.confirm_resume_boundary(
                lease_id=canary_prepared["leaseId"], process_observation=canary_resume,
                fleet_secret=self.secret, now=later,
            )
        self.assertEqual(canary.gate_state(fleet_secret=self.secret, now=later), "CLOSED")
        self.assertIn(canary_prepared["leaseId"], canary._os_locks)
        self.assertIn(canary_prepared["leaseId"], canary._artifact_handles)

    def test_r13_02_exact_reviewed_launch_profile_is_required_and_attested(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r12-reviewed-profile")
        self.transition(broker)
        allowed = self.authorize(broker)
        self.assertEqual(
            (allowed["model"], allowed["effort"], allowed["role"]),
            (self.request["model"], self.request["effort"], self.request["role"]),
        )

        economy = self.make_request("request-r12-economy")
        economy["effort"] = "minimal"
        economy["argv"][economy["argvBindings"]["effortIndex"]] = "minimal"
        economy["argvSha256"] = upc.digest_json(economy["argv"])
        other = upc.UniversalProviderBroker(self.root / "r12-unreviewed-economy")
        self.transition(other)
        self.assertEqual(
            self.authorize(other, economy)["reason"], "SCHEMA_VALIDATION_FAILED"
        )

    def test_r13_03_turn_context_and_all_token_ceilings_are_argv_bound_and_attested(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r12-token-bounds")
        self.transition(broker)
        allowed = self.authorize(broker)
        self.assertEqual(allowed["maxTurns"], self.request["maxTurns"])
        self.assertEqual(allowed["maxContextTokens"], self.request["maxContextTokens"])
        self.assertEqual(
            allowed["cumulativeTokenCeilings"], self.request["cumulativeTokenCeilings"]
        )

        over = self.make_request("request-r12-token-over")
        over["cumulativeTokenCeilings"]["cacheReadTokens"] = (
            self.profile["efficiency"]["maxCumulativeTokenCeilings"]["cacheReadTokens"] + 1
        )
        other = upc.UniversalProviderBroker(self.root / "r12-token-over")
        self.transition(other)
        self.assertEqual(
            self.authorize(other, over)["reason"], "CUMULATIVE_TOKEN_BOUND_EXCEEDED"
        )

        unbound = self.make_request("request-r12-token-unbound")
        unbound["cumulativeTokenCeilings"]["outputTokens"] -= 1
        unbound["generatedEnvelopeTokens"] -= 1
        third = upc.UniversalProviderBroker(self.root / "r12-token-unbound")
        self.transition(third)
        self.assertEqual(self.authorize(third, unbound)["reason"], "ARGV_BINDING_DRIFT")

    def test_r13_04_broker_recomputes_current_and_prior_demand_from_frozen_inputs(self) -> None:
        forged = self.make_request("request-r12-demand-forged")
        forged["demandFingerprint"] = SHA_A
        broker = upc.UniversalProviderBroker(self.root / "r12-demand-forged")
        self.transition(broker)
        self.assertEqual(
            self.authorize(broker, forged)["reason"], "DEMAND_FINGERPRINT_DRIFT"
        )

        forged_prior = self.make_request("request-r12-prior-forged")
        second = upc.UniversalProviderBroker(self.root / "r12-prior-forged")
        self.transition(second)
        forged_prior["priorIdleReceipt"]["stateRootIdentity"] = second.state_root_identity(self.secret)
        forged_prior["priorIdleReceipt"]["demandFingerprint"] = SHA_A
        self.assertEqual(
            self.authorize(second, forged_prior, preserve_prior_idle=True)["reason"],
            "CONTRACT_HMAC_INVALID"
        )

        drifted = self.make_request("request-r12-demand-bytes-drift")
        drifted["demandSnapshot"]["addressedWork"].append(
            {"kind": "ISSUE", "id": "foreign", "state": "READY", "subjectSha256": SHA_A}
        )
        third = upc.UniversalProviderBroker(self.root / "r12-demand-bytes-drift")
        self.transition(third)
        self.assertEqual(self.authorize(third, drifted)["reason"], "DEMAND_AUTHORITY_DRIFT")

    def test_r13_05_rollout_requires_containment_and_forbids_stage_skips(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r12-stage-skip")
        self.bind_runtime(broker)
        transition = {
            "schema": "fleet-universal-gate-transition/v1",
            "transitionId": "transition-r12-skip",
            "transitionEpoch": 1,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "from": "CLOSED", "to": "OPEN", "cause": "INDEPENDENT_ADJUDICATION",
            "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health),
            "reviewReceiptSha256": SHA_B, "testReceiptSha256": SHA_C,
            "stageProof": self.stage_proof("OPEN", receipt=SHA_D, serial=96),
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        transition["authorizationHmacSha256"] = upc.contract_hmac(
            "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "GATE_STAGE_SKIP"):
            broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)

        containment = upc.UniversalProviderBroker(self.root / "r12-containment")
        self.transition(containment, "CONTAINMENT")
        self.assertEqual(
            containment.gate_state(fleet_secret=self.secret, now=self.now), "CONTAINMENT"
        )
        self.assertEqual(
            self.authorize(containment)["reason"], "AUTOMATIC_LAUNCH_GATE_CLOSED"
        )

    # R15 certified-boundary and typed-proof hostile controls.

    def test_r15_01_single_request_process_permit_is_persisted_and_one_use(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r15-single-request")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        first = broker._begin_provider_request(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        upc.validate_contract("request_permit", first)
        with self.assertRaisesRegex(upc.ControlError, "PROVIDER_REQUEST_LIMIT_REACHED"):
            broker._begin_provider_request(
                lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
            )
        with broker._connect() as connection:
            row = connection.execute(
                "SELECT permit_count, permit_digest, state FROM token_reservations WHERE lease_id=?",
                (allowed["leaseId"],),
            ).fetchone()
        self.assertEqual(tuple(row), (1, upc.digest_json(first), "IN_FLIGHT"))

    def test_r15_02_semantic_demand_is_order_independent_and_idle_receipt_is_broker_signed(self) -> None:
        snapshot = copy.deepcopy(self.request["demandSnapshot"])
        snapshot["addressedWork"].append(
            {"kind": "REVIEW", "id": "review-9", "state": "OPEN", "subjectSha256": SHA_A}
        )
        reversed_snapshot = copy.deepcopy(snapshot)
        reversed_snapshot["addressedWork"].reverse()
        self.assertEqual(
            upc.canonical_demand_fingerprint(snapshot),
            upc.canonical_demand_fingerprint(reversed_snapshot),
        )
        broker = upc.UniversalProviderBroker(self.root / "r15-idle-receipt")
        self.prior_idle_authority.write_bytes(
            upc.canonical_json(self.prior_idle_snapshot).encode("utf-8")
        )
        broker.pin_demand_authority(
            project="test-project", authority_path=self.prior_idle_authority,
            authority_sha256=sha_file(self.prior_idle_authority), fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=1),
        )
        receipt = broker.record_prior_idle(
            project="test-project", fleet_secret=self.secret, now=self.now,
        )
        upc.validate_contract("prior_idle_receipt", receipt)
        forged = copy.deepcopy(receipt)
        forged["demandFingerprint"] = SHA_B
        with self.assertRaisesRegex(upc.ControlError, "CONTRACT_HMAC_INVALID"):
            upc.verify_contract_hmac(
                "prior-idle-receipt-v1", forged, self.secret, "receiptHmacSha256"
            )

    def test_r15_03_mutable_lease_capacity_cannot_extend_immutable_attestation(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r15-binding-drift")
        self.transition(broker)
        prepared = self.authorize(broker, confirm=False)
        with broker._connect() as connection:
            connection.execute(
                "UPDATE leases SET capacity_valid_until=? WHERE lease_id=?",
                (upc.iso(self.now + dt.timedelta(days=1)), prepared["leaseId"]),
            )
        resume = self.admission_observation(
            self.request, phase="RESUME", lease_id=prepared["leaseId"]
        )
        with self.assertRaisesRegex(upc.ControlError, "LEASE_BINDING_DRIFT"):
            broker.confirm_resume_boundary(
                lease_id=prepared["leaseId"], process_observation=resume,
                fleet_secret=self.secret, now=self.now,
            )
        self.assertIn(prepared["leaseId"], broker._os_locks)

    def test_r15_04_runtime_watchdog_marks_termination_required_at_boundary(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r15-watchdog")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        later = self.now + dt.timedelta(seconds=61)
        broker._clock = lambda: later
        with self.assertRaisesRegex(upc.ControlError, "RUNTIME_TERMINATION_REQUIRED"):
            broker.check_runtime_boundary(
                lease_id=allowed["leaseId"], fleet_secret=self.secret,
                now=later,
            )
        with broker._connect() as connection:
            state = connection.execute(
                "SELECT state FROM leases WHERE lease_id=?", (allowed["leaseId"],)
            ).fetchone()[0]
        self.assertEqual(state, "TERMINATION_REQUIRED")
        self.assertIn(allowed["leaseId"], broker._os_locks)

    def test_r15_05_quality_floor_and_exact_argv_contract_reject_weak_or_extra_launches(self) -> None:
        weak = self.make_request("request-r15-weak")
        weak["model"] = "tiny-economy-model"
        weak["argv"][weak["argvBindings"]["modelIndex"]] = weak["model"]
        weak["argvSha256"] = upc.digest_json(weak["argv"])
        weak["argvContractSha256"] = upc.canonical_argv_contract(weak["argv"], weak["argvBindings"])
        broker = upc.UniversalProviderBroker(self.root / "r15-quality")
        self.transition(broker)
        self.assertEqual(
            self.authorize(broker, weak)["reason"], "UNIVERSAL_QUALITY_FLOOR_VIOLATION"
        )
        extra = self.make_request("request-r15-extra")
        extra["argv"].append("--direct-provider-bypass")
        extra["argvSha256"] = upc.digest_json(extra["argv"])
        other = upc.UniversalProviderBroker(self.root / "r15-argv-extra")
        self.transition(other)
        self.assertEqual(self.authorize(other, extra)["reason"], "ARGV_CONTRACT_DRIFT")

    def test_r15_06_alternate_state_root_cannot_bypass_machine_quota_lock(self) -> None:
        first = upc.UniversalProviderBroker(self.root / "r15-root-a")
        self.transition(first)
        held = self.authorize(first, confirm=False)
        self.assertEqual(held["status"], "PREPARED_SUSPENDED")

        second = upc.UniversalProviderBroker(self.root / "r15-root-b")
        self.transition(second)
        request = self.make_request("request-r15-other-root")
        process = self.admission_observation(request)
        process["processId"] += 99
        process["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", process, self.secret, "observerHmacSha256"
        )
        self.assertEqual(
            self.authorize(second, request, confirm=False, process_observation=process)["reason"],
            "QUOTA_DOMAIN_OS_LOCK_HELD",
        )

    def test_r15_07_successful_canary_returns_to_containment_and_receipt_opens_once(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r15-canary-proof")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r15-canary")
        request["canary"] = True
        authorization = self.make_canary_authorization(request, "canary-r15-proof")
        allowed = self.authorize(broker, request, manual_authorization=authorization)
        released = broker.release_child(
            process_observation=self.process_observation(allowed, "EXITED", phase="TERMINAL"),
            fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CONTAINMENT")
        receipt_digest = released["canarySuccessReceiptSha256"]
        proof = self.stage_proof("OPEN", receipt=receipt_digest, serial=150)
        transition = {
            "schema": "fleet-universal-gate-transition/v1", "transitionId": "transition-r15-open",
            "transitionEpoch": 4, "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)), "from": "CONTAINMENT",
            "to": "OPEN", "cause": "INDEPENDENT_ADJUDICATION", "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health), "reviewReceiptSha256": SHA_B,
            "testReceiptSha256": SHA_C, "stageProof": proof,
            "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        transition["authorizationHmacSha256"] = upc.contract_hmac(
            "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
        )
        self.assertEqual(broker.transition_gate(transition, fleet_secret=self.secret, now=self.now), "OPEN")
        with broker._connect() as connection:
            used = connection.execute(
                "SELECT used_at FROM canary_success_receipts WHERE receipt_digest=?", (receipt_digest,)
            ).fetchone()[0]
        self.assertEqual(used, upc.iso(self.now))

    # Exact ecc8f07 R13 RED -> R14 GREEN target-directory owner-lifetime twin.

    def test_r14_01_posix_directory_close_refusal_poison_is_attempt_once(self) -> None:
        # Exact predecessor provenance is checked by the full-history manifest workflow;
        # keep this behavioral twin self-contained for depth-one test execution.
        self.assertEqual(R13_DIRECTORY_CLOSE_FIXTURE, "os.close(directory)")
        current_publication = inspect.getsource(upc._publish_owned_temporary)
        self.assertNotIn("os.close(directory)", current_publication)
        self.assertIn("_close_owned_descriptor(directory)", current_publication)
        self.assertIn('("target-directory-descriptor", directory)', current_publication)
        self.assertEqual(upc.MAX_CAPSULE_POISON_OWNERS, 259)

        if os.name != "posix":
            return
        if not Path("/proc/self/fd").is_dir() or not getattr(os, "O_TMPFILE", 0):
            self.skipTest("native anonymous publication route unavailable")

        source = self.root / "r14-directory-owner-source.bin"
        source.write_bytes(b"directory-owner-refusal")
        request = self.capsule_request(source, lengths=[8])
        real_close = upc._close_owned_descriptor
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        private_value = "PRIVATE-R14-DIRECTORY-CLOSE"

        for index, close_outcome in enumerate((False, RuntimeError(private_value))):
            output = self.root / f"r14-directory-owner-{index}.bin"
            key = os.path.normcase(os.path.abspath(str(output)))
            close_calls: list[int] = []

            try:
                probe = upc._open_posix_anonymous_temporary(
                    output.parent, flags, os.O_TMPFILE, output
                )
            except OSError:
                self.skipTest("test filesystem lacks native O_TMPFILE support")
            else:
                self.assertTrue(upc._attempt_file_close_verified(probe))

            def force_anonymous(_temporary, candidate_output):
                return (
                    upc._open_posix_anonymous_temporary(
                        candidate_output.parent, flags, os.O_TMPFILE, candidate_output
                    ),
                    False,
                )

            def refuse_directory_close(descriptor):
                close_calls.append(descriptor)
                if isinstance(close_outcome, BaseException):
                    raise close_outcome
                return close_outcome

            with mock.patch.object(upc, "_open_owned_temporary", side_effect=force_anonymous):
                with mock.patch.object(
                    upc, "_close_owned_descriptor", side_effect=refuse_directory_close
                ):
                    with self.assertRaises(upc.ControlError) as caught:
                        upc.build_evidence_capsule(request, output)

            self.assertEqual(caught.exception.reason, "CAPSULE_TEMP_CLEANUP_REFUSED")
            self.assertIsNone(caught.exception.__cause__)
            self.assertIsNone(caught.exception.__context__)
            self.assertNotIn(private_value, "".join(traceback.format_exception(caught.exception)))
            self.assertEqual(output.read_bytes(), source.read_bytes()[:8])
            self.assertEqual(len(close_calls), 1)
            owners = upc._UNPROVEN_CAPSULE_OWNERS[key]
            self.assertEqual(owners, [("target-directory-descriptor", close_calls[0])])
            self.assertLessEqual(
                sum(len(values) for values in upc._UNPROVEN_CAPSULE_OWNERS.values()),
                upc.MAX_CAPSULE_POISON_OWNERS,
            )

            rotated = self.root / f"r14-directory-owner-rotated-{index}.bin"
            with mock.patch.object(
                upc, "_open_owned_temporary", side_effect=AssertionError("new owner acquired")
            ) as acquisition:
                with mock.patch.object(
                    upc, "_close_owned_descriptor", side_effect=AssertionError("owner retried")
                ) as retry:
                    for blocked_output in (rotated, output):
                        with self.assertRaisesRegex(upc.ControlError, "CAPSULE_TEMP_BACKLOG"):
                            upc.build_evidence_capsule(request, blocked_output)
            acquisition.assert_not_called()
            retry.assert_not_called()
            self.assertEqual(close_calls, [owners[0][1]])
            with self.assertRaisesRegex(upc.ControlError, "CAPSULE_CLEANUP_POISONED"):
                upc.assert_process_cleanup_clear()

            real_close(owners[0][1])
            upc._UNPROVEN_CAPSULE_OWNERS.pop(key)
            output.with_name(output.name + ".cleanup-blocked").unlink()
            upc.assert_process_cleanup_clear()

    # R16 persistent demand, certified boundary, accounting, and reconciliation controls.

    def test_r16_01_prior_idle_is_persisted_fresh_monotonic_and_one_use(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-idle")
        self.transition(broker)
        broker.pin_demand_authority(
            project="test-project", authority_path=self.prior_idle_authority,
            authority_sha256=sha_file(self.prior_idle_authority), fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=13),
        )
        older = broker.record_prior_idle(
            project="test-project", fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=12),
        )
        newest = broker.record_prior_idle(
            project="test-project", fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=10),
        )
        broker.pin_demand_authority(
            project="test-project", authority_path=self.demand_authority,
            authority_sha256=sha_file(self.demand_authority), fleet_secret=self.secret,
            now=self.now - dt.timedelta(seconds=1),
        )
        stale_request = self.make_request("request-r16-idle-stale")
        stale_request["priorIdleReceipt"] = older
        self.assertEqual(
            self.authorize(broker, stale_request, preserve_prior_idle=True)["reason"],
            "PRIOR_IDLE_RECEIPT_REPLAY_OR_STALE",
        )
        request = self.make_request("request-r16-idle-current")
        request["priorIdleReceipt"] = newest
        allowed = self.authorize(
            broker, request, preserve_prior_idle=True, confirm=False
        )
        self.assertEqual(allowed["status"], "PREPARED_SUSPENDED")
        replay = self.make_request("request-r16-idle-replay")
        replay["priorIdleReceipt"] = newest
        self.assertEqual(
            self.authorize(broker, replay, preserve_prior_idle=True)["reason"],
            "PRIOR_IDLE_RECEIPT_REPLAY_OR_STALE",
        )

    def test_r16_02_broker_pinned_canonical_demand_rejects_fabricated_ready(self) -> None:
        fabricated = self.make_request("request-r16-fabricated-ready")
        fabricated["demandSnapshot"]["addressedWork"].append(
            {"kind": "ISSUE", "id": "fabricated", "state": "READY", "subjectSha256": SHA_A}
        )
        fabricated["demandFingerprint"] = upc.canonical_demand_fingerprint(
            fabricated["demandSnapshot"]
        )
        broker = upc.UniversalProviderBroker(self.root / "r16-demand")
        self.transition(broker)
        self.assertEqual(
            self.authorize(broker, fabricated)["reason"], "DEMAND_AUTHORITY_DRIFT"
        )

    def test_r16_03_usage_checkpoints_reserve_terminal_completion_exactly_once(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-accounting")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        permit = broker._begin_provider_request(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        first_usage = {
            "inputTokens": 1000, "cacheReadTokens": 2000, "cacheWriteTokens": 100,
            "reasoningTokens": 500, "outputTokens": 20000,
        }
        broker._checkpoint_provider_usage(
            lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=1,
            current_context_tokens=4000, peak_context_tokens=4000,
            token_usage=first_usage, fleet_secret=self.secret, now=self.now,
        )
        over_reserve = dict(first_usage, outputTokens=20001)
        with self.assertRaisesRegex(upc.ControlError, "COMPLETION_RESERVE_VIOLATION"):
            broker._checkpoint_provider_usage(
                lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=2,
                current_context_tokens=4000, peak_context_tokens=4000,
                token_usage=over_reserve, fleet_secret=self.secret, now=self.now,
            )
        terminal = broker._issue_terminal_request_permit(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        with self.assertRaisesRegex(upc.ControlError, "TERMINAL_REQUEST_ALREADY_ISSUED"):
            broker._issue_terminal_request_permit(
                lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
            )
        final_usage = dict(first_usage, outputTokens=25000)
        checkpoint = broker._checkpoint_provider_usage(
            lease_id=allowed["leaseId"], phase="TERMINAL", turn_count=1,
            current_context_tokens=4000, peak_context_tokens=4000,
            token_usage=final_usage, fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(checkpoint["providerRequestPermitSha256"], upc.digest_json(permit))
        self.assertEqual(checkpoint["terminalRequestPermitSha256"], upc.digest_json(terminal))

    def test_r16_04_durable_cross_root_claim_survives_owner_loss_until_authenticated_recovery(self) -> None:
        first = upc.UniversalProviderBroker(self.root / "r16-root-a")
        self.transition(first)
        held = self.authorize(first, confirm=False)
        first._release_terminal_owners(held["leaseId"])

        second = upc.UniversalProviderBroker(self.root / "r16-root-b")
        self.transition(second)
        request = self.make_request("request-r16-root-b")
        process = self.admission_observation(request)
        process["processId"] += 1
        process["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", process, self.secret, "observerHmacSha256"
        )
        self.assertEqual(
            self.authorize(second, request, confirm=False, process_observation=process)["reason"],
            "QUOTA_DOMAIN_DURABLE_CLAIM_HELD",
        )
        recovered = first.recover_orphan(
            process_observation=self.process_observation(held, "DEAD"),
            fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(recovered["status"], "RELEASED")
        fresh = self.make_request("request-r16-root-b-after-reconcile")
        fresh_process = self.admission_observation(fresh)
        fresh_process["processId"] += 2
        fresh_process["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", fresh_process, self.secret, "observerHmacSha256"
        )
        self.assertEqual(
            self.authorize(second, fresh, confirm=False, process_observation=fresh_process)["status"],
            "PREPARED_SUSPENDED",
        )

    def test_r16_05_temporal_binding_drift_closes_canary_and_retains_fences(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-canary-deadline")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r16-canary-deadline")
        request["canary"] = True
        authorization = self.make_canary_authorization(request, "canary-r16-deadline")
        allowed = self.authorize(
            broker, request, manual_authorization=authorization, begin_request=False
        )
        with broker._connect() as connection:
            connection.execute(
                "UPDATE leases SET watchdog_deadline=? WHERE lease_id=?",
                (upc.iso(self.now + dt.timedelta(minutes=5)), allowed["leaseId"]),
            )
        with self.assertRaisesRegex(upc.ControlError, "LEASE_BINDING_DRIFT"):
            broker.check_runtime_boundary(
                lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
            )
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")
        self.assertIn(allowed["leaseId"], broker._os_locks)
        self.assertIn(allowed["leaseId"], broker._artifact_handles)

    def test_r16_06_typed_quality_and_boundary_certifications_are_hmac_bound_and_stored(self) -> None:
        forged = self.make_request("request-r16-cert-forged")
        forged["qualityEquivalenceReceipt"]["independentReviewSha256"] = SHA_D
        broker = upc.UniversalProviderBroker(self.root / "r16-cert-forged")
        self.transition(broker)
        self.assertEqual(self.authorize(broker, forged)["reason"], "CONTRACT_HMAC_INVALID")

        stored_broker = upc.UniversalProviderBroker(self.root / "r16-cert-stored")
        self.transition(stored_broker)
        prepared = self.authorize(stored_broker, confirm=False)
        self.assertEqual(prepared["status"], "PREPARED_SUSPENDED")
        with stored_broker._connect() as connection:
            kinds = {row[0] for row in connection.execute(
                "SELECT artifact_kind FROM certification_artifacts"
            )}
        self.assertEqual(kinds, {"QUALITY_EQUIVALENCE", "WRAPPER_BOUNDARY"})

    def test_r16_07_canary_requires_hmac_output_quality_and_usage_reconciliation(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-canary-output")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r16-canary-output")
        request["canary"] = True
        authorization = self.make_canary_authorization(request, "canary-r16-output")
        allowed = self.authorize(broker, request, manual_authorization=authorization)
        terminal = self.process_observation(allowed, "EXITED", phase="TERMINAL")
        terminal["outputQualityReceipt"]["independentReviewSha256"] = SHA_D
        terminal["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", terminal, self.secret, "observerHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "CONTRACT_HMAC_INVALID"):
            broker.release_child(
                process_observation=terminal, fleet_secret=self.secret, now=self.now
            )
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CLOSED")
        self.assertIn(allowed["leaseId"], broker._os_locks)

    def test_r16_08_reusable_permit_cli_is_absent_and_never_reads_secret(self) -> None:
        import contextlib
        import io

        broker = upc.UniversalProviderBroker(self.root / "r16-cli")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        secret_file = self.root / "fleet-secret.bin"
        secret_file.write_bytes(self.secret)
        output = io.StringIO()
        with mock.patch("pathlib.Path.read_bytes", side_effect=AssertionError("secret read")):
            with contextlib.redirect_stdout(output):
                code = upc.main([
                    "provider-request-permit", str(broker.state_root), allowed["leaseId"],
                    str(secret_file.resolve()), upc.iso(self.now),
                ])
        self.assertEqual(code, 2)
        result = json.loads(output.getvalue())
        self.assertEqual(result, {"status": "UNEVALUABLE", "reason": "ARGUMENT_ERROR"})

    def test_r16_09_completed_usage_accumulates_across_terminal_leases(self) -> None:
        first = upc.UniversalProviderBroker(self.root / "r16-usage-first")
        self.transition(first)
        allowed = self.authorize(first)
        first.release_child(
            process_observation=self.process_observation(allowed, "EXITED", phase="TERMINAL"),
            fleet_secret=self.secret, now=self.now,
        )
        self.profile["efficiency"]["maxReservedTokenCeilings"] = copy.deepcopy(
            self.request["cumulativeTokenCeilings"]
        )
        second = upc.UniversalProviderBroker(self.root / "r16-usage-second")
        self.transition(second)
        request = self.make_request("request-r16-usage-second")
        process = self.admission_observation(request)
        process["processId"] += 1
        process["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", process, self.secret, "observerHmacSha256"
        )
        self.assertEqual(
            self.authorize(second, request, confirm=False, process_observation=process)["reason"],
            "COMPLETED_USAGE_CEILING_EXCEEDED",
        )

    def test_r16_10_termination_required_is_monotonic_and_cannot_mint_canary_success(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-terminated-canary")
        self.transition(broker, "CANARY")
        request = self.make_request("request-r16-terminated-canary")
        request["canary"] = True
        authorization = self.make_canary_authorization(request, "canary-r16-terminated")
        allowed = self.authorize(broker, request, manual_authorization=authorization)
        terminal = self.process_observation(allowed, "EXITED", phase="TERMINAL")
        later = self.now + dt.timedelta(seconds=61)
        broker._clock = lambda: later
        with self.assertRaisesRegex(upc.ControlError, "RUNTIME_TERMINATION_REQUIRED"):
            broker.check_runtime_boundary(
                lease_id=allowed["leaseId"], fleet_secret=self.secret, now=later
            )
        terminal["observedAt"] = upc.iso(later)
        terminal["observerHmacSha256"] = upc.contract_hmac(
            "process-observation-v1", terminal, self.secret, "observerHmacSha256"
        )
        with self.assertRaisesRegex(upc.ControlError, "TERMINATION_REQUIRED_FENCED"):
            broker.release_child(
                process_observation=terminal, fleet_secret=self.secret, now=later
            )
        with broker._connect() as connection:
            state = connection.execute(
                "SELECT state FROM leases WHERE lease_id=?", (allowed["leaseId"],)
            ).fetchone()[0]
            success_count = connection.execute(
                "SELECT COUNT(*) FROM canary_success_receipts"
            ).fetchone()[0]
        self.assertEqual(state, "TERMINATION_REQUIRED")
        self.assertEqual(success_count, 0)
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=later), "CLOSED")

    def test_r16_11_open_rejects_unparsed_or_forged_canary_receipt_rows(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-forged-canary-receipt")
        self.transition(broker, "CONTAINMENT")
        with broker._connect() as connection:
            connection.execute(
                """INSERT INTO canary_success_receipts(
                receipt_id, receipt_digest, receipt_bytes, gate_epoch,
                profile_digest, inventory_digest, used_at
                ) VALUES (?, ?, ?, 2, ?, ?, NULL)""",
                ("canary-success-" + "d" * 32, SHA_D, b"{}",
                 upc.digest_json(self.profile), upc.digest_json(self.inventory)),
            )
        proof = self.stage_proof("OPEN", receipt=SHA_D, serial=1611)
        transition = {
            "schema": "fleet-universal-gate-transition/v1",
            "transitionId": "transition-r16-forged-open", "transitionEpoch": 3,
            "issuedAt": upc.iso(self.now - dt.timedelta(seconds=1)),
            "expiresAt": upc.iso(self.now + dt.timedelta(minutes=5)),
            "from": "CONTAINMENT", "to": "OPEN", "cause": "INDEPENDENT_ADJUDICATION",
            "doctrineCommitSha256": SHA_A,
            "brokerExecutableSha256": sha_file(Path(upc.__file__).resolve()),
            "projectProfileSha256": upc.digest_json(self.profile),
            "inventorySha256": upc.digest_json(self.inventory),
            "brokerHealthSha256": upc.digest_json(self.health),
            "reviewReceiptSha256": SHA_B, "testReceiptSha256": SHA_C,
            "stageProof": proof, "authorizationHmacSha256": "hmac-sha256:" + "0" * 64,
        }
        transition["authorizationHmacSha256"] = upc.contract_hmac(
            "gate-transition-v1", transition, self.secret, "authorizationHmacSha256"
        )
        with self.assertRaises(upc.ControlError):
            broker.transition_gate(transition, fleet_secret=self.secret, now=self.now)
        self.assertEqual(broker.gate_state(fleet_secret=self.secret, now=self.now), "CONTAINMENT")

    def test_r16_12_provider_permit_token_ceilings_have_exact_keys(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r16-permit-keys")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        permit = broker._begin_provider_request(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        forged = copy.deepcopy(permit)
        forged["tokenCeilings"]["unreviewedTokens"] = 1
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("request_permit", forged)

    def test_r16_13_manifest_verifies_exact_ordered_reconciliation_and_forged_negatives(self) -> None:
        import check_universal_manifest as checker

        reconciliation = {
            "r15Base": {
                "commit": "30cd9b97eeebd30cb209bdb9798c38b415c9a0b4",
                "tree": "06aac4b6eb09ba896c98fd402851af09629d5351",
                "orderedParents": [
                    "00542530bfebad8ad7646724f64720adda8d1b49",
                    "874605e43531c9aa230ee16851f8107a8e0d9cec",
                ],
                "orderedParentTrees": [
                    "994b337e8b316cec31adc8bf4d5aaaaded299f7a",
                    "cafc358fd7b60812070cf9a465d7de38b88487c8",
                ],
            },
            "r16PreMaster": {
                "commit": "a560c63cbe72736efe4e1d5c3ecfac25d04f68d2",
                "tree": "36528454016fcaf71e63c75e751864e3305827da",
                "orderedParents": ["30cd9b97eeebd30cb209bdb9798c38b415c9a0b4"],
                "orderedParentTrees": ["06aac4b6eb09ba896c98fd402851af09629d5351"],
            },
            "r16FrozenBeforeLatestMaster": {
                "commit": "5956637cf088429364307c6816976d676bbb5092",
                "tree": "8a1d67957b5e6a8e946d38d68da6d529512191fe",
                "orderedParents": ["a0786f2eee16770632a2a947f65db64e60dd9820"],
                "orderedParentTrees": ["88f3caba68a192a159879e5f7dd2092f7cec50bc"],
            },
            "canonicalFleetMaster": {
                "commit": "cd21e5830ccb894af5847ce113af8a7d6570748a",
                "tree": "df856f1b9548c0a15b989de1539b26bfc2f0db0a",
                "orderedParents": [
                    "193b90f9e65450b4317c573f4de2e43d4120c3ff",
                    "3a06045e882b59fcc9ed508849eceada2d8fce12",
                ],
                "orderedParentTrees": [
                    "fdf2447fe780aaff2587de4e3af4823c63e66cdc",
                    "73110ee640dbc00ba0a7e4c95af0be7f97eedea6",
                ],
            },
            "r16MasterMerge": {
                "commit": "c6bc94fe3afcdbc927641164fd2d42c621c0bb67",
                "tree": "4d93e13f455033b44b6fd1db1269b9f751278360",
                "orderedParents": [
                    "5956637cf088429364307c6816976d676bbb5092",
                    "cd21e5830ccb894af5847ce113af8a7d6570748a",
                ],
                "orderedParentTrees": [
                    "8a1d67957b5e6a8e946d38d68da6d529512191fe",
                    "df856f1b9548c0a15b989de1539b26bfc2f0db0a",
                ],
            },
        }
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            swapped = copy.deepcopy(reconciliation)
            swapped["r16MasterMerge"]["orderedParents"].reverse()
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": swapped}, ":")
            forged_tree = copy.deepcopy(reconciliation)
            forged_tree["r15Base"]["orderedParentTrees"][0] = "0" * 40
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_PARENT_TREE_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged_tree}, ":")

    def test_r17_09_manifest_verifies_exact_ordered_merge_and_forged_negatives(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r17.json"
        reconciliation = json.loads(manifest_path.read_text(encoding="utf-8"))["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            swapped = copy.deepcopy(reconciliation)
            swapped["r17MasterMerge"]["orderedParents"].reverse()
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": swapped}, ":")
            forged_tree = copy.deepcopy(reconciliation)
            forged_tree["r17Wip"]["orderedParentTrees"][0] = "0" * 40
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_PARENT_TREE_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged_tree}, ":")

    def test_r18_06_manifest_binds_final_lineage_and_grants_zero_gate_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r18.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r18Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(
            upc.UniversalProviderBroker(self.root / "r18-manifest-closed").gate_state(),
            "CLOSED",
        )

    def test_r19_07_manifest_binds_restart_subject_and_grants_zero_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r19.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r19Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["processSpawnResumeKill"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")
        self.assertEqual(
            upc.UniversalProviderBroker(self.root / "r19-manifest-closed").gate_state(),
            "CLOSED",
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

    def test_r17_01_terminal_reserve_is_bound_to_frozen_checkpoint(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-terminal-baseline")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        broker._begin_provider_request(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        usage = {"inputTokens": 10, "cacheReadTokens": 20, "cacheWriteTokens": 1,
                 "reasoningTokens": 5, "outputTokens": 100}
        baseline = broker._checkpoint_provider_usage(
            lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=1,
            current_context_tokens=100, peak_context_tokens=100, token_usage=usage,
            fleet_secret=self.secret, now=self.now,
        )
        terminal = broker._issue_terminal_request_permit(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        self.assertEqual(terminal["baselineCheckpointSha256"], upc.digest_json(baseline))
        self.assertEqual(terminal["baselineOutputTokens"], 100)
        with self.assertRaisesRegex(upc.ControlError, "TERMINAL_REQUEST_ALREADY_ISSUED"):
            broker._checkpoint_provider_usage(
                lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=2,
                current_context_tokens=100, peak_context_tokens=100, token_usage=usage,
                fleet_secret=self.secret, now=self.now,
            )
        with self.assertRaisesRegex(upc.ControlError, "TERMINAL_RESERVE_DELTA_EXCEEDED"):
            broker._checkpoint_provider_usage(
                lease_id=allowed["leaseId"], phase="TERMINAL", turn_count=1,
                current_context_tokens=100, peak_context_tokens=100,
                token_usage=dict(usage, outputTokens=5101),
                fleet_secret=self.secret, now=self.now,
            )

    def test_r17_02_checkpoint_head_tamper_blocks_terminal_permit(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-checkpoint-head")
        self.transition(broker)
        allowed = self.authorize(broker, begin_request=False)
        broker._begin_provider_request(
            lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
        )
        usage = {"inputTokens": 1, "cacheReadTokens": 1, "cacheWriteTokens": 0,
                 "reasoningTokens": 0, "outputTokens": 1}
        broker._checkpoint_provider_usage(
            lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=1,
            current_context_tokens=1, peak_context_tokens=1, token_usage=usage,
            fleet_secret=self.secret, now=self.now,
        )
        connection = sqlite3.connect(broker.database)
        try:
            connection.execute(
                "UPDATE token_reservations SET checkpoint_head_hmac=? WHERE lease_id=?",
                ("hmac-sha256:" + "0" * 64, allowed["leaseId"]),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaisesRegex(upc.ControlError, "USAGE_CHECKPOINT_DRIFT"):
            broker._issue_terminal_request_permit(
                lease_id=allowed["leaseId"], fleet_secret=self.secret, now=self.now
            )

    def test_r17_03_quota_release_is_published_before_local_success(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-release-2pc")
        self.transition(broker)
        allowed = self.authorize(broker)
        terminal = self.process_observation(allowed, "EXITED", phase="TERMINAL")
        connection = sqlite3.connect(broker.database)
        initial_success_count = connection.execute(
            "SELECT COUNT(*) FROM canary_success_receipts"
        ).fetchone()[0]
        connection.close()
        with mock.patch.object(
            broker, "_release_quota_claim", side_effect=upc.ControlError("INJECTED_RELEASE_FAILURE")
        ):
            with self.assertRaisesRegex(upc.ControlError, "INJECTED_RELEASE_FAILURE"):
                broker.release_child(
                    process_observation=terminal, fleet_secret=self.secret, now=self.now
                )
        connection = sqlite3.connect(broker.database)
        try:
            state = connection.execute(
                "SELECT state FROM leases WHERE lease_id=?", (allowed["leaseId"],)
            ).fetchone()[0]
            success_count = connection.execute(
                "SELECT COUNT(*) FROM canary_success_receipts"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(state, "RELEASE_PREPARED")
        self.assertEqual(success_count, initial_success_count)
        self.assertEqual(
            broker.release_child(
                process_observation=terminal, fleet_secret=self.secret, now=self.now
            )["status"],
            "RELEASED",
        )

    def test_r17_04_quota_root_is_not_reselected_from_changed_home(self) -> None:
        first = upc.UniversalProviderBroker(self.root / "r17-root-first")
        first_path = first._quota_ledger_path()
        with mock.patch.object(Path, "home", return_value=self.root / "hostile-home"):
            second = upc.UniversalProviderBroker(self.root / "r17-root-second")
            second_path = second._quota_ledger_path()
        self.assertEqual(first_path, second_path)

    def test_r18_01_reference_candidate_exposes_no_callback_execution_boundary(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r18-no-execution-boundary")
        self.assertFalse(hasattr(broker, "provision_brokered_single_request"))
        self.assertFalse(hasattr(broker, "_run_brokered_single_request"))
        self.assertFalse(hasattr(upc, "CertifiedBrokeredSingleRequest"))
        self.assertEqual(
            broker.execution_boundary_status(),
            {
                "status": "UNEVALUABLE",
                "reason": "CERTIFIED_PROCESS_CHOKE_POINT_NOT_INSTALLED",
                "authority": "ZERO_AUTHORITY_REFERENCE_ONLY",
            },
        )
        self.assertEqual(broker.gate_state(), "CLOSED")
        source = inspect.getsource(upc)
        self.assertNotIn("provider_call:", source)
        self.assertNotIn("quality_observer(", source)
        self.assertNotIn("termination_observer(", source)

    def test_r17_06_prepared_quota_publication_retries_exactly(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-publication-retry")
        self.transition(broker)
        request = self.make_request("request-r17-publication-retry")
        real_activate = broker._activate_quota_claim
        with mock.patch.object(
            broker, "_activate_quota_claim",
            side_effect=upc.ControlError("INJECTED_ACTIVATION_FAILURE"),
        ):
            blocked = self.authorize(
                broker, request, confirm=False, begin_request=False
            )
        self.assertEqual(blocked["reason"], "QUOTA_PUBLICATION_INCOMPLETE")
        recovered = self.authorize(
            broker, request, confirm=False, begin_request=False
        )
        self.assertEqual(recovered["status"], "PREPARED_SUSPENDED")
        with broker._quota_connect() as connection:
            state = connection.execute(
                "SELECT state FROM quota_claims WHERE lease_id=?", (recovered["leaseId"],)
            ).fetchone()[0]
        self.assertEqual(state, "ACTIVE")

    def test_r18_02_crash_before_local_publication_reuses_exact_prepared_claim(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r18-pre-local-crash")
        self.transition(broker)
        request = self.make_request("request-r18-pre-local-crash")
        with mock.patch.object(
            broker, "_before_local_quota_publication",
            side_effect=upc.ControlError("INJECTED_PRE_LOCAL_CRASH"),
        ):
            blocked = self.authorize(
                broker, request, confirm=False, begin_request=False
            )
        self.assertEqual(blocked, {
            "status": "UNEVALUABLE", "reason": "QUOTA_PUBLICATION_INCOMPLETE"
        })
        with broker._quota_connect() as connection:
            prepared = connection.execute(
                "SELECT lease_id,state FROM quota_claims WHERE quota_domain_id=?",
                (self.quota_id,),
            ).fetchone()
        self.assertEqual(prepared["state"], "PREPARED")
        with broker._connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 0)
        recovered = self.authorize(
            broker, request, confirm=False, begin_request=False
        )
        self.assertEqual(recovered["status"], "PREPARED_SUSPENDED")
        self.assertEqual(recovered["leaseId"], prepared["lease_id"])
        with broker._quota_connect() as connection:
            self.assertEqual(connection.execute(
                "SELECT state FROM quota_claims WHERE quota_domain_id=?",
                (self.quota_id,),
            ).fetchone()[0], "ACTIVE")

    def test_r18_03_os_account_authority_ignores_home_in_fresh_processes(self) -> None:
        command = [
            sys.executable, "-c",
            "from tools import universal_provider_control as u; "
            "print(u._CANONICAL_QUOTA_AUTHORITY_ROOT)",
        ]
        roots = []
        for suffix in ("first", "second"):
            environment = dict(os.environ)
            environment["HOME"] = str(self.root / f"hostile-home-{suffix}")
            environment["USERPROFILE"] = str(self.root / f"hostile-profile-{suffix}")
            run = subprocess.run(
                command, cwd=ROOT, env=environment, text=True,
                capture_output=True, check=False, timeout=15,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            roots.append(run.stdout.strip())
        self.assertEqual(roots[0], roots[1])
        self.assertNotIn(str(self.root), roots[0])

    def test_r18_04_dead_after_zero_checkpoint_charges_full_reservation(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r18-conservative-orphan")
        self.transition(broker)
        allowed = self.authorize(broker)
        zero = {name: 0 for name in self.request["cumulativeTokenCeilings"]}
        broker._checkpoint_provider_usage(
            lease_id=allowed["leaseId"], phase="PRE_TURN", turn_count=1,
            current_context_tokens=0, peak_context_tokens=0, token_usage=zero,
            fleet_secret=self.secret, now=self.now,
        )
        recovered = broker.recover_orphan(
            process_observation=self.process_observation(allowed, "DEAD"),
            fleet_secret=self.secret, now=self.now,
        )
        self.assertEqual(recovered["status"], "RELEASED")
        with broker._connect() as connection:
            actual = json.loads(connection.execute(
                "SELECT actual_usage_json FROM token_reservations WHERE lease_id=?",
                (allowed["leaseId"],),
            ).fetchone()[0])
        self.assertEqual(actual, self.request["cumulativeTokenCeilings"])

    def test_r18_05_same_observer_or_fleet_key_is_not_independent(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r18-observer-independence")
        request = self.make_request("request-r18-observer-independence")
        boundary = request["boundaryCertification"]
        boundary["qualityObserverId"] = boundary["terminationObserverId"]
        boundary["qualityObserverKeySha256"] = upc.signer_key_sha256(self.secret)
        boundary["certificationHmacSha256"] = upc.contract_hmac(
            "wrapper-boundary-certification-v1", boundary, self.secret,
            "certificationHmacSha256",
        )
        request["boundaryCertificationSha256"] = upc.digest_json(boundary)
        self.request = request
        self.profile = self.make_profile()
        self.inventory = self.make_inventory()
        self.health = self.make_health()
        self.transition(broker)
        blocked = self.authorize(broker, request, confirm=False, begin_request=False)
        self.assertEqual(blocked["reason"], "OBSERVER_INDEPENDENCE_INVALID")

    def test_r19_01_prepared_retry_survives_restart_with_advancing_time(self) -> None:
        root = self.root / "r19-restart-convergence"
        first = upc.UniversalProviderBroker(root, clock=lambda: self.now)
        self.transition(first)
        request = self.make_request("request-r19-restart-convergence")
        original_process = self.admission_observation(request)
        with mock.patch.object(
            first, "_before_local_quota_publication",
            side_effect=upc.ControlError("INJECTED_PRE_LOCAL_CRASH"),
        ):
            blocked = self.authorize(
                first, request, confirm=False, begin_request=False,
                process_observation=copy.deepcopy(original_process),
            )
        self.assertEqual(blocked["reason"], "QUOTA_PUBLICATION_INCOMPLETE")
        with first._quota_connect() as connection:
            prepared = connection.execute(
                "SELECT lease_id,binding_digest,state FROM quota_claims WHERE quota_domain_id=?",
                (self.quota_id,),
            ).fetchone()
        self.assertEqual(prepared["state"], "PREPARED")

        self.now += dt.timedelta(seconds=1)
        restarted = upc.UniversalProviderBroker(root, clock=lambda: self.now)
        recovered = self.authorize(
            restarted, request, confirm=False, begin_request=False,
            process_observation=copy.deepcopy(original_process), now=self.now,
            profile=self.profile,
        )
        self.assertEqual(recovered["status"], "PREPARED_SUSPENDED", recovered)
        self.assertEqual(recovered["leaseId"], prepared["lease_id"])
        self.assertEqual(recovered["bindingSha256"], prepared["binding_digest"])
        self.assertEqual(
            recovered["issuedAt"], original_process["observedAt"]
        )
        self.assertEqual(
            upc.parse_time(recovered["expiresAt"]),
            upc.parse_time(original_process["observedAt"])
            + dt.timedelta(seconds=request["maxWallSeconds"]),
        )

    def test_r19_02_nonreproducible_prepared_claimant_stays_fenced(self) -> None:
        root = self.root / "r19-nonreproducible"
        first = upc.UniversalProviderBroker(root)
        self.transition(first)
        request = self.make_request("request-r19-nonreproducible")
        original_process = self.admission_observation(request)
        with mock.patch.object(
            first, "_before_local_quota_publication",
            side_effect=upc.ControlError("INJECTED_PRE_LOCAL_CRASH"),
        ):
            self.authorize(
                first, request, confirm=False, begin_request=False,
                process_observation=copy.deepcopy(original_process),
            )
        self.now += dt.timedelta(seconds=1)
        restarted = upc.UniversalProviderBroker(root)
        changed_process = self.admission_observation(request)
        blocked = self.authorize(
            restarted, request, confirm=False, begin_request=False,
            process_observation=changed_process, now=self.now, profile=self.profile,
        )
        self.assertEqual(blocked["status"], "UNEVALUABLE")
        self.assertEqual(blocked["reason"], "QUOTA_DOMAIN_DURABLE_CLAIM_HELD")
        with restarted._quota_connect() as connection:
            row = connection.execute(
                "SELECT lease_id,state,publication_digest FROM quota_claims WHERE quota_domain_id=?",
                (self.quota_id,),
            ).fetchone()
        self.assertEqual(row["state"], "PREPARED")
        self.assertIsNone(row["publication_digest"])

    def test_r19_03_canonical_authority_root_reparse_is_rejected(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r19-authority-root-reparse")
        authority = upc._CANONICAL_QUOTA_AUTHORITY_ROOT
        real_is_reparse = upc._is_reparse

        def mark_authority(path: Path) -> bool:
            if os.path.normcase(os.path.abspath(str(path))) == os.path.normcase(
                os.path.abspath(str(authority))
            ):
                return True
            return real_is_reparse(path)

        with mock.patch.object(upc, "_is_reparse", side_effect=mark_authority):
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                broker._quota_ledger_path()
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
                broker._lock_path(self.quota_id)

    def test_r19_04_real_authority_root_symlink_is_rejected_when_supported(self) -> None:
        target = self.root / "r19-real-authority-target"
        target.mkdir()
        link = self.root / "r19-real-authority-link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            source = inspect.getsource(upc._validated_quota_authority_root)
            self.assertIn("_is_reparse(authority)", source)
            return
        with mock.patch.object(upc, "_CANONICAL_QUOTA_AUTHORITY_ROOT", link), \
                mock.patch.object(upc, "_CANONICAL_QUOTA_LEDGER_ROOT", link / "quota-ledger"):
            broker = upc.UniversalProviderBroker(self.root / "r19-real-root-reparse")
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                broker._quota_ledger_path()

    def test_r19_05_observer_keys_cannot_alias_launch_artifact_identities(self) -> None:
        hostile_keys = (
            ("terminationObserverKeySha256", "executableSha256"),
            ("qualityObserverKeySha256", "launcherConfigSha256"),
            ("terminationObserverKeySha256", "argvContractSha256"),
        )
        for serial, (observer_field, request_field) in enumerate(hostile_keys, start=1):
            with self.subTest(observer=observer_field, artifact=request_field):
                request = self.make_request(f"request-r19-observer-artifact-{serial}")
                boundary = request["boundaryCertification"]
                boundary[observer_field] = request[request_field]
                boundary["certificationHmacSha256"] = upc.contract_hmac(
                    "wrapper-boundary-certification-v1", boundary, self.secret,
                    "certificationHmacSha256",
                )
                request["boundaryCertificationSha256"] = upc.digest_json(boundary)
                self.request = request
                self.profile = self.make_profile()
                self.inventory = self.make_inventory()
                self.health = self.make_health()
                broker = upc.UniversalProviderBroker(
                    self.root / f"r19-observer-artifact-{serial}"
                )
                self.transition(broker)
                blocked = self.authorize(
                    broker, request, confirm=False, begin_request=False
                )
                self.assertEqual(blocked["reason"], "OBSERVER_INDEPENDENCE_INVALID")

    def test_r19_06_test_brokers_never_mutate_default_account_ledger(self) -> None:
        default_database = (
            self.default_quota_authority_root / "quota-ledger" /
            "universal-quota-domain-v1.db"
        )

        def signature() -> tuple[bool, int | None, int | None]:
            if not default_database.exists():
                return (False, None, None)
            value = default_database.stat()
            return (True, value.st_size, value.st_mtime_ns)

        before = signature()
        broker = upc.UniversalProviderBroker(self.root / "r19-test-isolation")
        self.transition(broker)
        allowed = self.authorize(
            broker, self.make_request("request-r19-test-isolation"),
            confirm=False, begin_request=False,
        )
        self.assertEqual(allowed["status"], "PREPARED_SUSPENDED")
        self.assertEqual(before, signature())
        self.assertTrue(
            broker._quota_ledger_path().is_relative_to(self.root)
        )

    def test_r20_01_stale_caller_time_cannot_replay_after_authoritative_expiry(self) -> None:
        authoritative = [self.now]
        broker = upc.UniversalProviderBroker(
            self.root / "r20-stale-caller", clock=lambda: authoritative[0]
        )
        self.transition(broker)
        request = self.make_request("request-r20-stale-caller")
        prepared = self.authorize(broker, request, confirm=False, begin_request=False)
        self.assertEqual(prepared["status"], "PREPARED_SUSPENDED")
        authoritative[0] = self.now + dt.timedelta(seconds=request["maxWallSeconds"] + 1)
        blocked = self.authorize(
            broker, request, confirm=False, begin_request=False,
            now=self.now, profile=self.profile,
        )
        self.assertEqual(blocked, {"status": "UNEVALUABLE", "reason": "CALLER_TIME_DIVERGES"})
        with self.assertRaisesRegex(upc.ControlError, "LEASE_EXPIRED_BEFORE_RESUME"):
            broker.confirm_resume_boundary(
                lease_id=prepared["leaseId"],
                process_observation=self.admission_observation(
                    request, phase="RESUME", lease_id=prepared["leaseId"]
                ),
                fleet_secret=self.secret, now=self.now,
            )

    def test_r20_02_future_caller_time_cannot_extend_sampled_lease(self) -> None:
        broker = upc.UniversalProviderBroker(
            self.root / "r20-future-caller", clock=lambda: self.now
        )
        self.transition(broker)
        request = self.make_request("request-r20-future-caller")
        prepared = self.authorize(
            broker, request, confirm=False, begin_request=False,
            now=self.now + dt.timedelta(seconds=4),
        )
        self.assertEqual(prepared["status"], "PREPARED_SUSPENDED")
        self.assertEqual(upc.parse_time(prepared["issuedAt"]), self.now)
        self.assertEqual(
            upc.parse_time(prepared["expiresAt"]),
            self.now + dt.timedelta(seconds=request["maxWallSeconds"]),
        )

    def test_r20_03_every_authority_ancestor_component_is_reparse_checked(self) -> None:
        base = self.root / "r20-mocked-trusted-base"
        base.mkdir()
        authority = base / "SoftwareFactory" / "provider-control"
        marked = base / "SoftwareFactory"
        real_is_reparse = upc._is_reparse

        def mark_ancestor(path: Path) -> bool:
            if os.path.normcase(os.path.abspath(str(path))) == os.path.normcase(
                os.path.abspath(str(marked))
            ):
                return True
            return real_is_reparse(path)

        with mock.patch.object(upc, "_CANONICAL_QUOTA_TRUSTED_BASE", base), \
                mock.patch.object(upc, "_CANONICAL_QUOTA_AUTHORITY_ROOT", authority), \
                mock.patch.object(upc, "_CANONICAL_QUOTA_LEDGER_ROOT", authority / "quota-ledger"), \
                mock.patch.object(upc, "_is_reparse", side_effect=mark_ancestor):
            broker = upc.UniversalProviderBroker(self.root / "r20-mocked-ancestor")
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                broker._quota_ledger_path()
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
                broker._lock_path(self.quota_id)

    def test_r20_04_real_ancestor_junction_or_symlink_is_rejected(self) -> None:
        base = self.root / "r20-real-trusted-base"
        base.mkdir()
        target = self.root / "r20-real-target"
        target.mkdir()
        ancestor = base / "SoftwareFactory"
        created = False
        if os.name == "nt":
            run = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(ancestor), str(target)],
                capture_output=True, text=True, check=False, timeout=15,
            )
            created = run.returncode == 0
        else:
            try:
                ancestor.symlink_to(target, target_is_directory=True)
                created = True
            except (OSError, NotImplementedError):
                created = False
        if not created:
            source = inspect.getsource(upc._validated_quota_authority_root)
            self.assertIn("for component in relative.parts", source)
            self.assertIn("_is_reparse(current)", source)
            return
        authority = ancestor / "provider-control"
        with mock.patch.object(upc, "_CANONICAL_QUOTA_TRUSTED_BASE", base), \
                mock.patch.object(upc, "_CANONICAL_QUOTA_AUTHORITY_ROOT", authority), \
                mock.patch.object(upc, "_CANONICAL_QUOTA_LEDGER_ROOT", authority / "quota-ledger"):
            broker = upc.UniversalProviderBroker(self.root / "r20-real-ancestor")
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                broker._quota_ledger_path()
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
                broker._lock_path(self.quota_id)

    def test_r20_05_universal_workflow_runs_exact_workbench_suite(self) -> None:
        workflow = (
            ROOT / ".github/workflows/provider-capacity-governor.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:\n    branches: [master]", workflow)
        self.assertIn(
            'python -m unittest discover -s capacity-control/tests -p "test_*.py" -v',
            workflow,
        )

    def test_r20_06_manifest_binds_clock_path_ci_subject_and_zero_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r20.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r20Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["processSpawnResumeKill"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")
        self.assertEqual(
            upc.UniversalProviderBroker(self.root / "r20-manifest-closed").gate_state(),
            "CLOSED",
        )

    def test_r21_01_root_lock_wait_resamples_and_cannot_prepare_expired_lease(self) -> None:
        clock = [self.now]
        broker = upc.UniversalProviderBroker(
            self.root / "r21-root-lock-clock", clock=lambda: clock[0]
        )
        self.transition(broker)
        request = self.make_request("request-r21-root-lock-clock")
        request["maxWallSeconds"] = 60

        original_authorize = broker.authorize_suspended_child
        armed = [False]

        def arm_authorize(**arguments: object) -> dict:
            armed[0] = True
            return original_authorize(**arguments)

        class SelectiveAdvancingLock:
            def __enter__(inner_self):
                if armed[0]:
                    clock[0] = self.now + dt.timedelta(seconds=61)
                return inner_self

            def __exit__(inner_self, *_: object) -> None:
                return None

        broker._root_lock = SelectiveAdvancingLock()
        with mock.patch.object(broker, "authorize_suspended_child", side_effect=arm_authorize):
            result = self.authorize(
                broker, request, confirm=False, begin_request=False, now=self.now,
            )
        self.assertEqual(result["status"], "UNEVALUABLE")
        self.assertIn(
            result["reason"],
            {"LEASE_BOUNDARY_EXPIRED", "REQUEST_TIME_INVALID", "PROCESS_OBSERVATION_STALE"},
        )
        with broker._connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0], 0)

    def test_r21_02_quota_lock_wait_resamples_before_durable_publication(self) -> None:
        clock = [self.now]
        broker = upc.UniversalProviderBroker(
            self.root / "r21-quota-lock-clock", clock=lambda: clock[0]
        )
        self.transition(broker)
        request = self.make_request("request-r21-quota-lock-clock")
        request["maxWallSeconds"] = 60
        acquire = broker._acquire_os_lock

        def delayed_acquire(lease_id: str, quota_domain_id: str) -> None:
            acquire(lease_id, quota_domain_id)
            clock[0] = self.now + dt.timedelta(seconds=61)

        with mock.patch.object(broker, "_acquire_os_lock", side_effect=delayed_acquire):
            result = self.authorize(
                broker, request, confirm=False, begin_request=False, now=self.now,
            )
        self.assertEqual(
            result, {"status": "UNEVALUABLE", "reason": "ADMISSION_TIME_ELAPSED"}
        )
        with broker._connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0], 0)

    def test_r21_03_posix_missing_account_base_is_created_nofollow(self) -> None:
        if os.name == "nt":
            source = inspect.getsource(upc._ensure_posix_account_data_base)
            self.assertIn('getattr(os, "O_NOFOLLOW", 0)', source)
            self.assertIn("dir_fd=descriptor", source)
            self.assertIn("child_stat.st_uid != owner", source)
            return
        home = self.root / "fresh-passwd-home"
        home.mkdir(mode=0o700)
        base = upc._ensure_posix_account_data_base(home)
        self.assertEqual(base, home / ".local" / "share")
        for path in (home / ".local", base):
            item = path.stat(follow_symlinks=False)
            self.assertEqual(item.st_uid, os.getuid())
            self.assertEqual(stat.S_IMODE(item.st_mode), 0o700)
            self.assertFalse(path.is_symlink())

    def test_r21_04_ledger_component_swap_is_poisoned_before_use(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r21-ledger-swap")
        authority = upc._CANONICAL_QUOTA_AUTHORITY_ROOT
        displaced = authority.with_name(authority.name + "-displaced")

        def swap(surface: str) -> None:
            if surface == "ledger":
                authority.rename(displaced)
                authority.mkdir(mode=0o700)

        with mock.patch.object(broker, "_after_authority_snapshot", side_effect=swap):
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                with broker._quota_connect():
                    pass
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
            broker._quota_ledger_path()

    def test_r21_05_lock_component_swap_is_poisoned_before_use(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r21-lock-swap")
        authority = upc._CANONICAL_QUOTA_AUTHORITY_ROOT
        displaced = authority.with_name(authority.name + "-displaced")

        def swap(surface: str) -> None:
            if surface == "lock":
                authority.rename(displaced)
                authority.mkdir(mode=0o700)

        with mock.patch.object(broker, "_after_authority_snapshot", side_effect=swap):
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
                broker._acquire_os_lock("lease-r21-swapped-lock", self.quota_id)
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
            broker._lock_path(self.quota_id)

    def test_r21_06_provider_budget_law_is_request_scoped_and_zero_authority(self) -> None:
        doctrine = (
            ROOT / "specs" / "fleet-universal-provider-control-reconciliation.md"
        ).read_text(encoding="utf-8")
        required = {
            "CACHE_READ_FULL_ENVELOPE_WEIGHT=1.0",
            "REQUEST_LAYER_RECONCILIATION=REQUIRED",
            "MODEL_FREE_NO_WORK=BEFORE_SESSION_CREATION",
            "MAX_ASSEMBLED_PREFIX_TOKENS=REVIEWED_NUMERIC_REQUIRED",
            "MAX_ADDRESSED_WORK_CAPSULE_TOKENS=REVIEWED_NUMERIC_REQUIRED",
            "CACHE_AFFINITY_TTL=EXACT_IDENTITY_AND_UNEXPIRED_TTL",
            "MAX_PROVIDER_RETRIES=REVIEWED_NUMERIC_REQUIRED",
            "COMPLETION_RESERVE_FLOOR=0.20",
            "POSITIVE_DIRECT_LAUNCH_ENFORCEMENT=SEPARATELY_CERTIFIED_REQUIRED",
            "PRE-SHADOW SEALED",
        }
        self.assertEqual({marker for marker in required if marker not in doctrine}, set())
        self.assertIn("Failure, refusal, timeout, and retry attempts", doctrine)
        self.assertIn("earns no ratification, adoption, containment, or activation", doctrine)
        parser_source = inspect.getsource(upc._parser)
        self.assertNotIn('add_parser("provider-request-permit")', parser_source)
        self.assertNotIn('add_parser("brokered-single-request")', parser_source)
        self.assertEqual(
            upc.UniversalProviderBroker(self.root / "r21-budget-law-closed").gate_state(),
            "CLOSED",
        )

    def test_r21_07_manifest_binds_postlock_path_subject_and_zero_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r21.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r21Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["processSpawnResumeKill"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")
        self.assertEqual(
            upc.UniversalProviderBroker(self.root / "r21-manifest-closed").gate_state(),
            "CLOSED",
        )

    def test_r22_01_ledger_child_replacement_is_poisoned_before_open(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r22-ledger-child-swap")
        child = upc._CANONICAL_QUOTA_LEDGER_ROOT
        displaced = child.with_name(child.name + "-displaced")

        def swap(surface: str) -> None:
            if surface == "ledger":
                child.rename(displaced)
                child.mkdir(mode=0o700)

        with mock.patch.object(broker, "_after_authority_snapshot", side_effect=swap):
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
                with broker._quota_connect():
                    pass
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
            broker._quota_ledger_path()

    def test_r22_02_lock_child_replacement_is_poisoned_before_open(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r22-lock-child-swap")
        child = upc._CANONICAL_QUOTA_AUTHORITY_ROOT / "quota-locks"
        displaced = child.with_name(child.name + "-displaced")

        def swap(surface: str) -> None:
            if surface == "lock":
                child.rename(displaced)
                child.mkdir(mode=0o700)

        with mock.patch.object(broker, "_after_authority_snapshot", side_effect=swap):
            with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
                broker._acquire_os_lock("lease-r22-lock-child", self.quota_id)
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
            broker._lock_path(self.quota_id)

    def test_r22_03_native_ledger_child_identity_twin_rejects_replacement(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r22-ledger-native")
        broker._quota_ledger_path()
        child = upc._CANONICAL_QUOTA_LEDGER_ROOT
        snapshot = upc._quota_authority_snapshot("QUOTA_LEDGER_BOUNDARY_INVALID", child)
        child.rename(child.with_name(child.name + "-native-displaced"))
        child.mkdir(mode=0o700)
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LEDGER_BOUNDARY_INVALID"):
            upc._revalidate_quota_authority_snapshot(
                snapshot, "QUOTA_LEDGER_BOUNDARY_INVALID"
            )

    def test_r22_04_native_lock_child_identity_twin_rejects_replacement(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r22-lock-native")
        child = broker._lock_path(self.quota_id).parent
        snapshot = upc._quota_authority_snapshot("QUOTA_LOCK_BOUNDARY_INVALID", child)
        child.rename(child.with_name(child.name + "-native-displaced"))
        child.mkdir(mode=0o700)
        with self.assertRaisesRegex(upc.ControlError, "QUOTA_LOCK_BOUNDARY_INVALID"):
            upc._revalidate_quota_authority_snapshot(snapshot, "QUOTA_LOCK_BOUNDARY_INVALID")

    def test_r22_05_attended_receipt_is_private_strict_and_recomputed(self) -> None:
        receipt = upc.strict_json_file(
            ROOT / "receipts" / "attended-provider-rotation-20260819.json"
        )
        upc.validate_contract("attended_rotation_receipt", receipt)
        self.assertEqual(receipt["aggregate"]["cacheCreateTokens"], 59319)
        self.assertEqual(receipt["aggregate"]["cacheReadTokens"], 10723)
        self.assertEqual(receipt["aggregate"]["outputTokens"], 7540)
        self.assertFalse(receipt["providerAuthority"])
        self.assertFalse(receipt["adoptionCredit"])
        duplicate = copy.deepcopy(receipt)
        duplicate["requests"][1]["promptSha256"] = duplicate["requests"][0]["promptSha256"]
        with self.assertRaisesRegex(upc.ControlError, "ATTENDED_ROTATION_HASH_DUPLICATE"):
            upc.validate_contract("attended_rotation_receipt", duplicate)
        wrong_total = copy.deepcopy(receipt)
        wrong_total["requests"][0]["cacheCreateTokens"] -= 1
        with self.assertRaisesRegex(upc.ControlError, "ATTENDED_ROTATION_AGGREGATE_MISMATCH"):
            upc.validate_contract("attended_rotation_receipt", wrong_total)
        invalid_type = copy.deepcopy(receipt)
        invalid_type["requests"][0]["inputTokens"] = "1"
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("attended_rotation_receipt", invalid_type)
        duplicate_key_bytes = (
            b'{"schema":"fleet-universal-attended-rotation-receipt/v1",'
            b'"schema":"fleet-universal-attended-rotation-receipt/v1"}'
        )
        with self.assertRaisesRegex(upc.ControlError, "JSON_DUPLICATE_KEY"):
            upc.strict_json_bytes(duplicate_key_bytes)

    def test_r22_06_token_laws_are_strict_structured_policy(self) -> None:
        policy = upc.strict_json_file(
            ROOT / "policy" / "universal-provider-token-control-r22.json"
        )
        upc.validate_contract("token_control_policy", policy)
        self.assertEqual(policy["requestAccounting"]["scope"], "PROVIDER_REQUEST")
        self.assertEqual(policy["requestAccounting"]["cacheReadEnvelopeWeight"], 1.0)
        self.assertEqual(policy["completionReserve"]["quotaWindowFloor"], 0.2)
        weakened = copy.deepcopy(policy)
        weakened["requestAccounting"]["cacheReadEnvelopeWeight"] = 0.5
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("token_control_policy", weakened)
        reversed_budget = copy.deepcopy(policy)
        reversed_budget["prefixAndCapsule"]["maxAddressedWorkCapsuleTokens"] = 65536
        with self.assertRaisesRegex(upc.ControlError, "TOKEN_CONTROL_POLICY_BUDGET_ORDER_INVALID"):
            upc.validate_contract("token_control_policy", reversed_budget)
        extra = copy.deepcopy(policy)
        extra["serializationOverride"] = True
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("token_control_policy", extra)

    def test_r22_07_manifest_binds_child_receipt_policy_and_master_merge(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r22.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r22MasterMerge"]["orderedParents"].reverse()
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        subject_paths = {subject["path"] for subject in manifest["subjectFiles"]}
        self.assertIn("receipts/attended-provider-rotation-20260819.json", subject_paths)
        self.assertIn("policy/universal-provider-token-control-r22.json", subject_paths)
        self.assertIn("schemas/universal-attended-rotation-receipt-v1.schema.json", subject_paths)
        self.assertIn("schemas/universal-provider-token-control-policy-v1.schema.json", subject_paths)
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")

    def test_r23_01_attended_duration_and_provenance_are_non_authoritative(self) -> None:
        receipt = upc.strict_json_file(
            ROOT / "receipts" / "attended-provider-rotation-20260819.json"
        )
        upc.validate_contract("attended_rotation_receipt", receipt)
        self.assertEqual(
            [entry["wallDurationMs"] for entry in receipt["requests"]],
            [34299, 59757, 26400, 30577],
        )
        self.assertEqual(receipt["aggregate"]["totalWallDurationMs"], 151033)
        self.assertEqual(
            receipt["durationSemantics"],
            {
                "durationMs": "CLAUDE_CLI_REPORTED_END_TO_END",
                "durationApiMs": "CLAUDE_CLI_REPORTED_API",
                "wallDurationMs": "HOST_OBSERVED_WALL",
                "wallDurationConvention": "FLOOR_COMPLETED_AT_MINUS_STARTED_AT_MILLISECONDS",
                "maxCliOutsideApiMs": 10000,
                "maxHostOutsideCliMs": 5000,
            },
        )
        self.assertEqual(
            receipt["provenance"]["classification"],
            "AUTHOR_ATTESTED_LOCAL_CLI_MEASUREMENT",
        )
        self.assertFalse(receipt["provenance"]["providerAuthenticated"])
        self.assertFalse(receipt["provenance"]["independentObserver"])
        self.assertFalse(receipt["provenance"]["rawProviderReceiptCommitted"])
        self.assertFalse(receipt["provenance"]["authorityCredit"])
        self.assertEqual(receipt["creditClassification"], "MOTIVATION_AND_MEASUREMENT_ONLY")
        without_informational_url = copy.deepcopy(receipt)
        del without_informational_url["issueReceiptUrl"]
        upc.validate_contract("attended_rotation_receipt", without_informational_url)
        wrong_wall = copy.deepcopy(receipt)
        wrong_wall["requests"][0]["wallDurationMs"] += 1
        with self.assertRaisesRegex(
            upc.ControlError, "ATTENDED_ROTATION_WALL_DURATION_MISMATCH"
        ):
            upc.validate_contract("attended_rotation_receipt", wrong_wall)
        unbounded_overhead = copy.deepcopy(receipt)
        unbounded_overhead["requests"][0]["durationApiMs"] = 1
        with self.assertRaisesRegex(
            upc.ControlError, "ATTENDED_ROTATION_DURATION_OVERHEAD_INVALID"
        ):
            upc.validate_contract("attended_rotation_receipt", unbounded_overhead)
        forged_authority = copy.deepcopy(receipt)
        forged_authority["provenance"]["authorityCredit"] = True
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("attended_rotation_receipt", forged_authority)

    def test_r23_02_manifest_binds_semantics_and_zero_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r23.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r23Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")

    def test_r24_01_rfc3339_nanoseconds_floor_without_microsecond_truncation(self) -> None:
        start = "2026-08-19T04:00:00.0000000Z"

        def floor_ms(completed: str) -> int:
            return (
                upc._canonical_rfc3339_utc_epoch_nanoseconds(completed)
                - upc._canonical_rfc3339_utc_epoch_nanoseconds(start)
            ) // 1_000_000

        self.assertEqual(floor_ms("2026-08-19T04:00:00.0009999Z"), 0)
        self.assertEqual(floor_ms("2026-08-19T04:00:00.0010000Z"), 1)
        self.assertEqual(floor_ms("2026-08-19T04:00:00.0019992Z"), 1)
        self.assertEqual(floor_ms("2026-08-19T04:00:00.0020000Z"), 2)
        self.assertEqual(
            (
                upc._canonical_rfc3339_utc_epoch_nanoseconds(
                    "2026-08-19T04:01:00.0000001Z"
                )
                - upc._canonical_rfc3339_utc_epoch_nanoseconds(
                    "2026-08-19T04:00:59.9999999Z"
                )
            ) // 1_000_000,
            0,
        )
        for malformed in (
            "2026-08-19T04:00:00.1234567890Z",
            "2026-08-19T04:00:00.1234567+00:00",
            "2026-08-19T04:00:00.1234567z",
            "2026-02-30T04:00:00.1234567Z",
            "2026-08-19 04:00:00.1234567Z",
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(upc.ControlError, "DATE_TIME_INVALID"):
                    upc._canonical_rfc3339_utc_epoch_nanoseconds(malformed)
        receipt = upc.strict_json_file(
            ROOT / "receipts" / "attended-provider-rotation-20260819.json"
        )
        upc.validate_contract("attended_rotation_receipt", receipt)
        offset = copy.deepcopy(receipt)
        offset["requests"][0]["startedAt"] = "2026-08-19T04:33:55.7504404+00:00"
        with self.assertRaisesRegex(upc.ControlError, "SCHEMA_VALIDATION_FAILED"):
            upc.validate_contract("attended_rotation_receipt", offset)

    def test_r24_02_manifest_binds_exact_timestamp_evidence_and_zero_authority(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r24.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r24Wip"]["orderedParents"] = ["0" * 40]
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")

    def test_r25_01_two_endpoint_truncation_regression_stays_floor_one(self) -> None:
        started = "2026-08-19T04:33:55.7504409Z"
        completed = "2026-08-19T04:33:55.7524401Z"
        exact_delta_ns = (
            upc._canonical_rfc3339_utc_epoch_nanoseconds(completed)
            - upc._canonical_rfc3339_utc_epoch_nanoseconds(started)
        )
        self.assertEqual(exact_delta_ns, 1_999_200)
        self.assertEqual(exact_delta_ns // 1_000_000, 1)
        # The old datetime-microsecond path truncates both endpoints independently and
        # incorrectly observes 2.000 ms, which is the exact regression this fixture retains.
        old_started = upc.parse_time(started)
        old_completed = upc.parse_time(completed)
        old_delta = old_completed - old_started
        old_floor_ms = (
            old_delta.days * 86400000
            + old_delta.seconds * 1000
            + old_delta.microseconds // 1000
        )
        self.assertEqual(old_floor_ms, 2)

        receipt = upc.strict_json_file(
            ROOT / "receipts" / "attended-provider-rotation-20260819.json"
        )
        forged_floor_two = copy.deepcopy(receipt)
        entry = forged_floor_two["requests"][0]
        entry["startedAt"] = started
        entry["completedAt"] = completed
        entry["wallDurationMs"] = 2
        entry["durationMs"] = 1
        entry["durationApiMs"] = 1
        with self.assertRaisesRegex(
            upc.ControlError, "ATTENDED_ROTATION_WALL_DURATION_MISMATCH"
        ):
            upc.validate_contract("attended_rotation_receipt", forged_floor_two)

    def test_r25_02_manifest_binds_truncation_witness_and_master_merge(self) -> None:
        import check_universal_manifest as checker

        manifest_path = ROOT / "manifests" / "universal-provider-control-reconciliation-r25.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        reconciliation = manifest["reconciliation"]
        tuples = {
            record["commit"]: (record["tree"], record["orderedParents"])
            for record in reconciliation.values()
        }
        for record in reconciliation.values():
            for parent, tree in zip(record["orderedParents"], record["orderedParentTrees"]):
                tuples.setdefault(parent, (tree, []))
        with mock.patch.object(checker, "_commit_tuple", side_effect=lambda commit: tuples[commit]):
            checker.verify_reconciliation({"reconciliation": reconciliation}, ":")
            forged = copy.deepcopy(reconciliation)
            forged["r25MasterMerge"]["orderedParents"].reverse()
            with self.assertRaisesRegex(checker.ManifestError, "RECONCILIATION_COMMIT_MISMATCH"):
                checker.verify_reconciliation({"reconciliation": forged}, ":")
        self.assertEqual(manifest["status"], "CANDIDATE_ZERO_AUTHORITY")
        self.assertFalse(manifest["authority"]["providerExecution"])
        self.assertFalse(manifest["authority"]["containmentOrCanaryCredit"])
        self.assertEqual(manifest["authority"]["automaticGateState"], "CLOSED")

    def test_r17_07_low_level_request_primitives_are_not_public(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-no-public-primitives")
        self.assertFalse(hasattr(broker, "begin_provider_request"))
        self.assertFalse(hasattr(broker, "checkpoint_provider_usage"))
        self.assertFalse(hasattr(broker, "issue_terminal_request_permit"))

    def test_r17_08_completed_usage_is_partitioned_by_each_capacity_window(self) -> None:
        broker = upc.UniversalProviderBroker(self.root / "r17-window-ledger")
        self.transition(broker)
        allowed = self.authorize(broker)
        terminal = self.process_observation(allowed, "EXITED", phase="TERMINAL")
        broker.release_child(
            process_observation=terminal, fleet_secret=self.secret, now=self.now
        )
        with broker._quota_connect() as connection:
            rows = connection.execute(
                """SELECT dimension_name,last_reset_at,resets_at,usage_json
                FROM completed_usage_windows WHERE quota_domain_id=? ORDER BY dimension_name""",
                (self.quota_id,),
            ).fetchall()
        self.assertEqual([row["dimension_name"] for row in rows], ["session", "weekly"])
        self.assertTrue(all(json.loads(row["usage_json"])["outputTokens"] == 100 for row in rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
