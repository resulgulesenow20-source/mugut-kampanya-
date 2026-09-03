import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection('Kampanyalar').where('is_app_banner', '==', True).stream()

for doc in docs:
    data = doc.to_dict()
    print(f"ID: {doc.id}, Title: {data.get('title')}, ShopId: '{data.get('shopId')}', shop_id: '{data.get('shop_id')}'")
