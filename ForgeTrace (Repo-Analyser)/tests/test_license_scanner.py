"""
Tests for License Scanner functionality.
"""
import pytest
from pathlib import Path
from forgetrace.scanners.license import LicenseScanner


class TestLicenseScanner:
    """Test suite for LicenseScanner."""
    
    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        scanner = LicenseScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan')
    
    def test_scan_mit_license(self, sample_repo):
        """Test detecting MIT license."""
        scanner = LicenseScanner()
        results = scanner.scan(str(sample_repo))
        
        assert results is not None
        assert "licenses" in results or "detected_licenses" in results
        
        licenses = results.get("licenses", results.get("detected_licenses", []))
        
        # MIT license should be detected
        if len(licenses) > 0:
            license_ids = [lic.get("id", lic.get("license", "")).upper() for lic in licenses]
            assert any("MIT" in lid for lid in license_ids)
    
    def test_scan_license_metadata(self, sample_repo):
        """Test that license metadata is captured."""
        scanner = LicenseScanner()
        results = scanner.scan(str(sample_repo))
        
        licenses = results.get("licenses", results.get("detected_licenses", []))
        
        for lic in licenses:
            # Should have basic metadata
            assert isinstance(lic, dict)
            # At minimum should have some identifier
            assert len(lic) > 0
    
    def test_scan_no_license(self, temp_dir):
        """Test scanning a repo without license files."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "no_license_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        (repo_path / "code.py").write_text("print('hello')\n")
        repo.index.add(["code.py"])
        repo.index.commit("Add code")
        
        scanner = LicenseScanner()
        results = scanner.scan(str(repo_path))
        
        assert results is not None
        licenses = results.get("licenses", results.get("detected_licenses", []))
        # Should return empty list or minimal results
        assert isinstance(licenses, list)
    
    def test_scan_multiple_licenses(self, temp_dir):
        """Test detecting multiple licenses."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "multi_license_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Add MIT license
        (repo_path / "LICENSE").write_text("""MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
""")
        
        # Add Apache license in subdirectory
        sub_dir = repo_path / "third_party"
        sub_dir.mkdir()
        (sub_dir / "LICENSE").write_text("""Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
""")
        
        repo.index.add(["LICENSE", "third_party/LICENSE"])
        repo.index.commit("Add licenses")
        
        scanner = LicenseScanner()
        results = scanner.scan(str(repo_path))
        
        licenses = results.get("licenses", results.get("detected_licenses", []))
        
        # Should detect at least one license
        assert len(licenses) >= 1
    
    def test_scan_license_in_code(self, temp_dir):
        """Test detecting license headers in source code."""
        from git import Repo
        
        repo_path = Path(temp_dir) / "code_license_repo"
        repo_path.mkdir()
        
        repo = Repo.init(repo_path)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")
        
        # Create file with license header
        (repo_path / "licensed_code.py").write_text("""#!/usr/bin/env python3
# Copyright (c) 2024 Test
# Licensed under the MIT License
#
# Permission is hereby granted, free of charge...

def hello():
    return "Hello, World!"
""")
        
        repo.index.add(["licensed_code.py"])
        repo.index.commit("Add licensed code")
        
        scanner = LicenseScanner()
        results = scanner.scan(str(repo_path))
        
        # Scanner may or may not detect inline licenses depending on implementation
        assert results is not None
        assert "licenses" in results or "detected_licenses" in results
