FROM python:3.11-slim

WORKDIR /app

# System deps for Pillow / onnxruntime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model into the image so first requests are instant
RUN python -c "from rembg import new_session; new_session('birefnet-general')"

COPY app.py .

ENV PORT=3000
EXPOSE 3000

CMD ["python", "app.py"]
