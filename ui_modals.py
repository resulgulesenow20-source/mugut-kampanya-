import customtkinter as ctk
import tkinter.messagebox as messagebox
try:
    import database
    from firebase_admin import firestore
except ImportError:
    pass

def open_detail_modal(app, item, update_callback=None):
    modal = ctk.CTkToplevel(app)
    modal.title("Kayıt Detayları")
    modal.geometry("500x600")
    modal.attributes("-topmost", True)
    modal.configure(fg_color="#F8FAFC")
    
    modal.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (modal.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (modal.winfo_height() // 2)
    modal.geometry(f"+{x}+{y}")

    title_lbl = ctk.CTkLabel(modal, text="Tüm Bilgiler (Firebase)", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
    title_lbl.pack(pady=20)

    scroll_frame = ctk.CTkScrollableFrame(modal, fg_color="white", corner_radius=12)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    for key, value in item.items():
        row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        
        k_lbl = ctk.CTkLabel(row_frame, text=f"{key}:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64748B", width=120, anchor="w")
        k_lbl.pack(side="left", padx=(10, 5))
        
        v_lbl = ctk.CTkLabel(row_frame, text=str(value), font=ctk.CTkFont(size=14), text_color="#1E293B", wraplength=280, justify="left", anchor="w")
        v_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))

    if app.current_collection == "SponsorluRestoranlar":
        def delete_sponsor():
            if messagebox.askyesno("Onay", "Bu restoranı sponsorlu listeden kaldırmak istediğinize emin misiniz?"):
                try:
                    doc_id = item.get('id')
                    if not doc_id:
                        messagebox.showerror("Hata", "Silinecek belgenin ID'si bulunamadı.")
                        return
                    database.delete_data("SponsorluRestoranlar", doc_id)
                    messagebox.showinfo("Başarılı", "Restoran sponsorlu listeden silindi!")
                    modal.destroy()
                    app.load_list(app.current_collection)
                except Exception as e:
                    messagebox.showerror("Hata", f"Silinirken hata oluştu:\n{e}")

        del_btn = ctk.CTkButton(modal, text="Sil (Listeden Çıkar)", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", command=delete_sponsor)
        del_btn.pack(pady=15)

    if app.current_collection == "Emirler":
        def update_order_status(new_status):
            if messagebox.askyesno("Onay", f"Sipariş durumunu '{new_status}' olarak güncellemek istiyor musunuz?"):
                try:
                    doc_id = item.get('id')
                    if not doc_id:
                        messagebox.showerror("Hata", "Sipariş ID'si bulunamadı.")
                        return
                    
                    item['status'] = new_status
                    database.set_data("Emirler", doc_id, item)
                    
                    messagebox.showinfo("Başarılı", f"Sipariş durumu '{new_status}' yapıldı!")
                    modal.destroy()
                    if update_callback:
                        update_callback(new_status)
                    else:
                        app.load_list(app.current_collection)
                except Exception as e:
                    messagebox.showerror("Hata", f"Güncellenirken hata oluştu:\n{e}")

        action_frame = ctk.CTkFrame(modal, fg_color="transparent")
        action_frame.pack(pady=10, fill="x", padx=20)
        
        btn_onayla = ctk.CTkButton(action_frame, text="Onayla", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#3B82F6", hover_color="#2563EB", text_color="white", width=100, command=lambda: update_order_status("onaylandı"))
        btn_onayla.grid(row=0, column=0, padx=5, pady=5)
        
        btn_hazirla = ctk.CTkButton(action_frame, text="Hazırla", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", width=100, command=lambda: update_order_status("hazırlanıyor"))
        btn_hazirla.grid(row=0, column=1, padx=5, pady=5)
        
        btn_yola = ctk.CTkButton(action_frame, text="Yola Çıkar", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#8B5CF6", hover_color="#7C3AED", text_color="white", width=100, command=lambda: update_order_status("yolda"))
        btn_yola.grid(row=0, column=2, padx=5, pady=5)
        
        btn_teslim = ctk.CTkButton(action_frame, text="Teslim Et", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="white", width=100, command=lambda: update_order_status("teslim edildi"))
        btn_teslim.grid(row=0, column=3, padx=5, pady=5)
        
        btn_iptal = ctk.CTkButton(action_frame, text="İptal Et", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", width=100, command=lambda: update_order_status("iptal edildi"))
        btn_iptal.grid(row=1, column=0, columnspan=4, pady=10)
        
        action_frame.grid_columnconfigure((0,1,2,3), weight=1)

    if app.current_collection == "Kampanyalar":
        def update_campaign_status(is_active):
            status_text = "Aktif" if is_active else "Pasif"
            if messagebox.askyesno("Onay", f"Kampanyayı '{status_text}' yapmak istediğinize emin misiniz?"):
                try:
                    doc_id = item.get('id')
                    if not doc_id:
                        messagebox.showerror("Hata", "Kampanya ID'si bulunamadı.")
                        return
                    
                    database.db.collection("Kampanyalar").document(doc_id).update({"isActive": is_active})
                    messagebox.showinfo("Başarılı", f"Kampanya durumu '{status_text}' olarak güncellendi!")
                    modal.destroy()
                    app.load_list("Kampanyalar")
                except Exception as e:
                    messagebox.showerror("Hata", f"Güncellenirken hata oluştu:\n{e}")

        def delete_campaign():
            if messagebox.askyesno("Onay", "Bu kampanyayı tamamen silmek istediğinize emin misiniz?"):
                try:
                    doc_id = item.get('id')
                    if not doc_id:
                        messagebox.showerror("Hata", "Kampanya ID'si bulunamadı.")
                        return
                    database.delete_data("Kampanyalar", doc_id)
                    messagebox.showinfo("Başarılı", "Kampanya başarıyla silindi!")
                    modal.destroy()
                    app.load_list("Kampanyalar")
                except Exception as e:
                    messagebox.showerror("Hata", f"Silinirken hata oluştu:\n{e}")

        action_frame = ctk.CTkFrame(modal, fg_color="transparent")
        action_frame.pack(pady=10, fill="x", padx=20)
        
        btn_aktif = ctk.CTkButton(action_frame, text="Aktif Et (Onayla)", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="white", command=lambda: update_campaign_status(True))
        btn_aktif.pack(side="left", fill="x", expand=True, padx=5)

        btn_pasif = ctk.CTkButton(action_frame, text="Pasife Çek", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", command=lambda: update_campaign_status(False))
        btn_pasif.pack(side="left", fill="x", expand=True, padx=5)

        btn_sil = ctk.CTkButton(action_frame, text="Sil", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="white", command=delete_campaign)
        btn_sil.pack(side="left", fill="x", expand=True, padx=5)

    if app.current_collection == "Dukkanlar":
        def edit_commission():
            dialog = ctk.CTkInputDialog(text="Yeni Komisyon Oranı (%):", title="Komisyon Oranı Değiştir")
            val = dialog.get_input()
            if val is not None:
                try:
                    rate = float(val)
                    doc_id = item.get('id')
                    if not doc_id:
                        messagebox.showerror("Hata", "Restoran ID'si bulunamadı.")
                        return
                    database.db.collection("Dukkanlar").document(doc_id).update({"commission_rate": rate})
                    messagebox.showinfo("Başarılı", f"Komisyon oranı %{rate} olarak güncellendi!")
                    modal.destroy()
                    app.load_list("Dukkanlar")
                except ValueError:
                    messagebox.showerror("Hata", "Lütfen geçerli bir sayı giriniz.")
                except Exception as e:
                    messagebox.showerror("Hata", f"Hata oluştu:\n{e}")

        action_frame = ctk.CTkFrame(modal, fg_color="transparent")
        action_frame.pack(pady=10, fill="x", padx=20)
        btn_comm = ctk.CTkButton(action_frame, text="Komisyon Oranını Değiştir", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#F59E0B", hover_color="#D97706", text_color="white", command=edit_commission)
        btn_comm.pack(pady=10, fill="x")

def open_add_modal(app):
    if not app.db_connected:
        messagebox.showerror("Hata", "Lütfen önce Firebase bağlantısını (serviceAccountKey.json) sağlayın.")
        return

    if app.current_collection == "SponsorluRestoranlar":
        open_sponsor_modal(app)
    elif app.current_collection == "Kampanyalar":
        import ui_campaigns
        ui_campaigns.open_campaign_modal(app)
    elif app.current_collection == "top_categories":
        import ui_categories
        ui_categories.open_category_modal(app)
    elif app.current_collection == "DashboardBanners":
        open_dashboard_banner_modal(app)
    else:
        messagebox.showinfo("Bilgi", f"[{app.page_title.cget('text')}] için ekleme formu yakında eklenecek!")

def open_sponsor_modal(app):
    modal = ctk.CTkToplevel(app)
    modal.title("Sponsorlu Restoran Ekle")
    modal.geometry("400x380")
    modal.attributes("-topmost", True)
    modal.configure(fg_color="#F8FAFC")
    
    modal.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (modal.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (modal.winfo_height() // 2)
    modal.geometry(f"+{x}+{y}")

    title_lbl = ctk.CTkLabel(modal, text="Restoran Seçin", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B")
    title_lbl.pack(pady=(15, 5))

    try:
        dukkanlar = database.get_data("Dukkanlar")
    except Exception as e:
        messagebox.showerror("Hata", f"Restoranlar çekilemedi:\n{e}")
        modal.destroy()
        return

    restaurant_map = {}
    for d in dukkanlar:
        name = d.get("restaurantName", d.get("name", d.get("İsim", "Bilinmiyor")))
        restaurant_map[name] = d

    names = list(restaurant_map.keys())
    if not names:
        messagebox.showinfo("Bilgi", "Sistemde hiç restoran bulunamadı.")
        modal.destroy()
        return

    selected_name = ctk.StringVar(value=names[0])
    
    dropdown = ctk.CTkOptionMenu(modal, values=names, variable=selected_name, width=300, fg_color="#5D3EBC", button_color="#462E8E", button_hover_color="#322165")
    dropdown.pack(pady=10)

    slot_lbl = ctk.CTkLabel(modal, text="Hangi Karta Eklensin? (1-6)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64748B")
    slot_lbl.pack(pady=(10, 5))

    slot_options = ["1", "2", "3", "4", "5", "6"]
    selected_slot = ctk.StringVar(value="1")
    slot_dropdown = ctk.CTkOptionMenu(modal, values=slot_options, variable=selected_slot, width=300, fg_color="#64748B", button_color="#475569", button_hover_color="#334155")
    slot_dropdown.pack(pady=10)

    def save_sponsor():
        rest_name = selected_name.get()
        rest_data = restaurant_map.get(rest_name)
        slot_num = selected_slot.get()
        
        if rest_data:
            try:
                doc_id = rest_data.get('id', rest_data.get('mugut_id', rest_data.get('phone', '')))
                rest_data['original_id'] = doc_id
                rest_data['slot_index'] = int(slot_num)
                
                slot_doc_id = f"slot_{slot_num}"
                
                database.set_data("SponsorluRestoranlar", slot_doc_id, rest_data)
                messagebox.showinfo("Başarılı", f"{rest_name} başarıyla {slot_num}. karta eklendi!")
                modal.destroy()
                app.load_list(app.current_collection)
            except Exception as e:
                messagebox.showerror("Hata", f"Eklenirken hata oluştu:\n{e}")

    save_btn = ctk.CTkButton(modal, text="Ekle", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="white", command=save_sponsor)
    save_btn.pack(pady=15)

def open_dashboard_banner_modal(app):
    modal = ctk.CTkToplevel(app)
    modal.title("Fırsatlar Afişi Ekle")
    modal.geometry("400x300")
    modal.attributes("-topmost", True)
    modal.configure(fg_color="#F8FAFC")
    
    modal.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (modal.winfo_width() // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (modal.winfo_height() // 2)
    modal.geometry(f"+{x}+{y}")

    title_lbl = ctk.CTkLabel(modal, text="Fırsatlar Görselini Ayarla", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B")
    title_lbl.pack(pady=(20, 10))

    ctk.CTkLabel(modal, text="Görsel URL veya Yükle:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20)
    
    img_frame = ctk.CTkFrame(modal, fg_color="transparent")
    img_frame.pack(fill="x", pady=5, padx=20)
    
    entry_image = ctk.CTkEntry(img_frame, placeholder_text="http://...")
    entry_image.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def upload_image():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Afiş Seçin",
            filetypes=[("Resim", "*.jpg *.jpeg *.png *.webp"), ("Tüm Dosyalar", "*.*")]
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

    btn_upload_img = ctk.CTkButton(img_frame, text="Yükle", width=60, command=upload_image)
    btn_upload_img.pack(side="right")

    def save_banner():
        img_url = entry_image.get().strip()
        if not img_url:
            messagebox.showerror("Hata", "Lütfen bir resim URL'si girin veya yükleyin.")
            return
            
        try:
            data = {
                "imageUrl": img_url,
                "title": "Fırsatlar Banner",
                "createdAt": firestore.SERVER_TIMESTAMP if 'firestore' in globals() else None
            }
            # Kaydet: main_banner adında tek bir dökümanı eziyoruz
            database.set_data("DashboardBanners", "main_banner", data)
            messagebox.showinfo("Başarılı", "Fırsatlar afişi başarıyla kaydedildi!")
            modal.destroy()
            app.load_list(app.current_collection)
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilirken hata oluştu:\n{e}")

    save_btn = ctk.CTkButton(modal, text="Kaydet", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#10B981", hover_color="#059669", text_color="white", command=save_banner)
    save_btn.pack(pady=25)
