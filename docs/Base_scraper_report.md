# 📘 Base Scraper Architecture & Documentation

**Dự án:** Vietnam IT Market Analysis & Salary Prediction  
**Module:** Data Collection (Scraping Core)  
**Phiên bản:** 1.0  
**Ngày cập nhật:** 29/01/2026

***

## 1. Tổng quan (Overview)

File `base_scraper.py` chứa class `BaseScraper`. Đây là lớp cha (Parent Class) trừu tượng, đóng vai trò là xương sống cho toàn bộ hệ thống cào dữ liệu.

**Mục đích:**
1. **Quản lý kết nối tập trung:** Xử lý kết nối MongoDB Atlas, bảo mật SSL và xác thực.
2. **Chuẩn hóa dữ liệu:** Đảm bảo mọi dữ liệu cào về đều có đủ siêu dữ liệu (metadata) như nguồn, ngày cào.
3. **Xử lý lỗi:** Tự động bắt lỗi trùng lặp (`DuplicateKeyError`) để scraper không bị dừng đột ngột.

***

## 2. Các thư viện sử dụng (Dependencies)

Giải thích lý do tại sao dự án sử dụng các thư viện này:

| Thư viện     | Vai trò & Lý do sử dụng |
|--------------|-------------------------|
| **`abc`** (Abstract Base Class) | Tạo ra một "khuôn mẫu" bắt buộc. Nó ép buộc các class con (như `ITViecScraper`) phải viết hàm `scrape()`, giúp code đồng bộ. |
| **`pymongo`** | Driver chính thức để Python giao tiếp với MongoDB. Dùng để gửi lệnh `insert`, `find` tới Database. |
| **`certifi`** | **Quan trọng:** Cung cấp chứng chỉ bảo mật (Root CA) mới nhất. Giúp khắc phục lỗi `SSL handshake failed` khi kết nối MongoDB Atlas từ máy cá nhân/Windows. |
| **`logging`** | Ghi nhật ký hoạt động (`INFO`, `ERROR`, `WARNING`) thay vì dùng `print`. Giúp debug lỗi hiệu quả và chuyên nghiệp hơn. |
| **`dotenv`** | Bảo mật. Dùng để đọc mật khẩu DB từ file `.env` thay vì viết cứng (hardcode) trong code. |
| **`datetime`** | Lấy thời gian thực để gắn nhãn thời gian (`crawled_date`) cho dữ liệu. |

***

## 3. Chi tiết các hàm & Input (Function Specifications)

Dưới đây là tài liệu chi tiết về các hàm trong class, đặc biệt là ý nghĩa của các tham số đầu vào (Input).

### 3.1. Hàm khởi tạo `__init__`

Dùng để thiết lập môi trường và kết nối Database ngay khi Scraper được bật lên.

```python
def __init__(self, source_name, db_name="VietnamITMarket", collection_name="raw_jobs"):
```

| Tham số (Input) | Kiểu dữ liệu | Bắt buộc? | Mô tả & Tác dụng |
|-----------------|--------------|-----------|------------------|
| `source_name`   | `str`        | ✅ Có     | Tên nguồn dữ liệu. (VD: "ITviec", "TopCV"). Dùng để phân loại dữ liệu trong Database và tạo Logger riêng biệt. |
| `db_name`       | `str`        | ❌ Không  | Tên Database trên MongoDB. Mặc định là "VietnamITMarket". |
| `collection_name` | `str`     | ❌ Không  | Tên Collection (bảng) lưu trữ. Mặc định là "raw_jobs". |

### 3.2. Hàm lưu dữ liệu `save_job`

Hàm quan trọng nhất để đưa dữ liệu vào kho. Class con sẽ gọi hàm này sau khi cào xong 1 tin tuyển dụng.

```python
def save_job(self, job_data):
```

| Tham số (Input) | Kiểu dữ liệu      | Mô tả chi tiết |
|-----------------|--------------------|----------------|
| `job_data`      | `dict` (Dictionary) | Gói tin chứa thông tin việc làm. Đây là dữ liệu thô mà Scraper con thu thập được. |

**Cấu trúc bắt buộc của `job_data` (Input Schema):**

Để hàm này hoạt động, dictionary `job_data` đầu vào phải chứa ít nhất các trường sau:
- `url` (Bắt buộc): Link gốc của bài đăng (Dùng làm khóa chính để chống trùng).
- `job_title`: Tên công việc.
- `company_name`: Tên công ty.
- (Các trường khác như `salary`, `skills`... có thể có hoặc không)

**Logic xử lý bên trong:**
- Gắn Metadata: Tự động thêm `source` (lấy từ init) và `crawled_date` (giờ hiện tại) vào `job_data`.
- Validate: Kiểm tra xem có `url` không. Nếu không có -> Hủy lưu.
- Insert: Thử lưu vào DB. Nếu trùng URL -> Báo Log Warning và bỏ qua.

### 3.3. Hàm trừu tượng `scrape`

Hàm này chưa có nội dung (logic rỗng).

```python
@abstractmethod
def scrape(self):
```

**Input:** Không có (hoặc tùy biến ở class con).  
**Tác dụng:** Đây là một "lời hứa". Bất kỳ class nào kế thừa `BaseScraper` đều **BẮT BUỘC** phải viết code cho hàm này. Nếu không, chương trình sẽ báo lỗi.

***

## 4. Hướng dẫn sử dụng (Implementation Guide)

Dành cho Developer (Dev A, Dev B...) khi tạo Scraper mới.

### Bước 1: Tạo file `.env` (Bảo mật)

Tạo file `.env` tại thư mục gốc chứa chuỗi kết nối:

```
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
```

### Bước 2: Viết code kế thừa

Ví dụ tạo file `scrapers/itviec_scraper.py`:

```python
from base_scraper import BaseScraper

class ITViecScraper(BaseScraper):
    def __init__(self):
        # Gọi hàm khởi tạo của cha, đặt tên nguồn là "ITviec"
        super().__init__(source_name="ITviec")

    # BẮT BUỘC PHẢI VIẾT HÀM NAY
    def scrape(self):
        self.logger.info("Đang bắt đầu cào ITviec...")
        
        # ... (Viết code BeautifulSoup/Selenium ở đây) ...
        
        # Giả sử lấy được 1 job:
        my_job = {
            "url": "https://itviec.com/job/python-dev",
            "job_title": "Python Developer",
            "company_name": "FPT Software"
        }

        # Gọi hàm của cha để lưu
        self.save_job(my_job)

# Chạy thử
if __name__ == "__main__":
    bot = ITViecScraper()
    bot.scrape()
```

***

## 5. Các lỗi thường gặp (Troubleshooting)

| Lỗi                    | Nguyên nhân                          | Cách sửa |
|------------------------|--------------------------------------|----------|
| `SSL handshake failed` | Máy thiếu chứng chỉ bảo mật.         | Kiểm tra xem đã import `certifi` và thêm `tlsCAFile=certifi.where()` trong `BaseScraper` chưa. |
| `Can't instantiate abstract class` | Class con chưa viết hàm `scrape`. | Kiểm tra class con, định nghĩa lại hàm `def scrape(self):`. |
| `DuplicateKeyError`    | URL đã tồn tại trong DB.             | Không cần sửa. Đây là tính năng chống trùng lặp. Log sẽ hiện màu vàng (Warning). |
| `Authentication failed` | Sai User/Pass trong `MONGO_URI`.    | Kiểm tra lại file `.env`, đảm bảo mật khẩu không chứa ký tự đặc biệt gây lỗi URL. |