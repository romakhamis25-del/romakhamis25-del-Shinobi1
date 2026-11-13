FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap sqlmap curl ca-certificates unzip sudo \
    && rm -rf /var/lib/apt/lists/*

# Katana
RUN curl -sL https://github.com/projectdiscovery/katana/releases/latest/download/katana_linux_amd64.zip \
    -o /tmp/k.zip && unzip /tmp/k.zip -d /usr/local/bin && rm /tmp/k.zip

# Nuclei
RUN curl -sL https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip \
    -o /tmp/n.zip && unzip /tmp/n.zip -d /usr/local/bin && rm /tmp/n.zip \
    && nuclei -update-templates -silent || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN useradd -m shinobi && chown -R shinobi:shinobi /app
USER shinobi

CMD ["python", "shinobi.py"]
