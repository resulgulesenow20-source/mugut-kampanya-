import customtkinter as ctk

def render_list(app):
    for widget in app.content_scroll.winfo_children():
        widget.destroy()

    if app.current_collection == "Reklamlar":
        _render_splash_upload_section(app)
        return

    if app.current_collection == "AppBanners":
        _render_app_banners_upload_section(app)

    if len(app.current_data) == 0:
        empty_lbl = ctk.CTkLabel(app.content_scroll, text="Bu kategoride henüz veri bulunmuyor.", font=ctk.CTkFont(size=14, slant="italic"), text_color="#64748B")
        empty_lbl.pack(pady=40)
        return

    search_query = app.search_var.get().lower()
    
    if not hasattr(app, "trash_icon"):
        try:
            from PIL import Image
            app.trash_icon = ctk.CTkImage(Image.open("trash.png"), size=(22, 22))
        except:
            app.trash_icon = None


    filtered_data = []
    for item in app.current_data:
        item_text = " ".join(str(v).lower() for v in item.values())
        if search_query in item_text:
            filtered_data.append(item)

    if len(filtered_data) == 0 and search_query != "":
        empty_lbl = ctk.CTkLabel(app.content_scroll, text="Arama sonucu bulunamadı.", font=ctk.CTkFont(size=14, slant="italic"), text_color="#64748B")
        empty_lbl.pack(pady=40)
        return

    for item in filtered_data:
        card = ctk.CTkFrame(app.content_scroll, fg_color="white", corner_radius=16, border_width=1, border_color="#E2E8F0", cursor="hand2")
        card.pack(fill="x", pady=8, padx=5)
        card.grid_columnconfigure(0, weight=1)
        
        baslik = item.get("restaurantName", item.get("name", item.get("title", item.get("id", "İsimsiz"))))
        detay = item.get("address", item.get("cuisineType", item.get("email", item.get("description", str(item)))))
        durum = str(item.get("status", item.get("isOpen", item.get("isActive", item.get("is_active", "Bilinmiyor")))))
        
        if app.current_collection == "Emirler":
            shop = item.get('shop_name', item.get('restaurantName', 'Bilinmiyor'))
            baslik = f"Sipariş #{item.get('id', '')[-6:]} - {shop}"
            tutar = item.get('total', item.get('totalPrice', item.get('totalAmount', 0)))
            detay = f"Tutar: {tutar} TL"
            durum = item.get('status', 'Bekliyor')
        elif app.current_collection == "AppBanners":
            shop_id_val = item.get("shopId", "")
            if not shop_id_val:
                detay = "Özel Afiş Reklamı (Dükkana Yönlendirmez)"
            else:
                detay = f"Yönlendirilecek Dükkan ID: {shop_id_val}"
        elif app.current_collection == "top_categories":
            detay = f"Hedef Kategori: {item.get('target_category', '')} - Sıra: {item.get('order', '')}"

        title = ctk.CTkLabel(card, text=baslik, font=ctk.CTkFont(size=16, weight="bold"), text_color="#1E293B", cursor="hand2")
        title.grid(row=0, column=0, padx=24, pady=(18, 4), sticky="w")
        
        desc = ctk.CTkLabel(card, text=str(detay)[:100] + ("..." if len(str(detay))>100 else ""), font=ctk.CTkFont(size=13), text_color="#64748B", cursor="hand2")
        desc.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="w")
        
        durum_color = "#10B981" if durum.lower() in ["aktif", "true", "delivered", "completed", "teslim edildi"] else "#EF4444"
        display_durum = durum
        if durum.lower() == "true":
            display_durum = "+"
        elif durum.lower() == "false":
            display_durum = "-"
        
        if app.current_collection == "AppBanners":
            if durum.lower() in ["true", "aktif"]:
                display_durum = "✅ Yayında"
                durum_color = "#10B981"
        
        durum_badge = ctk.CTkButton(card, text=display_durum.upper(), font=ctk.CTkFont(size=22, weight="bold"), fg_color=durum_color, text_color="white", corner_radius=8, width=44, height=44, hover=False)
        durum_badge.grid(row=0, column=1, rowspan=2, padx=(20, 10) if (app.current_collection == "AppBanners" or app.current_collection == "users") else 20, pady=15, sticky="e")

        if app.current_collection == "AppBanners":
            def make_delete_cmd(b_id):
                def cmd():
                    import tkinter.messagebox as messagebox
                    if messagebox.askyesno("Onay", "Bu afişi kalıcı olarak silmek istediğinize emin misiniz?"):
                        try:
                            import database
                            database.delete_data("Kampanyalar", b_id)
                            messagebox.showinfo("Başarılı", "Afiş başarıyla silindi.")
                            app.load_list("AppBanners")
                        except Exception as e:
                            messagebox.showerror("Hata", f"Silinirken hata oluştu: {e}")
                return cmd
                
            btn_del = ctk.CTkButton(card, text="" if getattr(app, "trash_icon", None) else "🗑️", image=getattr(app, "trash_icon", None), width=44, height=44, corner_radius=8, font=ctk.CTkFont(size=18), fg_color="#FEE2E2", hover_color="#FECACA", text_color="#EF4444", command=make_delete_cmd(item.get("id")))
            btn_del.grid(row=0, column=2, rowspan=2, padx=(0, 20), pady=15, sticky="e")
            
        elif app.current_collection == "top_categories":
            def make_del_cat_cmd(c_id):
                def cmd():
                    import tkinter.messagebox as messagebox
                    if messagebox.askyesno("Onay", "Bu ana ekran kategorisini silmek istediğinize emin misiniz?"):
                        try:
                            import database
                            database.delete_data("top_categories", c_id)
                            messagebox.showinfo("Başarılı", "Kategori başarıyla silindi.")
                            app.load_list("top_categories")
                        except Exception as e:
                            messagebox.showerror("Hata", f"Silinirken hata oluştu: {e}")
                return cmd
                
            btn_del_cat = ctk.CTkButton(card, text="" if getattr(app, "trash_icon", None) else "🗑️", image=getattr(app, "trash_icon", None), width=44, height=44, corner_radius=8, font=ctk.CTkFont(size=18), fg_color="#FEE2E2", hover_color="#FECACA", text_color="#EF4444", command=make_del_cat_cmd(item.get("id")))
            btn_del_cat.grid(row=0, column=2, rowspan=2, padx=(0, 20), pady=15, sticky="e")
            
        if app.current_collection == "users":
            def make_chat_cmd(u_id, u_data):
                def cmd():
                    import tkinter.messagebox as messagebox
                    try:
                        import database
                        chat_ref = database.db.collection('chats').document(u_id)
                        chat_ref.set({
                            'userId': u_id,
                            'userName': u_data.get('name', 'İsimsiz'),
                            'userPhone': u_data.get('phone', ''),
                            'unreadByAdmin': 0,
                            'timestamp': database.firestore.SERVER_TIMESTAMP,
                            'lastMessage': 'Destek tarafından sohbet başlatıldı'
                        }, merge=True)
                        app.select_menu("SupportChats")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Sohbet başlatılamadı: {e}")
                return cmd
                
            btn_chat = ctk.CTkButton(card, text="💬 Sohbet", width=100, height=36, corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#DBEAFE", hover_color="#BFDBFE", text_color="#2563EB", border_width=1, border_color="#93C5FD", command=make_chat_cmd(item.get("id", item.get("userId")), item))
            btn_chat.grid(row=0, column=2, rowspan=2, padx=(0, 20), pady=15, sticky="e")

        def create_modal_cmd(item_ref, badge_ref):
            def _update_badge(new_status):
                new_color = "#10B981" if new_status.lower() in ["aktif", "true", "delivered", "completed", "teslim edildi"] else "#EF4444"
                badge_ref.configure(text=new_status, fg_color=new_color)
            def cmd(event):
                app.open_detail_modal(item_ref, update_callback=_update_badge)
            return cmd

        cmd = create_modal_cmd(item, durum_badge)
        card.bind("<Button-1>", cmd)
        title.bind("<Button-1>", cmd)
        desc.bind("<Button-1>", cmd)
        durum_badge.bind("<Button-1>", cmd)

def _render_splash_upload_section(app):
    import os
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.messagebox as messagebox
    import threading
    try:
        import database
    except ImportError:
        pass

    frame = ctk.CTkFrame(app.content_scroll, fg_color="white", corner_radius=16, border_color="#E2E8F0", border_width=2)
    frame.pack(fill="x", pady=(0, 20), padx=5)
    
    lbl_title = ctk.CTkLabel(frame, text="Müşteri Uygulaması Giriş Animasyonu", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B")
    lbl_title.pack(pady=(15, 5))
    
    lbl_info = ctk.CTkLabel(frame, text="Masaüstünüzden seçeceğiniz medya dosyası uygulamanın yeni açılış ekranı olacaktır.", font=ctk.CTkFont(size=14), text_color="#64748B")
    lbl_info.pack(pady=(0, 15))
    
    def on_upload():
        file_path = filedialog.askopenfilename(
            title="Giriş Animasyonu Seçin",
            filetypes=[("Medya", "*.mp4 *.jpg *.jpeg *.png *.json *.lottie"), ("Tüm Dosyalar", "*.*")]
        )
        if not file_path:
            return
            
        def process_upload():
            btn_upload.configure(text="Yükleniyor... Lütfen Bekleyin", state="disabled")
            app.update_idletasks()
            try:
                public_url = database.upload_file(file_path)
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in [".mp4", ".mov"]:
                    media_type = "video"
                elif file_ext in [".json", ".lottie"]:
                    media_type = "lottie"
                else:
                    media_type = "image"
                
                database.set_data("AppConfig", "SplashScreen", {
                    "url": public_url,
                    "type": media_type,
                    "updatedAt": firestore.SERVER_TIMESTAMP if 'firestore' in globals() else "now"
                })
                
                messagebox.showinfo("Başarılı", "Giriş animasyonu güncellendi! Uygulamayı yeniden başlatanlar görecektir.")
            except Exception as e:
                messagebox.showerror("Hata", f"Yükleme sırasında hata oluştu:\n{e}")
            finally:
                btn_upload.configure(text="✨ Medya Yükle", state="normal")
                
        threading.Thread(target=process_upload, daemon=True).start()
        
    btn_upload = ctk.CTkButton(frame, text="✨ Medya Yükle", font=ctk.CTkFont(size=15, weight="bold"), fg_color="#6366F1", hover_color="#4F46E5", text_color="white", corner_radius=12, height=44, border_width=2, border_color="#4338CA", command=on_upload)
    btn_upload.pack(pady=(0, 15))

def _render_app_banners_upload_section(app):
    import os
    import tkinter as tk
    from tkinter import filedialog
    import tkinter.messagebox as messagebox
    import threading
    try:
        import database
    except ImportError:
        pass

    frame = ctk.CTkFrame(app.content_scroll, fg_color="white", corner_radius=16, border_color="#E2E8F0", border_width=2)
    frame.pack(fill="x", pady=(0, 20), padx=5)
    
    lbl_title = ctk.CTkLabel(frame, text="Mobil Üst Afiş Reklamı Ekle", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B")
    lbl_title.pack(pady=(15, 5))
    
    lbl_info = ctk.CTkLabel(frame, text="Uygulamanın en üstünde kayan reklamlara yeni bir afiş ekleyin.", font=ctk.CTkFont(size=14), text_color="#64748B")
    lbl_info.pack(pady=(0, 15))
    
    try:
        dukkanlar = database.get_data("Dukkanlar")
    except:
        dukkanlar = []
        
    restaurant_map = {"Yok (Sadece Özel Reklam / Tıklanmaz)": ""}
    for d in dukkanlar:
        name = d.get("restaurantName", d.get("name", d.get("İsim", "Bilinmiyor")))
        restaurant_map[name] = d.get("mugut_id", d.get("id", ""))
        
    names = list(restaurant_map.keys())

    ctk.CTkLabel(frame, text="Tıklanınca Gidilecek Restoran:", font=ctk.CTkFont(weight="bold"), text_color="#581C87").pack(anchor="w", pady=(5, 0), padx=20)
    selected_shop = ctk.StringVar(value=names[0])
    ctk.CTkOptionMenu(frame, values=names, variable=selected_shop, fg_color="#9333EA", button_color="#7E22CE").pack(fill="x", pady=5, padx=20)
    
    ctk.CTkLabel(frame, text="Afiş Başlığı (Yönetim için):", font=ctk.CTkFont(weight="bold"), text_color="#581C87").pack(anchor="w", pady=(10, 0), padx=20)
    entry_title = ctk.CTkEntry(frame, placeholder_text="Örn: Coca-Cola Sponsorluğu veya KFC Fırsatı")
    entry_title.pack(fill="x", pady=5, padx=20)
    
    def on_upload():
        file_path = filedialog.askopenfilename(
            title="Afiş Medyası Seçin",
            filetypes=[("Medya", "*.mp4 *.jpg *.jpeg *.png *.json *.lottie"), ("Tüm Dosyalar", "*.*")]
        )
        if not file_path:
            return
            
        def process_upload():
            btn_upload.configure(text="Yükleniyor... Lütfen Bekleyin", state="disabled")
            app.update_idletasks()
            try:
                public_url = database.upload_file(file_path)
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in [".mp4", ".mov"]:
                    media_type = "video"
                elif file_ext in [".json", ".lottie"]:
                    media_type = "lottie"
                else:
                    media_type = "image"
                
                shop_name = selected_shop.get()
                shop_id = restaurant_map.get(shop_name, "")
                title_val = entry_title.get().strip()
                if not title_val:
                    title_val = "Genel Afiş Reklamı" if not shop_id else f"{shop_name} Afişi"

                database.set_data("AppBanners", None, {
                    "image": public_url,
                    "imageUrl": public_url,
                    "mediaType": media_type,
                    "title": title_val,
                    "description": "",
                    "shopId": shop_id,
                    "shop_id": shop_id,
                    "createdAt": "now"
                })
                
                messagebox.showinfo("Başarılı", "Yeni Afiş Reklamı başarıyla eklendi!")
                app.after(0, lambda: app.load_list("AppBanners"))
            except Exception as e:
                messagebox.showerror("Hata", f"Yükleme sırasında hata oluştu:\n{e}")
                try:
                    btn_upload.configure(text="✨ Afiş Yükle", state="normal")
                except:
                    pass
                
        threading.Thread(target=process_upload, daemon=True).start()
        
    btn_upload = ctk.CTkButton(frame, text="✨ Afiş Yükle", font=ctk.CTkFont(size=15, weight="bold"), fg_color="#6366F1", hover_color="#4F46E5", text_color="white", corner_radius=12, height=44, border_width=2, border_color="#4338CA", command=on_upload)
    btn_upload.pack(pady=(15, 20))
