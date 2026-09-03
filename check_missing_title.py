import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

users = db.collection('users').stream()
found = 0
for user in users:
    addrs = db.collection('users').document(user.id).collection('addresses').get()
    for a in addrs:
        d = a.to_dict()
        if 'title' not in d:
            print(f"User {user.id} address {a.id} is missing 'title'. Keys: {list(d.keys())}")
            print(d)
            found += 1
            if found >= 5:
                break
    if found >= 5:
        break

if found == 0:
    print("No addresses found missing 'title'.")
