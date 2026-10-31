FROM python:3.12-slim

WORKDIR /app

# Install dependencies first, so Docker can cache this layer between code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --reload restarts the server when files in the mounted /app folder change.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
