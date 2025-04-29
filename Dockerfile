FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Read port dynamically from environment variable (default to 8080)
EXPOSE 8080

CMD streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
