# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies (needed for some data libraries like OpenCV or psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy only the requirements first (optimizes Docker caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Expose the port GCP Cloud Run expects
EXPOSE 8080

# 8. Run the Streamlit app
# We explicitly set the port to 8080 and address to 0.0.0.0
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
