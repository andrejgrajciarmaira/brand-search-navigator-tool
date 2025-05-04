#!/usr/bin/env bash
set -euo pipefail

STREAMLIT_DIR="/app/.streamlit"
SECRETS_FILE="${STREAMLIT_DIR}/secrets.toml"

mkdir -p "${STREAMLIT_DIR}"

cat > "${SECRETS_FILE}" <<EOF
# auto-generated secrets.toml

GOOGLE_DEVELOPER_TOKEN   = '${GOOGLE_DEVELOPER_TOKEN}'
GOOGLE_CLIENT_ID         = '${GOOGLE_CLIENT_ID}'
GOOGLE_CLIENT_SECRET     = '${GOOGLE_CLIENT_SECRET}'
GOOGLE_REFRESH_TOKEN     = '${GOOGLE_REFRESH_TOKEN}'
GOOGLE_LOGIN_CUSTOMER_ID = '${GOOGLE_LOGIN_CUSTOMER_ID}'
GOOGLE_CUSTOMER_ID       = '${GOOGLE_CUSTOMER_ID}'
EOF

# debug: print out what you wrote
echo "---- /app/.streamlit/secrets.toml ----"
cat "${SECRETS_FILE}"
echo "--------------------------------------"

exec streamlit run app.py --server.port="${PORT:-8080}" --server.address=0.0.0.0
