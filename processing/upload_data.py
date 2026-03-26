import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PATH_FINAL = os.path.join(ROOT_DIR, 'data', 'final_ml_dataset.csv')
ENV_PATH = os.path.join(ROOT_DIR, '.env')

load_dotenv(ENV_PATH)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "VietnamITMarket")
COLLECTION_NAME = "final_dataset"

def upload_to_mongodb():
    print(f"🚀 Bắt đầu quá trình Upload lên MongoDB...")
    
    try:
        df = pd.read_csv(PATH_FINAL)
        print(f"📥 Đã đọc file {PATH_FINAL} thành công. Số lượng: {len(df)} dòng.")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {PATH_FINAL}. Hãy chắc chắn bạn đã chạy script merge.")
        return

    df = df.replace({pd.NA: None})
    df = df.where(pd.notnull(df), None)

    records = df.to_dict(orient='records')
    
    try:
        print("🔗 Đang kết nối tới MongoDB Atlas...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]


        print(f"☁️ Đang đẩy {len(records)} bản ghi lên {DB_NAME}.{COLLECTION_NAME}...")
        result = collection.insert_many(records)
        
        print(f"✅ HOÀN TẤT! Đã upload thành công {len(result.inserted_ids)} documents.")

    except Exception as e:
        print(f"🔥 Lỗi kết nối hoặc cấu hình MongoDB: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    upload_to_mongodb()
    