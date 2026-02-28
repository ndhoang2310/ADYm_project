# 🇻🇳 Vietnam IT Market Analysis & Salary Prediction

> **Dự án Data Science: Phân tích thị trường & Dự đoán lương IT tại Việt Nam (2025-2026)**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)](https://www.mongodb.com/)
[![Status](https://img.shields.io/badge/Status-In_Progress-orange)]()

## 📖 Giới thiệu (Overview)
Dự án này nhằm mục đích xây dựng một bức tranh toàn cảnh về thị trường việc làm IT tại Việt Nam thông qua dữ liệu thực tế.
**Mục tiêu chính:**
1.  **Data Collection:** Thu thập dữ liệu tin tuyển dụng từ ITviec, VietnamWorks, LinkedIn, TopCV, CareerViet.
2.  **Cleaning & Processing:** Làm sạch, chuẩn hóa lương (VND/USD), kỹ năng và địa điểm.
3.  **EDA:** Phân tích xu hướng công nghệ, kỹ năng đang hot.
4.  **Modeling:** Xây dựng mô hình AI dự đoán mức lương dựa trên kỹ năng và kinh nghiệm.

---

## 📂 Cấu trúc dự án (Project Structure)
Dự án được tổ chức theo mô hình Monorepo, chia tách rõ ràng giữa thu thập, xử lý và phân tích:

```text
Vietnam-IT-Market/
├── crawlers/              # [THU THẬP DỮ LIỆU] - Nơi chứa code cào data
│   ├── base_scraper.py    # [CORE] Class cha - Config chung cho mọi scraper
│   ├── topcv/             # Code crawler TopCV
│   ├── vietnamworks/      # Code crawler VietnamWorks
│   ├── careerviet/        # Code crawler CareerViet
│   └── ...
│
├── processing/            # [XỬ LÝ DỮ LIỆU] - Code làm sạch & chuẩn hóa
│   ├── clean_salary.py    # Xử lý cột lương (Text -> Number)
│   ├── clean_skills.py    # Tách từ khóa kỹ năng
│   └── dedup_logic.py     # Xử lý tin trùng lặp
│
├── analysis/              # [PHÂN TÍCH] - Notebooks EDA & Visualization
│   ├── 01_overview.ipynb  # Tổng quan thị trường
│   └── ...
│
├── data/                  # [RESOURCE] Schema, Từ điển & Config
│   ├── job_schema.json    # Luật validation của MongoDB
│   └── mapping_dict.json  # Từ điển mapping skill/location
│
├── docs/                  # [TÀI LIỆU] Báo cáo & Ghi chú dự án
│   ├── context.md
│   └── reports/
│
├── .gitignore             # File cấu hình chặn rác (venv, .env, __pycache__)
├── requirements.txt       # Danh sách thư viện cần thiết
└── README.md              # Hướng dẫn dự án