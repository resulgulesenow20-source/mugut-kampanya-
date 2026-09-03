import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import threading
try:
    import database
    from firebase_admin import firestore
except ImportError:
    pass

def open_category_modal(app):
    modal = ctk.CTkToplevel(app)
    modal.title("Yeni Kategori Ekle")
    modal.geometry("450x550")
    modal.attributes("-topmost", True)
    modal.configure(fg_color="#F8FAFC")
    
    modal.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (modal.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (modal.winfo_height() // 2)
    modal.geometry(f"+{x}+{y}")

    title_lbl = ctk.CTkLabel(modal, text="Kategori Detayları", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
    title_lbl.pack(pady=15)

    scroll_frame = ctk.CTkScrollableFrame(modal, fg_color="white", corner_radius=12)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # Kategori Başlığı
    ctk.CTkLabel(scroll_frame, text="Kategori İsmi (Görünen):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_title = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: Döner")
    entry_title.pack(fill="x", pady=5, padx=5)

    # Bağlanacağı Sistem Kategorisi
    ctk.CTkLabel(scroll_frame, text="Hangi Kategoriye Yönlendirsin?", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_target = ctk.CTkEntry(scroll_frame, placeholder_text="Sistemdeki kategori adı (Örn: Döner)")
    entry_target.pack(fill="x", pady=5, padx=5)

    # Kategori Sırası
    ctk.CTkLabel(scroll_frame, text="Sıra (1-8):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_order = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: 1")
    entry_order.pack(fill="x", pady=5, padx=5)

    # Görsel Yükleme
    ctk.CTkLabel(scroll_frame, text="Kategori Görseli (Resim URL):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    img_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    img_frame.pack(fill="x", pady=5, padx=5)
    
    entry_image = ctk.CTkEntry(img_frame, placeholder_text="http://...")
    entry_image.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def upload_category_media():
        file_path = filedialog.askopenfilename(
            title="Kategori Resmi Seçin",
            filetypes=[("Resim", "*.jpg *.jpeg *.png"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            btn_upload_img.configure(text="Yükleniyor...", state="disabled")
            app.update_idletasks()
            def process():
                try:
                    public_url = database.upload_file(file_path)
                    entry_image.delete(0, 'end')
                    entry_image.insert(0, public_url)
                except Exception as e:
                    messagebox.showerror("Hata", f"Yükleme hatası: {e}")
                finally:
                    btn_upload_img.configure(text="Yükle", state="normal")
            threading.Thread(target=process, daemon=True).start()

    btn_upload_img = ctk.CTkButton(img_frame, text="Yükle", width=60, command=upload_category_media)
    btn_upload_img.pack(side="right")

    def save_category():
        title = entry_title.get().strip()
        target = entry_target.get().strip()
        order_str = entry_order.get().strip()
        image_url = entry_image.get().strip()
        
        if not title or not target or not order_str or not image_url:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return

        try:
            order = int(order_str)
        except ValueError:
            messagebox.showerror("Hata", "Sıra alanı sayı olmalıdır (Örn: 1, 2, 3)")
            return
        
        data = {
            'title': title,
            'target_category': target,
            'image_url': image_url,
            'order': order,
            'is_active': True,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        try:
            database.db.collection('top_categories').add(data)
            messagebox.showinfo("Başarılı", "Kategori başarıyla ana ekrana eklendi!")
            modal.destroy()
            app.load_list("top_categories")
        except Exception as e:
            messagebox.showerror("Hata", f"Kategori eklenirken hata oluştu:\n{e}")
            
    btn_save = ctk.CTkButton(modal, text="Kategoriyi Kaydet", font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="#10B981", hover_color="#059669", text_color="white", command=save_category)
    btn_save.pack(pady=15, padx=20, fill="x")
