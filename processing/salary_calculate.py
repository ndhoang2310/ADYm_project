import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PATH_CSV_IN = os.path.join(ROOT_DIR, 'data', '04_jobs_imputed.csv')
PATH_CSV_OUT = os.path.join(ROOT_DIR, 'data', '05_final_dataset.csv')

def process_and_overwrite_salary():
    print(f"🚀 Đang đọc file dữ liệu từ: {PATH_CSV_IN}")
    
    try:
        df = pd.read_csv(PATH_CSV_IN)
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file 04_jobs_imputed.csv. Hãy kiểm tra lại đường dẫn.")
        return

    mask_both = df['salary_min'].notna() & df['salary_max'].notna() & (df['salary_min'] > 0)
    df_both = df[mask_both]

    if df_both.empty:
        print("⚠️ Cảnh báo: Không có job nào có đủ cả Min và Max để tính tỷ lệ R.")
        return

    R = (df_both['salary_max'] / df_both['salary_min']).median()
    
    coef_min = (1 + R) / 2
    coef_max = (1 + 1/R) / 2

    print(f"📊 Phân tích thị trường thành công:")
    print(f"   - Tỷ lệ Max/Min (R): {R:.2f} lần")
    print(f"   - Hệ số cho job 'Từ (Min)': {coef_min:.2f}")
    print(f"   - Hệ số cho job 'Lên tới (Max)': {coef_max:.2f}")

    print("🧮 Đang tính toán cột Target (salary_avg)...")
    
    df['salary_avg'] = np.nan

    df.loc[mask_both, 'salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

    mask_only_min = df['salary_min'].notna() & df['salary_max'].isna()
    df.loc[mask_only_min, 'salary_avg'] = df['salary_min'] * coef_min

    mask_only_max = df['salary_min'].isna() & df['salary_max'].notna()
    df.loc[mask_only_max, 'salary_avg'] = df['salary_max'] * coef_max

    print("💾 Đang lưu dữ liệu hoàn chỉnh vào file CSV mới...")
    df.to_csv(PATH_CSV_OUT, index=False, encoding='utf-8-sig')
    
    print(f"✅ Hoàn tất! Đã cập nhật xong cột salary_avg cho {len(df)} dòng dữ liệu.")

if __name__ == "__main__":
    process_and_overwrite_salary()