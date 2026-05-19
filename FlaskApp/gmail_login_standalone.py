"""
Gmail Login Dialog - Standalone Script
Chạy riêng biệt để tránh conflict với pystray
"""

import tkinter as tk
from tkinter import messagebox
import json
import sys
from pathlib import Path

def show_login_dialog():
    """Hiển thị dialog và trả về email, password qua stdout"""
    
    config_path = Path(__file__).parent / "config" / "config.json"
    
    # Thử load từ config
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            email = config.get('email', '')
            password = config.get('password', '')
            
            if email and password:
                # Trả về qua stdout
                print(f"{email}|||{password}")
                sys.exit(0)
    except:
        pass
    
    # Tạo dialog
    root = tk.Tk()
    root.title("Đăng nhập Gmail - AI Spam Detector")
    root.geometry("500x350")
    root.resizable(False, False)
    root.configure(bg='#f0f0f0')
    
    # Center
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 250
    y = (root.winfo_screenheight() // 2) - 175
    root.geometry(f"500x350+{x}+{y}")
    
    # Always on top
    root.attributes('-topmost', True)
    root.after(1000, lambda: root.attributes('-topmost', False))
    
    # Header
    header = tk.Frame(root, bg='#4F46E5', height=80)
    header.pack(fill='x')
    header.pack_propagate(False)
    
    tk.Label(
        header,
        text="🔐 Đăng nhập Gmail",
        font=('Arial', 20, 'bold'),
        bg='#4F46E5',
        fg='white'
    ).pack(expand=True)
    
    # Content
    content = tk.Frame(root, bg='#f0f0f0', padx=40, pady=30)
    content.pack(fill='both', expand=True)
    
    tk.Label(
        content,
        text="Nhập thông tin Gmail để sử dụng Email Monitor",
        font=('Arial', 10),
        bg='#f0f0f0',
        fg='#666'
    ).pack(pady=(0, 20))
    
    # Email
    tk.Label(
        content,
        text="📧 Email Gmail:",
        font=('Arial', 10, 'bold'),
        bg='#f0f0f0',
        anchor='w'
    ).pack(fill='x', pady=(0, 5))
    
    email_var = tk.StringVar()
    email_entry = tk.Entry(
        content,
        textvariable=email_var,
        font=('Arial', 11),
        relief='solid',
        bd=1
    )
    email_entry.pack(fill='x', ipady=8, pady=(0, 15))
    email_entry.focus()
    
    # Password
    tk.Label(
        content,
        text="🔑 App Password (16 ký tự):",
        font=('Arial', 10, 'bold'),
        bg='#f0f0f0',
        anchor='w'
    ).pack(fill='x', pady=(0, 5))
    
    password_var = tk.StringVar()
    password_entry = tk.Entry(
        content,
        textvariable=password_var,
        font=('Arial', 11),
        relief='solid',
        bd=1,
        show='•'
    )
    password_entry.pack(fill='x', ipady=8, pady=(0, 10))
    
    # Help
    def open_help():
        import webbrowser
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    help_label = tk.Label(
        content,
        text="💡 Tạo App Password: myaccount.google.com/apppasswords",
        font=('Arial', 9),
        bg='#f0f0f0',
        fg='#4F46E5',
        cursor='hand2'
    )
    help_label.pack(pady=(0, 20))
    help_label.bind('<Button-1>', lambda e: open_help())
    
    # Buttons
    btn_frame = tk.Frame(content, bg='#f0f0f0')
    btn_frame.pack(fill='x')
    
    def do_login():
        email = email_var.get().strip()
        password = password_var.get().strip()
        
        if not email:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập email!", parent=root)
            email_entry.focus()
            return
        
        if not password or len(password) < 16:
            messagebox.showwarning("Thiếu thông tin", "App Password phải có 16 ký tự!", parent=root)
            password_entry.focus()
            return
        
        # Hỏi lưu
        if messagebox.askyesno("Lưu thông tin", "Lưu vào config.json cho lần sau?", parent=root):
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    example_path = config_path.parent / "config.example.json"
                    if example_path.exists():
                        with open(example_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    else:
                        config = {}
                
                config['email'] = email
                config['password'] = password
                
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
            except:
                pass
        
        # Trả về qua stdout
        print(f"{email}|||{password}")
        root.quit()
        root.destroy()
        sys.exit(0)
    
    def do_cancel():
        root.quit()
        root.destroy()
        sys.exit(1)
    
    tk.Button(
        btn_frame,
        text="Hủy",
        font=('Arial', 10),
        bg='#e0e0e0',
        fg='#333',
        padx=20,
        pady=10,
        relief='flat',
        cursor='hand2',
        command=do_cancel
    ).pack(side='left', padx=(0, 10))
    
    tk.Button(
        btn_frame,
        text="🚀 Kết nối",
        font=('Arial', 10, 'bold'),
        bg='#4F46E5',
        fg='white',
        padx=20,
        pady=10,
        relief='flat',
        cursor='hand2',
        command=do_login
    ).pack(side='right')
    
    root.bind('<Return>', lambda e: do_login())
    root.bind('<Escape>', lambda e: do_cancel())
    
    root.mainloop()

if __name__ == "__main__":
    show_login_dialog()
