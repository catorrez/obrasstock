# ...
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmariadb-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el entrypoint desde django/ al lugar final en la imagen
COPY django/entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
