#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Idempotent bootstrap for docker-compose-prod-local.yml.
# Migrations always run (they are no-ops on subsequent boots).
# Admin creation and example loading are guarded by a sentinel file so
# repeated `docker compose up` cycles do not blow up the init container.

set -euo pipefail

SENTINEL="${SUPERSET_HOME:-/app/superset_home}/.prod_local_initialized"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"

# Install postgres extras for the metadata driver (skipped on workers, so
# we have to do it here once before invoking the superset CLI).
if [[ "${DATABASE_DIALECT:-}" == postgres* ]] && command -v uv >/dev/null 2>&1; then
    uv pip install -e .[postgres] >/dev/null
fi

echo "[prod-local-init] Applying DB migrations"
superset db upgrade

if [ -f "${SENTINEL}" ]; then
    echo "[prod-local-init] Sentinel ${SENTINEL} exists; skipping admin + examples"
    superset init
    exit 0
fi

echo "[prod-local-init] Creating admin user (admin / ${ADMIN_PASSWORD})"
superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@superset.local \
    --password "${ADMIN_PASSWORD}"

echo "[prod-local-init] Initialising roles and permissions"
superset init

if [ "${SUPERSET_LOAD_EXAMPLES:-no}" = "yes" ]; then
    echo "[prod-local-init] Loading example dashboards (this is slow on first run)"
    superset load_examples
fi

touch "${SENTINEL}"
echo "[prod-local-init] Done. Sentinel written to ${SENTINEL}"
