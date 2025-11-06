#!/bin/bash
# ForgeTrace Tool Installation Script
# Author: Peter Kolawole, BAMG Studio LLC

set -e

echo "=== ForgeTrace Tool Installer ==="
echo "Installing optional external tools..."
echo ""

# Syft (SBOM)
if ! command -v syft &> /dev/null; then
    echo "Installing Syft..."
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
else
    echo "✓ Syft already installed"
fi

# ScanCode Toolkit
if ! command -v scancode &> /dev/null; then
    echo "Installing ScanCode Toolkit..."
    pip install scancode-toolkit
else
    echo "✓ ScanCode already installed"
fi

# Semgrep
if ! command -v semgrep &> /dev/null; then
    echo "Installing Semgrep..."
    pip install semgrep
else
    echo "✓ Semgrep already installed"
fi

# TruffleHog
if ! command -v trufflehog &> /dev/null; then
    echo "Installing TruffleHog..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -sSfL https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_linux_amd64.tar.gz | tar -xz -C /usr/local/bin trufflehog
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install trufflehog
    fi
else
    echo "✓ TruffleHog already installed"
fi

# Gitleaks
if ! command -v gitleaks &> /dev/null; then
    echo "Installing Gitleaks..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gitleaks
    fi
else
    echo "✓ Gitleaks already installed"
fi

# jscpd (copy-paste detector)
if ! command -v jscpd &> /dev/null; then
    echo "Installing jscpd..."
    npm install -g jscpd
else
    echo "✓ jscpd already installed"
fi

echo ""
echo "=== Installation Complete ==="
echo "Run 'forgetrace audit /path/to/repo' to start auditing"
