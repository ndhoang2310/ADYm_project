ưimport pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from collections import Counter
from wordcloud import WordCloud
from itertools import combinations
# ====================================
# 1. LOAD DATA FROM MONGODB
# ====================================

client = MongoClient("mongodb+srv://ndhoang2310_db_user:hoang23102006@adym.qlakg5k.mongodb.net/")
db = client["VietnamITMarket"]
collection = db["jobs_clean"]

data = list(collection.find())

df = pd.DataFrame(data)

print("Dataset size:", df.shape)
print("Columns:", df.columns)


# ====================================
# 2. PROCESS TECH STACK
# ====================================

tech_list = []

for techs in df["tech_stack"].dropna():

    items = techs.split(",")

    for item in items:

        tech = item.strip()

        if tech != "":
            tech_list.append(tech)


# ====================================
# 3. COUNT TECHNOLOGY
# ====================================

tech_counter = Counter(tech_list)

top10 = tech_counter.most_common(10)

tech_names = [x[0] for x in top10]
tech_counts = [x[1] for x in top10]

print("\nTop 10 Tech Stack:")
for name, count in top10:
    print(name, count)


# ====================================
# 4. BAR CHART
# ====================================

plt.figure(figsize=(10,6))

plt.bar(tech_names, tech_counts)

plt.title("Top 10 Programming Languages / Frameworks")
plt.xlabel("Technology")
plt.ylabel("Number of Job Requirements")

plt.xticks(rotation=45)

plt.show()


# ====================================
# 5. WORD CLOUD FROM TECH STACK
# ====================================

text = " ".join(df["tech_stack"].dropna().astype(str))

wordcloud = WordCloud(
    width=1200,
    height=600,
    background_color="white",
    collocations=False
).generate(text)

plt.figure(figsize=(12,6))

plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

plt.title("Word Cloud of Tech Stack")

plt.show()
# ====================================
# 6. CO-OCCURRENCE ANALYSIS
# ====================================



pair_counter = Counter()

for techs in df["tech_stack"].dropna():

    tech_list = [t.strip() for t in techs.split(",") if t.strip() != ""]

    # tạo tất cả pair trong 1 job
    pairs = combinations(sorted(tech_list), 2)

    for pair in pairs:
        pair_counter[pair] += 1


# lấy top 10 pair
top_pairs = pair_counter.most_common(10)

print("\nTop 10 Tech Pairs (Co-occurrence):")

for pair, count in top_pairs:
    print(pair, count)
    
    
    
    
    
# ====================================
# 7. SALARY IMPACT OF ENGLISH REQUIREMENT
# ====================================

# Tính lương trung bình của mỗi job
df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)

# Loại bỏ job không có thông tin lương
salary_df = df.dropna(subset=["salary_avg"])

print("Total jobs with salary info:", salary_df.shape[0])


# ====================================
# GROUP BY ENGLISH REQUIREMENT
# ====================================

salary_compare = salary_df.groupby("language_req")["salary_avg"].mean()

print("\nAverage Salary by English Requirement:")
print(salary_compare)


# ====================================
# FORMAT OUTPUT (CHO DỄ ĐỌC)
# ====================================

no_eng = salary_compare.get(0, 0)
eng = salary_compare.get(1, 0)

print("\nFormatted Result:")
print(f"No English Required : {no_eng:.2f} million VND")
print(f"English Required    : {eng:.2f} million VND")

diff = eng - no_eng
print(f"Salary Difference   : {diff:.2f} million VND")


# ====================================
# VISUALIZATION
# ====================================

import matplotlib.pyplot as plt

labels = ["No English Required", "English Required"]
values = [no_eng, eng]

plt.figure(figsize=(6,5))

plt.bar(labels, values)

plt.title("Average Salary: English vs No English Requirement")
plt.ylabel("Average Salary (Million VND)")
plt.xlabel("English Requirement")

plt.show()