#!/usr/bin/env bash
set -euo pipefail

STREAMLIT_DIR="/app/.streamlit"
SECRETS_FILE="${STREAMLIT_DIR}/secrets.toml"
mkdir -p "${STREAMLIT_DIR}"

# Function to strip wrapping double-quotes
strip_quotes() {
  local v="$1"; v="${v#\"}"; v="${v%\"}"
  printf '%s' "$v"
}

# Clean each secret value
GOOGLE_DEVELOPER_TOKEN  ="$(strip_quotes "${GOOGLE_DEVELOPER_TOKEN}")"
GOOGLE_CLIENT_ID         ="$(strip_quotes "${GOOGLE_CLIENT_ID}")"
GOOGLE_CLIENT_SECRET     ="$(strip_quotes "${GOOGLE_CLIENT_SECRET}")"
GOOGLE_REFRESH_TOKEN     ="$(strip_quotes "${GOOGLE_REFRESH_TOKEN}")"
GOOGLE_LOGIN_CUSTOMER_ID ="$(strip_quotes "${GOOGLE_LOGIN_CUSTOMER_ID}")"
GOOGLE_CUSTOMER_ID       ="$(strip_quotes "${GOOGLE_CUSTOMER_ID}")"

# Write valid TOML
cat > "${SECRETS_FILE}" <<EOF
# auto-generated secrets.toml

GOOGLE_DEVELOPER_TOKEN   = '${GOOGLE_DEVELOPER_TOKEN}'
GOOGLE_CLIENT_ID         = '${GOOGLE_CLIENT_ID}'
GOOGLE_CLIENT_SECRET     = '${GOOGLE_CLIENT_SECRET}'
GOOGLE_REFRESH_TOKEN     = '${GOOGLE_REFRESH_TOKEN}'
GOOGLE_LOGIN_CUSTOMER_ID = '${GOOGLE_LOGIN_CUSTOMER_ID}'
GOOGLE_CUSTOMER_ID       = '${GOOGLE_CUSTOMER_ID}'
EOF

# Debug output
echo "---- /app/.streamlit/secrets.toml ----"
cat "${SECRETS_FILE}"
echo "--------------------------------------"

# Launch
exec streamlit run app.py --server.port="${PORT:-8080}" --server.address=0.0.0.0
