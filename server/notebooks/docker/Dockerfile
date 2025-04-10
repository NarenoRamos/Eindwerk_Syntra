# Gebruik een officiële Python image als basis
FROM python:3.12-slim

# Zet de werkdirectory in de container
WORKDIR /app

# Installeer de benodigde systeemafhankelijkheden
RUN apt-get update && \
    apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopieer het requirements.txt bestand naar de container
COPY requirements.txt .

# Installeer de Python packages uit het requirements.txt bestand
RUN pip install --no-cache-dir -r requirements.txt

# Exposeer de poort die Jupyter gebruikt
EXPOSE 8888

# Start JupyterLab bij het opstarten van de container
CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]