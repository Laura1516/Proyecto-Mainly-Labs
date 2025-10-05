FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including LDAP development libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]