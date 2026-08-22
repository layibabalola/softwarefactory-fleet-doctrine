import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "universal-production-wrapper-boundary-certification-v1.schema.json"


class ProductionBoundarySchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"), object_pairs_hook=self._strict_pairs)

    @staticmethod
    def _strict_pairs(pairs):
        result = {}
        folded = set()
        for key, value in pairs:
            if key in result or key.casefold() in folded:
                raise ValueError("duplicate or case-colliding key")
            result[key] = value
            folded.add(key.casefold())
        return result

    def test_schema_is_closed_and_production_positive(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(self.schema["additionalProperties"])
        properties = self.schema["properties"]
        self.assertEqual(
            properties["schema"]["const"],
            "fleet-universal-production-wrapper-boundary-certification/v1",
        )
        self.assertEqual(properties["requestBoundaryMode"]["const"], "SINGLE_REQUEST_PROCESS")
        self.assertEqual(properties["brokerPermitCommand"]["const"], "brokered-single-request")
        for name in (
            "processServiceChokePoint",
            "directInvocationImpossible",
            "rawProviderEntrypointsStructurallyUnavailable",
            "exactArgvRequired",
            "singleUsePermitRequired",
            "processTreeTerminationRequired",
        ):
            self.assertIs(properties[name]["const"], True)
        self.assertIs(properties["fleetSecretsInheritedByProvider"]["const"], False)
        self.assertIs(properties["observerSecretsInheritedByProvider"]["const"], False)

    def test_every_property_is_required_and_digest_patterns_are_strict(self):
        properties = self.schema["properties"]
        self.assertEqual(set(self.schema["required"]), set(properties))
        digest_fields = [name for name in properties if name.endswith("Sha256") and name != "certificationHmacSha256"]
        self.assertGreaterEqual(len(digest_fields), 9)
        for name in digest_fields:
            pattern = properties[name]["pattern"]
            self.assertIsNotNone(re.fullmatch(pattern, "sha256:" + "a" * 64), name)
            self.assertIsNone(re.fullmatch(pattern, "sha256:" + "A" * 64), name)
            self.assertIsNone(re.fullmatch(pattern, "sha256:" + "a" * 63), name)
        hmac_pattern = properties["certificationHmacSha256"]["pattern"]
        self.assertIsNotNone(re.fullmatch(hmac_pattern, "hmac-sha256:" + "b" * 64))
        self.assertIsNone(re.fullmatch(hmac_pattern, "sha256:" + "b" * 64))

    def test_reference_only_v1_remains_distinct_and_unchanged_in_meaning(self):
        reference = json.loads(
            (ROOT / "schemas" / "universal-wrapper-boundary-certification-v1.schema.json").read_text(encoding="utf-8")
        )
        properties = reference["properties"]
        self.assertEqual(properties["brokerPermitCommand"]["const"], "reference-only-no-execution")
        self.assertIs(properties["directInvocationImpossible"]["const"], False)
        self.assertNotEqual(reference["$id"], self.schema["$id"])


if __name__ == "__main__":
    unittest.main()
