import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

PATH_RAW = os.path.join(ROOT_DIR, 'data', 'raw_jobs.csv')
PATH_NLP = os.path.join(CURRENT_DIR, 'artifacts', 'clean_skills.csv')
PATH_STRUCT = os.path.join(CURRENT_DIR, 'artifacts', 'clean_salary.csv')
PATH_FINAL = os.path.join(ROOT_DIR, 'data', 'final_dataset.csv')

def process_and_merge():
    # 1. Load Data
    df_raw = pd.read_csv(PATH_RAW)
    df_nlp = pd.read_csv(PATH_NLP)
    df_struct = pd.read_csv(PATH_STRUCT)

    # 2. Hợp nhất 2 file từ team (Inner Join khử trùng cột URL)
    df_merged = pd.merge(df_nlp, df_struct, on='url', how='inner')

    # 3. Kéo và Xử lý Feature từ Raw (Làm giàu dữ liệu)
    # Kéo thêm education_raw và job_description vì 2 thành viên chưa làm
    df_raw_subset = df_raw[['url', 'company_name', 'source', 'education_raw', 'job_description']].drop_duplicates(subset=['url'])
    df_final = pd.merge(df_merged, df_raw_subset, on='url', how='left')

    # --- XỬ LÝ (PROCESSING) CÁC FEATURE MỚI ---
    # 3.1. Chuẩn hóa company_name (Chống lỗi gõ sai chữ hoa/thường để Dedup chuẩn)
    df_final['company_name_clean'] = df_final['company_name'].str.strip().str.upper()

    # 3.2. Chuẩn hóa source
    df_final['source'] = df_final['source'].str.lower()

    # 3.3. Xử lý education_level (từ education_raw)
    df_final['education_level'] = np.where(df_final['education_raw'].str.contains('Đại học|Bachelor', case=False, na=False), 'Bachelor',
                                  np.where(df_final['education_raw'].str.contains('Cao đẳng|College', case=False, na=False), 'College', 'None'))

    # 3.4. Xử lý is_shift_work (từ job_description)
    df_final['is_shift_work'] = np.where(df_final['job_description'].str.contains(r'ca xoay|theo ca|làm đêm|shift', case=False, na=False), 1, 0)

    # Xóa các cột text thô sau khi đã trích xuất xong
    df_final.drop(columns=['education_raw', 'job_description', 'company_name'], inplace=True)
    df_final.rename(columns={'company_name_clean': 'company_name'}, inplace=True)

    # 4. Lọc trùng lặp (Deduplication)
    df_final = df_final.drop_duplicates(subset=['job_title', 'company_name'], keep='first')

    # 5. Lưu file (Chưa tính avg, giữ nguyên min max)
    df_final.to_csv(PATH_FINAL, index=False, encoding='utf-8-sig')
    print(f"✅ Đã gộp, xử lý feature mới và lưu thành công tại: {PATH_FINAL}")

if __name__ == "__main__":
    process_and_merge()