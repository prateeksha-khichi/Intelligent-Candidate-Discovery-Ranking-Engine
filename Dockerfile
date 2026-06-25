FROM python:3.11-slim

WORKDIR /app

# Install dependencies needed by sentence-transformers, chromadb, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# We inject the missing core dependencies just in case they aren't fully listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn sentence-transformers chromadb pandas pydantic scikit-learn

COPY . .

# Change permissions for huggingface spaces (needs to run as non-root)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Hugging face exposes port 7860
EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "7860"]
