FROM python:3.11-slim

WORKDIR /app

# Install system deps (optional but safe)
RUN apt-get update && apt-get install -y build-essential

# Copy requirements first (for cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]