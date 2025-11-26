#!/usr/bin/env bash
# Configure Windows portproxy to forward localhost ports to WSL IP.
# Requires running from WSL with administrative rights on Windows.

set -euo pipefail

WSL_IP=$(hostname -I | awk '{print $1}')
# Port mappings: space-separated LISTEN:TARGET (default map same port)
MAPPINGS=("${@:-5050:5050 8001:8001 3001:3001}")

echo "WSL IP detected: ${WSL_IP}"
echo "Configuring portproxy rules:"
for m in "${MAPPINGS[@]}"; do
  LISTEN=${m%%:*}
  TARGET=${m##*:}
  echo "  127.0.0.1:${LISTEN} -> ${WSL_IP}:${TARGET}"
done

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "powershell.exe not available. Run the commands manually on Windows:"
  for m in "${MAPPINGS[@]}"; do
    LISTEN=${m%%:*}; TARGET=${m##*:}
    echo "  netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=${LISTEN} connectaddress=${WSL_IP} connectport=${TARGET}"
  done
  exit 1
fi

for m in "${MAPPINGS[@]}"; do
  LISTEN=${m%%:*}; TARGET=${m##*:}
  powershell.exe -Command "Start-Process powershell -Verb runAs -ArgumentList 'netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=${LISTEN} connectaddress=${WSL_IP} connectport=${TARGET}'"
done

echo "Done. Verify from Windows PowerShell:"
echo "  netsh interface portproxy show all"
echo "  curl http://localhost:5050/health   # MLflow"
echo "  curl http://localhost:8001/health   # Backend"
