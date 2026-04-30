# 1. Gunakan image Python yang stabil (Bookworm adalah versi Debian yang sangat stabil)
FROM python:3.11-slim-bookworm

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
# Membuang software-properties-common karena tidak diperlukan untuk library data standar
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements dulu untuk memanfaatkan Docker Layer Caching
COPY requirements.txt .

# 5. Install Python dependencies
# Menambahkan upgrade pip agar instalasi library modern lebih lancar
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh sisa kode aplikasi
COPY . .

# 7. Expose port 8080 (standar Cloud Run)
EXPOSE 8080

# 8. Jalankan Streamlit
# Healthcheck dinonaktifkan agar startup di Cloud Run lebih cepat
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
