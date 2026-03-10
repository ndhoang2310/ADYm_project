import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. SETUP ĐƯỜNG DẪN TỰ ĐỘNG
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PATH_FINAL = os.path.join(ROOT_DIR, 'data', 'dataset_after_categorical_imputing.csv')
ENV_PATH = os.path.join(ROOT_DIR, '.env')

# 2. LOAD BIẾN MÔI TRƯỜNG
load_dotenv(ENV_PATH)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "VietnamITMarket")
COLLECTION_NAME = "jobs_clean_1"  # Collection mới dành cho data đã sạch

def upload_to_mongodb():
    print(f"🚀 Bắt đầu quá trình Upload lên MongoDB...")
    
    # Bước 1: Đọc file CSV
    try:
        df = pd.read_csv(PATH_FINAL)
        print(f"📥 Đã đọc file {PATH_FINAL} thành công. Số lượng: {len(df)} dòng.")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {PATH_FINAL}. Hãy chắc chắn bạn đã chạy script merge.")
        return

    # Bước 2: Xử lý dữ liệu rỗng (Quan trọng)
    # Pandas dùng NaN (Not a Number), MongoDB dùng null. 
    # Cần thay thế toàn bộ NaN bằng None để pymongo tự động dịch sang null trong BSON.
    df = df.replace({pd.NA: None})
    df = df.where(pd.notnull(df), None)

    # Bước 3: Chuyển DataFrame thành danh sách các Dictionary (chuẩn JSON)
    records = df.to_dict(orient='records')
    
    # Bước 4: Kết nối và Upload
    try:
        print("🔗 Đang kết nối tới MongoDB Atlas...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # (Tùy chọn) Xóa dữ liệu cũ trong collection jobs_clean trước khi ghi đè mới
        # Nếu bạn muốn mỗi lần chạy là ghi đè toàn bộ bản mới nhất, hãy mở comment dòng dưới:
        # print("🧹 Đang dọn dẹp collection cũ...")
        # collection.delete_many({})

        print(f"☁️ Đang đẩy {len(records)} bản ghi lên {DB_NAME}.{COLLECTION_NAME}...")
        # insert_many giúp đẩy toàn bộ dữ liệu lên trong 1 lần (Batch Insert), rất nhanh
        result = collection.insert_many(records)
        
        print(f"✅ HOÀN TẤT! Đã upload thành công {len(result.inserted_ids)} documents.")

    except Exception as e:
        print(f"🔥 Lỗi kết nối hoặc cấu hình MongoDB: {e}")
    finally:
        # Luôn đóng kết nối sau khi làm xong
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    upload_to_mongodb()
    