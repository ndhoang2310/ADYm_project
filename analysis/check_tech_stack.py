import pandas as pd
import re
from pymongo import MongoClient

# =========================
# 1. LOAD DATA FROM MONGODB
# =========================

client = MongoClient("mongodb+srv://ndhoang2310_db_user:hoang23102006@adym.qlakg5k.mongodb.net/")
db = client["VietnamITMarket"]
collection = db["jobs_clean"]

data = list(collection.find())

df = pd.DataFrame(data)

print("Dataset size:", df.shape)


# =========================
# 2. TECH KEYWORD DICTIONARY
# =========================

tech_keywords = [
    "python","java","javascript","typescript","c++","c#",
    "react","angular","vue","node","nodejs",
    "django","flask","spring","spring boot",
    "docker","kubernetes","aws","azure","gcp",
    "sql","mysql","postgresql","mongodb","redis",
    "tensorflow","pytorch","scikit-learn",
    "pandas","numpy",
    "git","linux"
]


# =========================
# 3. QA CHECK
# =========================

errors = []

for idx, row in df.iterrows():

    requirements = str(row.get("requirements_text", "")).lower()

    tech_stack = row.get("tech_stack", [])

    if isinstance(tech_stack, list):
        tech_stack = [t.lower() for t in tech_stack]
    else:
        tech_stack = []

    # tìm keyword trong requirements
    found_keywords = []

    for tech in tech_keywords:
        if re.search(r"\b" + re.escape(tech) + r"\b", requirements):
            found_keywords.append(tech)

    # so sánh với tech_stack
    missing = [tech for tech in found_keywords if tech not in tech_stack]

    if missing:
        errors.append({
            "record_index": idx,
            "missing_keywords": missing,
            "tech_stack": tech_stack,
            "requirements_preview": requirements[:200]
        })


# =========================
# 4. EXPORT REPORT
# =========================

errors_df = pd.DataFrame(errors)

print("Total errors:", errors_df.shape)

errors_df.to_csv("qa_missing_tech_stack.csv", index=False)

print("QA report exported")


# =========================
# 5. SHOW SAMPLE ERRORS
# =========================

print("\nSample Errors:")
print(errors_df.head(10))