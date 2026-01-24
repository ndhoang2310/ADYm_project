```markdown
# Vietnam IT Market Analysis & Salary Prediction Project

## 🎯 Project Overview
**Tên dự án**: Vietnam IT Market Overview & Skill-based Salary Prediction  
**Thời gian**: 2025-2026  
**Mục tiêu chính**: 
- Phân tích toàn cảnh thị trường IT Việt Nam (EDA)
- Xây dựng model dự đoán mức lương dựa trên kỹ năng, kinh nghiệm, vị trí

**Đối tượng hưởng lợi**:
- Ứng viên: Định giá bản thân chính xác, đàm phán lương hiệu quả
- Nhà tuyển dụng: Benchmark lương thị trường, tối ưu ngân sách
- Sinh viên: Định hướng nghề nghiệp, lộ trình học tập

## 📊 Required Features (COMPLETE - 13 đặc trưng)

| Feature | Raw data format | Target type (sau xử lý) |
|---------|----------------|-------------------------|
| **Job title** | Text (string) | Categorical (nominal) |
| **Candidate requirements (skills section)** | Text (bullet points/free text) | Text → extracted skill features |
| **Programming languages** | Text (extracted from requirements) | Binary/Multi-hot encoded |
| **Frameworks/Tools** | Text (extracted from requirements) | Binary/Multi-hot encoded |
| **Years of experience required** | Text ("2+ years", "at least 3 years") | Numeric (continuous) |
| **Job level** | Text (Junior/Mid/Senior/Lead) | Ordinal categorical |
| **English proficiency requirement** | Text (required/preferred/not mentioned) | Ordinal or Binary |
| **Location** | Text (city/province) | Categorical (nominal) |
| **Work type** | Text (Onsite/Hybrid/Remote) | Categorical (nominal) |
| **Education requirement** | Text | Categorical |
| **Contract type** | Text | Categorical |
| **Posted date** | Date/Text | Date → numeric (time index) |
| **Company type/Industry** | Text (company desc/tags) | Categorical (nominal) → One-hot |
| **Salary range** (Target) | Text ("15–25 triệu", "$1000–1500") | **Numeric (continuous)** |

## 🗃️ DATA SOURCES & CURRENT TASKS

### Data Sources
```
1. ITviec (skills tags chất lượng cao)
2. VietnamWorks/TopCV (volume lớn)  
3. LinkedIn (Senior/MNC jobs)
4. Kaggle/GitHub datasets (backup)
```

### ✅ CURRENT TASK ASSIGNMENTS

#### **1. Leader Task: Database & Framework Setup**
```
📁 Tên: Setup MongoDB & Base Scraper Class
✅ Database: VietnamITMarket → raw_jobs collection
✅ Schema chuẩn:
{
  "job_title": "...",
  "company": "...",
  "salary_raw": "...", 
  "skills_raw": [...],
  "location": "...",
  "source": "itviec",  // QUAN TRỌNG
  "url": "...",
  "crawled_date": "ISODate()"
}
✅ Tạo GitHub repo, set quyền team
```

#### **2. Dev A: ITviec Scraper**
```
🎯 Target: ITviec (dữ liệu sạch nhất)
🛠️ Tech: Requests + BeautifulSoup
✅ Trọng tâm: Skills tags, "Why you'll love working here"
✅ Output: JSON → MongoDB
```

#### **3. Dev B: VietnamWorks Volume Scraper**
```
🎯 Target: VietnamWorks/TopCV (số lượng lớn)
🛠️ Tech: Selenium (nếu cần) + Pagination handling
✅ Lấy full job description cho NLP sau này
✅ Error handling mạnh
```

#### **4. Dev C: LinkedIn Advanced Scraper**
```
🎯 Target: LinkedIn (Senior jobs, MNCs)
🛠️ Tech: Selenium/Playwright + Login automation
✅ Backup: Kaggle LinkedIn dataset nếu bị block
✅ Seniority Level, Company Size
```

#### **5. QA/Controller: Data Validation**
```
✅ Daily MongoDB queries:
- Check duplicate URLs
- Compare salary formats across sources
- Data type validation
✅ Proxy support for Dev C
```

## 🚀 NEXT STEPS (CRISP-DM)
```
1. ✅ Data Collection (Scraping)
2. 🔄 Data Cleaning (Missing values, outliers, normalization)
3. 📈 EDA (Market overview dashboard)
4. 🤖 Modeling (XGBoost/LightGBM Salary Prediction)
5. 🚀 Deployment (Streamlit Web App)
```

## 📈 Expected KPIs
- **Dataset**: 10k+ job posts (2023-2026)
- **Model**: RMSE/MAE < 3-5M VND
- **Coverage**: HN, HCM, DN, CT + nationwide

---

**Status**: Active Data Collection Phase  
**Current Date**: January 2026  
**Lead**: [Your Name]
```

