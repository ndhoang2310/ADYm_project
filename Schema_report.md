# 📄 TECHNICAL REPORT: DATABASE SCHEMA SPECIFICATION

**Dự án:** Vietnam IT Market Analysis & Salary Prediction  
**Ngày lập:** 27/01/2026  
**Người lập:** Team Lead (Nguyễn Đình Hoàng)

---

## 1. Giới thiệu chung
Tài liệu này quy định chuẩn cấu trúc dữ liệu (Schema) cho Database `VietnamITMarket`. Đây là "bộ luật" bắt buộc mà tất cả các Scraper (ITviec, VietnamWorks, LinkedIn) phải tuân thủ trước khi lưu dữ liệu vào hệ thống.

Mục tiêu: Đảm bảo dữ liệu đầu vào đồng nhất, sạch sẽ để phục vụ cho bài toán **Dự đoán lương (Salary Prediction)** sau này.

---

## 2. Schema là gì? Tại sao cần Schema?

### Khái niệm
Hãy tưởng tượng Database của chúng ta là một **nhà kho**.
* **Dữ liệu (Job Post)** là các kiện hàng được các xe tải (Scraper của Dev A, Dev B...) chở đến.
* **Schema** chính là **người bảo vệ** đứng ở cửa kho.

### Vai trò của Schema trong dự án
Người bảo vệ này cầm một tờ danh sách kiểm tra (Checklist) và thực hiện nhiệm vụ:
1.  **Chặn hàng lỗi:** Nếu kiện hàng thiếu tem mác (thiếu `url`, `job_title`), bảo vệ sẽ từ chối nhập kho ngay lập tức.
2.  **Chuẩn hóa:** Đảm bảo mọi kiện hàng đều sắp xếp giống nhau. Không được phép có chuyện xe A ghi là "Lương", xe B ghi là "Thu nhập". Tất cả phải thống nhất là `salary_raw`.

👉 **Kết quả:** Khi team AI/Data Science lấy dữ liệu ra dùng, họ không mất thời gian sửa lỗi vặt và có thể chạy mô hình dự đoán ngay.

---

## 3. Quyết định kỹ thuật: Tại sao dùng `bsonType` thay vì `type`?

Trong MongoDB, chúng ta chọn sử dụng `bsonType` (Binary JSON) thay vì chuẩn JSON `type` thông thường. Dưới đây là lý do kỹ thuật liên quan trực tiếp đến bài toán dự đoán lương của dự án:

### Lý do 1: Xử lý thời gian (Time Series Analysis)
* **Vấn đề:** JSON thường chỉ hiểu ngày tháng là một dòng chữ (String), ví dụ: "2025-01-27". Máy tính không hiểu đây là thời gian, nên không thể so sánh "ngày nào trước, ngày nào sau" một cách nhanh chóng.
* **Giải pháp `bsonType`:** Hỗ trợ kiểu dữ liệu **`date`**.
* **Lợi ích:** Giúp ta dễ dàng lọc các tin tuyển dụng "trong 30 ngày gần nhất" hoặc vẽ biểu đồ biến động nhu cầu tuyển dụng theo thời gian thực.

### Lý do 2: Độ chính xác của con số (Numerical Precision)
* **Vấn đề:** JSON thường gộp chung số nguyên và số thập phân thành `number`.
* **Giải pháp `bsonType`:** Phân biệt rõ ràng giữa `int` (số nguyên - dùng cho số năm kinh nghiệm) và `double` (số thực - dùng cho tính toán lương trung bình).
* **Lợi ích:** Tăng độ chính xác cho thuật toán Hồi quy (Regression) khi dự đoán lương.

### Lý do 3: Hiệu năng (Performance)
* Dữ liệu lưu dưới dạng BSON (Nhị phân) nhẹ hơn và truy xuất nhanh hơn so với văn bản JSON thuần túy, đặc biệt quan trọng khi hệ thống mở rộng lên hàng chục nghìn bản ghi (Target: 10k+ job posts).

---

## 4. Chi tiết cấu trúc dữ liệu (Mapping 13 Features)

Dưới đây là bảng ánh xạ giữa 13 đặc trưng yêu cầu của dự án và tên trường trong Database.

| STT | Tên đặc trưng (Feature) | Tên trường trong DB (Key) | Kiểu dữ liệu (BSON) | Giải thích / Ràng buộc |
|:---|:---|:---|:---|:---|
| **1** | **Job title** | `job_title` | String | **Bắt buộc**. Tên vị trí tuyển dụng. |
| **2** | **Posted date** | `posted_date` | String / Date | Ngày đăng tin (chấp nhận cả chữ "2 days ago"). |
| **3** | **Company** | `company_name` | String | **Bắt buộc**. Tên công ty. |
| **4** | **Location** | `location_raw` | String | Tỉnh/Thành phố (HCM, HN, ĐN...). |
| **5** | **Salary Range** | `salary_raw` | String | Target chính. Lưu nguyên văn (VD: "15-20 Triệu"). |
| **6** | **Experience** | `experience_raw` | String | Yêu cầu kinh nghiệm thô. |
| **7** | **Skills (Reqs)** | `skills_tags` | Array (String) | Danh sách kỹ năng (VD: `["Python", "AWS"]`). |
| **8** | **Job Level** | `job_level` | String | Senior / Junior / Lead. |
| **9** | **Work Type** | `work_type` | String | Remote / Hybrid / Onsite. |
| **10** | **English** | `english_req` | String | Yêu cầu tiếng Anh (có/không/chứng chỉ). |
| **11** | **Education** | `education_raw` | String | Yêu cầu bằng cấp. |
| **12** | **Contract** | `contract_type` | String | Full-time / Part-time / Freelance. |
| **13** | **Languages/Tools** | *(Nằm trong skills_tags)* | Array | Gộp chung vào `skills_tags` để dễ xử lý. |
| *Mới* | *Data Source* | `source` | Enum | Chỉ chấp nhận: `itviec`, `topcv`, `linkedin`. |
| *Mới* | *Unique ID* | `url` | String | **Khóa chính**. Link gốc bài viết (Chống trùng lặp). |

---

## 5. JSON Schema Code (Dành cho Dev)

```json
{
  "$jsonSchema": {
    "bsonType": "object",
    "required": ["url", "source", "job_title", "company_name", "crawled_date"],
    "properties": {
      "url": { "bsonType": "string", "description": "Unique identifier (Link gốc)" },
      "source": { "enum": ["itviec", "vietnamworks", "linkedin", "topcv"] },
      "job_title": { "bsonType": "string" },
      "company_name": { "bsonType": "string" },
      "salary_raw": { "bsonType": ["string", "null"] },
      "location_raw": { "bsonType": "string" },
      "work_type": { "bsonType": ["string", "null"] },
      "job_level": { "bsonType": ["string", "null"] },
      "requirements_text": { "bsonType": "string", "description": "Full text for NLP" },
      "skills_tags": { 
        "bsonType": "array", 
        "items": { "bsonType": "string" }
      },
      "experience_raw": { "bsonType": ["string", "null"] },
      "education_raw": { "bsonType": ["string", "null"] },
      "contract_type": { "bsonType": ["string", "null"] },
      "english_req": { "bsonType": ["string", "null"] },
      "posted_date": { "bsonType": ["string", "date", "null"] },
      "crawled_date": { "bsonType": "date", "description": "Thời điểm chạy tool" }
    }
  }
}