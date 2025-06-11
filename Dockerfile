FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt')"

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=localhost
ENV OLLAMA_PORT=11434

# Create necessary directories
RUN mkdir -p documents

# Default command
CMD ["python", "nlp.py"] 