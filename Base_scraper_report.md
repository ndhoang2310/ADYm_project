# 📄 TECHNICAL REPORT: BASE SCRAPER ARCHITECTURE

**Dự án:** Vietnam IT Market Analysis & Salary Prediction  
**Ngày lập:** 27/01/2026  
**Người lập:** Team Lead (Nguyễn Đình Hoàng)

---

## 1. Tổng quan (Overview)
Trong dự án này, chúng ta có 3 Developer phụ trách 3 nguồn dữ liệu khác nhau (ITviec, VietnamWorks, LinkedIn). Để tránh việc "mạnh ai nấy làm", code bị lặp lại và khó quản lý, chúng ta sử dụng kiến trúc **OOP Inheritance (Kế thừa hướng đối tượng)**.

Class **`BaseScraper`** đóng vai trò là khung xương sống (Backbone). Tất cả các Scraper con **bắt buộc** phải kế thừa từ class này.

### Mục tiêu cốt lõi:
1.  **DRY (Don't Repeat Yourself):** Viết logic kết nối Database và xử lý lỗi một lần duy nhất ở class cha.
2.  **Consistency (Sự nhất quán):** Đảm bảo mọi bản ghi dữ liệu đều có đủ metadata (`source`, `crawled_date`, `url`) theo đúng Schema.
3.  **Safety (An toàn):** Xử lý tập trung các lỗi trùng lặp (`DuplicateKeyError`) và ngắt kết nối an toàn.

---

## 2. Kiến trúc hệ thống (Architecture)

```mermaid
classDiagram
    class BaseScraper {
        +String source
        +MongoClient client
        +Collection collection
        +__init__()
        +save_job(data)
        +close_connection()
        +scrape()*
    }
    
    class ITViecScraper {
        +scrape()
    }
    
    class VNWorksScraper {
        +scrape()
    }

    BaseScraper <|-- ITViecScraper : Inherits
    BaseScraper <|-- VNWorksScraper : Inherits