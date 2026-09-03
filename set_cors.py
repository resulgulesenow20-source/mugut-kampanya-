import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'mugt-gelsin.firebasestorage.app'
})

bucket = storage.bucket()
bucket.cors = [
    {
        "origin": ["*"],
        "method": ["GET", "HEAD", "OPTIONS"],
        "responseHeader": ["*"],
        "maxAgeSeconds": 3600
    }
]
bucket.patch()
print("CORS updated successfully!")
