import customtkinter as ctk
import tkinter.messagebox as messagebox
try:
    import database
except ImportError:
    pass

def render_chat_ui(app):
    app.chat_frame.grid_columnconfigure(0, weight=1)
    app.chat_frame.grid_columnconfigure(1, weight=3)
    app.chat_frame.grid_rowconfigure(0, weight=1)

    left_frame = ctk.CTkScrollableFrame(app.chat_frame, fg_color="white", corner_radius=12)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    right_frame = ctk.CTkFrame(app.chat_frame, fg_color="white", corner_radius=12)
    right_frame.grid(row=0, column=1, sticky="nsew")
    right_frame.grid_rowconfigure(1, weight=1)

    header_frame = ctk.CTkFrame(right_frame, fg_color="transparent", height=40)
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
    
    app.chat_title = ctk.CTkLabel(header_frame, text="Lütfen sohbet seçin", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1E293B")
    app.chat_title.pack(side="left", padx=5)

    if app.current_collection == "SupportChats":
        def close_current_chat():
            if not app.current_chat_uid: return
            if messagebox.askyesno("Onay", "Bu sohbeti tamamen sonlandırmak ve silmek istediğinize emin misiniz? Müşterinin ekranından da silinecektir."):
                try:
                    if database.chat_listener:
                        database.chat_listener.unsubscribe()
                    database.close_chat(app.current_chat_uid)
                    app.load_list("SupportChats")
                except Exception as e:
                    messagebox.showerror("Hata", str(e))

        close_btn = ctk.CTkButton(header_frame, text="Sohbeti Sonlandır ✕", width=120, fg_color="#EF4444", hover_color="#DC2626", text_color="white", command=close_current_chat)
        close_btn.pack(side="right", padx=5)

    app.msg_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
    app.msg_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    input_frame = ctk.CTkFrame(right_frame, fg_color="transparent", height=60)
    
    if app.current_collection == "SupportChats":
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        app.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Mesajınızı yazın...", font=ctk.CTkFont(size=14))
        app.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    
    app.current_chat_uid = None

    def load_messages(uid, name):
        if not uid: return
        app.current_chat_uid = uid
        app.chat_title.configure(text=name)
        for w in app.msg_scroll.winfo_children():
            w.destroy()
            
        loading = ctk.CTkLabel(app.msg_scroll, text="Mesajlar yükleniyor...", text_color="#64748B")
        loading.pack(pady=20)
        
        def render_msgs_ui(msgs):
            for w in app.msg_scroll.winfo_children():
                w.destroy()
            if not msgs:
                lbl = ctk.CTkLabel(app.msg_scroll, text="Henüz mesaj yok.", text_color="#64748B")
                lbl.pack(pady=20)
            for m in msgs:
                is_admin = m.get('isAdmin', False)
                align = "e" if is_admin else "w"
                color = "#E0F2FE" if is_admin else "#F1F5F9"
                
                m_frame = ctk.CTkFrame(app.msg_scroll, fg_color="transparent")
                m_frame.pack(fill="x", pady=5)
                
                lbl = ctk.CTkLabel(m_frame, text=m.get('text', ''), fg_color=color, text_color="#1E293B", corner_radius=8, padx=10, pady=5, font=ctk.CTkFont(size=14), wraplength=400, justify="left")
                lbl.pack(side="right" if align == "e" else "left")
            
            app.msg_scroll.update_idletasks()
            app.msg_scroll._parent_canvas.yview_moveto(1.0)
            
        try:
            if app.current_collection == "SupportChats":
                database.listen_to_chat(uid, lambda msgs: app.after(0, lambda: render_msgs_ui(msgs)))
            else:
                msgs = database.get_archived_messages(uid)
                render_msgs_ui(msgs)
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def send_msg(event=None):
        if app.current_collection != "SupportChats": return
        text = app.msg_entry.get().strip()
        if not text or not app.current_chat_uid: return
        try:
            database.send_chat_message(app.current_chat_uid, text)
            app.msg_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    if app.current_collection == "SupportChats":
        send_btn = ctk.CTkButton(input_frame, text="Gönder", width=80, fg_color="#10B981", hover_color="#059669", command=send_msg)
        send_btn.grid(row=0, column=1)
        app.msg_entry.bind("<Return>", send_msg)

    if app.current_collection == "SupportChats":
        def on_new_chat():
            # Kullanıcıları getir ve liste modalı aç
            try:
                if not database.db: database.initialize_firebase()
                users_ref = database.db.collection('users').get()
                
                modal = ctk.CTkToplevel(app)
                modal.title("Kullanıcı Seç")
                modal.geometry("400x500")
                modal.transient(app)
                modal.grab_set()
                
                ctk.CTkLabel(modal, text="Sohbet başlatmak için bir kullanıcı seçin:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
                
                scroll = ctk.CTkScrollableFrame(modal, fg_color="white")
                scroll.pack(fill="both", expand=True, padx=10, pady=10)
                
                for u in users_ref:
                    data = u.to_dict()
                    name = data.get('name', 'İsimsiz')
                    phone = data.get('phone', 'No: Yok')
                    
                    btn = ctk.CTkButton(scroll, text=f"{name}\n{phone}", fg_color="#F1F5F9", text_color="#1E293B", hover_color="#E2E8F0", anchor="w", command=lambda u_doc=u, d=data: start_chat_from_modal(modal, u_doc.id, d))
                    btn.pack(fill="x", pady=2)
                    
            except Exception as e:
                messagebox.showerror("Hata", str(e))
                
        def start_chat_from_modal(modal, uid, data):
            modal.destroy()
            try:
                chat_ref = database.db.collection('chats').document(uid)
                chat_ref.set({
                    'userId': uid,
                    'userName': data.get('name', 'İsimsiz'),
                    'userPhone': data.get('phone', ''),
                    'unreadByAdmin': 0,
                    'timestamp': database.firestore.SERVER_TIMESTAMP,
                    'lastMessage': 'Destek tarafından sohbet başlatıldı'
                }, merge=True)
                messagebox.showinfo("Başarılı", f"{data.get('name', 'İsimsiz')} ile sohbet başlatıldı.")
                app.load_list("SupportChats")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        
        new_btn = ctk.CTkButton(left_frame, text="+ Yeni Sohbet Başlat", font=ctk.CTkFont(weight="bold"), fg_color="#3B82F6", hover_color="#2563EB", command=on_new_chat)
        new_btn.pack(pady=(10, 10), padx=5, fill="x")

    if not app.current_data:
        ctk.CTkLabel(left_frame, text="Sohbet bulunamadı.").pack(pady=20)
    for chat in app.current_data:
        c_frame = ctk.CTkFrame(left_frame, fg_color="#F8FAFC", corner_radius=8, cursor="hand2")
        c_frame.pack(fill="x", pady=5, padx=5)
        name = chat.get('userName', chat.get('userId', 'İsimsiz'))
        unread = chat.get('unreadByAdmin', 0) > 0
        title = name + (" (YENİ)" if unread else "")
        color = "#1E293B" if unread else "#64748B"
        c_lbl = ctk.CTkLabel(c_frame, text=title, font=ctk.CTkFont(size=14, weight="bold" if unread else "normal"), text_color=color)
        c_lbl.pack(anchor="w", padx=10, pady=10)
        
        c_frame.bind("<Button-1>", lambda e, u=chat['id'], n=name: load_messages(u, n))
        c_lbl.bind("<Button-1>", lambda e, u=chat['id'], n=name: load_messages(u, n))

    if app.current_data:
        first = app.current_data[0]
        first_name = first.get('userName', first.get('userPhone', 'İsimsiz'))
        load_messages(first['id'], first_name)
