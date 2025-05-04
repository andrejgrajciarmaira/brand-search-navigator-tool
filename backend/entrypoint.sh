#!/usr/bin/env sh
set -e

# Ensure the .streamlit folder exists
mkdir -p /app/.streamlit

# Write out secrets.toml from environment variables
cat > /app/.streamlit/secrets.toml <<EOF
GOOGLE_DEVELOPER_TOKEN    = "${GOOGLE_DEVELOPER_TOKEN}"
GOOGLE_CLIENT_ID          = "${GOOGLE_CLIENT_ID}"
GOOGLE_CLIENT_SECRET      = "${GOOGLE_CLIENT_SECRET}"
GOOGLE_REFRESH_TOKEN      = "${GOOGLE_REFRESH_TOKEN}"
GOOGLE_LOGIN_CUSTOMER_ID  = "${GOOGLE_LOGIN_CUSTOMER_ID}"
GOOGLE_CUSTOMER_ID        = "${GOOGLE_CUSTOMER_ID}"
EOF

# Finally exec Streamlit
exec streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
