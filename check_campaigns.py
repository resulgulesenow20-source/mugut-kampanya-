import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection('Kampanyalar').get()

for doc in docs:
    data = doc.to_dict()
    try:
        print(f"ID: {doc.id}, isActive: {data.get('isActive')}, shopId: {data.get('shopId')}, image: {data.get('imageUrl') is not None}")
    except:
        print(f"ID: {doc.id}, could not print details due to encoding")
