import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
try:
    import winsound
except ImportError:
    winsound = None
import ui_chat
import ui_data_grid
import ui_modals
import ui_campaigns
import ui_categories
import ui_notifications
import ui_texts
import ui_wallet
try:
    import database
except ImportError:
    pass

# Tema ayarları
ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")  

class MugytKampanyaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mugyt Kampanya Yönetimi")
        self.geometry("1000x650")
        try:
            self.iconbitmap("logo.ico")
        except:
            pass
        self.configure(fg_color="#F1F5F9")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ----------------------------------------------------
        # 1. SOL MENÜ (SIDEBAR)
        # ----------------------------------------------------
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=260, corner_radius=0, fg_color="#5D3EBC")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 

        try:
            from PIL import Image
            logo_img = ctk.CTkImage(light_image=Image.open("logo.jpg"), dark_image=Image.open("logo.jpg"), size=(120, 120))
            self.logo_img_label = ctk.CTkLabel(self.sidebar_frame, text="", image=logo_img)
            self.logo_img_label.grid(row=0, column=0, padx=20, pady=(30, 0))
            
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MUGT GELSİN", font=ctk.CTkFont(size=18, weight="bold"), text_color="white")
            self.logo_label.grid(row=1, column=0, padx=20, pady=(5, 30))
            start_row = 2
        except Exception as e:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MUGT GELSİN", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
            self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
            start_row = 1

        # Menü Butonları
        self.lbl_kampanya = ctk.CTkLabel(self.sidebar_frame, text="KAMPANYA & REKLAM", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        self.lbl_kampanya.grid(row=start_row, column=0, padx=20, pady=(5, 0), sticky="w")

        self.btn_restoran = ctk.CTkButton(self.sidebar_frame, text="Restoran Kampanyaları", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("Kampanyalar"))
        self.btn_restoran.grid(row=start_row+1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_top_categories = ctk.CTkButton(self.sidebar_frame, text="Ana Ekran Kategorileri", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="#10B981", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("top_categories"))
        self.btn_top_categories.grid(row=start_row+2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_mugut = ctk.CTkButton(self.sidebar_frame, text="Mugt Kampanyası", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("MugutKampanyalar"))
        self.btn_mugut.grid(row=start_row+3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_sponsor = ctk.CTkButton(self.sidebar_frame, text="Sponsorlu Restoranlar", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("SponsorluRestoranlar"))
        self.btn_sponsor.grid(row=start_row+4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_splash = ctk.CTkButton(self.sidebar_frame, text="Açılış Animasyonu", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("Reklamlar"))
        self.btn_splash.grid(row=start_row+5, column=0, padx=20, pady=5, sticky="ew")

        self.btn_app_banners = ctk.CTkButton(self.sidebar_frame, text="Mobil Üst Afiş Reklamları", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("AppBanners"))
        self.btn_app_banners.grid(row=start_row+6, column=0, padx=20, pady=5, sticky="ew")

        self.btn_dashboard_banner = ctk.CTkButton(self.sidebar_frame, text="Fırsatlar Afişi", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="#FACC15", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("DashboardBanners"))
        self.btn_dashboard_banner.grid(row=start_row+7, column=0, padx=20, pady=5, sticky="ew")

        self.btn_notifications = ctk.CTkButton(self.sidebar_frame, text="Bildirim Gönder", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="#FFB020", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("Notifications"))
        self.btn_notifications.grid(row=start_row+8, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_texts = ctk.CTkButton(self.sidebar_frame, text="Uygulama Yazıları", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("AppTexts"))
        self.btn_texts.grid(row=start_row+9, column=0, padx=20, pady=5, sticky="ew")

        self.btn_wallet = ctk.CTkButton(self.sidebar_frame, text="Biriken Kuponlarım", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="#10B981", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("WalletConfig"))
        self.btn_wallet.grid(row=start_row+10, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.lbl_sistem = ctk.CTkLabel(self.sidebar_frame, text="SİSTEM YÖNETİMİ", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        self.lbl_sistem.grid(row=start_row+11, column=0, padx=20, pady=(5, 0), sticky="w")

        self.btn_siparis = ctk.CTkButton(self.sidebar_frame, text="Siparişler", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("Emirler"))
        self.btn_siparis.grid(row=start_row+12, column=0, padx=20, pady=5, sticky="ew")

        self.btn_restoranlar = ctk.CTkButton(self.sidebar_frame, text="Restoranlar", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("Dukkanlar"))
        self.btn_restoranlar.grid(row=start_row+13, column=0, padx=20, pady=5, sticky="ew")

        self.btn_kullanicilar = ctk.CTkButton(self.sidebar_frame, text="Kullanıcılar", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("users"))
        self.btn_kullanicilar.grid(row=start_row+14, column=0, padx=20, pady=5, sticky="ew")

        self.btn_musterihiz = ctk.CTkButton(self.sidebar_frame, text="Müşteri Hizmetleri", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("SupportChats"))
        self.btn_musterihiz.grid(row=start_row+15, column=0, padx=20, pady=5, sticky="ew")

        self.btn_gecmis = ctk.CTkButton(self.sidebar_frame, text="Geçmiş Sohbetler", font=ctk.CTkFont(size=14, weight="bold"), corner_radius=8, height=40, fg_color="transparent", text_color="white", hover_color="#462E8E", border_width=1, border_color="#7C3AED", anchor="w", command=lambda: self.select_menu("ArchivedChats"))
        self.btn_gecmis.grid(row=start_row+16, column=0, padx=20, pady=5, sticky="ew")

        self.sidebar_frame.grid_rowconfigure(start_row+17, weight=1)

        # ----------------------------------------------------
        # 2. SAĞ İÇERİK ALANI (MAIN FRAME)
        # ----------------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="white", height=70, corner_radius=12)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_propagate(False)

        self.page_title = ctk.CTkLabel(self.header_frame, text="Sayfa Yükleniyor...", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B")
        self.page_title.place(relx=0.03, rely=0.5, anchor="w")

        # Arama Çubuğu
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda name, index, mode, sv=self.search_var: self.render_list())
        self.search_entry = ctk.CTkEntry(self.header_frame, textvariable=self.search_var, placeholder_text="Arama yap...", width=300, height=36, corner_radius=8, border_color="#CBD5E1")
        self.search_entry.place(relx=0.5, rely=0.5, anchor="center")

        self.add_btn = ctk.CTkButton(self.header_frame, text="+ Yeni Ekle", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#6366F1", hover_color="#4F46E5", text_color="white", corner_radius=8, height=40, border_width=2, border_color="#4338CA", command=self.open_add_modal)
        self.add_btn.place(relx=0.97, rely=0.5, anchor="e")

        self.content_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.content_scroll.grid(row=1, column=0, sticky="nsew")

        self.current_data = [] # Firebase'den çekilen ham veriyi tutar

        # Check Firebase connection
        self.db_connected = False
        try:
            database.initialize_firebase()
            self.db_connected = True
            database.start_global_listener(self.on_global_new_message)
        except FileNotFoundError as e:
            self.show_error("Bağlantı Hatası", str(e))
        except Exception as e:
            self.show_error("Kritik Hata", f"Veritabanına bağlanılamadı:\n{e}")

        # Başlangıçta ilk menüyü seç
        self.current_collection = "Kampanyalar"
        self.select_menu(self.current_collection)

    def on_global_new_message(self, data):
        # Play a sound asynchronously
        try:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass
            
        # UI'ı tamamen yenilemek (load_list) CustomTkinter'da çökmeye ve 
        # kullanıcının yazdığı yazının silinmesine neden oluyor.
        # Bu yüzden sadece ses çalıyoruz. Mevcut sohbetteyse zaten listen_to_chat güncelliyor.

    def show_error(self, title, message):
        error_card = ctk.CTkFrame(self.content_scroll, fg_color="#FEE2E2", corner_radius=12, border_color="#EF4444", border_width=2)
        error_card.pack(fill="x", pady=20, padx=20)
        
        lbl_title = ctk.CTkLabel(error_card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#B91C1C")
        lbl_title.pack(pady=(20, 5))
        
        lbl_msg = ctk.CTkLabel(error_card, text=message, font=ctk.CTkFont(size=14), text_color="#7F1D1D")
        lbl_msg.pack(pady=(0, 20), padx=20)

    def select_menu(self, collection_name):
        self.current_collection = collection_name
        self.btn_restoran.configure(fg_color="transparent", text_color="white")
        self.btn_top_categories.configure(fg_color="transparent", text_color="white")
        self.btn_mugut.configure(fg_color="transparent", text_color="white")
        self.btn_sponsor.configure(fg_color="transparent", text_color="white")
        self.btn_splash.configure(fg_color="transparent", text_color="white")
        self.btn_app_banners.configure(fg_color="transparent", text_color="white")
        self.btn_dashboard_banner.configure(fg_color="transparent", text_color="white")
        self.btn_notifications.configure(fg_color="transparent", text_color="white")
        self.btn_texts.configure(fg_color="transparent", text_color="white")
        self.btn_wallet.configure(fg_color="transparent", text_color="white")
        self.btn_siparis.configure(fg_color="transparent", text_color="white")
        self.btn_restoranlar.configure(fg_color="transparent", text_color="white")
        self.btn_kullanicilar.configure(fg_color="transparent", text_color="white")
        self.btn_musterihiz.configure(fg_color="transparent", text_color="white")
        self.btn_gecmis.configure(fg_color="transparent", text_color="white")

        # Make sure search and add button are visible by default
        if hasattr(self, 'search_entry') and hasattr(self, 'add_btn'):
            self.search_entry.place(relx=0.5, rely=0.5, anchor="center")
            self.add_btn.place(relx=0.97, rely=0.5, anchor="e")

        # Update button colors & title
        if collection_name == "Kampanyalar":
            self.btn_restoran.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Restoran Kampanyaları")
        elif collection_name == "top_categories":
            self.btn_top_categories.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Ana Ekran Kategorileri")
        elif collection_name == "MugutKampanyalar":
            self.btn_mugut.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Mugt Kampanyası (Genel)")
        elif collection_name == "SponsorluRestoranlar":
            self.btn_sponsor.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Sponsorlu Restoranlar")
        elif collection_name == "ArchivedChats":
            self.btn_gecmis.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Geçmiş Sohbetler")
        elif collection_name == "Reklamlar":
            self.page_title.configure(text="Açılış Animasyonu")
            self.btn_splash.configure(fg_color="white", text_color="#5D3EBC")
        elif collection_name == "AppBanners":
            self.page_title.configure(text="Mobil Üst Afiş Reklamları")
            self.btn_app_banners.configure(fg_color="white", text_color="#5D3EBC")
        elif collection_name == "DashboardBanners":
            self.page_title.configure(text="Fırsatlar Afişi")
            self.btn_dashboard_banner.configure(fg_color="white", text_color="#5D3EBC")
        elif collection_name == "Notifications":
            self.btn_notifications.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Bildirim Merkezi")
            self.search_entry.place_forget()
            self.add_btn.place_forget()
            ui_notifications.render(self.content_scroll)
            return
        elif collection_name == "AppTexts":
            self.btn_texts.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Uygulama Yazıları")
            self.search_entry.place_forget()
            self.add_btn.place_forget()
            ui_texts.render(self.content_scroll)
            return
        elif collection_name == "WalletConfig":
            self.btn_wallet.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="💰 Biriken Kuponlarım / Cüzdan")
            self.search_entry.place_forget()
            self.add_btn.place_forget()
            ui_wallet.render(self.content_scroll)
            return
        elif collection_name == "Emirler":
            self.btn_siparis.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Siparişler")
        elif collection_name == "Dukkanlar":
            self.btn_restoranlar.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Restoran Yönetimi")
        elif collection_name == "users":
            self.btn_kullanicilar.configure(fg_color="white", text_color="#5D3EBC")
            self.page_title.configure(text="Kullanıcılar")
        elif collection_name == "SupportChats" or collection_name == "ArchivedChats":
            if collection_name == "SupportChats":
                self.btn_musterihiz.configure(fg_color="white", text_color="#5D3EBC")
            else:
                self.btn_gecmis.configure(fg_color="white", text_color="#5D3EBC")
            
        self.load_list(collection_name)

    def load_list(self, collection_name):
        if hasattr(self, 'chat_frame') and self.chat_frame.winfo_exists():
            self.chat_frame.destroy()

        for widget in self.content_scroll.winfo_children():
            widget.destroy()

        if not self.db_connected:
            self.show_error("Bağlantı Yok", "serviceAccountKey.json dosyası eksik olduğu için canlı veri çekilemiyor.\nFirebase Console'dan anahtarı indirip klasöre ekleyin.")
            return

        loading_lbl = ctk.CTkLabel(self.content_scroll, text="Veriler Yükleniyor...", font=ctk.CTkFont(size=14, slant="italic"), text_color="#64748B")
        loading_lbl.pack(pady=40)

        def fetch_task():
            try:
                if collection_name == "SupportChats":
                    self.current_data = database.get_support_chats()
                elif collection_name == "ArchivedChats":
                    self.current_data = database.get_archived_chats()
                else:
                    self.current_data = database.get_data(collection_name)
                self.after(0, lambda: self.finish_load(collection_name, True))
            except Exception as e:
                self.after(0, lambda: self.finish_load(collection_name, False, str(e)))

        threading.Thread(target=fetch_task, daemon=True).start()

    def finish_load(self, collection_name, success, error_msg=None):
        for w in self.content_scroll.winfo_children():
            w.destroy()
            
        if not success:
            self.show_error("Okuma Hatası", error_msg)
            return

        if collection_name in ["SupportChats", "ArchivedChats"]:
            self.content_scroll.grid_forget()
            self.chat_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.chat_frame.grid(row=1, column=0, sticky="nsew")
            self.render_chat_ui()
        else:
            self.content_scroll.grid(row=1, column=0, sticky="nsew")
            self.render_list()

    def render_chat_ui(self):
        ui_chat.render_chat_ui(self)

    def render_list(self):
        ui_data_grid.render_list(self)

    def open_detail_modal(self, item, update_callback=None):
        ui_modals.open_detail_modal(self, item, update_callback=update_callback)

    def open_add_modal(self):
        ui_modals.open_add_modal(self)

    def open_sponsor_modal(self):
        ui_modals.open_sponsor_modal(self)

if __name__ == "__main__":
    app = MugytKampanyaApp()
    app.mainloop()
