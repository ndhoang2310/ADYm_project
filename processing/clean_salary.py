import pandas as pd
import numpy as np
import re
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def process_salary(s):
    if pd.isna(s): 
        return np.nan, np.nan
        
    s = str(s).lower()
    
    if any(x in s for x in ['thương lượng', 'thỏa thuận', 'thoả thuận', 'cạnh tranh']):
        return np.nan, np.nan
    if s.strip() in ['0', '0.0 - 0.0 triệu', '0.0-0.0']:
        return np.nan, np.nan
        
    is_usd = 'usd' in s or '$' in s
    is_jpy = '¥' in s or 'jpy' in s or 'yên' in s
    is_year = 'năm' in s or 'year' in s or '/năm' in s
    
    is_trieu = any(x in s for x in ['triệu', 'tr', 'm', 'million'])
    
    if 'bonus' in s:
        s = s.split('bonus')[0]
        
    s_clean = s.replace(' ', '')
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
        
    converted_nums = []
    for n in nums:
        if is_usd and n >= 1000000:
            converted_nums.append(n / 1000000)
        elif is_usd:
            n_vnd = n * 25000
            converted_nums.append(n_vnd / 1000000)
        elif is_jpy:
            converted_nums.append((n * 160) / 1000000)
        else:
            if n >= 100000:
                val = n / 1000000
            elif n >= 1000:
                if is_trieu:
                    val = n
                else:
                    val = n / 1000 
            elif n >= 100:
                if is_trieu:
                    val = n
                else:
                    val = n / 1000 
            else:
                val = n
                
            if 'tỷ' in s or 'tỉ' in s:
                val = val * 1000
                
            converted_nums.append(val)
                
    if is_year:
        converted_nums = [n / 12 for n in converted_nums]
        
    if all(n == 0 for n in converted_nums):
        return np.nan, np.nan
        
    if len(converted_nums) == 1:
        val = converted_nums[0]
        if any(x in s for x in ['up to', 'upto', 'lên đến', 'tới', 'tối đa', 'max']):
            return np.nan, round(val, 2)
        elif any(x in s for x in ['từ', 'from', 'trên', 'min', 'hơn']):
            return round(val, 2), np.nan
        else:
            return round(val, 2), round(val, 2)
    else:
        c_min = min(converted_nums[0], converted_nums[1])
        c_max = max(converted_nums[0], converted_nums[1])
        return round(c_min, 2), round(c_max, 2)
    
def process_exp(s):
    if pd.isna(s): 
        return -1.0
        
    s_lower = str(s).lower().strip()
    
    if s_lower in ['không hiển thị', 'none', 'null', '']:
        return -1.0
        
    if any(x in s_lower for x in ['không yêu cầu', 'chưa có', 'fresher', 'mới tốt nghiệp', 'không đòi hỏi']):
        return 0.0
        
    if 'dưới 1' in s_lower or '< 1' in s_lower:
        return 0.5
        
    nums = re.findall(r'\d+(?:\.\d+)?', s_lower)
    
    if not nums:
        return -1.0
        
    num_vals = [float(n) for n in nums]
    
    if len(num_vals) == 1:
        return num_vals[0]
        
    elif len(num_vals) >= 2:
        return min(num_vals[0], num_vals[1])
        
    return -1.0
def process_location(s):
    if pd.isna(s): return 'Khác'
    
    s_lower = str(s).lower()
    
    if s_lower.strip() in ['0', 'unknown', 'not available, none', 'none']:
        return 'Khác'

    found_locs = [] 
    
    if any(x in s_lower for x in ['nước ngoài', 'nhật bản', 'quốc tế', 'international', 'japan', 'singapore']):
        found_locs.append('Khác')
        
    if any(x in s_lower for x in ['remote', 'từ xa', 'tại nhà']):
        found_locs.append('Remote')

    provinces_map = {
        'Hồ Chí Minh': ['hồ chí minh', 'hcm', 'sài gòn', 'saigon', 'thủ đức', 'nhà bè', 'cần giờ', 'củ chi', 'hóc môn'],
        'Hà Nội': ['hà nội', 'ha noi', 'hn', 'cầu giấy', 'nam từ liêm', 'bắc từ liêm', 'thanh xuân', 'hoàn kiếm', 'ba đình', 'đống đa', 'tây hồ', 'hoàng mai', 'long biên', 'gia lâm', 'hoài đức'],
        'Đà Nẵng': ['đà nẵng', 'da nang', 'đn', 'sơn trà', 'hải châu', 'liên chiểu', 'ngũ hành sơn', 'cẩm lệ'],
        'Bình Dương': ['bình dương', 'dĩ an', 'thuận an', 'thủ dầu một', 'bến cát', 'tân uyên'],
        'Đồng Nai': ['đồng nai', 'biên hòa', 'long thành', 'nhơn trạch'],
        'Bà Rịa - Vũng Tàu': ['bà rịa', 'vũng tàu', 'đất đỏ', 'tân thành'],
        'Thừa Thiên Huế': ['huế', 'thừa thiên huế'],
        'Đắk Lắk': ['đắk lắk', 'dak lak', 'đắc lắc'],
        'Hải Phòng': ['hải phòng', 'hai phong'],
        'Cần Thơ': ['cần thơ', 'can tho'],
        'Bắc Ninh': ['bắc ninh'],
        'Hưng Yên': ['hưng yên'],
        'Ninh Bình': ['ninh bình'],
        'Đồng Tháp': ['đồng tháp'],
        'Thái Nguyên': ['thái nguyên'],
        'Phú Thọ': ['phú thọ'],
        'Gia Lai': ['gia lai'],
        'Lâm Đồng': ['lâm đồng'],
        'Khánh Hòa': ['khánh hòa', 'nha trang'],
        'Quảng Ninh': ['quảng ninh'],
        'Tây Ninh': ['tây ninh'],
        'Quảng Trị': ['quảng trị'],
        'Quảng Ngãi': ['quảng ngãi'],
        'Nghệ An': ['nghệ an'],
        'Thanh Hóa': ['thanh hóa'],
        'Hà Nam': ['hà nam'],
        'Bến Tre': ['bến tre'],
        'Cà Mau': ['cà mau'],
        'Kiên Giang': ['kiên giang'],
        'Tiền Giang': ['tiền giang'],
        'Hải Dương': ['hải dương'],
        'Điện Biên': ['điện biên'],
        'Bình Phước': ['bình phước', 'đồng xoài'],
        'Long An': ['long an', 'cần giuộc'],
        'Cao Bằng': ['cao bằng'],
        'Lạng Sơn': ['lạng sơn'],
        'Vĩnh Phúc': ['vĩnh phúc'],
        'Hòa Bình': ['hòa bình'],
        'Sóc Trăng': ['sóc trăng'],
        'Thái Bình': ['thái bình'],
        'Hà Tĩnh': ['hà tĩnh'],
        'Bắc Giang': ['bắc giang']
    }

    for clean_name, keywords in provinces_map.items():
        if any(keyword in s_lower for keyword in keywords):
            if clean_name not in found_locs:
                found_locs.append(clean_name)

    if not found_locs:
        return 'Khác'
        
    return found_locs[0]

def process_level(s):
    if pd.isna(s): 
        return -1
        
    s_lower = str(s).lower().strip()
    
    if any(x in s_lower for x in ['giám đốc', 'cấp cao']):
        return 5
        
    if any(x in s_lower for x in ['quản lý', 'trưởng phòng', 'phó phòng', 'trưởng/phó phòng', 'trưởng chi nhánh']):
        return 4
        
    if any(x in s_lower for x in ['trưởng nhóm', 'giám sát']):
        return 3
        
    if 'nhân viên' in s_lower:
        return 2
        
    if 'mới tốt nghiệp' in s_lower or 'fresher' in s_lower:
        return 1
        
    if any(x in s_lower for x in ['thực tập', 'sinh viên', 'intern']):
        return 0
        
    return -1

def process_contract_type(s):
    if pd.isna(s):
        return np.nan
        
    s_lower = str(s).lower()
    types_found = []
    
    if any(x in s_lower for x in ['full-time', 'fulltime', 'nhân viên chính thức', 'toàn thời gian']):
        if 'Full-time' not in types_found:
            types_found.append('Full-time')
            
    if any(x in s_lower for x in ['part-time', 'parttime', 'bán thời gian']):
        if 'Part-time' not in types_found:
            types_found.append('Part-time')
            
    if any(x in s_lower for x in ['freelance', 'thời vụ', 'nghề tự do', 'dự án']):
        if 'Freelance' not in types_found:
            types_found.append('Freelance')
            
    if any(x in s_lower for x in ['thực tập', 'intern']):
        if 'Intern' not in types_found:
            types_found.append('Intern')
            
    if 'khác' in s_lower or 'làm tại nhà' in s_lower or len(types_found) == 0:
        if 'Khác' not in types_found:
            types_found.append('Khác')

    if len(types_found) == 1:
        return types_found[0]
    elif len(types_found) > 1:
        return types_found
    else:
        return np.nan

if __name__ == "__main__":
    input_path = 'data/00_raw_jobs.csv'
    logging.info(f"Đang nạp file {input_path}...")
    
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logging.error(f"Không tìm thấy file tại '{input_path}'. Hãy chắc chắn bạn đang chạy code từ thư mục gốc của dự án.")
        exit()
    
    logging.info("Đang xử lý các cột Structured Data...")
    df['salary_min'], df['salary_max'] = zip(*df['salary_raw'].apply(process_salary))
    df['exp_years'] = df['experience_raw'].apply(process_exp)
    df['location'] = df['location_raw'].apply(process_location)
    df['job_level'] = df['job_level'].apply(process_level)
    df['contract_type'] = df['contract_type'].apply(process_contract_type)
    
    final_cols = [
        'url', 'contract_type', 
        'salary_min', 'salary_max', 
        'exp_years', 'location', 'job_level'
    ]
    df_clean = df[final_cols]
    
    output_dir = 'processing/artifacts'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, '01_clean_salary.csv')
    
    df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"Hoàn tất! Data đã lưu tại: {output_path}")