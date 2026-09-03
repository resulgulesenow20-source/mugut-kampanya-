import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

users = db.collection('users').limit(10).stream()
for user in users:
    addrs = db.collection('users').document(user.id).collection('addresses').get()
    if addrs:
        print(f"User {user.id} has {len(addrs)} addresses:")
        for a in addrs:
            print(a.to_dict())
