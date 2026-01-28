# 🇻🇳 Vietnam IT Market Analysis & Salary Prediction

> **Dự án Data Science: Phân tích thị trường & Dự đoán lương IT tại Việt Nam (2025-2026)**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)](https://www.mongodb.com/)
[![Status](https://img.shields.io/badge/Status-Data_Collection-orange)]()

## 📖 Giới thiệu (Overview)
Dự án này nhằm mục đích xây dựng một bức tranh toàn cảnh về thị trường việc làm IT tại Việt Nam thông qua dữ liệu thực tế.
**Mục tiêu chính:**
1.  **Data Collection:** Thu thập 10,000+ tin tuyển dụng từ ITviec, VietnamWorks, LinkedIn.
2.  **EDA:** Phân tích xu hướng công nghệ, kỹ năng đang hot.
3.  **Modeling:** Xây dựng mô hình AI dự đoán mức lương dựa trên kỹ năng và kinh nghiệm.

---

## 🏗️ Kiến trúc hệ thống (Architecture)
Để đảm bảo tính nhất quán dữ liệu giữa các nguồn khác nhau, dự án sử dụng kiến trúc **OOP Scraper**:

* **Database:** MongoDB (Local) với Schema Validation chặt chẽ.
* **Core:** `BaseScraper` (Class cha) xử lý kết nối DB, ghi log và chống trùng lặp.
* **Spiders:** Các Scraper con (Dev A, B, C) kế thừa từ Core và thực hiện logic cào riêng biệt.

---

## 📂 Cấu trúc dự án (Project Structure)
```text
Vietnam-IT-Market/
├── data/                  # Chứa dữ liệu thô (nếu cần export ra file)
├── scrapers/              # KHÔNG GIAN LÀM VIỆC CỦA DEV
│   ├── __init__.py
│   ├── base_scraper.py    # [CORE] Class cha - KHÔNG SỬA file này
│   ├── itviec_scraper.py  # [Task Dev A]
│   ├── vnworks_scraper.py # [Task Dev B]
│   └── linkedin_scraper.py# [Task Dev C]
├── job_schema.json        # [RULES] Luật validation của Database
├── setup_db.py            # [SCRIPT] Khởi tạo Database & Index
├── requirements.txt       # Các thư viện cần thiết
└── README.md              # Tài liệu hướng dẫn