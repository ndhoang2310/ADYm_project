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
    
    if any(x in s for x in ['thương lượng', 'thỏa thuận', 'thoả thuận', 'cạnh tranh']):
        return np.nan, np.nan
    if s.strip() in ['0', '0.0 - 0.0 triệu', '0.0-0.0']:
        return np.nan, np.nan
        
    is_usd = 'usd' in s or '$' in s
    is_jpy = '¥' in s or 'jpy' in s or 'yên' in s
    is_year = 'năm' in s or 'year' in s or '/năm' in s
    
    # BẮT THÊM CỜ: Kiểm tra xem trong câu có chữ "triệu" không
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
            # === LOGIC MỚI SIÊU CHẶT CHẼ ===
            if n >= 100000:         # VD: 15.000.000 -> 15 Triệu
                val = n / 1000000
            elif n >= 1000:         # VD: 1000, 2000
                if is_trieu:        # Nếu ghi "1000 triệu"
                    val = n
                else:               # Nếu ghi "VND 1.000" -> 1 Triệu
                    val = n / 1000 
            elif n >= 100:          # VD: 800, 150, 100
                if is_trieu:        # Nếu ghi "100 - 150 triệu" -> Giữ nguyên 100 Triệu
                    val = n
                else:               # Nếu ghi "800 - 1000 ₫" -> 0.8 Triệu (800k)
                    val = n / 1000 
            else:                   # VD: 15, 20 -> 15 Triệu
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
    
# 2. Hàm xử lý Kinh nghiệm
def process_exp(s):
    # 1. Nếu trống (NaN, Null)
    if pd.isna(s): 
        return -1.0
        
    s_lower = str(s).lower().strip()
    
    # 2. Các từ khóa báo hiệu dữ liệu trống/ẩn
    if s_lower in ['không hiển thị', 'none', 'null', '']:
        return -1.0
        
    # 3. Không yêu cầu / Chưa có kinh nghiệm
    if any(x in s_lower for x in ['không yêu cầu', 'chưa có', 'fresher', 'mới tốt nghiệp', 'không đòi hỏi']):
        return 0.0
        
    # 4. Dưới 1 năm
    if 'dưới 1' in s_lower or '< 1' in s_lower:
        return 0.5
        
    # 5. Dùng Regex để móc TẤT CẢ các con số ra khỏi chuỗi
    # r'\d+' sẽ bỏ qua các dấu trừ (VD: "-1 - 15 năm" sẽ lấy được 1 và 15)
    nums = re.findall(r'\d+(?:\.\d+)?', s_lower)
    
    if not nums:
        return -1.0
        
    # Ép kiểu sang float
    num_vals = [float(n) for n in nums]
    
    # 6. Xử lý các số đã tìm được
    if len(num_vals) == 1:
        # Trường hợp chỉ có 1 số: "5 năm", "Trên 5 năm", "Lên đến 1 năm", "3"
        return num_vals[0]
        
    elif len(num_vals) >= 2:
        # Trường hợp a - b năm (VD: "3 - 5 năm", "0-50 năm", "-1 - 15 Năm")
        # Ta lấy giá trị nhỏ nhất (Min) theo như chiến thuật đã phân tích
        # Nếu bạn đổi ý muốn lấy trung bình, chỉ cần thay bằng: return (num_vals[0] + num_vals[1]) / 2.0
        return min(num_vals[0], num_vals[1])
        
    return -1.0
# 3. Hàm mapping Địa điểm
def process_location(s):
    if pd.isna(s): return 'Khác'
    
    s_lower = str(s).lower()
    
    # Những từ khóa rác báo hiệu dữ liệu trống hoặc không hợp lệ
    if s_lower.strip() in ['0', 'unknown', 'not available, none', 'none']:
        return 'Khác'

    found_locs = set() # Dùng set để tránh trùng lặp nếu chuỗi ghi "Hà Nội, Cầu Giấy, Hà Nội"
    
    # 1. Quét các yếu tố Quốc tế -> Gắn mác 'Khác'
    if any(x in s_lower for x in ['nước ngoài', 'nhật bản', 'quốc tế', 'international', 'japan', 'singapore']):
        found_locs.add('Khác')
        
    # 2. Quét Remote
    if any(x in s_lower for x in ['remote', 'từ xa', 'tại nhà']):
        found_locs.add('Remote')

    # 3. Từ điển 63 Tỉnh Thành & Các biến thể phổ biến
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

    # Quét chuỗi dựa trên từ điển
    for clean_name, keywords in provinces_map.items():
        if any(keyword in s_lower for keyword in keywords):
            found_locs.add(clean_name)

    # Nếu quét xong không tìm thấy tỉnh nào -> Cho vào 'Khác'
    if not found_locs:
        found_locs.add('Khác')
        
    # Xử lý format đầu ra: List nếu nhiều nơi, String nếu 1 nơi
    found_list = list(found_locs)
    if len(found_list) == 1:
        return found_list[0]
    else:
        return found_list

# 4. Hàm mapping Job Level (Ordinal Encoding)
def process_level(s):
    # Nếu trống (NaN, None) -> Trả về -1
    if pd.isna(s): 
        return -1
        
    s_lower = str(s).lower().strip()
    
    # Mức 5: Giám đốc / Cấp cao
    if any(x in s_lower for x in ['giám đốc', 'cấp cao']):
        return 5
        
    # Mức 4: Quản lý / Trưởng - Phó phòng / Trưởng chi nhánh
    if any(x in s_lower for x in ['quản lý', 'trưởng phòng', 'phó phòng', 'trưởng/phó phòng', 'trưởng chi nhánh']):
        return 4
        
    # Mức 3: Trưởng nhóm / Giám sát
    if any(x in s_lower for x in ['trưởng nhóm', 'giám sát']):
        return 3
        
    # Mức 2: Nhân viên
    if 'nhân viên' in s_lower:
        return 2
        
    # Mức 1: Mới tốt nghiệp = Fresher
    if 'mới tốt nghiệp' in s_lower or 'fresher' in s_lower:
        return 1
        
    # Mức 0: Thực tập sinh / Sinh viên = Intern
    if any(x in s_lower for x in ['thực tập', 'sinh viên', 'intern']):
        return 0
        
    # Nếu có giá trị nào khác không khớp với các từ khóa trên
    return -1

# 5. Chuẩn hóa contract_type:
def process_contract_type(s):
    if pd.isna(s):
        return np.nan # Trả về NaN cho các dòng trống
        
    s_lower = str(s).lower()
    types_found = []
    
    # 1. Full-time
    if any(x in s_lower for x in ['full-time', 'fulltime', 'nhân viên chính thức', 'toàn thời gian']):
        if 'Full-time' not in types_found:
            types_found.append('Full-time')
            
    # 2. Part-time
    if any(x in s_lower for x in ['part-time', 'parttime', 'bán thời gian']):
        if 'Part-time' not in types_found:
            types_found.append('Part-time')
            
    # 3. Freelance
    if any(x in s_lower for x in ['freelance', 'thời vụ', 'nghề tự do', 'dự án']):
        if 'Freelance' not in types_found:
            types_found.append('Freelance')
            
    # 4. Intern
    if any(x in s_lower for x in ['thực tập', 'intern']):
        if 'Intern' not in types_found:
            types_found.append('Intern')
            
    # 5. Khác (Bao gồm "Khác", "Làm tại nhà" hoặc những chuỗi không khớp với 4 loại trên)
    if 'khác' in s_lower or 'làm tại nhà' in s_lower or len(types_found) == 0:
        if 'Khác' not in types_found:
            types_found.append('Khác')

    # Trả về kết quả
    if len(types_found) == 1:
        return types_found[0] # Trả về chuỗi (string) nếu chỉ có 1
    elif len(types_found) > 1:
        return types_found    # Trả về mảng (list) nếu có nhiều hình thức
    else:
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
    df['contract_type'] = df['contract_type'].apply(process_contract_type)
    
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
    output_path = os.path.join(output_dir, 'clean_salary.csv')
    
    df_clean.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"Hoàn tất! Data đã lưu tại: {output_path}")