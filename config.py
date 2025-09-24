import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la aplicación
# IMPORTANTE: No compartas este fichero. Contiene información sensible.

# La SECRET_KEY se carga desde el archivo .env
SECRET_KEY = os.getenv('SECRET_KEY')
