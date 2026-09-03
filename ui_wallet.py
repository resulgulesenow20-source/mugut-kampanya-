import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
try:
    import firebase_admin
    from firebase_admin import firestore
except ImportError:
    pass

class WalletFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.lbl_title = ctk.CTkLabel(self, text="Cüzdan Mesajı (Gazanan TMT)", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
        self.lbl_title.pack(anchor="w", pady=(0, 10))
        
        self.lbl_desc = ctk.CTkLabel(self, text="Mobil uygulamadaki 'Gazanan TMT' (Cüzdan) alanında gösterilen geçici yazıyı buradan değiştirebilirsiniz.", text_color="#64748B")
        self.lbl_desc.pack(anchor="w", pady=(0, 20))
        
        self.form_scroll = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=12, width=600, height=200)
        self.form_scroll.pack(fill="both", expand=True, pady=10)
        
        lbl = ctk.CTkLabel(self.form_scroll, text="Cüzdan Geçici Mesajı:", font=ctk.CTkFont(weight="bold"))
        lbl.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.entry_msg = ctk.CTkTextbox(self.form_scroll, width=500, height=150)
        self.entry_msg.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.btn_save = ctk.CTkButton(self.form_scroll, text="Kaydet", fg_color="#5D3EBC", hover_color="#462E8E", font=ctk.CTkFont(weight="bold"), command=self.save_texts)
        self.btn_save.pack(anchor="w", padx=20, pady=30)
        
        self.load_current_texts()
        
    def load_current_texts(self):
        threading.Thread(target=self._fetch_texts, daemon=True).start()
        
    def _fetch_texts(self):
        try:
            db = firestore.client()
            doc = db.collection('SystemSettings').document('WalletConfig').get()
            
            if doc.exists:
                data = doc.to_dict()
                if 'tempMessage' in data:
                    msg = data['tempMessage']
                    self.master.after(0, lambda: self._populate_entry(msg))
        except Exception as e:
            print("Veri çekerken hata:", e)
            
    def _populate_entry(self, msg):
        self.entry_msg.delete("1.0", "end")
        self.entry_msg.insert("1.0", msg)
        
    def save_texts(self):
        self.btn_save.configure(state="disabled", text="Kaydediliyor...")
        msg = self.entry_msg.get("1.0", "end-1c").strip()
        threading.Thread(target=self._process_saving, args=(msg,), daemon=True).start()
        
    def _process_saving(self, msg):
        try:
            db = firestore.client()
            db.collection('SystemSettings').document('WalletConfig').set({
                'tempMessage': msg
            }, merge=True)
            self.master.after(0, lambda: messagebox.showinfo("Başarılı", "Gazanan TMT yazısı başarıyla güncellendi!"))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Hata", f"Kaydedilirken hata:\n{e}"))
        finally:
            self.master.after(0, lambda: self.btn_save.configure(state="normal", text="Kaydet"))

def render(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    frame = WalletFrame(parent)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
