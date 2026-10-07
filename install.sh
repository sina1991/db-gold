#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/root/xauusd_data_layer"
REPOSITORY_URL="https://github.com/sina1991/db-gold.git"
BRANCH="master"
PYTHON_BIN="python3"
VENV_DIR="${PROJECT_DIR}/.venv"

API_SERVICE="xauusd-data-layer-api.service"
COLLECTOR_SERVICE="xauusd-data-layer-collector.service"

echo "==> Installing XAUUSD Data Layer"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: install.sh must be run as root."
    exit 1
fi

if [ ! -f /etc/os-release ]; then
    echo "ERROR: Cannot detect operating system."
    exit 1
fi

. /etc/os-release

if [ "${ID}" = "ubuntu" ] || [ "${ID_LIKE:-}" = "debian" ]; then
    echo "==> Checking system packages"

    export DEBIAN_FRONTEND=noninteractive

    apt-get update
    apt-get install -y \
        git \
        python3 \
        python3-venv \
        curl
else
    echo "ERROR: Unsupported operating system: ${ID}"
    exit 1
fi

if [ ! -d "${PROJECT_DIR}/.git" ]; then
    echo "==> Cloning repository"
    rm -rf "${PROJECT_DIR}"
    git clone --branch "${BRANCH}" "${REPOSITORY_URL}" "${PROJECT_DIR}"
else
    echo "==> Updating repository"
    git -C "${PROJECT_DIR}" fetch origin "${BRANCH}"
    git -C "${PROJECT_DIR}" reset --hard "origin/${BRANCH}"
fi

cd "${PROJECT_DIR}"

echo "==> Creating virtual environment"
if [ ! -x "${VENV_DIR}/bin/python" ]; then
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

echo "==> Installing Python dependencies"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/pip" install -r requirements.txt

echo "==> Initializing database"
"${VENV_DIR}/bin/python" -c "from app.database import initialize; initialize()"

echo "==> Installing systemd services"
install -m 0644 \
    "${PROJECT_DIR}/systemd/${API_SERVICE}" \
    "/etc/systemd/system/${API_SERVICE}"

install -m 0644 \
    "${PROJECT_DIR}/systemd/${COLLECTOR_SERVICE}" \
    "/etc/systemd/system/${COLLECTOR_SERVICE}"

echo "==> Reloading systemd"
systemctl daemon-reload

echo "==> Enabling and starting services"
systemctl enable --now "${API_SERVICE}"
systemctl enable --now "${COLLECTOR_SERVICE}"

echo "==> Verifying services"
systemctl is-active --quiet "${API_SERVICE}"
systemctl is-active --quiet "${COLLECTOR_SERVICE}"

echo "==> API health check"
curl -fsS http://127.0.0.1:8000/health
echo

echo "==> Data pipeline check"
"${VENV_DIR}/bin/python" - <<'PYTHON'
import time

from app.database import get_latest_candle

candle = get_latest_candle()

if candle is None:
    raise SystemExit("ERROR: No candle found in SQLite.")

age = int(time.time()) - int(candle["time"])

print(
    f"Latest candle: time={candle['time']} "
    f"close={candle['close']} age={age}s"
)

if age < 0:
    raise SystemExit("ERROR: Latest candle timestamp is in the future.")

if age > 120:
    raise SystemExit(
        f"ERROR: Latest candle is too old ({age}s). "
        "Collector may not be receiving current market data."
    )

print("Data pipeline: OK")
PYTHON

echo
echo "XAUUSD Data Layer is ready."
