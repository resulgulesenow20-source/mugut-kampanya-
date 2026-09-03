import customtkinter as ctk
import tkinter.messagebox as messagebox
try:
    import database
    from firebase_admin import firestore
except ImportError:
    pass

def open_campaign_modal(app):
    modal = ctk.CTkToplevel(app)
    modal.title("Yeni Kampanya Ekle")
    modal.geometry("450x650")
    modal.attributes("-topmost", True)
    modal.configure(fg_color="#F8FAFC")
    
    modal.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (modal.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (modal.winfo_height() // 2)
    modal.geometry(f"+{x}+{y}")

    title_lbl = ctk.CTkLabel(modal, text="Kampanya Detayları", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
    title_lbl.pack(pady=15)

    scroll_frame = ctk.CTkScrollableFrame(modal, fg_color="white", corner_radius=12)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    try:
        dukkanlar = database.get_data("Dukkanlar")
    except Exception as e:
        messagebox.showerror("Hata", f"Restoranlar çekilemedi:\n{e}")
        modal.destroy()
        return

    restaurant_map = {}
    for d in dukkanlar:
        name = d.get("restaurantName", d.get("name", d.get("İsim", "Bilinmiyor")))
        restaurant_map[name] = d.get("mugut_id", d.get("id", ""))

    names = list(restaurant_map.keys())
    if not names:
        messagebox.showinfo("Bilgi", "Sistemde restoran bulunamadı.")
        modal.destroy()
        return

    ctk.CTkLabel(scroll_frame, text="Restoran Seçimi (Yoksa genel afiş):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    selected_shop = ctk.StringVar(value=names[0])
    ctk.CTkOptionMenu(scroll_frame, values=names, variable=selected_shop, fg_color="#3B82F6", button_color="#2563EB").pack(fill="x", pady=5, padx=5)

    regions = ["Tüm Bölgeler", "Aşgabat", "Ahal", "Balkanabat", "Balkan", "Mary", "Lebap", "Daşoguz", "Türkmenbaşı"]
    ctk.CTkLabel(scroll_frame, text="Hedef Bölge (Sadece burada gösterilir):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    selected_region = ctk.StringVar(value="Tüm Bölgeler")
    ctk.CTkOptionMenu(scroll_frame, values=regions, variable=selected_region, fg_color="#059669", button_color="#047857").pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="Kampanya Başlığı:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_title = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: Hafta Sonu Fırsatı")
    entry_title.pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="Açıklama:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_desc = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: Tüm menülerde %20 indirim")
    entry_desc.pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="Görsel / Animasyon Yükle veya URL:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    
    img_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    img_frame.pack(fill="x", pady=5, padx=5)
    
    entry_image = ctk.CTkEntry(img_frame, placeholder_text="http://...")
    entry_image.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def upload_campaign_media():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Kampanya Medyası Seçin",
            filetypes=[("Medya", "*.mp4 *.jpg *.jpeg *.png *.json *.lottie"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            btn_upload_img.configure(text="Yükleniyor...", state="disabled")
            app.update_idletasks()
            import threading
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

    btn_upload_img = ctk.CTkButton(img_frame, text="Yükle", width=60, command=upload_campaign_media)
    btn_upload_img.pack(side="right")

    ctk.CTkLabel(scroll_frame, text="Kampanya Kodu (Opsiyonel):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_code = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: MUGUT20")
    entry_code.pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="İndirim Tipi:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    selected_type = ctk.StringVar(value="percentage")
    ctk.CTkOptionMenu(scroll_frame, values=["percentage", "fixed"], variable=selected_type, fg_color="#8B5CF6", button_color="#7C3AED").pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="İndirim Değeri (Yüzde veya TL):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_value = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: 20")
    entry_value.pack(fill="x", pady=5, padx=5)

    ctk.CTkLabel(scroll_frame, text="Minimum Sepet Tutarı (TL):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0), padx=5)
    entry_min = ctk.CTkEntry(scroll_frame, placeholder_text="Örn: 100")
    entry_min.pack(fill="x", pady=5, padx=5)

    def save_campaign():
        title = entry_title.get().strip()
        desc = entry_desc.get().strip()
        val_str = entry_value.get().strip().replace(",", ".")
        min_str = entry_min.get().strip().replace(",", ".")
        
        if not title or not val_str:
            messagebox.showerror("Hata", "Başlık ve İndirim Değeri boş bırakılamaz.")
            return

        try:
            val = float(val_str)
            min_amt = float(min_str) if min_str else 0.0
        except ValueError:
            messagebox.showerror("Hata", "Miktar alanlarına lütfen sadece sayı giriniz.")
            return

        shop_name = selected_shop.get()
        shop_id = restaurant_map.get(shop_name, "")
        
        data = {
            'title': title,
            'description': desc,
            'imageUrl': entry_image.get().strip(),
            'code': entry_code.get().strip().upper() if entry_code.get().strip() else None,
            'type': selected_type.get(),
            'value': val,
            'minAmount': min_amt,
            'shop_id': shop_id,
            'region': selected_region.get(),
            'isActive': False,  # Restoran panelinden onaylanması için Pasif başlatılır
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        try:
            database.db.collection('Kampanyalar').add(data)
            messagebox.showinfo("Başarılı", "Kampanya başarıyla taslak olarak eklendi! Restoran sahibi kendi panelinden onayladığında (Aktif ettiğinde) mobil uygulamada müşterilere gözükecektir.")
            modal.destroy()
            app.load_list("Kampanyalar")
        except Exception as e:
            messagebox.showerror("Hata", f"Kampanya başlatılırken hata oluştu:\n{e}")
            
    btn_save = ctk.CTkButton(modal, text="Kampanyayı Başlat", font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="#10B981", hover_color="#059669", text_color="white", command=save_campaign)
    btn_save.pack(pady=15, padx=20, fill="x")
