from data.data_manager import STAFF_COLLECTION

def obtener_staff_todos():
    return list(STAFF_COLLECTION.find({}, {'_id': 0}))
