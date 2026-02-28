# 🇻🇳 Vietnam IT Market Analysis & Salary Prediction

> **Dự án Data Science: Phân tích thị trường & Dự đoán lương IT tại Việt Nam (2025-2026)**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)](https://www.mongodb.com/)
[![Machine Learning](https://img.shields.io/badge/Model-Scikit_Learn-orange)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-In_Development-yellow)]()

## 📖 Giới thiệu (Overview)
Dự án này nhằm mục đích xây dựng một bức tranh toàn cảnh về thị trường việc làm IT tại Việt Nam thông qua dữ liệu thực tế và ứng dụng AI để dự đoán mức lương.

**Quy trình xử lý (Pipeline):**
1.  **Data Collection:** Thu thập dữ liệu từ ITviec, VietnamWorks, LinkedIn, TopCV, CareerViet.
2.  **Cleaning & Processing:** Làm sạch, chuẩn hóa lương (VND/USD), kỹ năng (Skill mapping) và địa điểm.
3.  **EDA:** Phân tích xu hướng công nghệ, so sánh mức lương theo Level/Skill.
4.  **Modeling:** Huấn luyện mô hình Machine Learning dự đoán mức lương dựa trên profile ứng viên.

---

## 📂 Cấu trúc dự án (Project Structure)
Dự án được tổ chức theo mô hình chuẩn Data Science, tách biệt giữa Code và Dữ liệu/Model:

```text
Vietnam-IT-Market/
├── crawlers/              # [THU THẬP] - Code cào dữ liệu (Scrapers)
│   ├── base_scraper.py    # [CORE] Class cha - Config chung
│   ├── topcv/             # Crawler TopCV
│   ├── vietnamworks/      # Crawler VietnamWorks
│   ├── careerviet/        # Crawler CareerViet
│   └── ...
│
├── processing/            # [LÀM SẠCH] - Code xử lý thô (Raw -> Clean)
│   ├── clean_salary.py    # Xử lý cột lương (Text -> Number)
│   ├── clean_skills.py    # Tách và chuẩn hóa từ khóa kỹ năng
│   └── dedup_logic.py     # Thuật toán gộp tin trùng lặp
│
├── analysis/              # [EDA] - Notebooks phân tích & Biểu đồ
│   ├── 01_overview.ipynb  # Tổng quan thị trường
│   └── 02_skill_salary.ipynb
│
├── modeling/              # [MODELING] - Code huấn luyện AI (MỚI)
│   ├── experiments/       # Nơi chứa Notebook thử nghiệm (Nháp)
│   ├── features.py        # Feature Engineering (One-hot, Vectorizer)
│   ├── train.py           # Script chính để training ra model
│   └── predict.py         # Script chạy dự đoán thử
│
├── artifacts/             # [OUTPUT] - Chứa file Model/Scaler (.pkl)
│   └── .gitkeep           # (Folder này được gitignore, không up file nặng lên)
│
├── data/                  # [RESOURCE] - Schema & Config
│   ├── job_schema.json    # Validation rule của MongoDB
│   └── mapping_dict.json  # Từ điển mapping skill
│
├── docs/                  # [DOCS] - Tài liệu báo cáo
├── requirements.txt       # Danh sách thư viện
└── README.md              # Hướng dẫn dự án