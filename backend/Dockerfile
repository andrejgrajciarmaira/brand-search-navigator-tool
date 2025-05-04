FROM python:3.11-slim

WORKDIR /app

# Install system deps + bash
RUN apt-get update && \
    apt-get install -y libgomp1 bash && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy code + entrypoint
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
