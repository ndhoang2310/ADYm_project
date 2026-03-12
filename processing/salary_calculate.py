import os
import pandas as pd
import numpy as np

# 1. Định vị đường dẫn file (An toàn, chống lỗi FileNotFoundError)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PATH_CSV = os.path.join(ROOT_DIR, 'data', 'dataset_after_categorical_imputing.csv')

def process_and_overwrite_salary():
    print(f"🚀 Đang đọc file dữ liệu từ: {PATH_CSV}")
    
    try:
        df = pd.read_csv(PATH_CSV)
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file final_dataset.csv. Hãy kiểm tra lại đường dẫn.")
        return

    # 2. Xây dựng bộ quy tắc từ dữ liệu thực tế (Data-driven)
    # Tìm các công việc có đủ Min và Max (Min > 0 để tránh lỗi chia cho 0)
    mask_both = df['salary_min'].notna() & df['salary_max'].notna() & (df['salary_min'] > 0)
    df_both = df[mask_both]

    if df_both.empty:
        print("⚠️ Cảnh báo: Không có job nào có đủ cả Min và Max để tính tỷ lệ R.")
        return

    # Tính tỷ lệ R trung vị của thị trường
    R = (df_both['salary_max'] / df_both['salary_min']).median()
    
    # Suy ra 2 hệ số nhân
    coef_min = (1 + R) / 2
    coef_max = (1 + 1/R) / 2

    print(f"📊 Phân tích thị trường thành công:")
    print(f"   - Tỷ lệ Max/Min (R): {R:.2f} lần")
    print(f"   - Hệ số cho job 'Từ (Min)': {coef_min:.2f}")
    print(f"   - Hệ số cho job 'Lên tới (Max)': {coef_max:.2f}")

    # 3. Thực thi tính toán salary_avg
    print("🧮 Đang tính toán cột Target (salary_avg)...")
    
    # Khởi tạo cột bằng NaN
    df['salary_avg'] = np.nan

    # TH1: Có cả 2 (Tính trung bình bình thường)
    df.loc[mask_both, 'salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

    # TH2: Chỉ có Min
    mask_only_min = df['salary_min'].notna() & df['salary_max'].isna()
    df.loc[mask_only_min, 'salary_avg'] = df['salary_min'] * coef_min

    # TH3: Chỉ có Max
    mask_only_max = df['salary_min'].isna() & df['salary_max'].notna()
    df.loc[mask_only_max, 'salary_avg'] = df['salary_max'] * coef_max

    # 4. Ghi đè lại vào chính file cũ
    print("💾 Đang lưu đè dữ liệu vào file CSV gốc...")
    # Dùng index=False để không bị sinh thêm cột số thứ tự vô nghĩa
    df.to_csv(PATH_CSV, index=False, encoding='utf-8-sig')
    
    print(f"✅ Hoàn tất! Đã cập nhật xong cột salary_avg cho {len(df)} dòng dữ liệu.")

if __name__ == "__main__":
    process_and_overwrite_salary()