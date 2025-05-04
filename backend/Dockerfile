FROM python:3.11-slim

WORKDIR /app

# install bash + dependencies
RUN apt-get update && \
    apt-get install -y libgomp1 bash && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy application and entrypoint
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh

# ensure it’s executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

# use the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
