"""
fetch_data.py
=============
Kéo toàn bộ dữ liệu từ 5 collection MongoDB Atlas,
chuẩn hóa schema, xử lý duplicate và export ra raw_jobs.csv.

Yêu cầu file .env cùng thư mục:
    MONGO_URI=
    MONGO_DB=ADYM

Author : Leader (Nguyễn Đình Hoàng)
Project: Vietnam IT Market Analysis & Salary Prediction
"""

import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)



COLLECTIONS = [
    "careerviet_BAK",
    "topcv_Hoang",
    "topcv_Hoang_17_2",
    "it_viec_nt",
    "vietnamworks_nghgb",
    "glints_tnth",
]


OUTPUT_PATH = "data/00_raw_jobs.csv"

STANDARD_SCHEMA = [
    "url",
    "source",
    "job_title",
    "company_name",
    "salary_raw",
    "location_raw",
    "work_type",
    "job_level",
    "experience_raw",
    "experience_months",
    "job_domain",
    "requirements_text",
    "job_description",
    "skills_tags",
    "english_req",
    "education_raw",
    "contract_type",
    "benefits",
    "company_size",
    "posted_date",
    "crawled_date",
]

DEDUP_KEYS = ["url", "job_title", "company_name"]



def fetch_collection(db, name: str) -> pd.DataFrame:
    col = db[name]
    count = col.count_documents({})
    if count == 0:
        log.warning(f"  [{name}] Collection rỗng, bỏ qua.")
        return pd.DataFrame()

    docs = list(col.find({}, {"_id": 0}))
    df = pd.DataFrame(docs)
    log.info(f"  [{name}] {len(df):,} docs — {list(df.columns)}")
    return df


def fetch_all(mongo_uri: str, db_name: str) -> pd.DataFrame:
    log.info(f"Kết nối MongoDB Atlas — db: '{db_name}'")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10_000)
    client.admin.command("ping")
    log.info("Kết nối thành công.")

    db = client[db_name]
    frames = []
    for name in COLLECTIONS:
        df = fetch_collection(db, name)
        if not df.empty:
            frames.append(df)
    client.close()

    if not frames:
        raise RuntimeError("Không có dữ liệu nào được kéo về. Kiểm tra collection names.")

    combined = pd.concat(frames, ignore_index=True, sort=False)
    log.info(f"Sau concat: {len(combined):,} rows × {len(combined.columns)} cols")
    return combined



def normalise_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Cột có trong STANDARD_SCHEMA nhưng không có trong df → thêm vào với NaN
    - Cột không có trong STANDARD_SCHEMA (cột thừa) → drop
    - Sắp xếp lại đúng thứ tự STANDARD_SCHEMA
    """
    for col in STANDARD_SCHEMA:
        if col not in df.columns:
            df[col] = pd.NA
            log.info(f"  [schema] Thêm cột thiếu: '{col}' → NaN")

    extra = [c for c in df.columns if c not in STANDARD_SCHEMA]
    if extra:
        log.info(f"  [schema] Drop cột thừa: {extra}")
        df = df.drop(columns=extra)

    df = df[STANDARD_SCHEMA]
    log.info(f"Sau chuẩn hóa schema: {len(df.columns)} cols — đúng chuẩn ✅")
    return df



def completeness_score(row: pd.Series) -> int:
    """Đếm số field không null/rỗng — dùng để chọn row đầy đủ nhất."""
    def is_empty(v) -> bool:
        if isinstance(v, (list, dict)):
            return len(v) == 0
        try:
            if pd.isna(v):
                return True
        except (TypeError, ValueError):
            pass
        return str(v).strip() in ("", "nan", "NaN", "[]", "None")

    return row.apply(lambda v: 0 if is_empty(v) else 1).sum()


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dedup theo url + job_title + company_name.
    Với mỗi nhóm trùng → giữ row có nhiều thông tin nhất.
    """
    before = len(df)

    for key in DEDUP_KEYS:
        if key in df.columns:
            df[f"_key_{key}"] = df[key].astype(str).str.strip().str.lower()

    key_cols = [f"_key_{k}" for k in DEDUP_KEYS if f"_key_{k}" in df.columns]

    df["_score"] = df.apply(completeness_score, axis=1)
    df = df.sort_values("_score", ascending=False)
    df = df.drop_duplicates(subset=key_cols, keep="first")
    df = df.drop(columns=["_score"] + key_cols)

    after = len(df)
    log.info(f"Sau dedup: {after:,} rows ({before - after:,} duplicates removed) ✅")
    return df.reset_index(drop=True)



def export(df: pd.DataFrame, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    log.info(f"✅ Đã lưu → '{out}'  ({len(df):,} rows × {len(df.columns)} cols)")



if __name__ == "__main__":
    load_dotenv()

    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB  = os.getenv("MONGO_DB")

    if not MONGO_URI or not MONGO_DB:
        raise EnvironmentError("Thiếu MONGO_URI hoặc MONGO_DB trong file .env")

    df = fetch_all(MONGO_URI, MONGO_DB)
    df = normalise_schema(df)
    df = deduplicate(df)
    export(df, OUTPUT_PATH)