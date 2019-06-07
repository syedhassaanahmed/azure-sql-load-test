FROM python:3-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update \
        && apt-get install -y curl apt-transport-https gnupg2 \
        && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
        && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list \
        && apt-get update \
        && ACCEPT_EULA=Y apt-get install -y msodbcsql17 build-essential unixodbc-dev && \
        pip install --no-cache-dir -r requirements.txt

COPY test.py .

CMD ["sh", "-c", "curl -sS ${QUERY_SCRIPT_URL} > query.py && python -u ./test.py"]