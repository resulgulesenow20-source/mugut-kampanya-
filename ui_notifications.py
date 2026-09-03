import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
try:
    import firebase_admin
    from firebase_admin import messaging
    from firebase_admin import firestore
except ImportError:
    pass

class NotificationFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Başlık ve Açıklama
        self.lbl_title = ctk.CTkLabel(self, text="Toplu Bildirim (Push) Gönder", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
        self.lbl_title.pack(anchor="w", pady=(0, 10))
        
        self.lbl_desc = ctk.CTkLabel(self, text="Uygulamayı indiren ve bildirim izni veren tüm müşterilere anında bildirim gönderin.", text_color="#64748B")
        self.lbl_desc.pack(anchor="w", pady=(0, 20))
        
        # Bildirim Formu
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        self.form_frame.pack(fill="x", pady=10)
        
        self.lbl_notif_title = ctk.CTkLabel(self.form_frame, text="Bildirim Başlığı (Örn: Kaçmaz Fırsat!)", font=ctk.CTkFont(weight="bold"))
        self.lbl_notif_title.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.entry_title = ctk.CTkEntry(self.form_frame, width=400, placeholder_text="Başlık yazın...")
        self.entry_title.pack(anchor="w", padx=20, pady=(0, 15))
        
        self.lbl_notif_body = ctk.CTkLabel(self.form_frame, text="Bildirim İçeriği (Örn: Tüm menülerde %20 indirim başladı!)", font=ctk.CTkFont(weight="bold"))
        self.lbl_notif_body.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.entry_body = ctk.CTkTextbox(self.form_frame, width=400, height=100)
        self.entry_body.pack(anchor="w", padx=20, pady=(0, 20))
        
        self.btn_send = ctk.CTkButton(self.form_frame, text="Bildirimi Gönder", fg_color="#5D3EBC", hover_color="#462E8E", font=ctk.CTkFont(weight="bold"), command=self.send_notification)
        self.btn_send.pack(anchor="w", padx=20, pady=(0, 20))

    def send_notification(self):
        title = self.entry_title.get().strip()
        body = self.entry_body.get("1.0", "end-1c").strip()
        
        if not title or not body:
            messagebox.showwarning("Hata", "Lütfen başlık ve mesaj içeriğini boş bırakmayın.")
            return
            
        if not messagebox.askyesno("Onay", "Bu bildirim uygulamayı kullanan TÜM müşterilere gönderilecektir. Onaylıyor musunuz?"):
            return
            
        self.btn_send.configure(state="disabled", text="Gönderiliyor...")
        threading.Thread(target=self._process_sending, args=(title, body), daemon=True).start()
        
    def _process_sending(self, title, body):
        try:
            db = firestore.client()
            users_ref = db.collection("users").stream()
            
            # 1. Bildirimi veritabanına kalıcı olarak kaydet (Mobil uygulamada listelemek için)
            db.collection("notifications").add({
                "title": title,
                "body": body,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
            # 2. Cihazlara Push Notification gönder
            tokens = []
            for user in users_ref:
                data = user.to_dict()
                if data and "fcmToken" in data and data["fcmToken"]:
                    tokens.append(data["fcmToken"])
                    
            if not tokens:
                self.master.after(0, lambda: messagebox.showinfo("Bilgi", "Veritabanında bildirim gönderilecek hiç cihaz (FCM Token) bulunamadı."))
                self.master.after(0, lambda: self.btn_send.configure(state="normal", text="Bildirimi Gönder"))
                return
                
            # Firebase MulticastMessage kullanarak yüksek öncelikli (High Priority) toplu gönderim
            # Yüksek öncelik, telefon kapalıyken veya kilitliyken ekranı uyandırıp bildirimi düşürür.
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        default_sound=True,
                        default_vibrate_timings=True,
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound='default', badge=1)
                    )
                ),
                tokens=tokens,
            )
            
            response = messaging.send_each_for_multicast(message)
            success_count = response.success_count
            
            self.master.after(0, lambda: messagebox.showinfo("Başarılı", f"Bildirim başarıyla gönderildi!\nİletilen cihaz sayısı: {success_count}"))
            
            # Formu temizle
            self.master.after(0, lambda: self.entry_title.delete(0, "end"))
            self.master.after(0, lambda: self.entry_body.delete("1.0", "end"))
            
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Hata", f"Bildirim gönderilirken bir hata oluştu:\n{str(e)}"))
            
        finally:
            self.master.after(0, lambda: self.btn_send.configure(state="normal", text="Bildirimi Gönder"))

def render(parent_frame):
    # Ekrana frame'i yerleştir
    for widget in parent_frame.winfo_children():
        widget.destroy()
        
    frame = NotificationFrame(parent_frame)
    frame.pack(fill="both", expand=True)
