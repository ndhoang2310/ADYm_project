import pandas as pd
import re
import json
from collections import defaultdict

# 1. Đọc hạt giống
with open('tech_seed.txt', 'r', encoding='utf-8') as f:
    seeds = [line.strip() for line in f.readlines()]

# 2. Đọc 6000 jobs
df = pd.read_csv(r'D:\Documents\Clean\processing\data\raw_jobs.csv')
descriptions = df['requirements_text'].fillna('').astype(str).tolist()
full_text = " ".join(descriptions)

# 3. Thu hẹp Whitelist Suffix (Chỉ giữ lại những từ thực sự tạo thành tên công nghệ mới)
# Loại bỏ: Framework, Script, API, Server, Development... vì chúng chỉ là từ bổ trợ
tech_suffixes = {'core', 'se', 'ee', 'sharp', 'boot', 'plus', 'net'}

def get_real_variants(seeds, corpus):
    refined_dict = defaultdict(set)
    
    for seed in seeds:
        seed_esc = re.escape(seed)
        
        # --- QUY TẮC 1: Tìm chính xác cách viết trong văn bản (Case-sensitive thực tế) ---
        # Tìm mọi lần xuất hiện của seed để lấy đúng định dạng hoa/thường người ta viết
        actual_mentions = re.findall(rf'\b{seed_esc}\b', corpus, re.IGNORECASE)
        for m in actual_mentions:
            # Chỉ lấy nếu không phải là PYTHON (viết hoa toàn bộ thường là lỗi hoặc tiêu đề JD)
            # hoặc chỉ lấy nếu nó xuất hiện phổ biến (ví dụ: JAVA, JS)
            if not (m.isupper() and len(m) > 3): 
                refined_dict[seed].add(m)
            elif m in ["JAVA", "JS", "SQL", "PHP", "HTML", "CSS", "UI", "UX"]:
                refined_dict[seed].add(m)

        # --- QUY TẮC 2: Nhận diện Version hợp lý (VD: Java 17, không lấy C 1) ---
        # Yêu cầu: Số phiên bản thường đi kèm dấu chấm (3.x) hoặc là số > 1 để tránh số thứ tự (C 1, C 2)
        ver_pattern = rf'\b{seed_esc}[\s\-\/]?(\d+\.[\dxX]+|\d{{2,}}|\d\+)\b'
        for v in re.findall(ver_pattern, corpus, re.IGNORECASE):
            refined_dict[seed].add(f"{seed} {v}".strip())

        # --- QUY TẮC 3: Nhận diện Suffix đặc thù (VD: Java Core, C Sharp) ---
        sfx_pattern = rf'\b({seed_esc})\s+([A-Za-z\#\+]+)\b'
        for m_seed, s in re.findall(sfx_pattern, corpus, re.IGNORECASE):
            if s.lower() in tech_suffixes:
                # Tìm lại trong corpus để lấy đúng Case (ví dụ: Java Core thay vì Java core)
                match_text = re.search(rf'\b{m_seed}\s+{s}\b', corpus, re.IGNORECASE)
                if match_text:
                    refined_dict[seed].add(match_text.group())

        # --- QUY TẮC 4: Biến thể dính liền số (VD: Python3, Java8) ---
        sticky = re.findall(rf'\b({seed_esc}\d+)\b', corpus, re.IGNORECASE)
        refined_dict[seed].update(sticky)
        
        # --- QUY TẮC 5: Xử lý ngoại lệ thủ công cho các Tech quan trọng ---
        if seed == "Python" and "PySpark" in corpus:
            refined_dict[seed].add("PySpark")
        if seed == "JavaScript":
            refined_dict[seed].update(["JS", "js", "ES6+"])

    return refined_dict

# 4. Thực thi
print("Đang trích xuất biến thể thực tế từ 6000 jobs...")
extracted_mapping = get_real_variants(seeds, full_text)

# 5. Làm sạch lần cuối: Loại bỏ các biến thể quá dài hoặc chứa từ nhiễu
final_mapping = {}
for k, v in extracted_mapping.items():
    clean_list = set()
    for variant in v:
        # Loại bỏ nếu chứa các từ "thừa" bạn đã nêu
        if not any(word in variant.lower() for word in ['framework', 'api', 'server', 'script', 'development']):
            clean_list.add(variant)
        # Đặc cách cho các trường hợp ngoại lệ
        if "Spring Boot" in variant or "JavaScript" in variant:
            clean_list.add(variant)
            
    if clean_list:
        final_mapping[k] = sorted(list(clean_list))

# 6. Lưu kết quả
with open('mapping_dict.json', 'w', encoding='utf-8') as f:
    json.dump(final_mapping, f, ensure_ascii=False, indent=4)

print("Hoàn tất! Kết quả đã được lọc sạch nhiễu.")
