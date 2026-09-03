import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
try:
    import firebase_admin
    from firebase_admin import firestore
except ImportError:
    pass

class TextsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Başlık ve Açıklama
        self.lbl_title = ctk.CTkLabel(self, text="Uygulama İçi Metinleri Düzenle", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
        self.lbl_title.pack(anchor="w", pady=(0, 10))
        
        self.lbl_desc = ctk.CTkLabel(self, text="Uygulamadaki 'En Ucuz Lezzetler', 'Restoranlar' gibi ana başlıkları anında değiştirebilirsiniz.", text_color="#64748B")
        self.lbl_desc.pack(anchor="w", pady=(0, 20))
        
        self.form_scroll = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=12, width=600, height=400)
        self.form_scroll.pack(fill="both", expand=True, pady=10)
        
        # Metin Alanları (Dictionary key -> Label)
        self.text_fields = {
            'cheapest': 'En Ucuz Yemekler Başlığı',
            'restaurants': 'Restoranlar Listesi Başlığı',
            'highlights': 'Öne Çıkanlar Başlığı',
            'nav_home': 'Alt Menü: Ana Sayfa',
            'nav_favorites': 'Alt Menü: Favoriler',
            'nav_cart': 'Alt Menü: Sepetim',
            'nav_profile': 'Alt Menü: Profil',
            'start_shopping': 'Alışverişe Başla Butonu',
            'cheapest_desc': 'En Ucuz Yemekler Açıklaması (Opsiyonel)', # Eğer uygulamada varsa
            'search_hint': 'Arama Çubuğu Metni (Ana Sayfa)',
        }
        
        self.entries = {}
        
        for key, label_text in self.text_fields.items():
            lbl = ctk.CTkLabel(self.form_scroll, text=label_text, font=ctk.CTkFont(weight="bold"))
            lbl.pack(anchor="w", padx=20, pady=(15, 5))
            
            entry = ctk.CTkEntry(self.form_scroll, width=400)
            entry.pack(anchor="w", padx=20, pady=(0, 5))
            self.entries[key] = entry
            
        self.btn_save = ctk.CTkButton(self.form_scroll, text="Değişiklikleri Kaydet", fg_color="#5D3EBC", hover_color="#462E8E", font=ctk.CTkFont(weight="bold"), command=self.save_texts)
        self.btn_save.pack(anchor="w", padx=20, pady=30)
        
        # Mevcut verileri çek
        self.load_current_texts()
        
    def load_current_texts(self):
        threading.Thread(target=self._fetch_texts, daemon=True).start()
        
    def _fetch_texts(self):
        try:
            db = firestore.client()
            doc = db.collection('settings').document('translations').get()
            
            if doc.exists:
                data = doc.to_dict()
                if 'TR' in data:
                    tr_texts = data['TR']
                    self.master.after(0, lambda: self._populate_entries(tr_texts))
        except Exception as e:
            print("Metinleri çekerken hata:", e)
            
    def _populate_entries(self, tr_texts):
        for key, entry in self.entries.items():
            if key in tr_texts:
                entry.delete(0, "end")
                entry.insert(0, tr_texts[key])
                
    def save_texts(self):
        if not messagebox.askyesno("Onay", "Uygulamadaki yazıları değiştirmek istediğinize emin misiniz? (Uygulamayı yeniden açanlarda anında güncellenir)"):
            return
            
        self.btn_save.configure(state="disabled", text="Kaydediliyor...")
        
        tr_data = {}
        for key, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                tr_data[key] = val
                
        threading.Thread(target=self._process_saving, args=(tr_data,), daemon=True).start()
        
    def _process_saving(self, tr_data):
        try:
            db = firestore.client()
            # Mevcut veriyi ezmemek için Set(merge=True) kullanıyoruz
            db.collection('settings').document('translations').set({
                'TR': tr_data
            }, merge=True)
            
            self.master.after(0, lambda: messagebox.showinfo("Başarılı", "Uygulama yazıları başarıyla güncellendi!"))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Hata", f"Kaydedilirken hata oluştu:\n{e}"))
        finally:
            self.master.after(0, lambda: self.btn_save.configure(state="normal", text="Değişiklikleri Kaydet"))

def render(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    frame = TextsFrame(parent)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
