#!/usr/bin/env bash
# ==============================================================================
# Sovereign Practice Vault - Read-Only Network Share Mounting Script
# Purpose: Mounts practice documents over CIFS/SMB in strict read-only mode (ro).
# Invariants: The appliance cannot alter, write to, or delete master records.
# ==============================================================================

set -euo pipefail

SHARE_HOST="${1:-192.168.1.50}"
SHARE_NAME="${2:-practice_archive}"
MOUNT_POINT="${3:-/opt/practice-vault/data/network_shares}"
CREDENTIALS_FILE="${4:-/etc/practice-vault/smbcredentials}"

echo ">>> Initialising safe read-only share mount for: //${SHARE_HOST}/${SHARE_NAME}"

sudo mkdir -p "${MOUNT_POINT}"

if mountpoint -q "${MOUNT_POINT}"; then
  echo ">>> Target mountpoint already active: ${MOUNT_POINT}"
  exit 0
fi

if [[ -f "${CREDENTIALS_FILE}" ]]; then
  echo ">>> Mounting with credentials file: ${CREDENTIALS_FILE}"
  sudo mount -t cifs "//${SHARE_HOST}/${SHARE_NAME}" "${MOUNT_POINT}" \
    -o credentials="${CREDENTIALS_FILE}",ro,iocharset=utf8,vers=3.0,file_mode=0444,dir_mode=0555
else
  echo ">>> Mounting in guest read-only mode..."
  sudo mount -t cifs "//${SHARE_HOST}/${SHARE_NAME}" "${MOUNT_POINT}" \
    -o guest,ro,iocharset=utf8,vers=3.0,file_mode=0444,dir_mode=0555
fi

echo ">>> Share mounted successfully in strict read-only mode at: ${MOUNT_POINT}"
