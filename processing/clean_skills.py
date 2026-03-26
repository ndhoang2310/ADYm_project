import pandas as pd
import re
import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) 
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PATH_JSON_CONFIG = os.path.join(ROOT_DIR, 'data', 'mapping_dict.json')
PATH_RAW_CSV     = os.path.join(ROOT_DIR, 'data', '00_raw_jobs.csv')
PATH_OUTPUT_CSV  = os.path.join(CURRENT_DIR, 'artifacts', '01_clean_skills.csv')

if os.path.exists(PATH_JSON_CONFIG):
    with open(PATH_JSON_CONFIG, 'r', encoding='utf-8') as f:
        tech_mapping = json.load(f)
else:
    print(f"LỖI: Không tìm thấy file JSON tại {PATH_JSON_CONFIG}")
    tech_mapping = {}


def extract_tech_stack(row, mapping):
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
    text = (str(row.get('requirements_text', '')) + " " + str(row.get('job_description', ''))).lower()
    
    patterns = [
        r"english", r"tiếng anh", r"toeic", r"ielts",
        r"japanese", r"tiếng nhật", r"jlpt", r"\bn[1-5]\b",
        r"korean", r"tiếng hàn", r"topik",
        r"chinese", r"tiếng trung", r"hsk",
        r"french", r"tiếng pháp", r"delf", r"dalf",
        r"german", r"tiếng đức"
    ]
    
    for p in patterns:
        if re.search(p, text):
            return 1
            
    return 0

def get_work_method(row):
    text = (str(row['requirements_text']) + " " + str(row['job_description'])).lower()
    if any(word in text for word in ['remote', 'từ xa', 'tại nhà']):
        return 'Remote'
    if 'hybrid' in text:
        return 'Hybrid'
    return 'Onsite'


def main():
    print("--- Đang khởi động Pipeline làm sạch dữ liệu ---")

    df = pd.read_csv(PATH_RAW_CSV)
    
    print("--- Đang quét Tech Stack... ---")
    df['tech_stack'] = df.apply(lambda r: extract_tech_stack(r, tech_mapping), axis=1)
    
    print("--- Đang quét yêu cầu Ngôn ngữ... ---")
    df['language_req'] = df.apply(extract_language_req, axis=1)
    
    print("--- Đang phân loại hình thức làm việc... ---")
    df['work_method'] = df.apply(get_work_method, axis=1)
    
    print("--- Đang kiểm tra cấp bậc quản lý... ---")
    manager_keywords = r'leader|lead|manager|head|trưởng nhóm|director|giám đốc|chủ quản'
    df['is_manager'] = df['job_title'].str.contains(manager_keywords, case=False, na=False).astype(int)
    
    final_cols = ['url', 'job_title', 'tech_stack', 'language_req', 'is_manager', 'work_method']
    final_df = df[final_cols]
    
    final_df.to_csv(PATH_OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"\n--- HOÀN THÀNH ---")
    print(f"File lưu tại: {PATH_OUTPUT_CSV}")
    print(final_df.head())

if __name__ == "__main__":
    main()