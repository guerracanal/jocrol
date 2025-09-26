# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el fichero de requisitos e instalar las dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto 8080 para que Cloud Run pueda recibir tráfico
EXPOSE 8080

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app"]