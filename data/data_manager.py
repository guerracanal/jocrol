
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.jocrol

LANZAMIENTOS_COLLECTION = db.lanzamientos
EVENTOS_COLLECTION = db.eventos
CLIENTES_COLLECTION = db.clientes
RESERVAS_COLLECTION = db.reservas
STAFF_COLLECTION = db.staff
JUEGOS_COLECCIONES_COLLECTION = db.juegos_colecciones
