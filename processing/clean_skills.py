import pandas as pd
import re
import json
import os

# ============================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN 
# ============================================================
PATH_JSON_CONFIG = r'D:\Documents\Clean\data\mapping_dict.json'      # Đường dẫn tới file JSON bạn đã lưu
PATH_RAW_CSV     = r'D:\Documents\Clean\processing\data\raw_jobs.csv'           # File dữ liệu thô
PATH_OUTPUT_CSV  = 'clean_text.csv'         # File đầu ra sạch

# ============================================================
# 2. LOAD CẤU HÌNH TECH MAPPING
# ============================================================
if os.path.exists(PATH_JSON_CONFIG):
    with open(PATH_JSON_CONFIG, 'r', encoding='utf-8') as f:
        tech_mapping = json.load(f)
else:
    print(f"LỖI: Không tìm thấy file JSON tại {PATH_JSON_CONFIG}")
    tech_mapping = {}

# ============================================================
# 3. CÁC HÀM XỬ LÝ LOGIC CHUYÊN SÂU
# ============================================================

def extract_tech_stack(row, mapping):
    # Tier 1: Ưu tiên tags và requirements
    tier1_text = (str(row.get('skills_tags', '')) + " " + str(row.get('requirements_text', ''))).lower()
    found = []
    for tech, variants in mapping.items():
        for variant in variants:
            v_lower = variant.lower()
            pattern = re.escape(v_lower) if not v_lower.isalnum() else rf'\b{re.escape(v_lower)}\b'
            if re.search(pattern, tier1_text):
                found.append(tech)
                break
    
    if found: return ", ".join(list(set(found)))
    
    # Tier 2: Chỉ quét nếu Tier 1 trống
    tier2_text = (str(row.get('job_description', '')) + " " + str(row.get('benefits', ''))).lower()
    for tech, variants in mapping.items():
        for variant in variants:
            v_lower = variant.lower()
            pattern = re.escape(v_lower) if not v_lower.isalnum() else rf'\b{re.escape(v_lower)}\b'
            if re.search(pattern, tier2_text):
                found.append(tech)
                break
    return ", ".join(list(set(found))) if found else ''


def extract_language_req(row):
    """Trích xuất binary: 1 nếu yêu cầu ngoại ngữ, 0 nếu không."""
    # Kết hợp các văn bản và xử lý trường hợp dữ liệu bị trống (NaN)
    text = (str(row.get('requirements_text', '')) + " " + str(row.get('job_description', ''))).lower()
    
    # Danh sách tất cả các từ khóa ngoại ngữ 
    patterns = [
        r"english", r"tiếng anh", r"toeic", r"ielts",             # Anh
        r"japanese", r"tiếng nhật", r"jlpt", r"\bn[1-5]\b",       # Nhật
        r"korean", r"tiếng hàn", r"topik",                        # Hàn
        r"chinese", r"tiếng trung", r"hsk",                       # Trung
        r"french", r"tiếng pháp", r"delf", r"dalf",               # Pháp
        r"german", r"tiếng đức"                                   # Đức
    ]
    
    # Duyệt qua các mẫu regex
    for p in patterns:
        if re.search(p, text):
            return 1 # Có yêu cầu ngoại ngữ
            
    return 0 # Không tìm thấy yêu cầu ngoại ngữ

def get_work_method(row):
    text = (str(row['requirements_text']) + " " + str(row['job_description'])).lower()
    if any(word in text for word in ['remote', 'từ xa', 'tại nhà']):
        return 'Remote'
    if 'hybrid' in text:
        return 'Hybrid'
    return 'Onsite'

# ============================================================
# 4. CHƯƠNG TRÌNH CHÍNH (PIPELINE)
# ============================================================

def main():
    print("--- Đang khởi động Pipeline làm sạch dữ liệu ---")

    df = pd.read_csv(PATH_RAW_CSV)
    
    # 4.1 Trích xuất Tech Stack (Ưu tiên Skills Tags)
    print("--- Đang quét Tech Stack... ---")
    df['tech_stack'] = df.apply(lambda r: extract_tech_stack(r, tech_mapping), axis=1)
    
    # 4.2 Trích xuất Language Req (Đa ngôn ngữ)
    print("--- Đang quét yêu cầu Ngôn ngữ... ---")
    df['language_req'] = df.apply(extract_language_req, axis=1)
    
    # 4.3 Trích xuất Work Method
    print("--- Đang phân loại hình thức làm việc... ---")
    df['work_method'] = df.apply(get_work_method, axis=1)
    
    # 4.4 Trích xuất Is Manager
    print("--- Đang kiểm tra cấp bậc quản lý... ---")
    manager_keywords = r'leader|lead|manager|head|trưởng nhóm|director|giám đốc|chủ quản'
    df['is_manager'] = df['job_title'].str.contains(manager_keywords, case=False, na=False).astype(int)
    
    # 4.5 Lọc các cột đầu ra cuối cùng
    # Lưu ý: Giữ lại url và job_title như bạn yêu cầu
    final_cols = ['url', 'job_title', 'tech_stack', 'language_req', 'is_manager', 'work_method']
    final_df = df[final_cols]
    
    # 4.6 Lưu file
    final_df.to_csv(PATH_OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"\n--- HOÀN THÀNH ---")
    print(f"File lưu tại: {PATH_OUTPUT_CSV}")
    print(final_df.head())

if __name__ == "__main__":
    main()