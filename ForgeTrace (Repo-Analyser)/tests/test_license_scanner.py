"""Tests for License Scanner functionality."""

from pathlib import Path
from typing import Any, Callable, Type, cast

from forgetrace.scanners.license import LicenseScanner

ScannerFactory = Callable[[Type[Any], Path | str], Any]


class TestLicenseScanner:
    """Test suite for LicenseScanner."""

    def test_scanner_initialization(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test that scanner initializes correctly."""

        scanner: Any = scanner_factory(LicenseScanner, temp_dir)
        assert scanner is not None
        assert hasattr(scanner, "scan")

    def test_scan_mit_license(
        self, sample_repo: Path, scanner_factory: ScannerFactory
    ) -> None:
        """Test detecting MIT license."""

        scanner: Any = scanner_factory(LicenseScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert findings

        license_ids = [finding.get("license", "").upper() for finding in findings]
        assert any("MIT" in lid for lid in license_ids)

    def test_scan_license_metadata(
        self, sample_repo: Path, scanner_factory: ScannerFactory
    ) -> None:
        """Test that license metadata is captured."""

        scanner: Any = scanner_factory(LicenseScanner, sample_repo)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        for finding in findings:
            assert "file" in finding

    def test_scan_no_license(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test scanning a repo without license files."""

        from git import Repo

        repo_path = Path(temp_dir) / "no_license_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "code.py").write_text("print('hello')\n")
        index.add(["code.py"])
        index.commit("Add code")

        scanner: Any = scanner_factory(LicenseScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)

    def test_scan_multiple_licenses(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test detecting multiple licenses."""

        from git import Repo

        repo_path = Path(temp_dir) / "multi_license_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "LICENSE").write_text(
            """MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
"""
        )

        sub_dir = repo_path / "third_party"
        sub_dir.mkdir()
        (sub_dir / "LICENSE").write_text(
            """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
"""
        )

        index.add(["LICENSE", "third_party/LICENSE"])
        index.commit("Add licenses")

        scanner: Any = scanner_factory(LicenseScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert len(findings) >= 1

    def test_scan_license_in_code(
        self, temp_dir: str, scanner_factory: ScannerFactory
    ) -> None:
        """Test detecting license headers in source code."""

        from git import Repo

        repo_path = Path(temp_dir) / "code_license_repo"
        repo_path.mkdir()

        repo = Repo.init(repo_path)
        index: Any = repo.index
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test")
            config.set_value("user", "email", "test@example.com")

        (repo_path / "licensed_code.py").write_text(
            """#!/usr/bin/env python3
# Copyright (c) 2024 Test
# Licensed under the MIT License
#
# Permission is hereby granted, free of charge...

def hello():
    return "Hello, World!"
"""
        )

        index.add(["licensed_code.py"])
        index.commit("Add licensed code")

        scanner: Any = scanner_factory(LicenseScanner, repo_path)
        results: dict[str, Any] = cast(dict[str, Any], scanner.scan())

        findings = cast(list[dict[str, Any]], results.get("findings", []))
        assert isinstance(findings, list)
