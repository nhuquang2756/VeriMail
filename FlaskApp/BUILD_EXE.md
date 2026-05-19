# BUILD EXECUTABLE - Hướng dẫn

## Cách 1: Chạy trực tiếp (không cần build exe)

```bash
# Launcher đơn giản
python launcher.py

# Launcher với System Tray
python tray_launcher.py
```

## Cách 2: Build thành file .exe

### Bước 1: Cài đặt PyInstaller

```bash
pip install pyinstaller
```

### Bước 2: Build executable

#### Option A: Launcher đơn giản (console window)

```bash
pyinstaller --onefile --name "AI-Spam-Detector" launcher.py
```

#### Option B: Tray launcher (không có console)

```bash
pyinstaller --onefile --noconsole --name "AI-Spam-Detector" --icon=icon.ico tray_launcher.py
```

**Lưu ý:** Nếu muốn có icon, tạo file `icon.ico` trước.

### Bước 3: Build với tất cả dependencies

```bash
pyinstaller --onefile ^
    --noconsole ^
    --name "AI-Spam-Detector" ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "models;models" ^
    --add-data "config;config" ^
    --hidden-import flask ^
    --hidden-import sklearn ^
    tray_launcher.py
```

### Bước 4: Tìm file .exe

File exe sẽ nằm trong folder: `dist/AI-Spam-Detector.exe`

## Cách 3: Tạo installer với Inno Setup (Windows)

### Bước 1: Download Inno Setup
https://jrsoftware.org/isdl.php

### Bước 2: Tạo file setup script

Xem file `setup_script.iss`

### Bước 3: Compile installer

Mở Inno Setup Compiler và compile file `.iss`

## Lưu ý quan trọng

1. **Virtual Environment:** Nên build trong venv để tránh bao gồm các package không cần thiết.

2. **File size:** File exe có thể lớn (100-200MB) do chứa Python runtime và dependencies.

3. **Antivirus:** Một số antivirus có thể cảnh báo file exe do PyInstaller. Đây là false positive.

4. **Models:** Đảm bảo folder `models/` được đóng gói cùng.

5. **Config:** File `config/config.json` cần được tạo sau khi cài đặt.

## Troubleshooting

### Lỗi: ModuleNotFoundError

Thêm `--hidden-import <module_name>` vào lệnh PyInstaller.

### Lỗi: FileNotFoundError (templates/static)

Sử dụng `--add-data` để bao gồm các folder cần thiết.

### App không chạy sau khi build

Chạy từ command line để xem error message:

```bash
cd dist
AI-Spam-Detector.exe
```
