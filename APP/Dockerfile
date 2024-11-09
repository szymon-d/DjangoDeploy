FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /APP

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /APP/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . /APP

# Run application
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
