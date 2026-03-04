import pandas as pd
import numpy as np
import re
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. Hàm bóc tách và quy đổi Lương
def process_salary(s):
    if pd.isna(s):
        return np.nan, np.nan
    s = str(s).lower()
    
    # a. Nếu "Thương lượng", "Thỏa thuận" -> NaN
    if any(x in s for x in ['thương lượng', 'thỏa thuận', 'cạnh tranh']):
        return np.nan, np.nan
        
    # Nhận diện USD
    is_usd = 'usd' in s or '$' in s
    s_clean = s.replace(' ', '')
    
    # b. Regex tìm số 
    raw_nums = re.findall(r'\d+(?:[.,]\d+)*', s_clean)
    nums = []
    for num_str in raw_nums:
        if re.match(r'^\d{1,3}([.,]\d{3})+$', num_str):
            n = float(re.sub(r'[.,]', '', num_str))
        else:
            n = float(num_str.replace(',', '.'))
        nums.append(n)
        
    if not nums:
        return np.nan, np.nan
        
    # Quy đổi về Triệu VNĐ (Tỷ giá 25k)
    converted_nums = []
    for n in nums:
        if is_usd:
            converted_nums.append((n * 25000) / 1000000) 
        else:
            if n > 1000: 
                converted_nums.append(n / 1000000)
            else:        
                converted_nums.append(n)
                
    # c. Xác định salary_min, salary_max
    if len(converted_nums) == 1:
        val = converted_nums[0]
        if any(x in s for x in ['up to', 'upto', 'lên đến', 'tối đa']):
            return np.nan, val
        elif any(x in s for x in ['từ', 'from', 'trên', 'min']):
            return val, np.nan
        else:
            return val, val 
    else:
        return min(converted_nums[0], converted_nums[1]), max(converted_nums[0], converted_nums[1])

# 2. Hàm xử lý Kinh nghiệm
def process_exp(s):
    if pd.isna(s): return np.nan
    s = str(s).lower()
    
    # b. Quy ước Text sang số
    if any(x in s for x in ['không yêu cầu', 'chưa có', 'fresher', 'mới tốt nghiệp', 'không đòi hỏi']):
        return 0.0
    if 'dưới 1' in s or '< 1' in s or 'dưới 1 năm' in s:
        return 0.5
        
    # a. Tách Text ra số
    nums = re.findall(r'\d+(?:[.,]\d+)?', s)
    if nums:
        return float(nums[0].replace(',', '.'))
    return np.nan

# 3. Hàm mapping Địa điểm
def process_location(s):
    if pd.isna(s): return 'Others'
    s = str(s).lower()
    
    # a. Mapping theo Group
    if any(x in s for x in ['remote', 'từ xa']): return 'Remote'
    elif any(x in s for x in ['hồ chí minh', 'hcm', 'ho chi minh', 'thủ đức', 'sài gòn']): return 'Hồ Chí Minh'
    elif any(x in s for x in ['hà nội', 'ha noi', 'hn']): return 'Hà Nội'
    elif any(x in s for x in ['đà nẵng', 'da nang', 'đn']): return 'Đà Nẵng'
    else: return 'Others'

# 4. Hàm mapping Job Level (Ordinal Encoding)
def process_level(s):
    if pd.isna(s): return np.nan
    s = str(s).lower()
    
    if any(x in s for x in ['thực tập', 'intern', 'sinh viên']): return 0.0
    elif any(x in s for x in ['fresher', 'mới tốt nghiệp']): return 1.0
    elif any(x in s for x in ['nhân viên', 'junior', 'chuyên viên', 'staff', 'middle', 'mid']): return 2.0
    elif any(x in s for x in ['senior', 'trưởng nhóm', 'lead', 'chuyên gia', 'cao cấp']): return 3.0
    elif any(x in s for x in ['manager', 'quản lý', 'giám đốc', 'director', 'trưởng phòng', 'head']): return 4.0
    return np.nan

if __name__ == "__main__":
    # ĐÃ SỬA: Đường dẫn trỏ tới thư mục data
    input_path = 'data/raw_jobs.csv'
    logging.info(f"Đang nạp file {input_path}...")
    
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logging.error(f"Không tìm thấy file tại '{input_path}'. Hãy chắc chắn bạn đang chạy code từ thư mục gốc của dự án.")
        exit()
    
    # Transform dữ liệu
    logging.info("Đang xử lý các cột Structured Data...")
    df['salary_min'], df['salary_max'] = zip(*df['salary_raw'].apply(process_salary))
    df['exp_years'] = df['experience_raw'].apply(process_exp)
    df['location'] = df['location_raw'].apply(process_location)
    df['job_level'] = df['job_level'].apply(process_level)
    
    # Giữ lại đúng các feature theo yêu cầu
    final_cols = [
        'url', 'contract_type', 
        'salary_min', 'salary_max', 
        'exp_years', 'location', 'job_level'
    ]
    df_clean = df[final_cols]
    
    # Export đúng định dạng vào thư mục processing/artifacts
    output_dir = 'processing/artifacts'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'clean_structured.csv')
    
    df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"Hoàn tất! Data đã lưu tại: {output_path}")