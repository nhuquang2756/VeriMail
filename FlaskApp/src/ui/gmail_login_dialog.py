"""
Gmail Login Dialog - Simple Tkinter Version
Cửa sổ đơn giản để nhập email và password
"""

import tkinter as tk
from tkinter import messagebox
import json
from pathlib import Path

class GmailLoginDialog:
    def __init__(self):
        self.email = None
        self.password = None
        self.result = False
        self.config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        
    def show(self):
        """Hiển thị dialog đăng nhập"""
        # Thử load từ config trước
        if self._try_load_from_config():
            return self.email, self.password
        
        # Tạo window
        root = tk.Tk()
        root.title("Đăng nhập Gmail - AI Spam Detector")
        root.geometry("500x350")
        root.resizable(False, False)
        root.configure(bg='#f0f0f0')
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - 250
        y = (root.winfo_screenheight() // 2) - 175
        root.geometry(f"500x350+{x}+{y}")
        
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
        
        # Info
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
        
        # Help link
        help_label = tk.Label(
            content,
            text="💡 Tạo App Password: myaccount.google.com/apppasswords",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#4F46E5',
            cursor='hand2'
        )
        help_label.pack(pady=(0, 20))
        help_label.bind('<Button-1>', lambda e: self._open_help())
        
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
            
            self.email = email
            self.password = password
            self.result = True
            
            # Hỏi lưu config
            if messagebox.askyesno("Lưu thông tin", "Lưu email và password vào config.json?", parent=root):
                self._save_to_config()
            
            root.quit()
            root.destroy()
        
        def do_cancel():
            self.result = False
            root.quit()
            root.destroy()
        
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
        
        # Bind Enter key
        root.bind('<Return>', lambda e: do_login())
        root.bind('<Escape>', lambda e: do_cancel())
        
        # Run
        root.mainloop()
        
        if self.result:
            return self.email, self.password
        return None, None
    
    def _try_load_from_config(self):
        """Load từ config nếu có"""
        try:
            if not self.config_path.exists():
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.email = config.get('email', '')
            self.password = config.get('password', '')
            
            if self.email and self.password:
                self.result = True
                return True
            
            return False
        except:
            return False
    
    def _save_to_config(self):
        """Lưu vào config"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                example_path = self.config_path.parent / "config.example.json"
                if example_path.exists():
                    with open(example_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {}
            
            config['email'] = self.email
            config['password'] = self.password
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Không thể lưu config: {e}")
    
    def _open_help(self):
        """Mở trang App Password"""
        import webbrowser
        webbrowser.open("https://myaccount.google.com/apppasswords")
