# 🛡️ AI Spam Detector - Flask Web Application

Hệ thống phát hiện tin nhắn rác thông minh sử dụng Machine Learning với giao diện web Flask hiện đại.

## ✨ Tính năng

### 1. **Phân tích văn bản đơn**
- Nhập trực tiếp nội dung tin nhắn cần kiểm tra
- Hỗ trợ tiếng Việt và tiếng Anh
- So sánh kết quả từ nhiều mô hình AI

### 2. **Phân tích CSV hàng loạt**
- Upload file CSV chứa nhiều tin nhắn
- Phân tích hàng loạt và xuất báo cáo
- Tải xuống kết quả dưới dạng CSV

### 3. **Email Monitor**
- Kết nối Gmail qua App Password
- Quét hộp thư tự động
- Phân loại email spam/ham real-time

## 🚀 Cài đặt

### Yêu cầu
- Python 3.8+
- pip

### Các bước cài đặt

```bash
# 1. Clone repository
git clone <repository-url>
cd Streamlit

# 2. Tạo virtual environment
python -m venv myenv

# 3. Kích hoạt virtual environment
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Chạy ứng dụng
python app.py
```

Mở trình duyệt tại: **http://localhost:5000**

## 📁 Cấu trúc dự án

```
Streamlit/
├── app.py                  # Flask application chính
├── auto_checker.py         # Background email checker
├── requirements.txt        # Python dependencies
├── config/
│   ├── config.json        # Cấu hình (email, telegram)
│   └── config.example.json
├── models/
│   ├── classifiers/       # ML models (.pkl)
│   └── preprocessors/     # TF-IDF vectorizers
├── src/
│   ├── core/              # Core logic (ModelManager, TextProcessor)
│   ├── services/          # Services (EmailService, NotificationService)
│   └── utils/             # Utilities (Logger, ConfigLoader)
├── static/
│   ├── css/style.css      # Stylesheet
│   └── js/app.js          # Frontend JavaScript
├── templates/
│   └── index.html         # HTML template
└── logs/                  # Application logs
```

## 🤖 Mô hình AI có sẵn

1. **Logistic Regression**
2. **Naive Bayes**
3. **Decision Tree**
4. **Random Forest**
5. **SVM**
6. **XGBoost**
7. **Voting Classifier** ⭐ (Khuyến nghị - độ chính xác cao nhất)

## 📧 Cấu hình Email Monitor

### Tạo Gmail App Password

1. Truy cập: https://myaccount.google.com/apppasswords
2. Đăng nhập tài khoản Gmail
3. Tạo App Password mới (16 ký tự)
4. Sử dụng password này trong Email Monitor

### Cấu hình file `config/config.json`

```json
{
  "email": {
    "address": "your-email@gmail.com",
    "app_password": "your-16-char-password"
  },
  "telegram": {
    "bot_token": "your-bot-token",
    "chat_id": "your-chat-id"
  }
}
```

## 🔧 API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/` | GET | Trang chủ |
| `/api/predict` | POST | Phân tích văn bản đơn |
| `/api/predict-batch` | POST | Phân tích CSV |
| `/api/models` | GET | Danh sách models |
| `/api/gmail/connect` | POST | Kết nối Gmail |
| `/api/gmail/fetch` | POST | Lấy danh sách email |
| `/api/gmail/disconnect` | POST | Ngắt kết nối Gmail |

## 📊 Logs

Tất cả hoạt động được ghi log tại: `logs/app.log`

```bash
# Xem log real-time
Get-Content logs/app.log -Tail 50 -Wait
```

## 🎨 UI/UX Features

- ✅ Modern Light Theme
- ✅ Font Awesome 6 Icons
- ✅ Responsive Design (Mobile/Tablet/Desktop)
- ✅ Sidebar Navigation
- ✅ Interactive Components
- ✅ Loading Animations

## 🛠️ Tech Stack

- **Backend:** Flask 3.0
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **ML:** scikit-learn, XGBoost
- **Icons:** Font Awesome 6
- **Fonts:** Google Fonts (Outfit)

## 📝 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👨‍💻 Tác giả

Graduation Project - AI Spam Detector

---

**Lưu ý:** Đây là phiên bản Flask, thay thế cho phiên bản Streamlit cũ để có hiệu năng và khả năng tùy biến tốt hơn.
