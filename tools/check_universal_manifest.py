#!/usr/bin/env python3
"""Verify the universal-control candidate manifest against canonical Git blob bytes."""

from __future__ import annotations

import argparse
import ast
import contextlib
from dataclasses import dataclass
import hashlib
import inspect
import json
import linecache
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
from types import ModuleType
from types import MappingProxyType
from typing import Any, Callable, Mapping
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "manifests/universal-provider-control-reconciliation-r29.json"
R29_MANIFEST = MANIFEST
R26_MANIFEST = "manifests/universal-provider-control-reconciliation-r26.json"
R33_MANIFEST = "manifests/universal-provider-control-reconciliation-r33.json"
R34_MANIFEST = "manifests/universal-provider-control-reconciliation-r34.json"
R35_MANIFEST = "manifests/universal-provider-control-reconciliation-r35.json"
R36_MANIFEST = "manifests/universal-provider-control-reconciliation-r36.json"
R37_MANIFEST = "manifests/universal-provider-control-reconciliation-r37.json"
R38_MANIFEST = "manifests/universal-provider-control-reconciliation-r38.json"
R39_MANIFEST = "manifests/universal-provider-control-reconciliation-r39.json"
R40_MANIFEST = "manifests/universal-provider-control-reconciliation-r40.json"
R41_MANIFEST = "manifests/universal-provider-control-reconciliation-r41.json"
R42_MANIFEST = "manifests/universal-provider-control-reconciliation-r42.json"
R43_MANIFEST = "manifests/universal-provider-control-reconciliation-r43.json"
R44_MANIFEST = "manifests/universal-provider-control-reconciliation-r44.json"
REVIEW_SCHEMA = "schemas/universal-provider-review-admission-v1.schema.json"
FROZEN_CANDIDATE = "e70a044f31dd2f43ab7c716d63a4eb89318c61b6"
FROZEN_R29 = "fc76bf6d5ab52891d06b7f71eb2e993e413c124c"
FROZEN_R33 = "8e20b4a1652931af178e792eb62ab892a7d309fd"
FROZEN_R34 = "6a3803fd1543c1bd0944ec0013987f053852e3c4"
FROZEN_R35 = "64e6895c332a696af238007225148fd70582424f"
FROZEN_R36 = "d67b0781e1e926e1baebdb0ea9b7a0ef5c447d85"
FROZEN_R37 = "6568230545e473c6fac64bcd30166a284e712704"
FROZEN_R38 = "d897c304b1dd8e3b6dcbac71002c1eb2f7db519c"
FROZEN_R39 = "3bea531c2b3abbc4be4b506255d344d8ec6e712f"
FROZEN_R40 = "9924be835e6edd768f82cd6c50d97b83c747a265"
FROZEN_R41 = "e6d7dbd297a470cf97c7f9fefbb854dc3527b719"
FROZEN_R42 = "5b1abb9d01226e35721d14b9c525d87287722c8c"
FROZEN_R43 = "78218e277a4f03a7830058ab7c3cf04683066b9b"
SELF_PATTERN = re.compile(
    rb'("canonicalGitBlobSha256"\s*:\s*"sha256:)([0-9a-f]{64})(")'
)


class ManifestError(ValueError):
    pass


R27_BASE = {
    "commit": "8c7dc4f4339db82a8b3c2efd689bf5f72631ad6e",
    "tree": "5dcc00a7f9723a00992458ab9dd0d6b0fd373363",
    "orderedParents": [
        "e4e7f9363185a5e10bb3a92167c785ef29caf2b7",
        "53a48a6a0be5eade253ce1a508872d6874fd474a",
    ],
    "orderedParentTrees": [
        "5233fa0515fcef7b69e70a007f25e6bb78190c42",
        "b8501a0a285a417a8f3f55fff515d074fd55dd81",
    ],
}
R27_SOURCE = {
    "repository": "https://github.com/layibabalola/Cloudvore.git",
    "commit": "46674bf7ba004dd6c4cac69d5a26369ab11106c4",
    "tree": "bef6f545f773157807e81dcf71305cb13a25382e",
    "orderedParents": ["8dcd3393f5541aa1f7fe181c3869f4262b6e1a00"],
    "subjectFiles": [
        {"ordinal": 0, "path": "tools/provider-capacity-governor-shadow/provenance/HUB-DESIGN-provider-capacity-governor-shadow-adoption-0818.md", "gitBlobOid": "b18a478694439efa86d2015ebe13b0c97bc9d5dc", "sha256": "sha256:e2a08fbccee3542449778d12d35c7e446dc56bef1cd898643bda7341842929a7", "bytes": 31133},
        {"ordinal": 1, "path": "knowledge/provider-capacity-governor-shadow-profile-v1.json", "gitBlobOid": "9bd11a136528cced1fc16430688d089a3f80a36c", "sha256": "sha256:90c45346bc83a145547086434876168e2aad4db7d1e2b1baf95a2c14e443ebf3", "bytes": 21559},
        {"ordinal": 2, "path": "knowledge/provider-capacity-governor-shadow-profile-v1.schema.json", "gitBlobOid": "330228c8df279a6ab528d30da2bc7db7c88db2bc", "sha256": "sha256:a3239addf3872f8b08ee92bfc052a8274901075d741e718d10ad1b0a066656bd", "bytes": 23483},
        {"ordinal": 3, "path": "knowledge/provider-capacity-governor-shadow-proposal-manifest-v1.json", "gitBlobOid": "95b3304c46fd13c232781e4d7fff9f533624ade4", "sha256": "sha256:cf7fc691d04fd40388a772947b68504ccfca57c96f13182f0ac6acf25e566d88", "bytes": 2999},
        {"ordinal": 4, "path": "knowledge/provider-capacity-governor-shadow-proposal-manifest-v1.schema.json", "gitBlobOid": "880f776756eb45c9deef608300ba76e9befbb493", "sha256": "sha256:9e4b546b225a69e31a964a3c5294a806389d6310fadcca60d07281c097b190bf", "bytes": 3857},
        {"ordinal": 5, "path": "knowledge/provider-capacity-governor-shadow-proposal-receipt-2026-08-18.md", "gitBlobOid": "455415489bc98ae11c77702941a6bf42655b0d60", "sha256": "sha256:8d2d67c984b57243f05453c0897a930d745f7fd07fa600a38f98242922e0034b", "bytes": 11088},
        {"ordinal": 6, "path": "tools/provider-capacity-governor-shadow.tests.py", "gitBlobOid": "98191265e2e6b1878c0189d3fca8249f728c6543", "sha256": "sha256:d8657641168135afe09bacee8d1f55666890b9da4ecd3ae8281ec1218041c675", "bytes": 45023},
    ],
}
R28_BASE = {
    "commit": "f94cec826f8e3979a028b6e45516077895c44905",
    "tree": "08479b324dfcc1925d0b11794ca86098625c9f48",
    "orderedParents": ["8c7dc4f4339db82a8b3c2efd689bf5f72631ad6e"],
    "orderedParentTrees": ["5dcc00a7f9723a00992458ab9dd0d6b0fd373363"],
}
R28_IDENTITY = {
    "provider": "anthropic", "model": "claude-fable-5", "effort": "max",
    "serviceTier": "standard", "transport": "firstParty",
    "role": "INDEPENDENT_ADVERSARIAL_REVIEWER",
    "question": (
        "Review the exact seven-file Cloudvore provider-governor proposal for security, doctrine "
        "conformance, quality preservation, and fail-closed resource admission; return PASS or "
        "actionable findings with file and failure scenario."
    ),
    "nativeMaxOutputTokens": 64000, "substitutionAllowed": False,
    "loweringRequiresAcceptedNonInferiority": True,
}
R29_BASE = {
    "commit": "f2f71c2ca93f6c9dec934100dbd760b5643463a2",
    "tree": "6b81f2d9e40cfaac3e6b3efa9bdef3fc884e819a",
    "orderedParents": ["f94cec826f8e3979a028b6e45516077895c44905"],
    "orderedParentTrees": ["08479b324dfcc1925d0b11794ca86098625c9f48"],
}
R29_IDENTITY = R28_IDENTITY
R29_POLICY_DIGEST = "sha256:e7e3fde383f43972796b681023ff92d9b35365e275e6fc00d84cc2735de00c60"
R34_POLICY_DIGEST = "sha256:ebec57daeca11108b2ba2771471b92d7bedfac64f58f321c7c1752a6f8339b5f"
R35_POLICY_DIGEST = R34_POLICY_DIGEST
R36_POLICY_DIGEST = R35_POLICY_DIGEST
R37_POLICY_DIGEST = R36_POLICY_DIGEST
R38_POLICY_DIGEST = R37_POLICY_DIGEST
R39_POLICY_DIGEST = R38_POLICY_DIGEST
R40_POLICY_DIGEST = R39_POLICY_DIGEST
R41_POLICY_DIGEST = R40_POLICY_DIGEST
R42_POLICY_DIGEST = R41_POLICY_DIGEST
R43_POLICY_DIGEST = R42_POLICY_DIGEST
R44_POLICY_DIGEST = R43_POLICY_DIGEST
R33_BASE = {
    "commit": "55afee85ecf720eb857cea1980f511f331b9e86f",
    "tree": "6e58f77467320d53ced12906bf2be62b4fca3d56",
    "orderedParents": [
        "fc76bf6d5ab52891d06b7f71eb2e993e413c124c",
        "1f96975233bfa794dd039610c072bf67aa1d20ff",
    ],
    "orderedParentTrees": [
        "ce91367dda0365218def5e42f4439decf81ba92a",
        "fc54c4f9cb53a3dc272767dd4713b99b662368b5",
    ],
}
R33_SUBJECT_PATHS = [
    "README.md",
    "RECONCILIATION.md",
    REVIEW_SCHEMA,
    "specs/fleet-universal-provider-control-reconciliation.md",
    "tests/test_universal_provider_control.py",
    "tools/check_universal_manifest.py",
    "tools/universal_provider_control.py",
]
R34_BASE = {
    "commit": "edcbf5084e1c9cbb3b7654c683b91185cef1494b",
    "tree": "5b84b927f214c8f4834a4f665d1f2beebc9176ee",
    "orderedParents": [
        "8e20b4a1652931af178e792eb62ab892a7d309fd",
        "8149c3f06811f85b833b28940017f2d05448cf5d",
    ],
    "orderedParentTrees": [
        "bb740bd9434b417cd66a568b762f13a047a11abc",
        "1a8193ae7f8c9982bfe499d039e5c85ae74ea907",
    ],
}
R34_SUBJECT_PATHS = R33_SUBJECT_PATHS
R35_BASE = {
    "commit": "fbf53f59c18b6dc8d1cc404730b0d42a38496a07",
    "tree": "750b031a6793cec63d7eeaaf05eeb6a6c52a80d7",
    "orderedParents": [
        "6a3803fd1543c1bd0944ec0013987f053852e3c4",
        "7ae14db4506fb2869f0e84647785865e504c9af8",
    ],
    "orderedParentTrees": [
        "52378a42695fbf1e9376995493972153c83ab2df",
        "64f23fbe78ee6159a63fca7ff175a2cb4440dadf",
    ],
}
R35_SUBJECT_PATHS = R34_SUBJECT_PATHS
R36_BASE = {
    "commit": "64e6895c332a696af238007225148fd70582424f",
    "tree": "4a0baf72d925349a30aeae785b10391e10102000",
    "orderedParents": ["fbf53f59c18b6dc8d1cc404730b0d42a38496a07"],
    "orderedParentTrees": ["750b031a6793cec63d7eeaaf05eeb6a6c52a80d7"],
}
R36_SUBJECT_PATHS = R35_SUBJECT_PATHS
R37_BASE = {
    "commit": "d67b0781e1e926e1baebdb0ea9b7a0ef5c447d85",
    "tree": "53d91a85bcd0a09ef7b349bed477f5aac1be93cc",
    "orderedParents": ["64e6895c332a696af238007225148fd70582424f"],
    "orderedParentTrees": ["4a0baf72d925349a30aeae785b10391e10102000"],
}
R37_SUBJECT_PATHS = R36_SUBJECT_PATHS
R38_BASE = {
    "commit": FROZEN_R37,
    "tree": "aa7338aad75cf4bb12481439a776c5c174fe1a94",
    "orderedParents": [FROZEN_R36],
    "orderedParentTrees": ["53d91a85bcd0a09ef7b349bed477f5aac1be93cc"],
}
R38_SUBJECT_PATHS = R37_SUBJECT_PATHS
R39_BASE = {
    "commit": FROZEN_R38,
    "tree": "8a7344e0fbea8b43719ca44f89b1af354c5dd5fb",
    "orderedParents": [FROZEN_R37],
    "orderedParentTrees": ["aa7338aad75cf4bb12481439a776c5c174fe1a94"],
}
R39_SUBJECT_PATHS = R38_SUBJECT_PATHS
R40_BASE = {
    "commit": FROZEN_R39,
    "tree": "9a77aa147120666bfd620ecc400507933aef0ef0",
    "orderedParents": [FROZEN_R38],
    "orderedParentTrees": ["8a7344e0fbea8b43719ca44f89b1af354c5dd5fb"],
}
R40_SUBJECT_PATHS = R39_SUBJECT_PATHS
R41_BASE = {
    "commit": FROZEN_R40,
    "tree": "431b94081fe0f4fd8b29fb4f540ddf69ce47601f",
    "orderedParents": [FROZEN_R39],
    "orderedParentTrees": ["9a77aa147120666bfd620ecc400507933aef0ef0"],
}
R41_SUBJECT_PATHS = R40_SUBJECT_PATHS
R42_BASE = {
    "commit": FROZEN_R41,
    "tree": "c422aa60fe0d50bd0072b58fb1846adf04ee3ecd",
    "orderedParents": [FROZEN_R40],
    "orderedParentTrees": ["431b94081fe0f4fd8b29fb4f540ddf69ce47601f"],
}
R42_SUBJECT_PATHS = R41_SUBJECT_PATHS
R43_BASE = {
    "commit": FROZEN_R42,
    "tree": "3e4867c2efe777f25d64676ce8d7989ae50fe903",
    "orderedParents": [FROZEN_R41],
    "orderedParentTrees": ["c422aa60fe0d50bd0072b58fb1846adf04ee3ecd"],
}
R43_SUBJECT_PATHS = R42_SUBJECT_PATHS
R44_BASE = {
    "commit": FROZEN_R43,
    "tree": "d31cda26840f019dbc2f9b445d0b8e1a9cdeb607",
    "orderedParents": [FROZEN_R42],
    "orderedParentTrees": ["3e4867c2efe777f25d64676ce8d7989ae50fe903"],
}
R44_SUBJECT_PATHS = R43_SUBJECT_PATHS
EXPECTED_LAYER_ROUNDS = (26, 29, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44)
CURRENT_CANDIDATE = ":"
HISTORICAL_TEST_BODY_SHA256: Mapping[str, str] = MappingProxyType({
    'ReviewResourceAdmissionR29Tests.test_r28_01_runtime_refuses_before_reading_any_caller_input': '51808e5b02757ce0ff6a1e92b07c87041d7ba6f6970c161e80c45f167d2c9537',
    'ReviewResourceAdmissionR29Tests.test_r28_02_complete_fixture_is_conformance_only_never_runtime_admission': 'd037f0c5505f08895295fc80b423485ad78903a9122ec37809a796488d0caf2d',
    'ReviewResourceAdmissionR29Tests.test_r28_03_universal_mechanism_is_provider_neutral_and_profile_exact': '420cdf1cbb6f78cc8ca430165d077a8b7dcfe4e30e524b1068c6ef53803beb54',
    'ReviewResourceAdmissionR29Tests.test_r28_04_committed_policy_digest_rejects_source_substitution': '46ac6bde828e29d8953da959bc287be4cbab00f052a4306453b54bb33455c5db',
    'ReviewResourceAdmissionR29Tests.test_r28_05_packet_rehash_duplicate_and_execution_drift_refuse': '08cbae10f7c37fe8fb9a63b69d5434e7a5250bb8ad680953a3a729bb2b21a3fc',
    'ReviewResourceAdmissionR29Tests.test_r28_06_captured_raw_handle_and_tokenizer_binding_are_mandatory': 'bc3ea493fa827df76630b858548f3ee25d6b5435eec7d8b281d6fe6ca65b1d5b',
    'ReviewResourceAdmissionR29Tests.test_r28_07_native_charge_unknown_cache_other_and_output_fail_closed': '77badfd0bbf031ef3731ebd09735dabb763e1618a994dfdbd9113522025aab3f',
    'ReviewResourceAdmissionR29Tests.test_r28_08_all_windows_timestamp_order_positive_reserves_and_floor': '0515203ca3b3aca8d26405d5d00a0633b02c2b6c3ccc1f052bf048a0e69a0eb7',
    'ReviewResourceAdmissionR29Tests.test_r28_09_tools_argv_hooks_and_allowedtools_never_imply_containment': '3326b46baebb040b0b8294954b9a728fd704102bb17db4e1fc1bfb7818b2ed5a',
    'ReviewResourceAdmissionR29Tests.test_r28_10_capability_handles_are_profile_bound_and_conformance_only': '4c7395431ac55aa998476a9af96dfd3526a51ee6535b5d4c4049757ae16f3ecb',
    'ReviewResourceAdmissionR29Tests.test_r28_11_lease_and_authority_repetition_aba_and_early_release_refuse': '306929c190cfbb050ac61baae2bf79b77c128ef6e8c1e33c384ec6b2d1baef09',
    'ReviewResourceAdmissionR29Tests.test_r28_12_terminal_unknown_is_unevaluable_and_overruns_refuse': 'b54315e6e991e33135d631c914cdbbd9f82f40d989b9c66c86f26508973519fd',
    'ReviewResourceAdmissionR29Tests.test_r28_13_schema_ordinals_and_manifest_source_are_independently_bound': 'fa91ab9d0fd9db39bef3b655b40edcd7fa7acdeb51f14951c858f3995bbc29ae',
    'ReviewResourceAdmissionR29Tests.test_r29_01_nonseven_provider_neutral_fixture_is_conformance_only': '21694fac937dfadedabaeb4603614d59f6e67cc41dba9b16d762588be8bf85cd',
    'ReviewResourceAdmissionR29Tests.test_r33_01_integration_merge_and_exact_policy_are_literal': 'a5bdb44ef14ba1b46f5c7404109d99554b9a60b0d80e034e846c2d5c827e0e3f',
    'ReviewResourceAdmissionR29Tests.test_r33_02_current_manifest_rejects_base_policy_and_carrier_substitution': 'f3da517fd01fcd8ff5974dfc711333b900d6e0c2690a1abf1542e9d4223c9953',
    'ReviewResourceAdmissionR29Tests.test_r33_03_current_manifest_requires_integration_base_ancestry': 'ff39b98d9c2866249cde3468c0abbd4945ebbd98326b6fbc6a58bb0c7bb7eaf9',
    'ReviewResourceAdmissionR29Tests.test_r33_04_frozen_r29_manifest_rejects_drift_and_source_substitution': '399f4899d83a7f95e8b6ddd3b9355e780ef09be00674f166d97fb8ac739a1ebe',
    'ReviewResourceAdmissionR29Tests.test_r33_05_checker_validates_all_three_literal_trust_layers': '87797a0c5190a296bf27250a41c45738b9f69232e4e67ab7cf75c1d5039d5508',
    'ReviewResourceAdmissionR29Tests.test_r34_01_code_owned_charge_result_rejects_self_attested_amounts': '6d66d7dbbe73d26ac616aea6bbb66d8d94ab2dc2876106addfc44385e253e974',
    'ReviewResourceAdmissionR29Tests.test_r34_02_terminal_native_charges_are_derived_from_actual_usage': '611493779fbee5130ea3ed05c30f2b529017d0e89d929cdf6aeea64033e62d88',
    'ReviewResourceAdmissionR29Tests.test_r34_03_policy_mode_defeats_fully_rebound_projection_selection': '541960c4423538e7a5d07140978a89a403feca38cdfbcebdc7aabd03792446f2',
    'ReviewResourceAdmissionR29Tests.test_r34_04_cache_capability_is_exactly_request_profile_domain_and_mode_bound': '3acfdc4cd3aa17cd35778655175c9afcd89a3f38eae39c7dbca0471c94f0958e',
    'ReviewResourceAdmissionR29Tests.test_r34_05_native_charge_integer_representation_is_exact': '04fc7ba3986c9cbb16fbf048b8cea38008d58e0ea111320b91775b6ac7424c50',
    'ReviewResourceAdmissionR29Tests.test_r34_06_bounded_mode_allows_zero_actual_cache_but_keeps_reservation': 'c8e9019c01af72bad0d40014108b54ecb9c824733a59e650b719b1082ba6f8cc',
    'ReviewResourceAdmissionR29Tests.test_r34_07_generic_schema_accepts_1_and_64_but_rejects_65_subjects': 'afdb02c5df7df809a0d6abbb7cfa1445ca725586362b7c8c27950a6316180157',
    'ReviewResourceAdmissionR29Tests.test_r34_08_manifest_pins_integration_mode_profile_and_policy_digest': '92ae8c909b3256b3bacb20783f53965e809a1988fa82859d468e4baa6ad358cd',
    'ReviewResourceAdmissionR29Tests.test_r34_09_manifest_rejects_recomputed_policy_and_instance_substitution': '8e00edfbdcb38c7a91b51dec00f7b9abb316c674c2afe7e4ae66d7d7e962a4e1',
    'ReviewResourceAdmissionR29Tests.test_r34_10_frozen_r33_layer_rejects_drift': '9d4dbcea7fc6afce821b4719729d7152d3af97c480f0ba195f3f5ebd80b2c9d4',
    'ReviewResourceAdmissionR29Tests.test_r35_01_current_layer_pins_exact_integration_tuple_and_quality': '1b33177f986cc39e1b74d18f92ae065222d3e8b4e9093d87c84e5d5634db6b59',
    'ReviewResourceAdmissionR29Tests.test_r35_02_base_tree_parent_policy_and_subject_drift_fail_closed': '95e66e14aa1fca3be7d993e60e021ad0e95dae32be0c05de47b64489026160e0',
    'ReviewResourceAdmissionR29Tests.test_r35_03_frozen_r34_layer_rejects_manifest_drift': 'daab402eb6b333072a7c2f5f96f4cd057f1dcfb86952c92d3e2930f73fb45b16',
    'ReviewResourceAdmissionR29Tests.test_r35_04_frozen_subject_and_self_drift_fail_closed': 'd7d08e429afbc5264b8072aff81cb5e1489c0e002854ad32fcd555d8edad8b85',
    'ReviewResourceAdmissionR29Tests.test_r35_05_checker_has_five_literal_layers_and_runtime_stays_refused': '670e7ae2d5683b5568f13780f8fec5349506c4c8c74c77acd06d8ab5445e1543',
    'ReviewResourceAdmissionR29Tests.test_r36_01_exact_integer_reserve_boundaries_use_full_fixture': '32b2e746aa04d2c335faa39f7528641253db044a5e4b3b46c3d94882714f9a53',
    'ReviewResourceAdmissionR29Tests.test_r36_02_evidence_age_equality_and_microsecond_overage_are_exact': '67f7b021bf04544cf919278a74b22967e48761ce8317bb003305c9e81dd13db7',
    'ReviewResourceAdmissionR29Tests.test_r36_03_capacity_boundary_implementation_has_no_float_derivation': 'd5b3af083be618137799b044a6aed0feb4ad2293cad0e24a7206bef053cb3c69',
    'ReviewResourceAdmissionR29Tests.test_r36_04_current_layer_pins_r35_base_and_unchanged_policy': '367daa0298f444d913eb457547a58d2e3e5dddd9d2d6f4db22f384f656210091',
    'ReviewResourceAdmissionR29Tests.test_r36_05_r35_frozen_layer_and_r36_tuple_subject_self_drift_fail': '7cdbad682adde5f16f68d9c7c6c76e54624082398a68eec698aceefc7dec2d77',
    'ReviewResourceAdmissionR29Tests.test_r36_06_checker_has_six_literal_layers_and_runtime_stays_refused': '670e7ae2d5683b5568f13780f8fec5349506c4c8c74c77acd06d8ab5445e1543',
    'ReviewResourceAdmissionR29Tests.test_r37_01_current_layer_pins_adverse_r36_and_unchanged_policy': 'eb0d88ce22782e56bb3b1d8c81662c0d8c037a6169e67305cd7622e9920a87af',
    'ReviewResourceAdmissionR29Tests.test_r37_02_frozen_r36_and_current_tuple_subject_self_drift_fail': 'c7e4d7f5628f678577c5bc498f181b6935bd3d83786a28e6f86e64bbb9552123',
    'ReviewResourceAdmissionR29Tests.test_r37_03_checker_has_seven_literal_layers_and_runtime_stays_refused': '670e7ae2d5683b5568f13780f8fec5349506c4c8c74c77acd06d8ab5445e1543',
    'ReviewResourceAdmissionR29Tests.test_r38_02_current_tuple_subject_self_and_policy_are_exact': '13184d2828ab7a57fb43685c14fa484f512092fbff6e245ccf94e5fdbe67a636',
    'ReviewResourceAdmissionR29Tests.test_r38_03_checker_has_eight_layers_and_runtime_stays_refused': '1029db5a637bc546c03cba0d0de25c16fc0e8d8b3d5b7db6ebcf8279fb161e5f',
    'ReviewResourceAdmissionR29Tests.test_r40_01_frozen_carrier_tuple_is_literal': '568aaee318fe65434d93b6cfbc6fb95afcd38a046b23d5e74c719fb719266441',
    'ReviewResourceAdmissionR29Tests.test_r40_02_frozen_subject_and_self_are_literal': '6f4f598fab2650b85c835582a0f54715560d6663f65a6ddaf63cd5caebc361cc',
    'ReviewResourceAdmissionR29Tests.test_r40_03_frozen_policy_and_unchanged_runtime_oids': 'd83ac79c39a0824f4f3d27ad7bc9d9296a8f4e3d5ef1bf80a5cf0d712002d0f9',
    'ReviewResourceAdmissionR29Tests.test_r41_01_frozen_carrier_tuple_is_literal': 'b290e836c8b78b0675774cfd55a39a7df5ddde200ebbe295cc985898e0028840',
    'ReviewResourceAdmissionR29Tests.test_r41_02_frozen_subject_and_self_are_literal': '4174020ceba4924a1446d06ca3f80de4805f6d7f0fd3597cdd20b890780a94f4',
    'ReviewResourceAdmissionR29Tests.test_r41_03_frozen_policy_and_unchanged_runtime_oids': '15985d967715130fa398d53121aca6f1cddb82ed9ee85f959e38a121e6a149d4',
    'UniversalProviderControlTests.test_r10_01_capsule_poison_blocks_distinct_output_before_acquisition': '6a77fb4220d527db60bdc58926b5dbc35f7d1c855d2c72670e67d2af2c37f327',
    'UniversalProviderControlTests.test_r10_02_broker_artifact_poison_blocks_fresh_lease_and_close': '050d2e93d4a93e4cad742ac6e5903b2563e9deee6beab0fba0849a7a53c1b1cd',
    'UniversalProviderControlTests.test_r10_03_posix_runtimeerror_close_poison_blocks_output_rotation': '754e9f0aad3a60dda4947d8f45147e6271912494ca3e8a8e0219674f61fbf473',
    'UniversalProviderControlTests.test_r11_01_root_lock_linearizes_terminal_authorize_confirm_and_close': '52e2d938def8f6fba77165455e4e57c4f85d1c4e88c365711e8633f6c405b038',
    'UniversalProviderControlTests.test_r11_02_all_prepared_lease_owners_fit_exact_poison_bound': '0d2a07943265f813f6731c14b31335452b5a81e01fbdad27ca1231e6ebc2b38f',
    'UniversalProviderControlTests.test_r11_03_os_lock_unlock_and_close_failures_are_attempt_once_no_echo': 'df4d4d0f5d403629a591c4768934208aeb232e2cf5a91dfca03cf7e892b6790c',
    'UniversalProviderControlTests.test_r11_04_close_and_del_are_assertions_not_child_release': 'b90a2801f880170e594e23700ac15d3e063a4af2082533b22d9dfba8f6505132',
    'UniversalProviderControlTests.test_r12_01_manifest_self_uses_canonical_git_blob_under_crlf_checkout': '773e7f39a2cb1934e87f1d9521e02e4eb88fe0a0ef3819ca651ec4240649318b',
    'UniversalProviderControlTests.test_r12_02_posix_hostile_mutations_patch_actual_publication_syscall': 'c74bfec0fbc2ae2b23be84f9f5ca07312556042bca8f549f4edbd256ac635f3f',
    'UniversalProviderControlTests.test_r13_01_prepare_before_reset_confirm_after_is_denied_and_fenced': 'c4041622ee4fabba761028b48be5a4908cfc951d81e2b787217b2ccf99153268',
    'UniversalProviderControlTests.test_r13_02_exact_reviewed_launch_profile_is_required_and_attested': 'b6e0c177e1524bebddbeee93366b221467270134091303d3a6e60a5593d925e0',
    'UniversalProviderControlTests.test_r13_03_turn_context_and_all_token_ceilings_are_argv_bound_and_attested': 'eca3b6d136fee25b494418b4b9e3291d7f2a809922f1a2aa2ba7e641d6995298',
    'UniversalProviderControlTests.test_r13_04_broker_recomputes_current_and_prior_demand_from_frozen_inputs': 'be3a0f11d015e9657110bb3382443e45142d467f62d677e2057d572169bdee97',
    'UniversalProviderControlTests.test_r13_05_rollout_requires_containment_and_forbids_stage_skips': '15d5ec6ab71233ea513764bf1c7bbf29d023e89501906ecfd42887ebaeee6119',
    'UniversalProviderControlTests.test_r14_01_posix_directory_close_refusal_poison_is_attempt_once': 'c194cd91f2d90756e84741ecdab02ecd02689db9f6beef90472488e3041d816b',
    'UniversalProviderControlTests.test_r15_01_single_request_process_permit_is_persisted_and_one_use': '68472ab10e9c5ccbc082a871cb4c6b6824da7a03b96c5ff6ff8e382878d77d0e',
    'UniversalProviderControlTests.test_r15_02_semantic_demand_is_order_independent_and_idle_receipt_is_broker_signed': '10edf0fe57a1af2cf8b543d3a95f0894d24bbe56e4e021b3bd4e6e15de9e4e1a',
    'UniversalProviderControlTests.test_r15_03_mutable_lease_capacity_cannot_extend_immutable_attestation': 'c8724c3f5f23fd8eb5a321160755bb8b017c2dc23543834e6c5df98f33be5e63',
    'UniversalProviderControlTests.test_r15_04_runtime_watchdog_marks_termination_required_at_boundary': 'a7f7594dedc01e4229833f33c6dbfa828691b1ebc0bfd6d7b0e4dfee3b2fe7f2',
    'UniversalProviderControlTests.test_r15_05_quality_floor_and_exact_argv_contract_reject_weak_or_extra_launches': 'd2adc04d9a3db561224b00ff0652e8cabe1f74bcc37599f87613c8d457618826',
    'UniversalProviderControlTests.test_r15_06_alternate_state_root_cannot_bypass_machine_quota_lock': 'ceb0f0c5a76b1491c9414135595d40d4e1216eb9c9813c526122099411d30d4f',
    'UniversalProviderControlTests.test_r15_07_successful_canary_returns_to_containment_and_receipt_opens_once': '00cd76faabe3eb3013d43dfdb51d78ebd43eb78cd944f52dbd45618148b5f7ec',
    'UniversalProviderControlTests.test_r16_01_prior_idle_is_persisted_fresh_monotonic_and_one_use': '80fb6ada1d9c09392ca4ed0d44e7f8c53862b6b6e8d4f062c1bb6f5e0e75c6a9',
    'UniversalProviderControlTests.test_r16_02_broker_pinned_canonical_demand_rejects_fabricated_ready': 'a94c9565916c335cb660cf71dc5504b25038379badd458012e2cd20bb8cce2e3',
    'UniversalProviderControlTests.test_r16_03_usage_checkpoints_reserve_terminal_completion_exactly_once': '75633e944b24792e8234a81fed9dbe89fcdfecd9b86333e34a3ed16c2fa78ad2',
    'UniversalProviderControlTests.test_r16_04_durable_cross_root_claim_survives_owner_loss_until_authenticated_recovery': '8eeed4be1d673edf54a808d63bcf5123ceb2a2c22cca38c5d1fb0241015fbfe9',
    'UniversalProviderControlTests.test_r16_05_temporal_binding_drift_closes_canary_and_retains_fences': '16caa60f6ac1371c17e70319df3e95df8f76670bf39b2a5707473c13e6ac40a2',
    'UniversalProviderControlTests.test_r16_06_typed_quality_and_boundary_certifications_are_hmac_bound_and_stored': '981fa054d4a8f9e053f5b73b0f023d51966c13f9326951fc1e978a0c304411ef',
    'UniversalProviderControlTests.test_r16_07_canary_requires_hmac_output_quality_and_usage_reconciliation': 'b593135c1226b511db26fef368bcc1680932bb1b3a2ac84c4500960782e6c506',
    'UniversalProviderControlTests.test_r16_08_reusable_permit_cli_is_absent_and_never_reads_secret': 'efe54f651a1ef4fa8856e5aff8e9d7a75830046a0f4574427f76ef80722c4554',
    'UniversalProviderControlTests.test_r16_09_completed_usage_accumulates_across_terminal_leases': 'c4017f62bda94b6faba2960f141c4388e3bdcf2fe6c4e85e6a53c161c9cd42f5',
    'UniversalProviderControlTests.test_r16_10_termination_required_is_monotonic_and_cannot_mint_canary_success': 'c8e34722d177f44eb97d633cd27821c2fa16f380086d960f4ee9d71c31c23b0e',
    'UniversalProviderControlTests.test_r16_11_open_rejects_unparsed_or_forged_canary_receipt_rows': 'a79d7cd5c293ca3baacb3ae666beb6ad34d5388ba8a1039f7d9eaf89531e5305',
    'UniversalProviderControlTests.test_r16_12_provider_permit_token_ceilings_have_exact_keys': 'b1564c350e75f40eca2ee9494f90df78cb0743cb5f2b13e156d8747b8ca47819',
    'UniversalProviderControlTests.test_r16_13_manifest_verifies_exact_ordered_reconciliation_and_forged_negatives': 'cb9f55d4458ec6864e97cfe0a4d2c074c5dcd532d53b3e8531ebb88662e8b7d4',
    'UniversalProviderControlTests.test_r17_01_terminal_reserve_is_bound_to_frozen_checkpoint': '1f51c9928b06d415d81c3e6dde5147c3c7b4595c68f0bdfc54eb605ef28b2ee0',
    'UniversalProviderControlTests.test_r17_02_checkpoint_head_tamper_blocks_terminal_permit': 'ec73c0f11224b67805cc75179effa3974854cda9ab7b0fd940ad64e908fedd28',
    'UniversalProviderControlTests.test_r17_03_quota_release_is_published_before_local_success': '6bd7d450891c9a09fcb29e50f4bfcd29263066093fd8fe810e67f494b047e9ac',
    'UniversalProviderControlTests.test_r17_04_quota_root_is_not_reselected_from_changed_home': '0607e5d1739836a5d986f30f2891ba6aedfdd96fc822c3a18d5d45c528948479',
    'UniversalProviderControlTests.test_r17_06_prepared_quota_publication_retries_exactly': '9917b721f20b28acfeee8c3f775b8f85ab8ae5f65a01053db5faa04950c4ef96',
    'UniversalProviderControlTests.test_r17_07_low_level_request_primitives_are_not_public': 'bf7f13222f99aa35ff96cad3197fa02e441a08924380cb58ab31a0958178763b',
    'UniversalProviderControlTests.test_r17_08_completed_usage_is_partitioned_by_each_capacity_window': 'd14fd5aa6a286ed4f128930ddfea497f2a837885991eab4aa3a5cc76c34fde28',
    'UniversalProviderControlTests.test_r17_09_manifest_verifies_exact_ordered_merge_and_forged_negatives': '239ff2e8eae21f33f9e4580ccec9ba85b099030a7dd29c628d346a25a3e4814c',
    'UniversalProviderControlTests.test_r18_01_reference_candidate_exposes_no_callback_execution_boundary': 'd87005bc7172c48c7a7801eed6d89ca3498cdabaee397eae4ff24e880ded8022',
    'UniversalProviderControlTests.test_r18_02_crash_before_local_publication_reuses_exact_prepared_claim': '8eacccb46fdbd557ac17d688a3cc21e72f5a954c72fd05f3c509260c626dec83',
    'UniversalProviderControlTests.test_r18_03_os_account_authority_ignores_home_in_fresh_processes': '4cf7f95de2d36a6fcf93b4ebdf0609f019caa93698aea5089aa5c7b8e6ea2eb6',
    'UniversalProviderControlTests.test_r18_04_dead_after_zero_checkpoint_charges_full_reservation': '792fbffe000f4c5c64369d0f0d9106e2317f0cabb4559fed019a06b25d1a0a73',
    'UniversalProviderControlTests.test_r18_05_same_observer_or_fleet_key_is_not_independent': '771e22d3f158569ee5bb854ba3d084ddde42cc2a959be3c0652773127e017321',
    'UniversalProviderControlTests.test_r18_06_manifest_binds_final_lineage_and_grants_zero_gate_authority': '3d409517e61ca8c749b1e203a9db4abed53a7e90b6d0275a918c407f4be57b3b',
    'UniversalProviderControlTests.test_r19_01_prepared_retry_survives_restart_with_advancing_time': '6869a4ba676576b737f70f0199a43b84708e2c9a2028b02acab6826c6f0df071',
    'UniversalProviderControlTests.test_r19_02_nonreproducible_prepared_claimant_stays_fenced': '5dc2909716db860fd71326a4bdebd61976e8b42696ff39f10442691af20f6b84',
    'UniversalProviderControlTests.test_r19_03_canonical_authority_root_reparse_is_rejected': 'db4ef02387188b0d2ba66e57ebbe4d7ba78d4d8678ad1b360c7d92116121335d',
    'UniversalProviderControlTests.test_r19_04_real_authority_root_symlink_is_rejected_when_supported': '5a0edc003a4c3d207f66ace2c1859bfaca94b495bf9a281d6c2e93abf3ac085c',
    'UniversalProviderControlTests.test_r19_05_observer_keys_cannot_alias_launch_artifact_identities': 'f9d7bc786c8f90421a40bdd98717dd9140451b0c406d53dc09e71dcbd69613f0',
    'UniversalProviderControlTests.test_r19_06_test_brokers_never_mutate_default_account_ledger': '55c77b754ec2fdd0bf9ab5e8932e814f88c5e6bd2d01a7392ab44260fbebcd48',
    'UniversalProviderControlTests.test_r19_07_manifest_binds_restart_subject_and_grants_zero_authority': '6ea833cb72dafe13a445a7cb147224f03413a27f6894dc827b1c5142f4565639',
    'UniversalProviderControlTests.test_r20_01_stale_caller_time_cannot_replay_after_authoritative_expiry': '175fe4bd2b0ad4156135c39b47ed25faf392d25b950e02ff21c574476e190007',
    'UniversalProviderControlTests.test_r20_02_future_caller_time_cannot_extend_sampled_lease': '5ed819618451cca778996d5f96ac694a4bc48a8e7f93d15962f81734253f5344',
    'UniversalProviderControlTests.test_r20_03_every_authority_ancestor_component_is_reparse_checked': 'a29503bed784e209237d42113edcae3445cd39d51dd4490a64f6dbf8eabee38e',
    'UniversalProviderControlTests.test_r20_04_real_ancestor_junction_or_symlink_is_rejected': '271f28dd28aefb87d98bc4eb3996b52fe777a1a1aa40a972f6bdbeb862e4fdc1',
    'UniversalProviderControlTests.test_r20_05_universal_workflow_runs_exact_workbench_suite': '2f81f499365cb04491b72d7d12e0c6fb25416d7160e22022f43d859a8382dba1',
    'UniversalProviderControlTests.test_r20_06_manifest_binds_clock_path_ci_subject_and_zero_authority': 'b92f322dda66ef27763d3c057224608940c7688a1c91e3d314952f0e5c4bf759',
    'UniversalProviderControlTests.test_r21_01_root_lock_wait_resamples_and_cannot_prepare_expired_lease': 'c04c77b7eacd8833f9534f433982588749a0965f4f5f72972e895fb002ea6b3b',
    'UniversalProviderControlTests.test_r21_02_quota_lock_wait_resamples_before_durable_publication': 'a17162bbc98d40c97798314c79b4c947f72896328db64af44be71ec14f42428d',
    'UniversalProviderControlTests.test_r21_03_posix_missing_account_base_is_created_nofollow': '7a617198b0a41e94653a76b3bc94ce04d177fb83c5750c0343f7ca0f290e7bd1',
    'UniversalProviderControlTests.test_r21_04_ledger_component_swap_is_poisoned_before_use': 'bd90fa578c5489da3b30eb696dc8dc5d19f088bb080dfc0432d330063a9f78cf',
    'UniversalProviderControlTests.test_r21_05_lock_component_swap_is_poisoned_before_use': 'aac0c6a7d7075a92b15e644dba5f7f7269233a30337abc0bad59b672c88bbe7c',
    'UniversalProviderControlTests.test_r21_06_provider_budget_law_is_request_scoped_and_zero_authority': '23cb6ed2cb85fc2f42e85c3796c18849cadee0685451828cd563859aee064b90',
    'UniversalProviderControlTests.test_r21_07_manifest_binds_postlock_path_subject_and_zero_authority': '37295314976e46d77c7d62f0af280587ac2d2a9cb22a0cfcb04273d8a9ddbce7',
    'UniversalProviderControlTests.test_r22_01_ledger_child_replacement_is_poisoned_before_open': '4fecfb65459fc40ff6710a65986a3f83366587b6f29870bd26398c99e8c152dc',
    'UniversalProviderControlTests.test_r22_02_lock_child_replacement_is_poisoned_before_open': 'eee102753a1e0e01eaface0dcefb6e8f973695e4d710fb0295853c0f547f883f',
    'UniversalProviderControlTests.test_r22_03_native_ledger_child_identity_twin_rejects_replacement': 'd5bc802ff0cfe2a9eb3d91ca80c4ff74ce9ffdc47c06ba5e7562b68da4e59047',
    'UniversalProviderControlTests.test_r22_04_native_lock_child_identity_twin_rejects_replacement': '4648511382ca79b8d62975defbb74c8cf2e01298b872c8a298a9002a4cf784db',
    'UniversalProviderControlTests.test_r22_05_attended_receipt_is_private_strict_and_recomputed': '9118b618760f823c9fe6d25173d72cb0cc66f9b78809034067c4025d2b27a985',
    'UniversalProviderControlTests.test_r22_06_token_laws_are_strict_structured_policy': '13f9ca5b38e38c065e6c0b107c414302ccf22843bd6b0caf4b6d19a53263d41c',
    'UniversalProviderControlTests.test_r22_07_manifest_binds_child_receipt_policy_and_master_merge': '00d99ca6c59e6bb8ee76267a89e36901a36c45eb7c27ac316de74cc6d4410519',
    'UniversalProviderControlTests.test_r23_01_attended_duration_and_provenance_are_non_authoritative': 'fb13eff99ecbf7bb634546d499e15a21251e099fd0e225fe3528fea9a10ee42f',
    'UniversalProviderControlTests.test_r23_02_manifest_binds_semantics_and_zero_authority': 'dd90818b19861aaf9bb4619993b136d3891ff333aaa5b894c17cd93f9b825eb4',
    'UniversalProviderControlTests.test_r24_01_rfc3339_nanoseconds_floor_without_microsecond_truncation': 'ddc8711acad6ad504fbf4e4b44292feab238491819e42cde9aa8af61fb6d1469',
    'UniversalProviderControlTests.test_r24_02_manifest_binds_exact_timestamp_evidence_and_zero_authority': '425e96c2f24a0e50a7c1a9db6f0d157ba120d5bb5e8010eeb30431ebb5d3c2b3',
    'UniversalProviderControlTests.test_r25_01_two_endpoint_truncation_regression_stays_floor_one': '8c136f6d32938e0911daaf5e450e580000b7ef3c8aaa586e0b1a08c2c90c9348',
    'UniversalProviderControlTests.test_r26_02_manifest_binds_posix_fixture_repair_and_r25_parent': '4b0fb3481d342900425b461bd78eb5899ca7828df5cb47553ee118197fce1470',
    'UniversalProviderControlTests.test_r26_03_manifest_verifies_frozen_candidate_across_later_doctrine': '8e5970c50294871a8b83661f7782b02bdf90548c50501a48141ed6fde27a96b7',
    'UniversalProviderControlTests.test_r26_04_manifest_requires_frozen_candidate_ancestry': 'c8cfb4d8497149a3ac75ca3c23b8c7c189f08487e52daddb73f803180920e569',
    'UniversalProviderControlTests.test_r26_05_manifest_rejects_post_candidate_manifest_drift': 'de3bd26dbb4d7847393bca58b5cf08a3b2cede1fc221c151ef5a35bcbdf7665c',
    'UniversalProviderControlTests.test_r26_06_manifest_rejects_current_subject_substitution': 'c53055e734d9807a608f6ab9c58eda04616406d47e8fa7579f128f5b860df5f2',
    'UniversalProviderControlTests.test_r2_01_signed_gate_record_r1_red_r2_green': 'dd7079bf795851b3d26137b742d02d8c726ca165a1ac48a77fb2f0f57ddb99a5',
    'UniversalProviderControlTests.test_r2_02_multihost_declaration_r1_red_r2_green': '15a6485fa0fa2d840531af2fc1d13bf4b4bbd07f0e29500045c088fb584a983c',
    'UniversalProviderControlTests.test_r2_03_process_receipts_r1_red_r2_green': 'b74376375ec9960f1a036dd44f2f54181b57234271ea65d12c08337569c715ae',
    'UniversalProviderControlTests.test_r2_04_replay_restart_authority_r1_red_r2_green': 'dbc04782e1324a9075a077996ae660b8e258af61b830d6ad97effea590fe1d7c',
    'UniversalProviderControlTests.test_r2_05_canary_epoch_and_reseal_r1_red_r2_green': 'fe232643c6da5f0dc00851c204864ff36a0341e28dfb46ff1609d44d326555ae',
    'UniversalProviderControlTests.test_r2_06_complete_inventory_bytes_r1_red_r2_green': 'ef0cd39bc73f66ee0d0fda1286f2124b926162c8149d71e34078b91817c57228',
    'UniversalProviderControlTests.test_r2_07_two_phase_retained_handles_r1_red_r2_green': '66819bf6b4b865023aec1e60a86cae1264e85f296e9173ab657c24019b624c9e',
    'UniversalProviderControlTests.test_r2_08_portable_git_blob_manifest_r1_red_r2_green': '40b98aab7e4d13026fc4b1be8958321b66a7764809ca13e3b9d5be3122b7d264',
    'UniversalProviderControlTests.test_r2_09_digest_grammar_r1_red_r2_green': '43da81ca1616fcf64e439f850323b06cf85149504e65fa1634449d5272f8413d',
    'UniversalProviderControlTests.test_r2_10_capacity_and_request_timeline_r1_red_r2_green': 'b7fbe344ca8b3b1ff9ef39e7c7ba11edc2b1fa94c2763b711f01a3c0898d08be',
    'UniversalProviderControlTests.test_r2_11_bounded_hashing_and_amplification_r1_red_r2_green': '74ec2c875df54ce8b6029152b536d9940ee536eb8c39e294082c3843885e05a3',
    'UniversalProviderControlTests.test_r2_12_dual_platform_hash_locked_workflow_r1_red_r2_green': '3d72d271bdcde3e94d690ea9915daa78e194bf3285ca85e8d6b0a536f291938c',
    'UniversalProviderControlTests.test_r2_13_candidate_not_ratified_r1_red_r2_green': '669b3138d9ee702a009639320f692299b09e1d0f4892802e382fce7aa7a942e9',
    'UniversalProviderControlTests.test_r2_14_lock_and_rollback_controls_remain_r1_red_r2_green': 'ffa993586e14ff11280afa770ba19eff9b2196a14873e268d66fd835d20d6495',
    'UniversalProviderControlTests.test_r3_01_expired_prepared_lease_never_allows_and_remains_fenced': 'd46ce1a1412f5f447c6fdf7398de91e045323cd02f8fc5edfdd0aa012662ed2e',
    'UniversalProviderControlTests.test_r3_02_capacity_rollover_blocks_pre_reset_evidence': '6cefed2d7f898df139c46908ccec2cef152ed800c530ced388a1e4644e6c94f0',
    'UniversalProviderControlTests.test_r3_03_capsule_unique_open_and_actual_handle_limits': 'fe05c09bd8169a20275f505f4bab03888d28f7fe82f3c73d5b464242c56356a6',
    'UniversalProviderControlTests.test_r3_04_capsule_unexpected_pre_publish_failure_cleans_all': '8e1282aaf5528d29df74aa9b4055719f980a0b474ddf2e1227b5ca77d878047e',
    'UniversalProviderControlTests.test_r3_05_capacity_estimates_are_broker_derived_not_caller_selected': '5266411ca57480807e49fc37c23eb27e8ac13826cc26a021ba741c2bc71e4ac4',
    'UniversalProviderControlTests.test_r3_06_ambiguous_canary_recovery_reseals_and_malformed_is_stable': '5d1dca87653389284ec5c9fbfb4288a43b83cbb71f1884a6d05d6446afbd5374',
    'UniversalProviderControlTests.test_r4_01_single_pass_mutation_bytes_match_bound_source_hash': '3c3cfd03332feab62fdb84a93ef6f0cff045d895f6821374aa93db091d1d29d6',
    'UniversalProviderControlTests.test_r4_02_growing_source_reads_fixed_budget_plus_one_probe': '0aeeea9b792bf8c7f6888f5c4b33fae0be979f6476efdca29cf33741c86ccd98',
    'UniversalProviderControlTests.test_r4_03_no_clobber_publication_preserves_foreign_races': 'd79cb1561d158278412ad8fc08659208288a367280976e40732d89df3df19ef8',
    'UniversalProviderControlTests.test_r5_01_publication_binds_retained_temp_identity_and_exact_bytes': '8bc3a6710f6dee195da8c1866019a7424990579917d7f24007728b27cc8325da',
    'UniversalProviderControlTests.test_r5_02_temp_collision_preserves_foreign_temp_and_reason': 'e480764cfb78037d1c655715364b5a918da7d01190b8a82593be386fc4683dbd',
    'UniversalProviderControlTests.test_r5_03_retained_artifact_resume_reads_expected_plus_one_only': 'e87fcacc0f5518f08c157007c61d3351b2b5ce50bab69565eae2b2933bc5ed4f',
    'UniversalProviderControlTests.test_r5_04_sixty_four_hardlink_aliases_use_one_open_hash_pass': '03a62a47217eaabb56ff5a63aca426df44cfe7baa8a2cb09e5ed6acb4eea2619',
    'UniversalProviderControlTests.test_r5_05_link_raise_after_real_link_is_verified_success': 'eb362d263e200c26e9ab3f88a2d05a9d6d10ed1401d0614d6adf0d91d764365b',
    'UniversalProviderControlTests.test_r6_01_private_temp_replacement_survives_handle_bound_cleanup': 'bfa1254b481dfe7148b4e60002e4a679072529eb7bf68b5ef2c03fa815bfc623',
    'UniversalProviderControlTests.test_r6_02_public_replacement_survives_and_no_path_cleanup_exists': 'c837a49898be4ef3f4bd2d1df6211dd8aa9b3a141f2366b127d9a5bcfc6fad1c',
    'UniversalProviderControlTests.test_r6_03_cleanup_refusal_is_surfaced_and_bounds_repetition': '81e2bef5ba8a7e793171997cda13770cada389bdcca9e02f3aae967d419e7faf',
    'UniversalProviderControlTests.test_r7_01_unprivileged_linux_proc_fd_publication': '068ce3de80d31017c4e26eb90b182155b6e46f671fc873d04f7829685fe94419',
    'UniversalProviderControlTests.test_r7_02_temporary_cleanup_is_required_runtime_evidence': '555e8d5835e36c0b92f29e9952fe354d021f271aee3b2233062cdf5b10d6459c',
    'UniversalProviderControlTests.test_r7_03_cleanup_helper_exception_is_contained_after_publication': '398983649d904d3a63d55667a044ef14f2c0eaff8eaf98f41f2475ed8b8717f9',
    'UniversalProviderControlTests.test_r7_04_cleanup_helper_exception_failure_and_success_are_stable': '629afb01333edb69c7519a898d9741876cf14464958e2cb996f2f4598a7366b8',
    'UniversalProviderControlTests.test_r8_01_primary_failure_has_no_private_exception_topology': '3784a0a5ac4fd3151a533d9fc6ba905c04a5d25d005764aff8e366aeda3e9142',
    'UniversalProviderControlTests.test_r8_02_cleanup_failure_has_no_private_exception_topology': '908c5450a19174a3a35ef76117e9032b1da5b0ffdb5f5e6bdd4e4c77fe70cf84',
    'UniversalProviderControlTests.test_r8_03_open_osfhandle_failure_closes_native_owner_once': '0131e1dde7a05854d0d8ed9631c32232386a758e5fb5db48c48e6ff9f413fd40',
    'UniversalProviderControlTests.test_r8_04_fdopen_failure_closes_descriptor_owner_once': 'd2f120805b687fb7e83ff8de1c48d2a009249083af706f16e9d06a4381863757',
    'UniversalProviderControlTests.test_r8_05_posix_fdopen_transfer_closes_exact_owner_once': 'b23840cf0cd21439cfac80255d3bbbd87f95aaf4d3c14f28ab01f791581ec845',
    'UniversalProviderControlTests.test_r9_01_preflight_failure_is_fully_sanitized': '5ef3454f361a14aa433a3d7be876edccfadddfddc1dd702409311f2e19c47c27',
    'UniversalProviderControlTests.test_r9_02_unproven_publication_closes_never_report_clean': '896e1fd07c2587ec035641ded4a30b243ae98cb0095bc334bc1cedd0d6480162',
    'UniversalProviderControlTests.test_r9_03_finalizer_exception_class_is_sanitized_and_retained': '3e1fc6f4d36a187430781f90dc17595cf5e8d5fcd28ed9a8fc95cba54907b64a',
    'UniversalProviderControlTests.test_r9_04_false_disposition_blocks_native_and_descriptor_failures': 'bb8bb40fc556ff82f88389ef258989fe15edf3057021a1ba2e34b8f491ac4f79',
    'UniversalProviderControlTests.test_r9_05_false_closehandle_is_unproven_and_fenced': '193d8506fce4ef631cf954e24100add835e79a381a99249391849a37b2a43369',
    'UniversalProviderControlTests.test_r9_06_posix_close_refusal_fences_repetition': '1d25fe069edd4e8225ee2ae5bfbffe4360a58dfccbe4f53899f427bb5e1aa64c',
    'UniversalProviderControlTests.test_r9_07_source_and_artifact_close_refusals_retain_exact_owners': '705e781f11b3da87ceadb967b43151c475fec89f0346e13b8ac47729526cf65a',
})
FROZEN_R43_HISTORICAL_FUNCTION_SPANS: Mapping[str, str] = MappingProxyType({
    'ReviewResourceAdmissionR29Tests.test_r28_01_runtime_refuses_before_reading_any_caller_input': 'c1b552d5daf58093cfe7e3d4435639086d9003133c91a7872a5f0cb56278b76a',
    'ReviewResourceAdmissionR29Tests.test_r28_02_complete_fixture_is_conformance_only_never_runtime_admission': '38ed1a8c626ac6c29234bcf496d76c86c6b5dbf55d68c454837b0c6fa2e4946d',
    'ReviewResourceAdmissionR29Tests.test_r28_03_universal_mechanism_is_provider_neutral_and_profile_exact': '99caa046e57cfdc52883deabaafc16a9c2ad34fc8a70b22d955e0a2644cbc791',
    'ReviewResourceAdmissionR29Tests.test_r28_04_committed_policy_digest_rejects_source_substitution': '0eabe1932bc3e2191a15150d6f01b80b31360c2f9318466e4db8b2ce8394b62a',
    'ReviewResourceAdmissionR29Tests.test_r28_05_packet_rehash_duplicate_and_execution_drift_refuse': '90a1fbfc5c0e0ab059a12205f732302a5682ce31e4b28283b0be2bb7985c830a',
    'ReviewResourceAdmissionR29Tests.test_r28_06_captured_raw_handle_and_tokenizer_binding_are_mandatory': 'dd36b8244226e0d9a5e091f6b9e6ed02e2f4a48feaf7e5a49cc1edbb568b4be3',
    'ReviewResourceAdmissionR29Tests.test_r28_07_native_charge_unknown_cache_other_and_output_fail_closed': 'bbebcfad106c67cd471cf0621a895ec75bedd35bc8acf315bb00c029627cc0a8',
    'ReviewResourceAdmissionR29Tests.test_r28_08_all_windows_timestamp_order_positive_reserves_and_floor': 'f45399cd530293c7847275abdb399c484bf2da5c300af8626a1cb4dbe3535206',
    'ReviewResourceAdmissionR29Tests.test_r28_09_tools_argv_hooks_and_allowedtools_never_imply_containment': '51c689f3ef46ad3bb3f6315c9950313f1417a01b9b51d795fbe3684532439347',
    'ReviewResourceAdmissionR29Tests.test_r28_10_capability_handles_are_profile_bound_and_conformance_only': 'fb5567cbb1ab81da5801859fbd7328728948a9acf1c9be39058408c4227dec6c',
    'ReviewResourceAdmissionR29Tests.test_r28_11_lease_and_authority_repetition_aba_and_early_release_refuse': 'c54b93a56011025919ef52737baa581ea058c2af7702e1138f2b38f509debf4a',
    'ReviewResourceAdmissionR29Tests.test_r28_12_terminal_unknown_is_unevaluable_and_overruns_refuse': '383805bb9dee163494eba0f3748aa35dc1ca3a8dd94013c9b35b8fe4cf82d1b9',
    'ReviewResourceAdmissionR29Tests.test_r28_13_schema_ordinals_and_manifest_source_are_independently_bound': 'ab8ab2f45aaad12b7a5a70e53639f443338c5aa5ea0aef89298421d96db29981',
    'ReviewResourceAdmissionR29Tests.test_r29_01_nonseven_provider_neutral_fixture_is_conformance_only': '6f1ac254bd0dee8bf7020d341bfe8a7cb6cbfb697b22cbe9035464c8cbb9f093',
    'ReviewResourceAdmissionR29Tests.test_r33_01_integration_merge_and_exact_policy_are_literal': '953970d0939e9fbe666db3548ddc47219faa7951067f46b2301074548077fa7d',
    'ReviewResourceAdmissionR29Tests.test_r33_02_current_manifest_rejects_base_policy_and_carrier_substitution': '982930ea216d764997bed9e20247d2a32ddff235b2cd0a5281be5f1263641bc0',
    'ReviewResourceAdmissionR29Tests.test_r33_03_current_manifest_requires_integration_base_ancestry': '2e566b7d13417a728a3efac459e24942eb754e393028f3f17bd7e12149fbef24',
    'ReviewResourceAdmissionR29Tests.test_r33_04_frozen_r29_manifest_rejects_drift_and_source_substitution': 'f949e33ec9eb39c3f3ca99f7ec6089c49d0edf1354d06319736e2b51ec6405a8',
    'ReviewResourceAdmissionR29Tests.test_r33_05_checker_validates_all_three_literal_trust_layers': '4f5261abd1b2d1d396374176c5b5396ea734cd8a8c32bdec1f2fb29d8d77718e',
    'ReviewResourceAdmissionR29Tests.test_r34_01_code_owned_charge_result_rejects_self_attested_amounts': '996afcd920d0b03179add8dad7aad3eddb0d6303fc13c70ad8282b760844d3f3',
    'ReviewResourceAdmissionR29Tests.test_r34_02_terminal_native_charges_are_derived_from_actual_usage': 'e80647735ba8586624ed4b6615a2196c6b3c283a9012037a335c70a468a2089c',
    'ReviewResourceAdmissionR29Tests.test_r34_03_policy_mode_defeats_fully_rebound_projection_selection': '1f17c23bba178befb9cae1ed0d8691d1f5849114c4bcc7f757cf701e56a51c05',
    'ReviewResourceAdmissionR29Tests.test_r34_04_cache_capability_is_exactly_request_profile_domain_and_mode_bound': '599c7d1e7e765fffdb902d8e6a18ef981c4dfd0bfc9763228ade9e7369e0a32a',
    'ReviewResourceAdmissionR29Tests.test_r34_05_native_charge_integer_representation_is_exact': '3c9429a28cb80ea737e3af188ede731849e0f08cfd4a622911692f4f7e780e60',
    'ReviewResourceAdmissionR29Tests.test_r34_06_bounded_mode_allows_zero_actual_cache_but_keeps_reservation': '973be56fe07f8ed41584ef7cedd67e2998e7441ee78a7e58a8e61ee880f1243e',
    'ReviewResourceAdmissionR29Tests.test_r34_07_generic_schema_accepts_1_and_64_but_rejects_65_subjects': '5c6b85456b146d71573428421dce3057d97167c9aa133f6711c4169b9f551a95',
    'ReviewResourceAdmissionR29Tests.test_r34_08_manifest_pins_integration_mode_profile_and_policy_digest': '7fa3bcd9a175da03abdb9cc305996cb665ffbc44bcb15b5f973ab22bce3cc811',
    'ReviewResourceAdmissionR29Tests.test_r34_09_manifest_rejects_recomputed_policy_and_instance_substitution': '612e48a69f34a26ffeca5eea0630c59ed6375b5d758cda5fd5aa54bc9c6856e7',
    'ReviewResourceAdmissionR29Tests.test_r34_10_frozen_r33_layer_rejects_drift': '551560d4ce71a8fab4bf51b1e3a179a09285ba0b819b8a72b927aa02bb249e1d',
    'ReviewResourceAdmissionR29Tests.test_r35_01_current_layer_pins_exact_integration_tuple_and_quality': 'f3e7db1d1cfe25b09076ba1dd960d3b6b107868575d3ec9898088746183299c7',
    'ReviewResourceAdmissionR29Tests.test_r35_02_base_tree_parent_policy_and_subject_drift_fail_closed': '22e4d61230f570ce939fbf91d30bcdb1a1a9606a5febaef67f8194a2a80379fa',
    'ReviewResourceAdmissionR29Tests.test_r35_03_frozen_r34_layer_rejects_manifest_drift': 'a61af6c7b95d4406a59f5aa12360f17d514d8024dc81dd1186ad4bebe381d57f',
    'ReviewResourceAdmissionR29Tests.test_r35_04_frozen_subject_and_self_drift_fail_closed': 'b4bc0e1838b26bcbf4254e4b6048cc7708313e58b7b95970d8c56f2b318f9ca9',
    'ReviewResourceAdmissionR29Tests.test_r35_05_checker_has_five_literal_layers_and_runtime_stays_refused': 'f0947336e5d5601d3b601c523b6e12935d48e54c1b798656f3d150c6d8e74a58',
    'ReviewResourceAdmissionR29Tests.test_r36_01_exact_integer_reserve_boundaries_use_full_fixture': '68c7c01cb804ab17067983462678bfc3483625ee630280277b1faa2f1d86a8f2',
    'ReviewResourceAdmissionR29Tests.test_r36_02_evidence_age_equality_and_microsecond_overage_are_exact': '8b1f86f7dc7477c47696a4b845aa41dbafd113edd1953d83f469844b91205dad',
    'ReviewResourceAdmissionR29Tests.test_r36_03_capacity_boundary_implementation_has_no_float_derivation': '82d95d637f2ec4924f4c92a64892036c7defd531116558f02cf7ba2237d7934c',
    'ReviewResourceAdmissionR29Tests.test_r36_04_current_layer_pins_r35_base_and_unchanged_policy': '72f2414af5383cac82fc5501412837590fde8dc2548c43372c91852da2025e8a',
    'ReviewResourceAdmissionR29Tests.test_r36_05_r35_frozen_layer_and_r36_tuple_subject_self_drift_fail': '3888d948c41fc2d4e20c9b876ff5757f1d1dcdfc2fd751c7b294b1774ac64232',
    'ReviewResourceAdmissionR29Tests.test_r36_06_checker_has_six_literal_layers_and_runtime_stays_refused': '68f7178d44f7a08e49893f681e7e2ff02c695285e265b31353ef4dc6f91db2c5',
    'ReviewResourceAdmissionR29Tests.test_r37_01_current_layer_pins_adverse_r36_and_unchanged_policy': '68be5bc1464d738ec1b691ac33d8376b259413aca028bad40b36ada57f1fc127',
    'ReviewResourceAdmissionR29Tests.test_r37_02_frozen_r36_and_current_tuple_subject_self_drift_fail': 'ce5203f5d90d35a6cdb56fe25fff506522281126622c43f60f55a9df38ad0a31',
    'ReviewResourceAdmissionR29Tests.test_r37_03_checker_has_seven_literal_layers_and_runtime_stays_refused': '217b7462dbe1c66d7a0e54a4911e9b03b34886746a90245a50ee15174081934d',
    'ReviewResourceAdmissionR29Tests.test_r38_02_current_tuple_subject_self_and_policy_are_exact': '2c56b3c57cd356bffd9e613ea90d5180dac856355e729ac34509f74e27e89bcb',
    'ReviewResourceAdmissionR29Tests.test_r38_03_checker_has_eight_layers_and_runtime_stays_refused': '8a6d8e1b451de41f200e9c13eb0ea06a645bc9c878954a6ff18ea241d3736daa',
    'ReviewResourceAdmissionR29Tests.test_r40_01_frozen_carrier_tuple_is_literal': 'b261b8b21d040a0f2a76249401f0692efab825edf887cfeb56d48bb48df47605',
    'ReviewResourceAdmissionR29Tests.test_r40_02_frozen_subject_and_self_are_literal': '0de3cf120d0c7862ed4ac0dfe485f7570c7e21f9c2e764a6e404d5452c4c0d7c',
    'ReviewResourceAdmissionR29Tests.test_r40_03_frozen_policy_and_unchanged_runtime_oids': '3b48ab1881bb480215b22548db2f751d0e7b411f09166d4a4d7de73d6c316c40',
    'ReviewResourceAdmissionR29Tests.test_r41_01_frozen_carrier_tuple_is_literal': 'c6daebab62fbece267dd82f7e1119ab28aad8ff08baa46d0f27711419e57b044',
    'ReviewResourceAdmissionR29Tests.test_r41_02_frozen_subject_and_self_are_literal': 'e1a3f10fda72e2dc900b6411038af8da5e7b5d6199d96f704d8518269faebbe4',
    'ReviewResourceAdmissionR29Tests.test_r41_03_frozen_policy_and_unchanged_runtime_oids': '9aa83561f81a2f3da427601c6a54431cc52e6287843e6b43bbd2f089570f4179',
    'UniversalProviderControlTests.test_r10_01_capsule_poison_blocks_distinct_output_before_acquisition': '42550cae9f0e9497128ae94ada98f64dbec5b0ca0975c1e7f92c4e7402f82aa8',
    'UniversalProviderControlTests.test_r10_02_broker_artifact_poison_blocks_fresh_lease_and_close': 'e186152a0c6eb58586725da5e0096ed0334db78eee2864f4f6841501714c58e6',
    'UniversalProviderControlTests.test_r10_03_posix_runtimeerror_close_poison_blocks_output_rotation': '0024156ea79d0adb3efe9c6bdd4c70375f5354888f3e17eb2cfcd4466969e3e1',
    'UniversalProviderControlTests.test_r11_01_root_lock_linearizes_terminal_authorize_confirm_and_close': '4b68e4f36504b49276bf275308a5f3126883bc651bfaf68ae2f837b33e9e54aa',
    'UniversalProviderControlTests.test_r11_02_all_prepared_lease_owners_fit_exact_poison_bound': '7da00395e65f438961f03fed4ab81f8fe2e738a433b486a228359b546a2784da',
    'UniversalProviderControlTests.test_r11_03_os_lock_unlock_and_close_failures_are_attempt_once_no_echo': '3862f54f3c37a30f8a0f42555c7966ff44329aad792c2eeab0b1c55fce0f39c9',
    'UniversalProviderControlTests.test_r11_04_close_and_del_are_assertions_not_child_release': '93faeb0834927357f18dae5dee3659199f21d79b95368b8a2e727d8ac0c7d384',
    'UniversalProviderControlTests.test_r12_01_manifest_self_uses_canonical_git_blob_under_crlf_checkout': 'b5714fa45b5189b52be9310681c74eac90ecca6820dcf4130b7185dab15e20db',
    'UniversalProviderControlTests.test_r12_02_posix_hostile_mutations_patch_actual_publication_syscall': 'e2993464727bb9231323ee858d9a74965730cdf62a3187466e18853eaf2959ea',
    'UniversalProviderControlTests.test_r13_01_prepare_before_reset_confirm_after_is_denied_and_fenced': '4bf85d7bb8db68d70bc7ddaa7844d4f6ec744b5b18411ac96c24a043786dbc14',
    'UniversalProviderControlTests.test_r13_02_exact_reviewed_launch_profile_is_required_and_attested': '8a872999e684fdcd4339e2a9e37489e2328a41aac03d3032cf4cec5e966d42f9',
    'UniversalProviderControlTests.test_r13_03_turn_context_and_all_token_ceilings_are_argv_bound_and_attested': 'e8e0fff6500c82c01341a20bf7b9dad1255fd36d646580e5b73bf31a9a969c32',
    'UniversalProviderControlTests.test_r13_04_broker_recomputes_current_and_prior_demand_from_frozen_inputs': 'c6cec2d50d31f8e77ec4ca1c1445f34d8d25de353e589e5b97cd45bb252bf95e',
    'UniversalProviderControlTests.test_r13_05_rollout_requires_containment_and_forbids_stage_skips': '89c14f993fda77192fb3614e2ecd2a43c2ebbb7f4f31484dd7632ab15211375d',
    'UniversalProviderControlTests.test_r14_01_posix_directory_close_refusal_poison_is_attempt_once': '04faa783cf184ec1118d484891b79466c231717df623dd4578465d6503663e34',
    'UniversalProviderControlTests.test_r15_01_single_request_process_permit_is_persisted_and_one_use': '6d0309b0a79a5f6ad176917172e097ccf12a4f6a0ceccd27720c5f629c6e2196',
    'UniversalProviderControlTests.test_r15_02_semantic_demand_is_order_independent_and_idle_receipt_is_broker_signed': '8ee0d7b6327d66aa3b0b4ce1ec593cc806ea4c6856d984d743dfeee5a4669888',
    'UniversalProviderControlTests.test_r15_03_mutable_lease_capacity_cannot_extend_immutable_attestation': 'bb6ff1cd43279c19e31ed03511184a1bd038a487dfbb145244ee34d9eebc2b8b',
    'UniversalProviderControlTests.test_r15_04_runtime_watchdog_marks_termination_required_at_boundary': 'aa1c38caeb0862f847fa7c98300c9fa0210ddcaab9ae3e8d5577d281a7e62c13',
    'UniversalProviderControlTests.test_r15_05_quality_floor_and_exact_argv_contract_reject_weak_or_extra_launches': 'd3bb57e52096e9409917d743a9c974fad6a6f94d0cf1ab4bd97aaa49b4e3c96a',
    'UniversalProviderControlTests.test_r15_06_alternate_state_root_cannot_bypass_machine_quota_lock': '2a19e6d72ed89a7985bfa07f25218d4ffe97911e68abb81e1cecafca736f6a8e',
    'UniversalProviderControlTests.test_r15_07_successful_canary_returns_to_containment_and_receipt_opens_once': 'fdfd37bd31ae84a693e539edf59c2ca24f76259c7afded4200c0635f7f18c1c6',
    'UniversalProviderControlTests.test_r16_01_prior_idle_is_persisted_fresh_monotonic_and_one_use': 'ef42e0071e9709547deb51b9bf3d1a3aab277e199f2f288561ae102c51b267b3',
    'UniversalProviderControlTests.test_r16_02_broker_pinned_canonical_demand_rejects_fabricated_ready': '2c7d14349e8ce184b6e54c09abc822ad5e5acc2abb75050ec4c06a92abfbae58',
    'UniversalProviderControlTests.test_r16_03_usage_checkpoints_reserve_terminal_completion_exactly_once': '95f5c83cc63405afabe904f56fe16a59602350152d7be6de356f185fbf3a9aa9',
    'UniversalProviderControlTests.test_r16_04_durable_cross_root_claim_survives_owner_loss_until_authenticated_recovery': 'd7771069c4bcc8eb9b6bcd44748c69210b7362379440edfd568e24ec2467ac27',
    'UniversalProviderControlTests.test_r16_05_temporal_binding_drift_closes_canary_and_retains_fences': 'fb2ffcd1bcaec79e7a672d7385dfa1a69ede05bbaec4a37d7ccb6d54f4602b9b',
    'UniversalProviderControlTests.test_r16_06_typed_quality_and_boundary_certifications_are_hmac_bound_and_stored': '0fc22216cab9f3ffd16f53febb7af687d48d7d11f7dd175e5fc8bffa895b3a97',
    'UniversalProviderControlTests.test_r16_07_canary_requires_hmac_output_quality_and_usage_reconciliation': '6ff0b57bf7dd24f4d15ae2c7c6cea8fa6e00c2e2e6f24534a6b18118f970d961',
    'UniversalProviderControlTests.test_r16_08_reusable_permit_cli_is_absent_and_never_reads_secret': '863a9e08a88edb58f3225954da33542da836ffa17b96a449088d6f3156367870',
    'UniversalProviderControlTests.test_r16_09_completed_usage_accumulates_across_terminal_leases': '7351724bc7aca423eccb96b9796ef9fe9910591ad7b72fbb0710aa55015d8b0d',
    'UniversalProviderControlTests.test_r16_10_termination_required_is_monotonic_and_cannot_mint_canary_success': '6aeda5002d7a9a3938b2ae698c79b216273f48c3cac439a3bb86cafc0cdba26f',
    'UniversalProviderControlTests.test_r16_11_open_rejects_unparsed_or_forged_canary_receipt_rows': '7643cc14130acc4a88dcb75c94ca6099d96c7738a5b30464240e192b75a7f463',
    'UniversalProviderControlTests.test_r16_12_provider_permit_token_ceilings_have_exact_keys': '45e717db864ea2ce35167a2aa8f74b89ddc7b3fe026aad0dba351ea2c6136ad7',
    'UniversalProviderControlTests.test_r16_13_manifest_verifies_exact_ordered_reconciliation_and_forged_negatives': '388e912b7ffa31ea6633c1a9a077be3d481f3618623c0fdcf8ba7a7a20e19aa8',
    'UniversalProviderControlTests.test_r17_01_terminal_reserve_is_bound_to_frozen_checkpoint': 'fb2a37c244e776ddb0ceb5ee27bd6195e982ca0d0d241c8b59bbfc448c51700d',
    'UniversalProviderControlTests.test_r17_02_checkpoint_head_tamper_blocks_terminal_permit': 'c5d80d99092bd3029af6e8e66324460baa60264be0536925a7eb9bdd7357038a',
    'UniversalProviderControlTests.test_r17_03_quota_release_is_published_before_local_success': 'fecfa6c0df4fe35652bceb8366221576629f8d909f0e8ef3334d5052f13f4d04',
    'UniversalProviderControlTests.test_r17_04_quota_root_is_not_reselected_from_changed_home': '892a173f27a637cac7f19a13100d26a78c389e236944634b6650108b29269d54',
    'UniversalProviderControlTests.test_r17_06_prepared_quota_publication_retries_exactly': '28133fe4d3edd31c666af83cb6c5785b9d14ce36fc59f27bd3331a41cfb5c097',
    'UniversalProviderControlTests.test_r17_07_low_level_request_primitives_are_not_public': 'fbb5de031b28676fb3552d1666d35bca3283a432bbd675ea469386827c2a8274',
    'UniversalProviderControlTests.test_r17_08_completed_usage_is_partitioned_by_each_capacity_window': '668de6f086a4e793ae7acfe639417f8bd78c37007de58e98c870a146b5c0c133',
    'UniversalProviderControlTests.test_r17_09_manifest_verifies_exact_ordered_merge_and_forged_negatives': 'b5b03a57ff67e7b2c964d5dc4d4ddc67393192ef5d42c3711efa2b72c9507eba',
    'UniversalProviderControlTests.test_r18_01_reference_candidate_exposes_no_callback_execution_boundary': 'c5a6ecf9db1504bd028d47b3c1816070be34927a4a15795b32d64477dbac7103',
    'UniversalProviderControlTests.test_r18_02_crash_before_local_publication_reuses_exact_prepared_claim': '8904c909fd8336b5bc36e19c487b023d4a17d5188f2722990c2eaf167109d1a6',
    'UniversalProviderControlTests.test_r18_03_os_account_authority_ignores_home_in_fresh_processes': '6bfd273e912d02657ed0abc67a9f0af9e7feae5eebaa78fbae666baea3d74714',
    'UniversalProviderControlTests.test_r18_04_dead_after_zero_checkpoint_charges_full_reservation': '4c92379aa5cc3e9ed24213a7e9201fb058ba70adacfd05a7996bfa81525b65e4',
    'UniversalProviderControlTests.test_r18_05_same_observer_or_fleet_key_is_not_independent': '8434fc885b37daf0301fe5edf9de2c14d22608d86d57121010ec7ea98b3f3d5a',
    'UniversalProviderControlTests.test_r18_06_manifest_binds_final_lineage_and_grants_zero_gate_authority': 'daa4cde61fa822e8509fe4c209a8fe38ed44c800d3f498caa759be7a8e9a2202',
    'UniversalProviderControlTests.test_r19_01_prepared_retry_survives_restart_with_advancing_time': '4295d951d6f6d2ee80c476a1a553eb4a24549eed62194be51533c83d88854970',
    'UniversalProviderControlTests.test_r19_02_nonreproducible_prepared_claimant_stays_fenced': 'b3128a20a86e15acfc2ea794ace3732dd8a09aa8547df4fb8a6521d40ed02e26',
    'UniversalProviderControlTests.test_r19_03_canonical_authority_root_reparse_is_rejected': '9d60825d3c006439310a2a51d3769c2ccd08bc6bc98d459967e51e081e8176fa',
    'UniversalProviderControlTests.test_r19_04_real_authority_root_symlink_is_rejected_when_supported': 'f95cb184f51065ce0fe9a745f3a25f6592a72b5d9bc63f619b4a6ab51667e580',
    'UniversalProviderControlTests.test_r19_05_observer_keys_cannot_alias_launch_artifact_identities': '52aa568409cfc08390da8aa82f315f9d724ff8b66ff95cb86bf01fe1c4fdaae8',
    'UniversalProviderControlTests.test_r19_06_test_brokers_never_mutate_default_account_ledger': '2c5dfc56955254ca29e36cb87ea16f61e1f10c168baa84e9ab398fcf197c3be4',
    'UniversalProviderControlTests.test_r19_07_manifest_binds_restart_subject_and_grants_zero_authority': '8e3cbe375d40fef3b06935fef519e6e32ab1cf1aa2327a2a9401533e4fcd4101',
    'UniversalProviderControlTests.test_r20_01_stale_caller_time_cannot_replay_after_authoritative_expiry': '7005d74dcf589d62b5f86f274965c9cf23cbfff0fbe1c74065dd103ee27e8140',
    'UniversalProviderControlTests.test_r20_02_future_caller_time_cannot_extend_sampled_lease': 'ab233c33567a2cec6d049bfe13bded4839744542d800d3f84d6e16a229464779',
    'UniversalProviderControlTests.test_r20_03_every_authority_ancestor_component_is_reparse_checked': '8cf6289b81244521ae352d1f5a0d546069578ffbfa35fe207f081c31be1a8923',
    'UniversalProviderControlTests.test_r20_04_real_ancestor_junction_or_symlink_is_rejected': 'fd2497a9c7455f78376c18fc9c3621d2739bb51d6f6b07bf1e1fd0648f2abb98',
    'UniversalProviderControlTests.test_r20_05_universal_workflow_runs_exact_workbench_suite': 'd174ba77122304a11a4fb8e06eab907448ca8e5d2c6e167eb64c74b5342ccf33',
    'UniversalProviderControlTests.test_r20_06_manifest_binds_clock_path_ci_subject_and_zero_authority': 'fc5115a36beb5384ee6595609450072cb1618883e4debff16e30c51e49b43c50',
    'UniversalProviderControlTests.test_r21_01_root_lock_wait_resamples_and_cannot_prepare_expired_lease': '8e284160a2d3f2c6d91fb04ca0f5f26c691922d017b91e31f679d564a2bf9f69',
    'UniversalProviderControlTests.test_r21_02_quota_lock_wait_resamples_before_durable_publication': '6be377088a10b01aa692dd3dfaa8a1cc71a8faae552eb6e2d4b50e204d3363c4',
    'UniversalProviderControlTests.test_r21_03_posix_missing_account_base_is_created_nofollow': '5f834e41de59e2fe673892a7281d1ce6b8d196a4a35a2a512f509b2dbda006b9',
    'UniversalProviderControlTests.test_r21_04_ledger_component_swap_is_poisoned_before_use': '558dfbd765bb5332f2fff1fccddf78d521fe90351c87033a04b5ac48ab00adfa',
    'UniversalProviderControlTests.test_r21_05_lock_component_swap_is_poisoned_before_use': '184db3db875fee0ad410127dec2434088088fca0a982e434c7863271a91975e2',
    'UniversalProviderControlTests.test_r21_06_provider_budget_law_is_request_scoped_and_zero_authority': 'ccbbc6112563e2e78d6da24041f0abcc407996f21831b24ecff2106e63ac195c',
    'UniversalProviderControlTests.test_r21_07_manifest_binds_postlock_path_subject_and_zero_authority': 'e2a309dda330348bf4b3c618c140380bf64db3a81b427038175f9a243ac48cd0',
    'UniversalProviderControlTests.test_r22_01_ledger_child_replacement_is_poisoned_before_open': '997ffb866d5daa3dbddee2d461cc5c60b7a1a889e2a535439686022199e4c044',
    'UniversalProviderControlTests.test_r22_02_lock_child_replacement_is_poisoned_before_open': 'a896e330e67044a1aa95fea9491c9772b0df0e685233801004fafa6dcb16a317',
    'UniversalProviderControlTests.test_r22_03_native_ledger_child_identity_twin_rejects_replacement': '3338e117711a7cdc211a2e4dabb9ddce6a1c407029a30b7192621937570fa4cd',
    'UniversalProviderControlTests.test_r22_04_native_lock_child_identity_twin_rejects_replacement': '1c4fbafccf5ca75ad588e39be13d79d39aca0f3678408bb84b7388c5e089fd00',
    'UniversalProviderControlTests.test_r22_05_attended_receipt_is_private_strict_and_recomputed': '6fc0868b4ead222310ac78548b46fc3d03ab742b5dc3c311d7c74778686461dc',
    'UniversalProviderControlTests.test_r22_06_token_laws_are_strict_structured_policy': '931de6b375e78d6f24f4b43373eab4df8d6abf45c86bbfafb224208aea796ebd',
    'UniversalProviderControlTests.test_r22_07_manifest_binds_child_receipt_policy_and_master_merge': '2bd89b5b7f30da4cd9b085b5595ce6585925b20dc0c68dc1e38389b042d16cf8',
    'UniversalProviderControlTests.test_r23_01_attended_duration_and_provenance_are_non_authoritative': '5c4ea7fb9accdf1608c92abc90b4011fb9f203ff60eaa1e47d76473c4032102a',
    'UniversalProviderControlTests.test_r23_02_manifest_binds_semantics_and_zero_authority': '4317e06dfd541e885396cbf73c5cab81e6eea27376a21eecfdc6901c18721757',
    'UniversalProviderControlTests.test_r24_01_rfc3339_nanoseconds_floor_without_microsecond_truncation': 'd5560f5e5db992be2e9e09336220d521a68a242f767f181536f900043901d461',
    'UniversalProviderControlTests.test_r24_02_manifest_binds_exact_timestamp_evidence_and_zero_authority': 'c675c328632f80118abafbc4a2a98d4200e9a4dde1fb0f40d3dc2486b132bdef',
    'UniversalProviderControlTests.test_r25_01_two_endpoint_truncation_regression_stays_floor_one': '186d9d04d3fe2dd7e08657b6c40692fb03e6102debc842cb0c28997ceed036bc',
    'UniversalProviderControlTests.test_r26_02_manifest_binds_posix_fixture_repair_and_r25_parent': '6a73dc6ec95132bcfbc5e81a06fbc94c13c8de603f68b994d9c26512bf49d9ed',
    'UniversalProviderControlTests.test_r26_03_manifest_verifies_frozen_candidate_across_later_doctrine': 'ecbc83de0af8206fafff26ac30cc13a3539caa94009e5e7084beef5851790eec',
    'UniversalProviderControlTests.test_r26_04_manifest_requires_frozen_candidate_ancestry': 'dd9d5678685b0867c38be02dd0275bc1f00ea3bf4ca894f3a4fb22de493966d8',
    'UniversalProviderControlTests.test_r26_05_manifest_rejects_post_candidate_manifest_drift': 'cf3982996af286018516058109924c27124fc1b09c12a9c1d31c314315966e82',
    'UniversalProviderControlTests.test_r26_06_manifest_rejects_current_subject_substitution': 'b673f160fa421deedc1ef27e568924a9789ed5e68020ba60cca390ea07f77e92',
    'UniversalProviderControlTests.test_r2_01_signed_gate_record_r1_red_r2_green': 'da2566941d04d123bf224d846ccd584974f2b5af9a45b7a92794ace9b81d1595',
    'UniversalProviderControlTests.test_r2_02_multihost_declaration_r1_red_r2_green': '9a34ad7674e96d6a13a65c35ded48f50443cacd8e9940f04e820ffe8fb6f7edb',
    'UniversalProviderControlTests.test_r2_03_process_receipts_r1_red_r2_green': 'f1b1e459d4cdf07b04f7ca4e368d14d3be87022264a409a0b23963387014afd6',
    'UniversalProviderControlTests.test_r2_04_replay_restart_authority_r1_red_r2_green': 'aeac9852653305ef0c4c1921147b7914768b85275406b6284296c44d26a0ff66',
    'UniversalProviderControlTests.test_r2_05_canary_epoch_and_reseal_r1_red_r2_green': 'c13a2a03e7df89f0ecfeea950abb0d17e3ff0c493e14bf469bcdc4f9c73f76a8',
    'UniversalProviderControlTests.test_r2_06_complete_inventory_bytes_r1_red_r2_green': '03c6703f21d17674a56dbd8ccfaa1299aa1024ba9b5f8ce5a96deb350677f373',
    'UniversalProviderControlTests.test_r2_07_two_phase_retained_handles_r1_red_r2_green': 'a63b656dedbc5c4befe93322226a9f0ce4baddd47ef855a0faba3eeb313b1e70',
    'UniversalProviderControlTests.test_r2_08_portable_git_blob_manifest_r1_red_r2_green': 'f0609c63f51f8ba79b9b2e67905ec43415918f59644ce43e08aea7a8e518e013',
    'UniversalProviderControlTests.test_r2_09_digest_grammar_r1_red_r2_green': '1900086f0abbb955992dccd9846428a325f77c2deaf81240a1d5919dfe4c9c57',
    'UniversalProviderControlTests.test_r2_10_capacity_and_request_timeline_r1_red_r2_green': '6819ff5d002c2d05dbb0e1ba24e31be80427e510018ecdee886c2c8f6d6d2401',
    'UniversalProviderControlTests.test_r2_11_bounded_hashing_and_amplification_r1_red_r2_green': '5d9cc65597e80e99a718829c5b43b024fea0c1c78ac7e7f2e36d94944a77d79a',
    'UniversalProviderControlTests.test_r2_12_dual_platform_hash_locked_workflow_r1_red_r2_green': 'fc4e5b0ca0bfc67bae5a910f56cad1bf11f1dc0cf63debdbe8dc7865969d538f',
    'UniversalProviderControlTests.test_r2_13_candidate_not_ratified_r1_red_r2_green': '8b2533a9f10f3209d3050d8ac877e13caf4858f8bd6f06f925e413c6523d7ce0',
    'UniversalProviderControlTests.test_r2_14_lock_and_rollback_controls_remain_r1_red_r2_green': '52e8c0f862033af826e522d2268bcaee25a06b7a0dc6f6c457a6a32fc76a1c26',
    'UniversalProviderControlTests.test_r3_01_expired_prepared_lease_never_allows_and_remains_fenced': '5630caa0ad2ee9d5c7d4d9c0fb78f3552d8b59a1d0641130e6a2ba8f5ea0935f',
    'UniversalProviderControlTests.test_r3_02_capacity_rollover_blocks_pre_reset_evidence': 'aa15a84c97492632c436310ab3590d00eded2ad3e8c96cad69e2c12a20ea1f61',
    'UniversalProviderControlTests.test_r3_03_capsule_unique_open_and_actual_handle_limits': 'f1bfb0de432ecfcb459a82ef49551bf26ea6a0318753c501ff61f246a38a5d35',
    'UniversalProviderControlTests.test_r3_04_capsule_unexpected_pre_publish_failure_cleans_all': 'be3de10320d5de86c6b39bdac34e3798698021ab54b00d318a3e992ec054cd14',
    'UniversalProviderControlTests.test_r3_05_capacity_estimates_are_broker_derived_not_caller_selected': 'd91152a1214e63d2909bd06bb944c66898ed7bb8dc1eb001fde4a76ae8c911c9',
    'UniversalProviderControlTests.test_r3_06_ambiguous_canary_recovery_reseals_and_malformed_is_stable': '5a158d85141a1a70dbef639b8339832b87692ccb004f86910fbded58946d3fc4',
    'UniversalProviderControlTests.test_r4_01_single_pass_mutation_bytes_match_bound_source_hash': 'db5283c38e04e888fa0cf1ac9a2047c06c0f65446ad7a85e04e4adf7f9aa02e2',
    'UniversalProviderControlTests.test_r4_02_growing_source_reads_fixed_budget_plus_one_probe': 'b15cd8e1989447e8ac2142cb4197766fef44faad971c67bbb35a5862d93d5721',
    'UniversalProviderControlTests.test_r4_03_no_clobber_publication_preserves_foreign_races': 'f6352a5bd3abea89a71958383987194d587a53b73a02309eaeca26ffc5410d29',
    'UniversalProviderControlTests.test_r5_01_publication_binds_retained_temp_identity_and_exact_bytes': 'cd8c27d12832d5f9d663cfefbb02762d956824351b404fb48f94dd01a4b8b6e1',
    'UniversalProviderControlTests.test_r5_02_temp_collision_preserves_foreign_temp_and_reason': 'b773918a52298f48366bedd5cf901ee739434d701a2bd3760c5361161e081f20',
    'UniversalProviderControlTests.test_r5_03_retained_artifact_resume_reads_expected_plus_one_only': 'a4a3d32942ea3c08040bb67e1c6fce8346aeb74a44172a9d15b549c3411b3e01',
    'UniversalProviderControlTests.test_r5_04_sixty_four_hardlink_aliases_use_one_open_hash_pass': 'b275096e55e0b1d490ca2ac9a9d8b521d182d230389293978463dbcec39e92ee',
    'UniversalProviderControlTests.test_r5_05_link_raise_after_real_link_is_verified_success': '1217ede95af9749ef1a0183bc1cbfe72fb2b8250552340305046294e722a0190',
    'UniversalProviderControlTests.test_r6_01_private_temp_replacement_survives_handle_bound_cleanup': 'e03f2bc9380091a70d595f8870e7b856239a32b0921e6f5a73c649dfb4cb1fac',
    'UniversalProviderControlTests.test_r6_02_public_replacement_survives_and_no_path_cleanup_exists': '80665275cfce72c379ae08dd7361ee9b120aa5855d34218788ac075e1157ae2a',
    'UniversalProviderControlTests.test_r6_03_cleanup_refusal_is_surfaced_and_bounds_repetition': '1ee9c03df1ee3fa4ae8aea735e53aa7a8c9ff5bbcbd1d0218b046298f060cabf',
    'UniversalProviderControlTests.test_r7_01_unprivileged_linux_proc_fd_publication': '22dd287ad7c0d22c42ebaa48a0cbdafb463dcedb2b95f1502246d52841936571',
    'UniversalProviderControlTests.test_r7_02_temporary_cleanup_is_required_runtime_evidence': 'a82c5f0bbb7ae1b7ea115cfdafc6a345e14f2b4adac93b0ba4047a4ed56104c6',
    'UniversalProviderControlTests.test_r7_03_cleanup_helper_exception_is_contained_after_publication': '5f63b4fec2588460f3aee08e866f89c7f0acf5be51754c81bf4084b0811bff8f',
    'UniversalProviderControlTests.test_r7_04_cleanup_helper_exception_failure_and_success_are_stable': '7ece26324c48c5accbe0af8d0c035a560b9399293e61f8427726d483ff492406',
    'UniversalProviderControlTests.test_r8_01_primary_failure_has_no_private_exception_topology': 'bdfd922235ffb1d56e41b0d9b22db0d6b890751a8f6fd00a6fca04c311c9f7e2',
    'UniversalProviderControlTests.test_r8_02_cleanup_failure_has_no_private_exception_topology': '37292aaa711e21ed155f90d080769cb88d78524609c84e78e98987e677651bf4',
    'UniversalProviderControlTests.test_r8_03_open_osfhandle_failure_closes_native_owner_once': 'f5ab67f5cb1370fd937c7e73266c45110d705febddd8279af0cc59dcbe60fd54',
    'UniversalProviderControlTests.test_r8_04_fdopen_failure_closes_descriptor_owner_once': '42255f24c9e3158dcbf433e96fef3f5f6a89ac25a5de87abd7aeb3dddf0d95bd',
    'UniversalProviderControlTests.test_r8_05_posix_fdopen_transfer_closes_exact_owner_once': '85a4b171536b39e220a249dcddaeaddc97994a8d8a6483d0725bddfcb998fc85',
    'UniversalProviderControlTests.test_r9_01_preflight_failure_is_fully_sanitized': 'f9a9f246de262ce6b79122669aa87174637a13df961ffc3b9e5cdf486f732591',
    'UniversalProviderControlTests.test_r9_02_unproven_publication_closes_never_report_clean': '7640fd38e6c1d7635b1876fee626b18cc28e6e6d7b56fdf4601fde7497f9e9ce',
    'UniversalProviderControlTests.test_r9_03_finalizer_exception_class_is_sanitized_and_retained': '7e89ff6bf584d9c95d2c09d2cb5f9ed90ed07fc16b3b84734be2556b0e2f69c0',
    'UniversalProviderControlTests.test_r9_04_false_disposition_blocks_native_and_descriptor_failures': '4c38312b768e22c4b23a903a25121803bbf27bca39adbc068078754bd0af32af',
    'UniversalProviderControlTests.test_r9_05_false_closehandle_is_unproven_and_fenced': 'a58e71897cfde243c8e266fc2041440ded264db92c1e9ae4aa7777d73f93745e',
    'UniversalProviderControlTests.test_r9_06_posix_close_refusal_fences_repetition': 'c424a4202053380045bdde53133b8045153f99b47af2145747ea9724b8ae061a',
    'UniversalProviderControlTests.test_r9_07_source_and_artifact_close_refusals_retain_exact_owners': 'f0e6168275393aea2e952f1ec417be031e299635c2a054cbafca7bc728e70975',
})

FROZEN_R43_HISTORICAL_CLASS_SPANS: Mapping[str, str] = MappingProxyType({
    'UniversalProviderControlTests': 'ac8369f4bcd969fd5feb84c55fc1b478dca436efaeae1bbc366e666a7a427764',
    'ReviewResourceAdmissionR29Tests': 'cb216fc94aec1907156513884b795e7695fc4ba266530d750c225086a3371b1a',
})

LAYER_PATH_PATTERN = re.compile(
    r"^manifests/universal-provider-control-reconciliation-r([0-9]+)\.json$"
)
TRACKED_RECONCILIATION_PREFIX = "manifests/universal-provider-control-reconciliation-r"
TRACKED_RECONCILIATION_SUFFIX = ".json"


@dataclass(frozen=True, slots=True)
class ManifestLayerDescriptor:
    manifest_path: str
    candidate: str
    schema: str
    verifier: Callable[[dict[str, Any], str], None]
    report_candidate: str

    @property
    def round(self) -> int:
        match = LAYER_PATH_PATTERN.fullmatch(self.manifest_path)
        if match is None:
            raise ManifestError("MANIFEST_DESCRIPTOR_PATH_INVALID")
        return int(match.group(1))


@dataclass(frozen=True, slots=True)
class ManifestLayerTrustAnchor:
    round: int
    manifest_path: str
    candidate: str
    schema: str
    verifier: Callable[[dict[str, Any], str], None]
    report_candidate: str


@dataclass(frozen=True, slots=True)
class FrozenExecutionBlobAnchor:
    path: str
    oid: str
    sha256: str
    bytes: int


@dataclass(frozen=True, slots=True)
class FrozenHistoricalExecutionReport:
    executed: int
    expected_windows_skips: int
    errors: int
    failures: int
    unexpected_skips: int
    expected_failures: int
    unexpected_successes: int


FROZEN_R43_EXECUTION_BLOB_ANCHORS: Mapping[str, FrozenExecutionBlobAnchor] = (
    MappingProxyType(
        {
            R43_MANIFEST: FrozenExecutionBlobAnchor(
                R43_MANIFEST,
                "04eb2bb92de8ec5bcf5a268f429aa294e8a87128",
                "sha256:40f929ceac009af6b5154765775f59410f2a3133c313e9b8180d0bd76c75ee02",
                10966,
            ),
            "tests/test_universal_provider_control.py": FrozenExecutionBlobAnchor(
                "tests/test_universal_provider_control.py",
                "aa1d1974d9470ad7d554db057807a645730b77be",
                "sha256:2379a4d8931980915e74f0f70db449543d4d528b5f161296eb4792a1ba2b2e22",
                380414,
            ),
            "tools/check_universal_manifest.py": FrozenExecutionBlobAnchor(
                "tools/check_universal_manifest.py",
                "23d3918728c814a82289f5ab171cb5f412461fe1",
                "sha256:cb0e1a89b10b667cf6ddb86aa0de7ddf72d2230290ddd03cef68d0dfa3ab3450",
                117263,
            ),
            "tools/universal_provider_control.py": FrozenExecutionBlobAnchor(
                "tools/universal_provider_control.py",
                "4c9afea1833c6f62820daa893d2125e9beb48ed4",
                "sha256:c24eadc90ba14592d355252c753f8d81a14371d4cd52011657d17d09caea4418",
                308014,
            ),
        }
    )
)
FROZEN_R43_OWNED_TEST_CLASSES = (
    "UniversalProviderControlTests",
    "ReviewResourceAdmissionR29Tests",
)
FROZEN_R43_WINDOWS_SKIPS: Mapping[str, str] = MappingProxyType(
    {
        "UniversalProviderControlTests.test_r8_03_open_osfhandle_failure_closes_native_owner_once":
            "Windows native-handle ownership control",
        "UniversalProviderControlTests.test_r8_04_fdopen_failure_closes_descriptor_owner_once":
            "Windows CRT-descriptor ownership control",
        "UniversalProviderControlTests.test_r9_04_false_disposition_blocks_native_and_descriptor_failures":
            "Windows false-disposition ownership controls",
        "UniversalProviderControlTests.test_r9_05_false_closehandle_is_unproven_and_fenced":
            "Windows false-CloseHandle ownership control",
    }
)
_FROZEN_R43_MODULE_LOCK = threading.RLock()


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            raise ManifestError("DUPLICATE_KEY")
        result[key] = value
    return result


def _git(spec: str, *, text: bool = False) -> bytes | str:
    run = subprocess.run(
        ["git", "show", spec], cwd=ROOT, check=False, capture_output=True,
        text=text, encoding="utf-8" if text else None,
    )
    if run.returncode != 0:
        raise ManifestError("GIT_BLOB_UNAVAILABLE")
    return run.stdout


def _blob_spec(treeish: str, path: str) -> str:
    return f":{path}" if treeish == ":" else f"{treeish}:{path}"


def _oid(treeish: str, path: str) -> str:
    spec = _blob_spec(treeish, path)
    run = subprocess.run(
        ["git", "rev-parse", spec], cwd=ROOT, check=False, capture_output=True, text=True,
        encoding="utf-8",
    )
    if run.returncode != 0 or re.fullmatch(r"[0-9a-f]{40,64}\n?", run.stdout) is None:
        raise ManifestError("GIT_BLOB_OID_UNAVAILABLE")
    return run.stdout.strip()


def _utf8_source_span(raw: bytes, node: ast.AST) -> bytes:
    """Return the exact decorated definition span using UTF-8 byte column offsets."""

    if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ManifestError("R43_HISTORICAL_SOURCE_NODE_INVALID")
    if node.end_lineno is None or node.end_col_offset is None:
        raise ManifestError("R43_HISTORICAL_SOURCE_LOCATION_INVALID")
    lines = raw.splitlines(keepends=True)
    start_line = min(
        (node.lineno, *(decorator.lineno for decorator in node.decorator_list))
    )
    start = sum(len(line) for line in lines[: start_line - 1]) + node.col_offset
    end = sum(len(line) for line in lines[: node.end_lineno - 1]) + node.end_col_offset
    if not (0 <= start < end <= len(raw)):
        raise ManifestError("R43_HISTORICAL_SOURCE_LOCATION_INVALID")
    return raw[start:end]


def _frozen_r43_source_inventory(
    raw: bytes, *, require_exact_classes: bool
) -> tuple[tuple[str, ...], Mapping[str, tuple[int, int]]]:
    """Attest exact historical source spans; this diagnostic never executes input bytes."""

    try:
        source = raw.decode("utf-8", errors="strict")
        module = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ManifestError("R43_HISTORICAL_SOURCE_INVALID") from exc
    owned_nodes = {
        node.name: node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name in FROZEN_R43_OWNED_TEST_CLASSES
    }
    if tuple(name for name in FROZEN_R43_OWNED_TEST_CLASSES if name in owned_nodes) != (
        FROZEN_R43_OWNED_TEST_CLASSES
    ) or len(owned_nodes) != 2:
        raise ManifestError("R43_HISTORICAL_TEST_CLASS_INVALID")
    for class_name, class_node in owned_nodes.items():
        if (
            class_node.decorator_list
            or class_node.keywords
            or len(class_node.bases) != 1
            or not isinstance(class_node.bases[0], ast.Attribute)
            or not isinstance(class_node.bases[0].value, ast.Name)
            or class_node.bases[0].value.id != "unittest"
            or class_node.bases[0].attr != "TestCase"
        ):
            raise ManifestError("R43_HISTORICAL_TEST_CLASS_INVALID")
        if require_exact_classes:
            digest = hashlib.sha256(_utf8_source_span(raw, class_node)).hexdigest()
            if FROZEN_R43_HISTORICAL_CLASS_SPANS.get(class_name) != digest:
                raise ManifestError("R43_HISTORICAL_CLASS_SPAN_MISMATCH")
    spans: dict[str, str] = {}
    locations: dict[str, tuple[int, int]] = {}
    for class_name in FROZEN_R43_OWNED_TEST_CLASSES:
        for node in owned_nodes[class_name].body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            match = re.fullmatch(r"test_r([0-9]+)_.*", node.name)
            if match is None or int(match.group(1)) >= 43:
                continue
            qualified = f"{class_name}.{node.name}"
            spans[qualified] = hashlib.sha256(_utf8_source_span(raw, node)).hexdigest()
            locations[qualified] = (
                min((node.lineno, *(item.lineno for item in node.decorator_list))),
                node.end_lineno or 0,
            )
    if spans != dict(FROZEN_R43_HISTORICAL_FUNCTION_SPANS):
        if set(spans) != set(FROZEN_R43_HISTORICAL_FUNCTION_SPANS):
            raise ManifestError("R43_HISTORICAL_FUNCTION_SET_MISMATCH")
        raise ManifestError("R43_HISTORICAL_FUNCTION_SPAN_MISMATCH")
    if require_exact_classes:
        anchor = FROZEN_R43_EXECUTION_BLOB_ANCHORS[
            "tests/test_universal_provider_control.py"
        ]
        if (
            len(raw) != anchor.bytes
            or "sha256:" + hashlib.sha256(raw).hexdigest() != anchor.sha256
        ):
            raise ManifestError("R43_HISTORICAL_MODULE_BLOB_MISMATCH")
    return tuple(sorted(spans)), MappingProxyType(locations)


def _diagnose_frozen_r43_test_source(raw: bytes) -> None:
    """Non-authoritative mutation diagnostic; it cannot load or execute modules."""

    _frozen_r43_source_inventory(raw, require_exact_classes=True)


def _load_frozen_r43_execution_blobs() -> Mapping[str, bytes]:
    blobs: dict[str, bytes] = {}
    for path, anchor in FROZEN_R43_EXECUTION_BLOB_ANCHORS.items():
        if anchor.path != path or _oid(FROZEN_R43, path) != anchor.oid:
            raise ManifestError("R43_HISTORICAL_BLOB_OID_MISMATCH")
        raw = _git(_blob_spec(FROZEN_R43, path))
        assert isinstance(raw, bytes)
        if (
            len(raw) != anchor.bytes
            or "sha256:" + hashlib.sha256(raw).hexdigest() != anchor.sha256
        ):
            raise ManifestError("R43_HISTORICAL_BLOB_DIGEST_MISMATCH")
        blobs[path] = raw
    manifest_raw = blobs[R43_MANIFEST]
    manifest = _parse_manifest(
        manifest_raw, "fleet-universal-provider-control-candidate-manifest/v3"
    )
    verify_r43(manifest, FROZEN_R43)
    if _verify_subjects_and_self(
        manifest,
        manifest_raw,
        manifest_path=R43_MANIFEST,
        candidate=FROZEN_R43,
    ) != 7:
        raise ManifestError("R43_HISTORICAL_MANIFEST_SUBJECT_COUNT_INVALID")
    _diagnose_frozen_r43_test_source(blobs["tests/test_universal_provider_control.py"])
    return MappingProxyType(blobs)


def _load_exact_source_module(
    name: str, raw: bytes, *, compile_path: Path, initial_file: Path
) -> ModuleType:
    module = ModuleType(name)
    module.__file__ = str(initial_file)
    module.__package__ = ""
    module.__loader__ = None
    sys.modules[name] = module
    try:
        code = compile(raw, str(compile_path), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except Exception as exc:
        raise ManifestError("R43_HISTORICAL_MODULE_LOAD_FAILED") from exc
    module.__file__ = str(compile_path)
    return module


class _FrozenR43HistoricalModules:
    def __init__(
        self,
        test_module: ModuleType,
        checker_module: ModuleType,
        runtime_module: ModuleType,
        test_path: Path,
        locations: Mapping[str, tuple[int, int]],
    ) -> None:
        self.test_module = test_module
        self.checker_module = checker_module
        self.runtime_module = runtime_module
        self.test_path = test_path
        self.locations = locations
        self.historical_names = tuple(FROZEN_R43_HISTORICAL_FUNCTION_SPANS)
        self._bound_methods = {
            qualified: getattr(
                getattr(test_module, qualified.split(".", 1)[0]),
                qualified.split(".", 1)[1],
            )
            for qualified in self.historical_names
        }
        self._unittest_marks = {
            qualified: (
                getattr(bound, "__unittest_skip__", False),
                getattr(bound, "__unittest_skip_why__", None),
                getattr(bound, "__unittest_expecting_failure__", False),
            )
            for qualified, bound in self._bound_methods.items()
        }

    def _assert_graph(self) -> None:
        module = self.test_module
        bound_test_cases: dict[str, type[unittest.TestCase]] = {}
        for name, value in vars(module).items():
            if not inspect.isclass(value) or value is unittest.TestCase:
                continue
            try:
                is_case = issubclass(value, unittest.TestCase)
            except TypeError:
                is_case = False
            if is_case:
                bound_test_cases[name] = value
        if tuple(bound_test_cases) != FROZEN_R43_OWNED_TEST_CLASSES:
            raise ManifestError("R43_HISTORICAL_RUNTIME_CLASS_SET_INVALID")
        if sys.modules.get("universal_provider_control") is not self.runtime_module:
            raise ManifestError("R43_HISTORICAL_RUNTIME_ALIAS_INVALID")
        if sys.modules.get("check_universal_manifest") is not self.checker_module:
            raise ManifestError("R43_HISTORICAL_CHECKER_ALIAS_INVALID")
        for class_name in FROZEN_R43_OWNED_TEST_CLASSES:
            case_type = bound_test_cases[class_name]
            if (
                case_type.__bases__ != (unittest.TestCase,)
                or case_type.__module__ != module.__name__
            ):
                raise ManifestError("R43_HISTORICAL_RUNTIME_CLASS_INVALID")
            direct = {
                name
                for name in case_type.__dict__
                if (match := re.fullmatch(r"test_r([0-9]+)_.*", name)) is not None
                and int(match.group(1)) < 43
            }
            expected = {
                name.split(".", 1)[1]
                for name in self.historical_names
                if name.startswith(class_name + ".")
            }
            if direct != expected:
                raise ManifestError("R43_HISTORICAL_RUNTIME_FUNCTION_SET_INVALID")
            for method_name in expected:
                qualified = f"{class_name}.{method_name}"
                bound = case_type.__dict__[method_name]
                function = inspect.unwrap(bound)
                if (
                    bound is not self._bound_methods[qualified]
                    or (
                        getattr(bound, "__unittest_skip__", False),
                        getattr(bound, "__unittest_skip_why__", None),
                        getattr(bound, "__unittest_expecting_failure__", False),
                    ) != self._unittest_marks[qualified]
                    or
                    not inspect.isfunction(function)
                    or function.__module__ != module.__name__
                    or function.__globals__ is not module.__dict__
                    or function.__qualname__ != qualified
                    or Path(function.__code__.co_filename) != self.test_path
                    or function.__code__.co_firstlineno != self.locations[qualified][0]
                ):
                    raise ManifestError("R43_HISTORICAL_RUNTIME_FUNCTION_INVALID")

    def execute_all(self) -> FrozenHistoricalExecutionReport:
        self._assert_graph()
        executed = 0
        expected_windows_skips = 0
        for qualified in self.historical_names:
            class_name, method_name = qualified.split(".", 1)
            self._assert_graph()
            results: list[unittest.TestResult] = []
            real_unittest = self.test_module.unittest

            class ResultCapturingUnittest:
                def __getattr__(_self, name: str) -> Any:
                    return getattr(real_unittest, name)

                @staticmethod
                def TestResult() -> unittest.TestResult:
                    result = unittest.TestResult()
                    results.append(result)
                    return result

            self.test_module.unittest = ResultCapturingUnittest()
            try:
                self.test_module._run_historical_case_under_quarantine(
                    getattr(self.test_module, class_name), method_name
                )
            except Exception as exc:
                raise ManifestError(
                    f"R43_HISTORICAL_EXECUTION_FAILED:{qualified}:{type(exc).__name__}"
                ) from exc
            finally:
                self.test_module.unittest = real_unittest
            if len(results) != 1 or results[0].testsRun != 1:
                raise ManifestError("R43_HISTORICAL_RESULT_ACCOUNTING_INVALID")
            result = results[0]
            if result.errors or result.failures:
                raise ManifestError("R43_HISTORICAL_RESULT_FAILURE")
            if result.expectedFailures or result.unexpectedSuccesses:
                raise ManifestError("R43_HISTORICAL_RESULT_EXPECTATION_INVALID")
            if result.skipped:
                if len(result.skipped) != 1:
                    raise ManifestError("R43_HISTORICAL_RESULT_SKIP_INVALID")
                reason = result.skipped[0][1]
                if (
                    os.name == "nt"
                    or FROZEN_R43_WINDOWS_SKIPS.get(qualified) != reason
                ):
                    raise ManifestError("R43_HISTORICAL_RESULT_SKIP_INVALID")
                expected_windows_skips += 1
            else:
                executed += 1
            self._assert_graph()
        expected = (184, 0) if os.name == "nt" else (180, 4)
        if (executed, expected_windows_skips) != expected:
            raise ManifestError("R43_HISTORICAL_RESULT_TOTAL_INVALID")
        return FrozenHistoricalExecutionReport(
            executed=executed,
            expected_windows_skips=expected_windows_skips,
            errors=0,
            failures=0,
            unexpected_skips=0,
            expected_failures=0,
            unexpected_successes=0,
        )


@contextlib.contextmanager
def _open_frozen_r43_historical_modules() -> Any:
    """Select and isolate exact R43 provenance; this is not a Python sandbox."""

    with _FROZEN_R43_MODULE_LOCK:
        blobs = _load_frozen_r43_execution_blobs()
        _names = (
            "universal_provider_control",
            "check_universal_manifest",
            "test_universal_provider_control",
            "tests.test_universal_provider_control",
            "_fleet_frozen_r43_runtime",
            "_fleet_frozen_r43_checker",
            "_fleet_frozen_r43_tests",
        )
        saved_modules = {name: sys.modules.get(name) for name in _names}
        saved_path = list(sys.path)
        saved_dont_write = sys.dont_write_bytecode
        saved_linecache = dict(linecache.cache)
        with tempfile.TemporaryDirectory(prefix="fleet-r43-history-") as temp_name:
            temp = Path(temp_name)
            runtime_path = temp / "tools" / "universal_provider_control.py"
            checker_path = temp / "tools" / "check_universal_manifest.py"
            test_path = temp / "tests" / "test_universal_provider_control.py"
            runtime_path.parent.mkdir(parents=True)
            test_path.parent.mkdir(parents=True)
            runtime_path.write_bytes(blobs["tools/universal_provider_control.py"])
            checker_path.write_bytes(blobs["tools/check_universal_manifest.py"])
            test_path.write_bytes(blobs["tests/test_universal_provider_control.py"])
            try:
                sys.dont_write_bytecode = True
                runtime_module = _load_exact_source_module(
                    "_fleet_frozen_r43_runtime",
                    blobs["tools/universal_provider_control.py"],
                    compile_path=runtime_path,
                    initial_file=ROOT / "tools" / "universal_provider_control.py",
                )
                sys.modules["universal_provider_control"] = runtime_module
                checker_module = _load_exact_source_module(
                    "_fleet_frozen_r43_checker",
                    blobs["tools/check_universal_manifest.py"],
                    compile_path=checker_path,
                    initial_file=ROOT / "tools" / "check_universal_manifest.py",
                )
                sys.modules["check_universal_manifest"] = checker_module
                test_module = _load_exact_source_module(
                    "_fleet_frozen_r43_tests",
                    blobs["tests/test_universal_provider_control.py"],
                    compile_path=test_path,
                    initial_file=ROOT / "tests" / "test_universal_provider_control.py",
                )
                sys.modules["test_universal_provider_control"] = test_module
                sys.modules["tests.test_universal_provider_control"] = test_module
                historical_names, locations = _frozen_r43_source_inventory(
                    blobs["tests/test_universal_provider_control.py"],
                    require_exact_classes=True,
                )
                opened = _FrozenR43HistoricalModules(
                    test_module, checker_module, runtime_module, test_path, locations
                )
                if opened.historical_names != historical_names:
                    raise ManifestError("R43_HISTORICAL_FUNCTION_ORDER_INVALID")
                opened._assert_graph()
                yield opened
                opened._assert_graph()
            finally:
                sys.path[:] = saved_path
                sys.dont_write_bytecode = saved_dont_write
                linecache.cache.clear()
                linecache.cache.update(saved_linecache)
                for name, previous in saved_modules.items():
                    if previous is None:
                        sys.modules.pop(name, None)
                    else:
                        sys.modules[name] = previous


def _verify_current_historical_source_spans(treeish: str) -> None:
    raw = _git(_blob_spec(treeish, "tests/test_universal_provider_control.py"))
    assert isinstance(raw, bytes)
    _frozen_r43_source_inventory(raw, require_exact_classes=False)


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    run = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT,
        check=False, capture_output=True,
    )
    if run.returncode not in (0, 1):
        raise ManifestError("MANIFEST_ANCESTRY_UNAVAILABLE")
    return run.returncode == 0


def _frozen_manifest_bytes(
    treeish: str,
    manifest_path: str = R26_MANIFEST,
    candidate: str = FROZEN_CANDIDATE,
) -> bytes:
    """Bind a checked descendant to one literal immutable candidate manifest."""

    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(candidate, descendant):
        raise ManifestError("MANIFEST_CANDIDATE_NOT_ANCESTOR")
    frozen = _git(_blob_spec(candidate, manifest_path))
    current = _git(_blob_spec(treeish, manifest_path))
    assert isinstance(frozen, bytes)
    assert isinstance(current, bytes)
    if current != frozen or _oid(treeish, manifest_path) != _oid(candidate, manifest_path):
        raise ManifestError("MANIFEST_FROZEN_BLOB_MISMATCH")
    return frozen


def _commit_tuple(commit: str) -> tuple[str, list[str]]:
    run = subprocess.run(
        ["git", "show", "-s", "--format=%T%n%P", commit], cwd=ROOT,
        check=False, capture_output=True, text=True, encoding="utf-8",
    )
    if run.returncode != 0:
        raise ManifestError("RECONCILIATION_OBJECT_UNAVAILABLE")
    lines = run.stdout.splitlines()
    if len(lines) != 2 or re.fullmatch(r"[0-9a-f]{40,64}", lines[0]) is None:
        raise ManifestError("RECONCILIATION_OBJECT_INVALID")
    parents = lines[1].split() if lines[1] else []
    if any(re.fullmatch(r"[0-9a-f]{40,64}", parent) is None for parent in parents):
        raise ManifestError("RECONCILIATION_OBJECT_INVALID")
    return lines[0], parents


def verify_reconciliation(manifest: dict[str, Any], treeish: str = "HEAD") -> None:
    """Verify the exact R15-R26 linear subjects and ordered canonical-master merges."""

    reconciliation = manifest.get("reconciliation")
    if not isinstance(reconciliation, dict):
        raise ManifestError("RECONCILIATION_INVALID")
    base_names = (
        "r15Base", "r16PreMaster", "r16FrozenBeforeLatestMaster",
        "canonicalFleetMaster", "r16MasterMerge",
    )
    r17_names = ("r16Final", "r17Wip", "r17CanonicalMaster", "r17MasterMerge")
    r18_names = ("r17ManifestFreeze", "r17Final", "r18Wip")
    r19_names = (
        "r18Final", "r19Wip", "r19Evidence", "r19CanonicalMaster", "r19MasterMerge",
    )
    r20_names = ("r19Final", "r20Wip", "r20Evidence")
    r21_names = ("r20Final", "r21Wip", "r21Evidence", "r21Doctrine")
    r22_names = (
        "r21Final", "r22Wip", "r22CanonicalMaster", "r22MasterMerge", "r22Evidence",
        "r22ManifestFreeze", "r22Repair",
    )
    r23_names = ("r22Final", "r23Wip", "r23Evidence")
    r24_names = ("r23Final", "r24Wip", "r24Evidence")
    r25_names = (
        "r24Final", "r25Wip", "r25CanonicalMaster", "r25MasterMerge", "r25Evidence",
        "r25FinalPreLatestMaster", "r25LatestCanonicalMaster",
        "r25LatestMasterMerge", "r25LatestEvidence",
    )
    r26_names = ("r25Final", "r26Evidence")
    if all(name in reconciliation for name in r26_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names + r25_names + r26_names
        )
    elif all(name in reconciliation for name in r25_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names + r25_names
        )
    elif all(name in reconciliation for name in r24_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names + r24_names
        )
    elif all(name in reconciliation for name in r23_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names + r23_names
        )
    elif all(name in reconciliation for name in r22_names):
        names = (
            base_names + r17_names + r18_names + r19_names + r20_names
            + r21_names + r22_names
        )
    elif all(name in reconciliation for name in r21_names):
        names = base_names + r17_names + r18_names + r19_names + r20_names + r21_names
    elif all(name in reconciliation for name in r20_names):
        names = base_names + r17_names + r18_names + r19_names + r20_names
    elif all(name in reconciliation for name in r19_names):
        names = base_names + r17_names + r18_names + r19_names
    elif all(name in reconciliation for name in r18_names):
        names = base_names + r17_names + r18_names
    elif all(name in reconciliation for name in r17_names):
        names = base_names + r17_names
    else:
        names = base_names
    if set(reconciliation) != set(names):
        raise ManifestError("RECONCILIATION_INVALID")
    for name in names:
        record = reconciliation.get(name)
        if not isinstance(record, dict) or set(record) != {
            "commit", "tree", "orderedParents", "orderedParentTrees"
        }:
            raise ManifestError("RECONCILIATION_INVALID")
        tree, parents = _commit_tuple(record["commit"])
        if tree != record["tree"] or parents != record["orderedParents"]:
            raise ManifestError("RECONCILIATION_COMMIT_MISMATCH")
        if len(parents) != len(record["orderedParentTrees"]):
            raise ManifestError("RECONCILIATION_PARENT_TREE_MISMATCH")
        actual_parent_trees = [_commit_tuple(parent)[0] for parent in parents]
        if actual_parent_trees != record["orderedParentTrees"]:
            raise ManifestError("RECONCILIATION_PARENT_TREE_MISMATCH")
    r15 = reconciliation["r15Base"]
    pre_master = reconciliation["r16PreMaster"]
    frozen = reconciliation["r16FrozenBeforeLatestMaster"]
    canonical = reconciliation["canonicalFleetMaster"]
    merged = reconciliation["r16MasterMerge"]
    if (
        pre_master["orderedParents"] != [r15["commit"]]
        or frozen["orderedParents"] != ["a0786f2eee16770632a2a947f65db64e60dd9820"]
        or merged["orderedParents"] != [frozen["commit"], canonical["commit"]]
    ):
        raise ManifestError("RECONCILIATION_ORDER_INVALID")
    terminal = merged
    if all(name in reconciliation for name in r17_names):
        r16_final = reconciliation["r16Final"]
        r17_wip = reconciliation["r17Wip"]
        r17_master = reconciliation["r17CanonicalMaster"]
        r17_merge = reconciliation["r17MasterMerge"]
        if (
            r16_final["orderedParents"] != [merged["commit"]]
            or r17_wip["orderedParents"] != [r16_final["commit"]]
            or r17_merge["orderedParents"] != [r17_wip["commit"], r17_master["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r17_merge
    if all(name in reconciliation for name in r18_names):
        r17_freeze = reconciliation["r17ManifestFreeze"]
        r17_final = reconciliation["r17Final"]
        r18_wip = reconciliation["r18Wip"]
        if (
            r17_freeze["orderedParents"] != [terminal["commit"]]
            or r17_final["orderedParents"] != [r17_freeze["commit"]]
            or r18_wip["orderedParents"] != [r17_final["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r18_wip
    if all(name in reconciliation for name in r19_names):
        r18_final = reconciliation["r18Final"]
        r19_wip = reconciliation["r19Wip"]
        r19_evidence = reconciliation["r19Evidence"]
        r19_master = reconciliation["r19CanonicalMaster"]
        r19_merge = reconciliation["r19MasterMerge"]
        if (
            r18_final["orderedParents"] != [terminal["commit"]]
            or r19_wip["orderedParents"] != [r18_final["commit"]]
            or r19_evidence["orderedParents"] != [r19_wip["commit"]]
            or r19_merge["orderedParents"]
            != [r19_evidence["commit"], r19_master["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r19_merge
    if all(name in reconciliation for name in r20_names):
        r19_final = reconciliation["r19Final"]
        r20_wip = reconciliation["r20Wip"]
        r20_evidence = reconciliation["r20Evidence"]
        if (
            r19_final["orderedParents"] != [terminal["commit"]]
            or r20_wip["orderedParents"] != [r19_final["commit"]]
            or r20_evidence["orderedParents"] != [r20_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r20_evidence
    if all(name in reconciliation for name in r21_names):
        r20_final = reconciliation["r20Final"]
        r21_wip = reconciliation["r21Wip"]
        r21_evidence = reconciliation["r21Evidence"]
        r21_doctrine = reconciliation["r21Doctrine"]
        if (
            r20_final["orderedParents"] != [terminal["commit"]]
            or r21_wip["orderedParents"] != [r20_final["commit"]]
            or r21_evidence["orderedParents"] != [r21_wip["commit"]]
            or r21_doctrine["orderedParents"] != [r21_evidence["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r21_doctrine
    if all(name in reconciliation for name in r22_names):
        r21_final = reconciliation["r21Final"]
        r22_wip = reconciliation["r22Wip"]
        r22_master = reconciliation["r22CanonicalMaster"]
        r22_merge = reconciliation["r22MasterMerge"]
        r22_evidence = reconciliation["r22Evidence"]
        r22_manifest_freeze = reconciliation["r22ManifestFreeze"]
        r22_repair = reconciliation["r22Repair"]
        if (
            r21_final["orderedParents"] != [terminal["commit"]]
            or r22_wip["orderedParents"] != [r21_final["commit"]]
            or r22_merge["orderedParents"] != [r22_wip["commit"], r22_master["commit"]]
            or r22_evidence["orderedParents"] != [r22_merge["commit"]]
            or r22_manifest_freeze["orderedParents"] != [r22_evidence["commit"]]
            or r22_repair["orderedParents"] != [r22_manifest_freeze["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r22_repair
    if all(name in reconciliation for name in r23_names):
        r22_final = reconciliation["r22Final"]
        r23_wip = reconciliation["r23Wip"]
        r23_evidence = reconciliation["r23Evidence"]
        if (
            r22_final["orderedParents"] != [terminal["commit"]]
            or r23_wip["orderedParents"] != [r22_final["commit"]]
            or r23_evidence["orderedParents"] != [r23_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r23_evidence
    if all(name in reconciliation for name in r24_names):
        r23_final = reconciliation["r23Final"]
        r24_wip = reconciliation["r24Wip"]
        r24_evidence = reconciliation["r24Evidence"]
        if (
            r23_final["orderedParents"] != [terminal["commit"]]
            or r24_wip["orderedParents"] != [r23_final["commit"]]
            or r24_evidence["orderedParents"] != [r24_wip["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r24_evidence
    if all(name in reconciliation for name in r25_names):
        r24_final = reconciliation["r24Final"]
        r25_wip = reconciliation["r25Wip"]
        r25_master = reconciliation["r25CanonicalMaster"]
        r25_merge = reconciliation["r25MasterMerge"]
        r25_evidence = reconciliation["r25Evidence"]
        r25_final_pre_latest = reconciliation["r25FinalPreLatestMaster"]
        r25_latest_master = reconciliation["r25LatestCanonicalMaster"]
        r25_latest_merge = reconciliation["r25LatestMasterMerge"]
        r25_latest_evidence = reconciliation["r25LatestEvidence"]
        if (
            r24_final["orderedParents"] != [terminal["commit"]]
            or r25_wip["orderedParents"] != [r24_final["commit"]]
            or r25_merge["orderedParents"] != [r25_wip["commit"], r25_master["commit"]]
            or r25_evidence["orderedParents"] != [r25_merge["commit"]]
            or r25_final_pre_latest["orderedParents"] != [r25_evidence["commit"]]
            or r25_latest_merge["orderedParents"]
            != [r25_final_pre_latest["commit"], r25_latest_master["commit"]]
            or r25_latest_evidence["orderedParents"] != [r25_latest_merge["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r25_latest_evidence
    if all(name in reconciliation for name in r26_names):
        r25_final = reconciliation["r25Final"]
        r26_evidence = reconciliation["r26Evidence"]
        if (
            r25_final["orderedParents"] != [terminal["commit"]]
            or r26_evidence["orderedParents"] != [r25_final["commit"]]
        ):
            raise ManifestError("RECONCILIATION_ORDER_INVALID")
        terminal = r26_evidence
    if treeish != ":":
        run = subprocess.run(
            ["git", "merge-base", "--is-ancestor", terminal["commit"], treeish],
            cwd=ROOT, check=False, capture_output=True,
        )
        if run.returncode != 0:
            raise ManifestError("RECONCILIATION_NOT_ANCESTOR")


def canonical_self_sha256(raw: bytes) -> str:
    """Return the zeroed-field self digest over canonical Git blob bytes only."""

    matches = list(SELF_PATTERN.finditer(raw))
    if len(matches) != 1:
        raise ManifestError("MANIFEST_SELF_INVALID")
    zeroed = SELF_PATTERN.sub(lambda match: match.group(1) + b"0" * 64 + match.group(3), raw)
    return "sha256:" + hashlib.sha256(zeroed).hexdigest()


def canonical_policy_sha256(policy: dict[str, Any]) -> str:
    raw = (
        json.dumps(
            policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        + b"\n"
    )
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def verify_r33(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the literal integration base and exact current R33 policy instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R33_CANONICAL_R31_R32_INTEGRATION_ZERO_AUTHORITY"
    ):
        raise ManifestError("R33_STATUS_INVALID")
    if manifest.get("candidateBase") != R33_BASE:
        raise ManifestError("R33_BASE_INVALID")
    tree, parents = _commit_tuple(R33_BASE["commit"])
    if tree != R33_BASE["tree"] or parents != R33_BASE["orderedParents"]:
        raise ManifestError("R33_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R33_BASE["orderedParentTrees"]:
        raise ManifestError("R33_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R33_BASE["commit"], descendant):
        raise ManifestError("R33_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R33_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R33_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R33_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R33_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R29_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R29_POLICY_DIGEST
    ):
        raise ManifestError("R33_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R33_SUBJECT_PATHS
    ):
        raise ManifestError("R33_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(FROZEN_R33, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R33_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R33_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R33_VALIDATION_AUTHORITY_INVALID")


def verify_r34(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the literal phase6-16 integration base and exact current R34 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R34_CACHE_ADMISSION_CAPABILITY_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R34_STATUS_INVALID")
    if manifest.get("candidateBase") != R34_BASE:
        raise ManifestError("R34_BASE_INVALID")
    tree, parents = _commit_tuple(R34_BASE["commit"])
    if tree != R34_BASE["tree"] or parents != R34_BASE["orderedParents"]:
        raise ManifestError("R34_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R34_BASE["orderedParentTrees"]:
        raise ManifestError("R34_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R34_BASE["commit"], descendant):
        raise ManifestError("R34_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R34_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R34_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R34_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R34_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R34_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R34_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R34_POLICY_DIGEST
    ):
        raise ManifestError("R34_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R34_SUBJECT_PATHS
    ):
        raise ManifestError("R34_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R34_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R34_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R34_VALIDATION_AUTHORITY_INVALID")


def verify_r35(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the repaired-canonical integration base and exact current R35 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R35_CANONICAL_CI_INTEGRATION_REBIND_ZERO_AUTHORITY"
    ):
        raise ManifestError("R35_STATUS_INVALID")
    if manifest.get("candidateBase") != R35_BASE:
        raise ManifestError("R35_BASE_INVALID")
    tree, parents = _commit_tuple(R35_BASE["commit"])
    if tree != R35_BASE["tree"] or parents != R35_BASE["orderedParents"]:
        raise ManifestError("R35_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R35_BASE["orderedParentTrees"]:
        raise ManifestError("R35_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R35_BASE["commit"], descendant):
        raise ManifestError("R35_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R35_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R35_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R35_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R35_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R35_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R35_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R35_POLICY_DIGEST
    ):
        raise ManifestError("R35_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R35_SUBJECT_PATHS
    ):
        raise ManifestError("R35_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R35_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R35_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R35_VALIDATION_AUTHORITY_INVALID")


def verify_r36(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact R35 base and the current integer-boundary R36 instance."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R36_EXACT_REVIEW_CAPACITY_ARITHMETIC_ZERO_AUTHORITY"
    ):
        raise ManifestError("R36_STATUS_INVALID")
    if manifest.get("candidateBase") != R36_BASE:
        raise ManifestError("R36_BASE_INVALID")
    tree, parents = _commit_tuple(R36_BASE["commit"])
    if tree != R36_BASE["tree"] or parents != R36_BASE["orderedParents"]:
        raise ManifestError("R36_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R36_BASE["orderedParentTrees"]:
        raise ManifestError("R36_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R36_BASE["commit"], descendant):
        raise ManifestError("R36_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R36_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R36_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R36_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R36_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R36_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R36_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R36_POLICY_DIGEST
    ):
        raise ManifestError("R36_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R36_SUBJECT_PATHS
    ):
        raise ManifestError("R36_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R36_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R36_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R36_VALIDATION_AUTHORITY_INVALID")


def verify_r37(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R36 base and the current frozen-layer R37 rebind."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R37_FROZEN_R36_FULL_MATRIX_REBIND_ZERO_AUTHORITY"
    ):
        raise ManifestError("R37_STATUS_INVALID")
    if manifest.get("candidateBase") != R37_BASE:
        raise ManifestError("R37_BASE_INVALID")
    tree, parents = _commit_tuple(R37_BASE["commit"])
    if tree != R37_BASE["tree"] or parents != R37_BASE["orderedParents"]:
        raise ManifestError("R37_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R37_BASE["orderedParentTrees"]:
        raise ManifestError("R37_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R37_BASE["commit"], descendant):
        raise ManifestError("R37_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R37_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R37_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R37_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R37_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R37_QUOTA_WINDOWS_MISMATCH")
    if (
        manifest.get("reviewAdmissionPolicyDigest") != R37_POLICY_DIGEST
        or canonical_policy_sha256(policy) != R37_POLICY_DIGEST
    ):
        raise ManifestError("R37_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if (
        not isinstance(subjects, list)
        or [subject.get("path") for subject in subjects if isinstance(subject, dict)]
        != R37_SUBJECT_PATHS
    ):
        raise ManifestError("R37_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R37_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R37_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R37_VALIDATION_AUTHORITY_INVALID")


def verify_r38(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R37 base and the lifecycle-safe R38 rebind."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R38_FROZEN_LAYER_LIFECYCLE_REBIND_ZERO_AUTHORITY":
        raise ManifestError("R38_STATUS_INVALID")
    if manifest.get("candidateBase") != R38_BASE:
        raise ManifestError("R38_BASE_INVALID")
    tree, parents = _commit_tuple(R38_BASE["commit"])
    if tree != R38_BASE["tree"] or parents != R38_BASE["orderedParents"]:
        raise ManifestError("R38_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R38_BASE["orderedParentTrees"]:
        raise ManifestError("R38_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R38_BASE["commit"], descendant):
        raise ManifestError("R38_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R38_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R38_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R38_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R38_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R38_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R38_POLICY_DIGEST or canonical_policy_sha256(
        policy
    ) != R38_POLICY_DIGEST:
        raise ManifestError("R38_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [
        subject.get("path") for subject in subjects if isinstance(subject, dict)
    ] != R38_SUBJECT_PATHS:
        raise ManifestError("R38_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R38_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R38_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R38_VALIDATION_AUTHORITY_INVALID")


def verify_r39(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R38 base and the lifecycle-safe R39 rebind."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R39_CURRENT_CHECKER_LIFECYCLE_REBIND_ZERO_AUTHORITY":
        raise ManifestError("R39_STATUS_INVALID")
    if manifest.get("candidateBase") != R39_BASE:
        raise ManifestError("R39_BASE_INVALID")
    tree, parents = _commit_tuple(R39_BASE["commit"])
    if tree != R39_BASE["tree"] or parents != R39_BASE["orderedParents"]:
        raise ManifestError("R39_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R39_BASE["orderedParentTrees"]:
        raise ManifestError("R39_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R39_BASE["commit"], descendant):
        raise ManifestError("R39_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R39_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R39_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R39_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R39_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R39_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R39_POLICY_DIGEST or canonical_policy_sha256(
        policy
    ) != R39_POLICY_DIGEST:
        raise ManifestError("R39_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [
        subject.get("path") for subject in subjects if isinstance(subject, dict)
    ] != R39_SUBJECT_PATHS:
        raise ManifestError("R39_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R39_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R39_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R39_VALIDATION_AUTHORITY_INVALID")



def verify_r40(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R39 base and the closed-descriptor R40 rebind."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R40_CLOSED_LAYER_DESCRIPTOR_REBIND_ZERO_AUTHORITY":
        raise ManifestError("R40_STATUS_INVALID")
    if manifest.get("candidateBase") != R40_BASE:
        raise ManifestError("R40_BASE_INVALID")
    tree, parents = _commit_tuple(R40_BASE["commit"])
    if tree != R40_BASE["tree"] or parents != R40_BASE["orderedParents"]:
        raise ManifestError("R40_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R40_BASE["orderedParentTrees"]:
        raise ManifestError("R40_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R40_BASE["commit"], descendant):
        raise ManifestError("R40_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R40_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R40_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R40_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R40_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R40_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R40_POLICY_DIGEST or canonical_policy_sha256(
        policy
    ) != R40_POLICY_DIGEST:
        raise ManifestError("R40_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [
        subject.get("path") for subject in subjects if isinstance(subject, dict)
    ] != R40_SUBJECT_PATHS:
        raise ManifestError("R40_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R40_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R40_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R40_VALIDATION_AUTHORITY_INVALID")


def verify_r41(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R40 base and independently anchored R41 descriptors."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R41_INDEPENDENT_LAYER_TRUST_ANCHORS_ZERO_AUTHORITY":
        raise ManifestError("R41_STATUS_INVALID")
    if manifest.get("candidateBase") != R41_BASE:
        raise ManifestError("R41_BASE_INVALID")
    tree, parents = _commit_tuple(R41_BASE["commit"])
    if tree != R41_BASE["tree"] or parents != R41_BASE["orderedParents"]:
        raise ManifestError("R41_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R41_BASE["orderedParentTrees"]:
        raise ManifestError("R41_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R41_BASE["commit"], descendant):
        raise ManifestError("R41_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R41_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R41_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R41_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R41_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R41_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R41_POLICY_DIGEST or canonical_policy_sha256(
        policy
    ) != R41_POLICY_DIGEST:
        raise ManifestError("R41_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [
        subject.get("path") for subject in subjects if isinstance(subject, dict)
    ] != R41_SUBJECT_PATHS:
        raise ManifestError("R41_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R41_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R41_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R41_VALIDATION_AUTHORITY_INVALID")


def verify_r42(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R41 base and successor-safe R42 test ownership."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R42_SUCCESSOR_SAFE_TEST_OWNERSHIP_ZERO_AUTHORITY":
        raise ManifestError("R42_STATUS_INVALID")
    if manifest.get("candidateBase") != R42_BASE:
        raise ManifestError("R42_BASE_INVALID")
    tree, parents = _commit_tuple(R42_BASE["commit"])
    if tree != R42_BASE["tree"] or parents != R42_BASE["orderedParents"]:
        raise ManifestError("R42_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R42_BASE["orderedParentTrees"]:
        raise ManifestError("R42_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R42_BASE["commit"], descendant):
        raise ManifestError("R42_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R42_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R42_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R42_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R42_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R42_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R42_POLICY_DIGEST or canonical_policy_sha256(policy) != R42_POLICY_DIGEST:
        raise ManifestError("R42_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [subject.get("path") for subject in subjects if isinstance(subject, dict)] != R42_SUBJECT_PATHS:
        raise ManifestError("R42_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R42_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R42_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R42_VALIDATION_AUTHORITY_INVALID")


def verify_r43(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R42 base and complete historical-test quarantine."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R43_HISTORICAL_TEST_QUARANTINE_ZERO_AUTHORITY":
        raise ManifestError("R43_STATUS_INVALID")
    if manifest.get("candidateBase") != R43_BASE:
        raise ManifestError("R43_BASE_INVALID")
    tree, parents = _commit_tuple(R43_BASE["commit"])
    if tree != R43_BASE["tree"] or parents != R43_BASE["orderedParents"]:
        raise ManifestError("R43_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R43_BASE["orderedParentTrees"]:
        raise ManifestError("R43_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R43_BASE["commit"], descendant):
        raise ManifestError("R43_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R43_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R43_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R43_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R43_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R43_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R43_POLICY_DIGEST or canonical_policy_sha256(policy) != R43_POLICY_DIGEST:
        raise ManifestError("R43_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [subject.get("path") for subject in subjects if isinstance(subject, dict)] != R43_SUBJECT_PATHS:
        raise ManifestError("R43_CARRIER_SUBJECT_MISMATCH")
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R43_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R43_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R43_VALIDATION_AUTHORITY_INVALID")


def verify_r44(manifest: dict[str, Any], treeish: str) -> None:
    """Verify exact adverse R43 base and literal-source historical execution binding."""

    if manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY" or manifest.get(
        "subjectCoverage"
    ) != "R44_LITERAL_FROZEN_HISTORY_EXECUTION_ZERO_AUTHORITY":
        raise ManifestError("R44_STATUS_INVALID")
    if manifest.get("candidateBase") != R44_BASE:
        raise ManifestError("R44_BASE_INVALID")
    tree, parents = _commit_tuple(R44_BASE["commit"])
    if tree != R44_BASE["tree"] or parents != R44_BASE["orderedParents"]:
        raise ManifestError("R44_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R44_BASE["orderedParentTrees"]:
        raise ManifestError("R44_BASE_PARENT_TREE_MISMATCH")
    descendant = "HEAD" if treeish == ":" else treeish
    if not _is_ancestor(R44_BASE["commit"], descendant):
        raise ManifestError("R44_BASE_NOT_ANCESTOR")
    if manifest.get("authority") != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R44_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R44_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R44_EXACT_PROFILE_MISMATCH")
    if policy.get("cacheAdmissionMode") != "EXACTLY_BOUNDED_AND_CHARGED":
        raise ManifestError("R44_CACHE_ADMISSION_MODE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R44_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != R44_POLICY_DIGEST or canonical_policy_sha256(policy) != R44_POLICY_DIGEST:
        raise ManifestError("R44_POLICY_DIGEST_MISMATCH")
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or [subject.get("path") for subject in subjects if isinstance(subject, dict)] != R44_SUBJECT_PATHS:
        raise ManifestError("R44_CARRIER_SUBJECT_MISMATCH")
    _verify_current_historical_source_spans(treeish)
    try:
        import jsonschema
        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R44_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R44_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False, "activation": False,
    }:
        raise ManifestError("R44_VALIDATION_AUTHORITY_INVALID")


def verify_r29(
    manifest: dict[str, Any], treeish: str, *, verify_objects: bool = True
) -> None:
    """Verify R29 base, exact seven-row instance, generic schema, and zero authority."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R29_GENERIC_SUBJECT_CARDINALITY_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R29_STATUS_INVALID")
    if manifest.get("candidateBase") != R29_BASE:
        raise ManifestError("R29_BASE_INVALID")
    if verify_objects:
        tree, parents = _commit_tuple(R29_BASE["commit"])
        if tree != R29_BASE["tree"] or parents != R29_BASE["orderedParents"]:
            raise ManifestError("R29_BASE_OBJECT_MISMATCH")
        if [_commit_tuple(parent)[0] for parent in parents] != R29_BASE["orderedParentTrees"]:
            raise ManifestError("R29_BASE_PARENT_TREE_MISMATCH")
        if treeish != ":":
            run = subprocess.run(
                ["git", "merge-base", "--is-ancestor", R29_BASE["commit"], treeish],
                cwd=ROOT, check=False, capture_output=True,
            )
            if run.returncode != 0:
                raise ManifestError("R29_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R29_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R29_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R29_IDENTITY:
        raise ManifestError("R29_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R29_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != canonical_policy_sha256(policy):
        raise ManifestError("R29_POLICY_DIGEST_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(FROZEN_R29, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R29_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R29_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R29_VALIDATION_AUTHORITY_INVALID")


def verify_r28(
    manifest: dict[str, Any], treeish: str, *, verify_objects: bool = True
) -> None:
    """Verify R28 base, exact external instance, canonical policy digest, and zero authority."""

    if (
        manifest.get("status") != "CANDIDATE_ZERO_AUTHORITY"
        or manifest.get("subjectCoverage")
        != "R28_PROVIDER_NEUTRAL_REVIEW_ADMISSION_REPAIR_ZERO_AUTHORITY"
    ):
        raise ManifestError("R28_STATUS_INVALID")
    if manifest.get("candidateBase") != R28_BASE:
        raise ManifestError("R28_BASE_INVALID")
    if verify_objects:
        tree, parents = _commit_tuple(R28_BASE["commit"])
        if tree != R28_BASE["tree"] or parents != R28_BASE["orderedParents"]:
            raise ManifestError("R28_BASE_OBJECT_MISMATCH")
        if [_commit_tuple(parent)[0] for parent in parents] != R28_BASE["orderedParentTrees"]:
            raise ManifestError("R28_BASE_PARENT_TREE_MISMATCH")
        if treeish != ":":
            run = subprocess.run(
                ["git", "merge-base", "--is-ancestor", R28_BASE["commit"], treeish],
                cwd=ROOT, check=False, capture_output=True,
            )
            if run.returncode != 0:
                raise ManifestError("R28_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R28_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R28_SOURCE_SUBJECT_MISMATCH")
    if policy.get("identity") != R28_IDENTITY:
        raise ManifestError("R28_EXACT_PROFILE_MISMATCH")
    if policy.get("capacity", {}).get("requiredQuotaWindows") != ["session", "weekly"]:
        raise ManifestError("R28_QUOTA_WINDOWS_MISMATCH")
    if manifest.get("reviewAdmissionPolicyDigest") != canonical_policy_sha256(policy):
        raise ManifestError("R28_POLICY_DIGEST_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R28_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError("R28_POLICY_SCHEMA_INVALID") from exc
    if manifest.get("validation") != {
        "universalProviderControl": {"required": True, "claimedGreen": False},
        "providerCapacityGovernor": {"required": True, "claimedGreen": False},
        "canonicalCapacityControl": {"required": True, "claimedGreen": False},
        "hosted": {"requiredFresh": True, "claimedGreen": False},
        "providerInvocation": False,
        "activation": False,
    }:
        raise ManifestError("R28_VALIDATION_AUTHORITY_INVALID")


def verify_r27(manifest: dict[str, Any], treeish: str) -> None:
    """Verify the exact doctrine base, external R5 subject, strict policy, and zero authority."""

    if manifest.get("candidateBase") != R27_BASE:
        raise ManifestError("R27_BASE_INVALID")
    tree, parents = _commit_tuple(R27_BASE["commit"])
    if tree != R27_BASE["tree"] or parents != R27_BASE["orderedParents"]:
        raise ManifestError("R27_BASE_OBJECT_MISMATCH")
    if [_commit_tuple(parent)[0] for parent in parents] != R27_BASE["orderedParentTrees"]:
        raise ManifestError("R27_BASE_PARENT_TREE_MISMATCH")
    if treeish != ":":
        run = subprocess.run(
            ["git", "merge-base", "--is-ancestor", R27_BASE["commit"], treeish],
            cwd=ROOT, check=False, capture_output=True,
        )
        if run.returncode != 0:
            raise ManifestError("R27_BASE_NOT_ANCESTOR")
    authority = manifest.get("authority")
    if authority != {
        "providerExecution": False, "processSpawnResumeKill": False,
        "containmentOrCanaryCredit": False, "automaticGateState": "CLOSED",
        "runtimeImplementation": "NOT_INSTALLED_UNCONDITIONAL_REFUSE",
        "activationRequiresSeparateAdjudication": True, "authorRecused": True,
    }:
        raise ManifestError("R27_AUTHORITY_INVALID")
    policy = manifest.get("reviewAdmissionPolicy")
    if not isinstance(policy, dict) or policy.get("source") != R27_SOURCE:
        raise ManifestError("R27_SOURCE_SUBJECT_MISMATCH")
    try:
        import jsonschema

        schema_raw = _git(_blob_spec(treeish, REVIEW_SCHEMA))
        assert isinstance(schema_raw, bytes)
        schema = json.loads(schema_raw.decode("utf-8"), object_pairs_hook=_pairs)
        jsonschema.Draft202012Validator.check_schema(schema)
        if next(jsonschema.Draft202012Validator(schema).iter_errors(policy), None) is not None:
            raise ManifestError("R27_POLICY_SCHEMA_INVALID")
    except ManifestError:
        raise
    except (ImportError, UnicodeDecodeError, json.JSONDecodeError, Exception) as exc:
        raise ManifestError("R27_POLICY_SCHEMA_INVALID") from exc
    validation = manifest.get("validation")
    if not isinstance(validation, dict) or validation.get("providerInvocation") is not False:
        raise ManifestError("R27_VALIDATION_AUTHORITY_INVALID")
    if validation.get("activation") is not False or validation.get("hosted", {}).get("claimedGreen") is not False:
        raise ManifestError("R27_VALIDATION_AUTHORITY_INVALID")


def _parse_manifest(raw: bytes, expected_schema: str) -> dict[str, Any]:
    try:
        manifest = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ManifestError) as exc:
        raise ManifestError("MANIFEST_INVALID") from exc
    if manifest.get("schema") != expected_schema:
        raise ManifestError("MANIFEST_SCHEMA_INVALID")
    return manifest


def _verify_subjects_and_self(
    manifest: dict[str, Any], raw: bytes, *, manifest_path: str, candidate: str
) -> int:
    subjects = manifest.get("subjectFiles")
    if not isinstance(subjects, list) or not subjects:
        raise ManifestError("MANIFEST_SUBJECTS_INVALID")
    seen: set[str] = set()
    for subject in subjects:
        if not isinstance(subject, dict) or set(subject) != {"path", "gitBlobOid", "sha256", "bytes"}:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        path = subject["path"]
        if not isinstance(path, str) or path in seen or path == manifest_path:
            raise ManifestError("MANIFEST_SUBJECT_INVALID")
        seen.add(path)
        blob = _git(_blob_spec(candidate, path))
        assert isinstance(blob, bytes)
        expected_sha = "sha256:" + hashlib.sha256(blob).hexdigest()
        if subject["sha256"] != expected_sha or subject["bytes"] != len(blob):
            raise ManifestError("MANIFEST_SUBJECT_MISMATCH")
        if subject["gitBlobOid"] != _oid(candidate, path):
            raise ManifestError("MANIFEST_BLOB_OID_MISMATCH")
    self_binding = manifest.get("manifestSelf")
    if not isinstance(self_binding, dict) or self_binding.get("path") != manifest_path:
        raise ManifestError("MANIFEST_SELF_INVALID")
    if self_binding.get("bytes") != len(raw):
        raise ManifestError("MANIFEST_SELF_SIZE_MISMATCH")
    expected_self = canonical_self_sha256(raw)
    if self_binding.get("canonicalGitBlobSha256") != expected_self:
        raise ManifestError("MANIFEST_SELF_MISMATCH")
    return len(subjects)


LAYER_DESCRIPTORS = (
    ManifestLayerDescriptor(
        R26_MANIFEST, FROZEN_CANDIDATE,
        "fleet-universal-provider-control-candidate-manifest/v2",
        verify_reconciliation, FROZEN_CANDIDATE,
    ),
    ManifestLayerDescriptor(R29_MANIFEST, FROZEN_R29, "fleet-universal-provider-control-candidate-manifest/v3", verify_r29, FROZEN_R29),
    ManifestLayerDescriptor(R33_MANIFEST, FROZEN_R33, "fleet-universal-provider-control-candidate-manifest/v3", verify_r33, FROZEN_R33),
    ManifestLayerDescriptor(R34_MANIFEST, FROZEN_R34, "fleet-universal-provider-control-candidate-manifest/v3", verify_r34, FROZEN_R34),
    ManifestLayerDescriptor(R35_MANIFEST, FROZEN_R35, "fleet-universal-provider-control-candidate-manifest/v3", verify_r35, FROZEN_R35),
    ManifestLayerDescriptor(R36_MANIFEST, FROZEN_R36, "fleet-universal-provider-control-candidate-manifest/v3", verify_r36, FROZEN_R36),
    ManifestLayerDescriptor(R37_MANIFEST, FROZEN_R37, "fleet-universal-provider-control-candidate-manifest/v3", verify_r37, FROZEN_R37),
    ManifestLayerDescriptor(R38_MANIFEST, FROZEN_R38, "fleet-universal-provider-control-candidate-manifest/v3", verify_r38, FROZEN_R38),
    ManifestLayerDescriptor(R39_MANIFEST, FROZEN_R39, "fleet-universal-provider-control-candidate-manifest/v3", verify_r39, FROZEN_R39),
    ManifestLayerDescriptor(R40_MANIFEST, FROZEN_R40, "fleet-universal-provider-control-candidate-manifest/v3", verify_r40, FROZEN_R40),
    ManifestLayerDescriptor(R41_MANIFEST, FROZEN_R41, "fleet-universal-provider-control-candidate-manifest/v3", verify_r41, FROZEN_R41),
    ManifestLayerDescriptor(R42_MANIFEST, FROZEN_R42, "fleet-universal-provider-control-candidate-manifest/v3", verify_r42, FROZEN_R42),
    ManifestLayerDescriptor(R43_MANIFEST, FROZEN_R43, "fleet-universal-provider-control-candidate-manifest/v3", verify_r43, FROZEN_R43),
    ManifestLayerDescriptor(R44_MANIFEST, CURRENT_CANDIDATE, "fleet-universal-provider-control-candidate-manifest/v3", verify_r44, R44_BASE["commit"]),
)


LAYER_TRUST_ANCHORS: Mapping[str, ManifestLayerTrustAnchor] = MappingProxyType(
    {
        R26_MANIFEST: ManifestLayerTrustAnchor(26, R26_MANIFEST, FROZEN_CANDIDATE, "fleet-universal-provider-control-candidate-manifest/v2", verify_reconciliation, FROZEN_CANDIDATE),
        R29_MANIFEST: ManifestLayerTrustAnchor(29, R29_MANIFEST, FROZEN_R29, "fleet-universal-provider-control-candidate-manifest/v3", verify_r29, FROZEN_R29),
        R33_MANIFEST: ManifestLayerTrustAnchor(33, R33_MANIFEST, FROZEN_R33, "fleet-universal-provider-control-candidate-manifest/v3", verify_r33, FROZEN_R33),
        R34_MANIFEST: ManifestLayerTrustAnchor(34, R34_MANIFEST, FROZEN_R34, "fleet-universal-provider-control-candidate-manifest/v3", verify_r34, FROZEN_R34),
        R35_MANIFEST: ManifestLayerTrustAnchor(35, R35_MANIFEST, FROZEN_R35, "fleet-universal-provider-control-candidate-manifest/v3", verify_r35, FROZEN_R35),
        R36_MANIFEST: ManifestLayerTrustAnchor(36, R36_MANIFEST, FROZEN_R36, "fleet-universal-provider-control-candidate-manifest/v3", verify_r36, FROZEN_R36),
        R37_MANIFEST: ManifestLayerTrustAnchor(37, R37_MANIFEST, FROZEN_R37, "fleet-universal-provider-control-candidate-manifest/v3", verify_r37, FROZEN_R37),
        R38_MANIFEST: ManifestLayerTrustAnchor(38, R38_MANIFEST, FROZEN_R38, "fleet-universal-provider-control-candidate-manifest/v3", verify_r38, FROZEN_R38),
        R39_MANIFEST: ManifestLayerTrustAnchor(39, R39_MANIFEST, FROZEN_R39, "fleet-universal-provider-control-candidate-manifest/v3", verify_r39, FROZEN_R39),
        R40_MANIFEST: ManifestLayerTrustAnchor(40, R40_MANIFEST, FROZEN_R40, "fleet-universal-provider-control-candidate-manifest/v3", verify_r40, FROZEN_R40),
        R41_MANIFEST: ManifestLayerTrustAnchor(41, R41_MANIFEST, FROZEN_R41, "fleet-universal-provider-control-candidate-manifest/v3", verify_r41, FROZEN_R41),
        R42_MANIFEST: ManifestLayerTrustAnchor(42, R42_MANIFEST, FROZEN_R42, "fleet-universal-provider-control-candidate-manifest/v3", verify_r42, FROZEN_R42),
        R43_MANIFEST: ManifestLayerTrustAnchor(43, R43_MANIFEST, FROZEN_R43, "fleet-universal-provider-control-candidate-manifest/v3", verify_r43, FROZEN_R43),
        R44_MANIFEST: ManifestLayerTrustAnchor(44, R44_MANIFEST, CURRENT_CANDIDATE, "fleet-universal-provider-control-candidate-manifest/v3", verify_r44, R44_BASE["commit"]),
    }
)


def _tracked_reconciliation_paths(treeish: str) -> tuple[str, ...]:
    if treeish == CURRENT_CANDIDATE:
        args = ["git", "ls-files", "--", "manifests"]
    else:
        args = ["git", "ls-tree", "-r", "--name-only", treeish, "--", "manifests"]
    run = subprocess.run(args, cwd=ROOT, check=False, capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        raise ManifestError("MANIFEST_DESCRIPTOR_TRACKING_INVALID")
    paths = tuple(
        line
        for line in run.stdout.splitlines()
        if line.startswith(TRACKED_RECONCILIATION_PREFIX)
        and line.endswith(TRACKED_RECONCILIATION_SUFFIX)
    )
    if not paths or len(paths) != len(set(paths)):
        raise ManifestError("MANIFEST_DESCRIPTOR_TRACKING_INVALID")
    return paths


FROZEN_R43_RECONCILIATION_PATHS = _tracked_reconciliation_paths(FROZEN_R43)
EXPECTED_CURRENT_RECONCILIATION_PATHS = tuple(
    sorted(FROZEN_R43_RECONCILIATION_PATHS + (R44_MANIFEST,))
)


def _diagnose_layer_configuration(
    descriptors: tuple[ManifestLayerDescriptor, ...],
    trust_anchors: Mapping[str, ManifestLayerTrustAnchor],
) -> None:
    """Non-authoritative structural diagnostic; never loads, verifies, reports, or returns receipts."""

    if type(descriptors) is not tuple or not descriptors:
        raise ManifestError("MANIFEST_DESCRIPTOR_SET_INVALID")
    if any(type(descriptor) is not ManifestLayerDescriptor for descriptor in descriptors):
        raise ManifestError("MANIFEST_DESCRIPTOR_SET_INVALID")
    try:
        rounds = tuple(descriptor.round for descriptor in descriptors)
    except ManifestError:
        raise
    if rounds != EXPECTED_LAYER_ROUNDS:
        raise ManifestError("MANIFEST_DESCRIPTOR_SEQUENCE_INVALID")
    paths = tuple(descriptor.manifest_path for descriptor in descriptors)
    if len(set(paths)) != len(paths) or tuple(trust_anchors) != paths:
        raise ManifestError("MANIFEST_DESCRIPTOR_PATH_INVALID")
    current = tuple(
        index for index, descriptor in enumerate(descriptors)
        if descriptor.candidate == CURRENT_CANDIDATE
    )
    if current != (len(descriptors) - 1,):
        raise ManifestError("MANIFEST_DESCRIPTOR_CURRENT_INVALID")
    for descriptor in descriptors:
        anchor = trust_anchors.get(descriptor.manifest_path)
        if type(anchor) is not ManifestLayerTrustAnchor:
            raise ManifestError("MANIFEST_DESCRIPTOR_ANCHOR_INVALID")
        if anchor.round != descriptor.round:
            raise ManifestError("MANIFEST_DESCRIPTOR_SEQUENCE_INVALID")
        if anchor.manifest_path != descriptor.manifest_path:
            raise ManifestError("MANIFEST_DESCRIPTOR_PATH_INVALID")
        if anchor.candidate != descriptor.candidate:
            raise ManifestError("MANIFEST_DESCRIPTOR_CANDIDATE_INVALID")
        if anchor.schema != descriptor.schema:
            raise ManifestError("MANIFEST_DESCRIPTOR_SCHEMA_INVALID")
        if not callable(descriptor.verifier) or anchor.verifier is not descriptor.verifier:
            raise ManifestError("MANIFEST_DESCRIPTOR_VERIFIER_INVALID")
        if anchor.report_candidate != descriptor.report_candidate:
            raise ManifestError("MANIFEST_DESCRIPTOR_REPORT_INVALID")
        expected_schema = (
            "fleet-universal-provider-control-candidate-manifest/v2"
            if descriptor.round == 26
            else "fleet-universal-provider-control-candidate-manifest/v3"
        )
        if descriptor.schema != expected_schema:
            raise ManifestError("MANIFEST_DESCRIPTOR_SCHEMA_INVALID")
        if descriptor.candidate == CURRENT_CANDIDATE:
            if descriptor.report_candidate != R44_BASE["commit"]:
                raise ManifestError("MANIFEST_DESCRIPTOR_REPORT_INVALID")
        elif (
            re.fullmatch(r"[0-9a-f]{40}", descriptor.candidate) is None
            or descriptor.report_candidate != descriptor.candidate
        ):
            raise ManifestError("MANIFEST_DESCRIPTOR_CANDIDATE_INVALID")


def _validate_layer_descriptors(treeish: str) -> None:
    _diagnose_layer_configuration(LAYER_DESCRIPTORS, LAYER_TRUST_ANCHORS)
    frozen_paths = _tracked_reconciliation_paths(FROZEN_R43)
    if frozen_paths != FROZEN_R43_RECONCILIATION_PATHS:
        raise ManifestError("MANIFEST_DESCRIPTOR_TRACKING_INVALID")
    tracked_paths = _tracked_reconciliation_paths(treeish)
    if tracked_paths != EXPECTED_CURRENT_RECONCILIATION_PATHS:
        raise ManifestError("MANIFEST_DESCRIPTOR_TRACKING_INVALID")


def _execute_manifest_layers(treeish: str) -> tuple[dict[str, Any], ...]:
    _validate_layer_descriptors(treeish)
    receipts: list[dict[str, Any]] = []
    for descriptor in LAYER_DESCRIPTORS:
        subject_candidate = (
            treeish if descriptor.candidate == CURRENT_CANDIDATE else descriptor.candidate
        )
        if descriptor.candidate == CURRENT_CANDIDATE:
            raw = _git(_blob_spec(treeish, descriptor.manifest_path))
        else:
            raw = _frozen_manifest_bytes(treeish, descriptor.manifest_path, descriptor.candidate)
        assert isinstance(raw, bytes)
        manifest = _parse_manifest(raw, descriptor.schema)
        descriptor.verifier(manifest, subject_candidate)
        subjects = _verify_subjects_and_self(
            manifest,
            raw,
            manifest_path=descriptor.manifest_path,
            candidate=subject_candidate,
        )
        receipts.append(
            {
                "path": descriptor.manifest_path,
                "round": descriptor.round,
                "candidate": descriptor.candidate,
                "subjectCandidate": subject_candidate,
                "verifier": descriptor.verifier,
                "subjects": subjects,
                "reportCandidate": descriptor.report_candidate,
            }
        )
    return tuple(receipts)


def check(treeish: str) -> int:
    receipts = _execute_manifest_layers(treeish)
    count_report = " ".join(
        f"r{receipt['round']}_subjects={receipt['subjects']}" for receipt in receipts
    )
    candidates = ",".join(receipt["reportCandidate"] for receipt in receipts)
    print(f"MANIFEST_PASS {count_report} self=PASS candidates={candidates} checked={treeish}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    args = parser.parse_args()
    try:
        return check(args.treeish)
    except ManifestError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
