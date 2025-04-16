# Usa Python en Alpine para una imagen más ligera
FROM python:3.11.11-alpine3.21

ENV PYTHONNUNBUFFERED = 
# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para PostgreSQL y compilar paquetes de Python
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    libffi-dev \
    && pip install --upgrade pip

# Copia los requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . .

# Expone el puerto para Django
EXPOSE 8000

# Comando para ejecutar el servidor de desarrollo de Django
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
