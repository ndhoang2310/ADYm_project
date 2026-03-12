import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ==========================================
# CÁC HÀM XỬ LÝ
# ==========================================
def salvage_job_level(row):
    # Nếu đã có data chuẩn (khác -1 và NaN), giữ nguyên
    if pd.notna(row['job_level']) and row['job_level'] != -1 and row['job_level'] != -1.0:
        return row['job_level']
        
    title = str(row['job_title']).lower()
    exp = row['exp_years']
    
    # --- LỚP 1: Bắt Keyword từ job_title ---
    if any(x in title for x in ['giám đốc', 'director', 'cdo', 'cto', 'ceo', 'cfo', 'head']): return 5.0
    if any(x in title for x in ['quản lý', 'manager', 'trưởng phòng', 'phó phòng']): return 4.0
    if any(x in title for x in ['senior', 'trưởng nhóm', 'lead', 'chuyên gia']): return 3.0
    if any(x in title for x in ['junior', 'nhân viên', 'chuyên viên', 'staff']): return 2.0
    if any(x in title for x in ['fresher', 'mới tốt nghiệp']): return 1.0
    if any(x in title for x in ['intern', 'thực tập', 'sinh viên']): return 0.0

    # --- LỚP 2: Suy ngược từ exp_years ---
    if pd.notna(exp) and exp != -1 and exp != -1.0:
        if exp == 0: return 1.0           # Fresher
        elif 0 < exp <= 2.5: return 2.0   # Junior / Staff
        elif 2.5 < exp <= 5.0: return 3.0 # Senior
        elif exp > 5.0: return 4.0        # Manager
        
    # --- LỚP 3: Bó tay -> Trả về NaN để lát điền Mode ---
    return np.nan


# ==========================================
# LUỒNG CHẠY CHÍNH
# ==========================================
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    input_path = os.path.join(project_root,'data', 'final_dataset_title.csv')
    output_path = os.path.join(project_root, 'data', 'dataset_after_categorical_imputing.csv')
    
    logging.info(f"Đang nạp bộ dataset tổng: {input_path}")
    try:
        df = pd.read_csv(input_path)
        logging.info(f"Kích thước bộ dữ liệu (Shape): {df.shape}")
    except FileNotFoundError:
        logging.error(f"❌ Không tìm thấy file tại '{input_path}'.")
        exit()
        
    # ---------------------------------------------------------
    # 1. XỬ LÝ CATEGORICAL FEATURES
    # ---------------------------------------------------------
    logging.info("Đang xử lý Missing Values cho các cột Categorical...")
    if 'education_level' in df.columns:
        df['education_level'] = df['education_level'].fillna("Unknown")
    if 'contract_type' in df.columns:
        df['contract_type'] = df['contract_type'].fillna("Full-time")
    if 'tech_stack' in df.columns:
        df['tech_stack'] = df['tech_stack'].fillna("Not Specified")
    if 'company_name' in df.columns:
        df['company_name'] = df['company_name'].fillna("Unknown")
        
    # ---------------------------------------------------------
    # 2. KHÔI PHỤC JOB_LEVEL (Giai đoạn 1)
    # ---------------------------------------------------------
    logging.info("Đang khôi phục job_level từ job_title và exp_years...")
    df['job_level'] = df.apply(salvage_job_level, axis=1)

    # Điền Mode cho những dòng còn sót lại ở Lớp 3
    mode_level = df['job_level'].mode()[0] 
    df['job_level'] = df['job_level'].fillna(mode_level)

    # ---------------------------------------------------------
    # 3. KHÔI PHỤC EXP_YEARS (Giai đoạn 2)
    # ---------------------------------------------------------
    logging.info("Đang khôi phục exp_years bằng Median theo từng job_level...")
    df['exp_years'] = df['exp_years'].replace({-1: np.nan, -1.0: np.nan})
    df['exp_years'] = df.groupby('job_level')['exp_years'].transform(lambda x: x.fillna(x.median()))

    # Quét lần cuối (Phòng trường hợp ngoại lệ)
    overall_median_exp = df['exp_years'].median()
    df['exp_years'] = df['exp_years'].fillna(overall_median_exp)
    
    # ---------------------------------------------------------
    # 4. BÁO CÁO VÀ XUẤT FILE
    # ---------------------------------------------------------
    cols_to_check = ['education_level', 'contract_type', 'tech_stack', 'company_name', 'job_level', 'exp_years']
    existing_cols = [c for c in cols_to_check if c in df.columns]
    
    missing_after = df[existing_cols].isnull().sum()
    logging.info(f"Số ô trống còn lại của các feature vừa xử lý:\n{missing_after}")
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"✅ Hoàn tất! Đã lưu file sạch vào: {output_path}")