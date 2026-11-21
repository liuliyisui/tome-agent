"""The package migration only accepts reviewed whole-version fingerprints."""

import copy
import unittest
from unittest.mock import patch

from check_memory import _migration_manifest, reviewed_package_sources, source_hashes


class PackageMigrationTests(unittest.TestCase):
    def test_profile_restores_prior_layout_and_rejects_tampering(self):
        manifest = _migration_manifest()
        actual = source_hashes()
        # The migration profile describes a historical reviewed target, not
        # the newer writer. Keep testing the pinned pair without approving the
        # newer runtime for automatic migration.
        current = {
            name.replace("src/@package/", "src/tome_writer/"): values["new"][0]
            for name, values in manifest["sources"].items()
        }
        profile = manifest["profiles"][0]["sources"]
        previous = {}
        for name, values in profile.items():
            # Old package path names are taken from the checkpoint; only the
            # layout of the package segment matters to the verifier.
            key = name.replace("src/@package/", "src/previous_package/")
            previous[key] = values[0]
        self.assertTrue(reviewed_package_sources(previous, current))
        self.assertFalse(reviewed_package_sources(previous, actual))
        changed = copy.deepcopy(previous)
        changed["writing.py"] = "0" * 64
        self.assertFalse(reviewed_package_sources(changed, current))
        changed = copy.deepcopy(current)
        changed["writing.py"] = "0" * 64
        self.assertFalse(reviewed_package_sources(previous, changed))
        with patch("check_memory._MIGRATION_MANIFEST_SHA256", "0" * 64):
            self.assertFalse(reviewed_package_sources(previous, current))
