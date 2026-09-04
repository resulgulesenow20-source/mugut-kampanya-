import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import threading
import uuid

db = None

def initialize_firebase():
    global db
    if db is not None:
        return db
        
    key_path = "serviceAccountKey.json"
    
    if not os.path.exists(key_path):
        raise FileNotFoundError("Firebase erişimi için serviceAccountKey.json dosyası bulunamadı.\nLütfen Firebase Console'dan indirip klasöre ekleyin.")
    
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'mugt-gelsin.firebasestorage.app'
        })
        
    db = firestore.client()
    return db

def get_data(collection_name):
    """Verilen koleksiyondan verileri okur."""
    try:
        if not db:
            initialize_firebase()
            
        if collection_name == "Emirler":
            docs = db.collection(collection_name).order_by("createdAt", direction=firestore.Query.DESCENDING).limit(50).stream()
        elif collection_name == "AppBanners":
            docs = db.collection("Kampanyalar").where("is_app_banner", "==", True).limit(50).stream()
        else:
            docs = db.collection(collection_name).limit(50).stream()
            
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        raise Exception(f"Veri çekme hatası: {e}")

def set_data(collection_name, doc_id, data):
    """Verilen koleksiyona doküman ekler veya günceller."""
    try:
        if not db:
            initialize_firebase()
            
        if 'id' in data:
            data_to_save = data.copy()
            del data_to_save['id']
        else:
            data_to_save = data
            
        if collection_name == "AppBanners":
            collection_name = "Kampanyalar"
            data_to_save["is_app_banner"] = True
            data_to_save["isActive"] = True
            
        if doc_id:
            db.collection(collection_name).document(doc_id).set(data_to_save)
        else:
            db.collection(collection_name).add(data_to_save)
        return True
    except Exception as e:
        raise Exception(f"Veri ekleme hatası: {e}")

def upload_file(file_path, destination_path=None):
    """Dosyayı Firebase Storage'a yükler ve public URL döndürür."""
    import tempfile
    import os
    try:
        from PIL import Image
    except ImportError:
        Image = None

    try:
        if not db:
            initialize_firebase()
            
        if destination_path is None:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1]
            destination_path = f"AppConfig/{uuid.uuid4()}{ext}"
            
        upload_path = file_path
        temp_file = None
        ext_lower = os.path.splitext(file_path)[1].lower()
        
        # Resim sıkıştırma algoritması
        if Image and ext_lower in ['.png', '.jpg', '.jpeg']:
            try:
                img = Image.open(file_path)
                max_dim = 500
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                
                has_alpha = False
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    has_alpha = True
                
                if has_alpha:
                    alpha = img.convert('RGBA').split()[-1]
                    if alpha.getextrema()[0] == 255:
                        has_alpha = False
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext_lower)
                temp_file.close() # Windows'ta başka bir process'in dosyaya yazabilmesi için kapatıyoruz
                
                if has_alpha:
                    img.save(temp_file.name, format='PNG', optimize=True)
                else:
                    img = img.convert('RGB')
                    img.save(temp_file.name, format='JPEG', quality=85)
                
                upload_path = temp_file.name
            except Exception as e:
                print(f"Resim sıkıştırma atlandı: {e}")
            
        bucket = storage.bucket()
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(upload_path)
        
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.remove(temp_file.name)
            except:
                pass
                
        blob.make_public()
        return blob.public_url
    except Exception as e:
        raise Exception(f"Dosya yükleme hatası: {e}")

def delete_data(collection_name, doc_id):
    """Verilen koleksiyondan doküman siler."""
    try:
        if not db:
            initialize_firebase()
            
        db.collection(collection_name).document(doc_id).delete()
        return True
    except Exception as e:
        raise Exception(f"Veri silme hatası: {e}")

def get_support_chats():
    try:
        if not db: initialize_firebase()
        docs = db.collection('chats').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Fetch real name if it says 'Müşteri'
            name = data.get('userName', 'Müşteri')
            if name == 'Müşteri' and 'userId' in data:
                try:
                    user_doc = db.collection('users').document(data['userId']).get()
                    if user_doc.exists:
                        real_name = user_doc.to_dict().get('name')
                        if real_name:
                            data['userName'] = real_name
                except:
                    pass
            
            results.append(data)
        return results
    except Exception as e:
        raise Exception(f"Sohbetler çekilirken hata: {e}")

chat_listener = None

def listen_to_chat(uid, callback):
    global chat_listener
    try:
        if not db: initialize_firebase()
        if chat_listener:
            chat_listener.unsubscribe()
            
        query = db.collection('chats').document(uid).collection('messages').order_by('timestamp', direction=firestore.Query.ASCENDING).limit(100)
        
        def on_snapshot(col_snapshot, changes, read_time):
            results = []
            for doc in col_snapshot:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            callback(results)
            
        chat_listener = query.on_snapshot(on_snapshot)
    except Exception as e:
        raise Exception(f"Mesajlar dinlenirken hata: {e}")

global_chats_listener = None

def start_global_listener(on_new_message_callback):
    global global_chats_listener
    try:
        if not db: initialize_firebase()
        
        query = db.collection('chats')
        is_initial = True
        
        def on_snapshot(col_snapshot, changes, read_time):
            nonlocal is_initial
            if is_initial:
                is_initial = False
                return
                
            for change in changes:
                if change.type.name in ['ADDED', 'MODIFIED']:
                    data = change.document.to_dict()
                    if data.get('unreadByAdmin', 0) > 0:
                        on_new_message_callback(data)
                        
        global_chats_listener = query.on_snapshot(on_snapshot)
    except Exception as e:
        print(f"Global dinleyici başlatılamadı: {e}")

def send_chat_message(uid, text):
    try:
        if not db: initialize_firebase()
        
        # 1. Yeni mesajı Messages alt koleksiyonuna ekle
        msg_ref = db.collection('chats').document(uid).collection('messages').document()
        timestamp = firestore.SERVER_TIMESTAMP
        msg_data = {
            'text': text,
            'senderId': 'admin',
            'senderName': 'Mugt Destek',
            'isAdmin': True,
            'timestamp': timestamp
        }
        msg_ref.set(msg_data)
        
        # 2. Ana belgeyi güncelle
        db.collection('chats').document(uid).update({
            'lastMessage': text,
            'timestamp': timestamp,
            'unreadByAdmin': 0,
            'unreadByUser': firestore.Increment(1)
        })
        return True
    except Exception as e:
        raise Exception(f"Mesaj gönderilirken hata: {e}")

import time

def close_chat(uid):
    try:
        if not db: initialize_firebase()
        
        chat_ref = db.collection('chats').document(uid)
        chat_doc = chat_ref.get()
        if not chat_doc.exists: return True
        
        archive_id = f"{uid}_{int(time.time())}"
        archive_ref = db.collection('ArchivedChats').document(archive_id)
        
        # Copy main doc
        archive_data = chat_doc.to_dict()
        archive_data['isArchived'] = True
        archive_ref.set(archive_data)
        
        # Copy and delete messages
        messages = chat_ref.collection('messages').stream()
        batch = db.batch()
        count = 0
        for doc in messages:
            # Copy
            archive_ref.collection('messages').document(doc.id).set(doc.to_dict())
            # Delete
            batch.delete(doc.reference)
            count += 1
            if count == 400:
                batch.commit()
                batch = db.batch()
                count = 0
        if count > 0:
            batch.commit()
            
        # Delete main doc
        chat_ref.delete()
        return True
    except Exception as e:
        raise Exception(f"Sohbet kapatılırken hata: {e}")

def start_chat_with_user(phone):
    try:
        if not db: initialize_firebase()
        users = db.collection('users').where('phone', '==', phone).get()
        if not users:
            raise Exception("Bu telefon numarasına sahip bir kullanıcı bulunamadı.")
            
        user_doc = users[0]
        uid = user_doc.id
        user_data = user_doc.to_dict()
        
        chat_ref = db.collection('chats').document(uid)
        chat_ref.set({
            'userId': uid,
            'userName': user_data.get('name', 'İsimsiz'),
            'userPhone': phone,
            'unreadByAdmin': 0,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'lastMessage': 'Destek tarafından sohbet başlatıldı'
        }, merge=True)
        return uid, user_data.get('name', 'İsimsiz')
    except Exception as e:
        raise Exception(f"Sohbet başlatılırken hata: {e}")

def get_archived_chats():
    try:
        if not db: initialize_firebase()
        docs = db.collection('ArchivedChats').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Fetch real name if it says 'Müşteri'
            name = data.get('userName', 'Müşteri')
            if name == 'Müşteri' and 'userId' in data:
                try:
                    user_doc = db.collection('users').document(data['userId']).get()
                    if user_doc.exists:
                        real_name = user_doc.to_dict().get('name')
                        if real_name:
                            data['userName'] = real_name
                except:
                    pass
            
            results.append(data)
        return results
    except Exception as e:
        raise Exception(f"Arşiv çekilirken hata: {e}")

def get_archived_messages(archive_id):
    try:
        if not db: initialize_firebase()
        docs = db.collection('ArchivedChats').document(archive_id).collection('messages').order_by('timestamp', direction=firestore.Query.ASCENDING).limit(100).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        return results
    except Exception as e:
        raise Exception(f"Arşiv mesajları çekilirken hata: {e}")
