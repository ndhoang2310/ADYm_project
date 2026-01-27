import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Cấu hình Logging (để in ra màn hình trạng thái chạy)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class BaseScraper(ABC):
    """
    Class cha cho tất cả các Scraper.
    Nhiệm vụ: Quản lý kết nối Database và hàm lưu dữ liệu chung.
    """

    def __init__(self, source_name, db_name="VietnamITMarket", collection_name="raw_jobs"):
        # 1. Định danh: Scraper này tên gì? (itviec, topcv, hay linkedin?)
        self.source = source_name
        
        # 2. Tạo Logger riêng để dễ theo dõi lỗi
        self.logger = logging.getLogger(self.source)

        # 3. Kết nối MongoDB
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.logger.info(f"✅ Đã kết nối MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            self.logger.error(f"❌ Lỗi kết nối MongoDB: {e}")
            raise e

    def save_job(self, job_data):
        """
        Hàm quan trọng nhất: Lưu job vào DB và xử lý trùng lặp.
        """
        # A. Tự động điền các thông tin quản lý (Metadata)
        job_data['source'] = self.source
        job_data['crawled_date'] = datetime.now()  # Thời điểm hiện tại

        # B. Kiểm tra sơ bộ (Validation) - đảm bảo có URL và Title
        if 'url' not in job_data or not job_data['url']:
            self.logger.warning("⚠️ Bỏ qua Job thiếu URL")
            return

        # C. Thử lưu vào Database
        try:
            # insert_one: Lệnh của Mongo để thêm 1 bản ghi
            self.collection.insert_one(job_data)
            self.logger.info(f"💾 Đã lưu: {job_data.get('job_title', 'Unknown')} ({job_data['url']})")
        
        except DuplicateKeyError:
            # Nếu trùng URL (do index unique), Mongo sẽ báo lỗi này.
            # Ta bắt lỗi lại và chỉ in ra cảnh báo, không làm sập chương trình.
            self.logger.warning(f"⏩ Đã tồn tại (Bỏ qua): {job_data['url']}")
        
        except Exception as e:
            # Các lỗi khác (sai định dạng, mất mạng...)
            self.logger.error(f"❌ Lỗi khi lưu: {e}")

    @abstractmethod
    def scrape(self):
        """
        Hàm trừu tượng.
        Class cha không viết gì ở đây cả.
        Bắt buộc Class con (Dev A, Dev B) phải tự viết logic cào của riêng họ.
        """
        pass

    def close_connection(self):
        """Đóng kết nối khi chạy xong để giải phóng tài nguyên"""
        self.client.close()
        self.logger.info("Đã đóng kết nối Database.")import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Cấu hình Logging (để in ra màn hình trạng thái chạy)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class BaseScraper(ABC):
    """
    Class cha cho tất cả các Scraper.
    Nhiệm vụ: Quản lý kết nối Database và hàm lưu dữ liệu chung.
    """

    def __init__(self, source_name, db_name="VietnamITMarket", collection_name="raw_jobs"):
        # 1. Định danh: Scraper này tên gì? (itviec, topcv, hay linkedin?)
        self.source = source_name
        
        # 2. Tạo Logger riêng để dễ theo dõi lỗi
        self.logger = logging.getLogger(self.source)

        # 3. Kết nối MongoDB
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.logger.info(f"✅ Đã kết nối MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            self.logger.error(f"❌ Lỗi kết nối MongoDB: {e}")
            raise e

    def save_job(self, job_data):
        """
        Hàm quan trọng nhất: Lưu job vào DB và xử lý trùng lặp.
        """
        # A. Tự động điền các thông tin quản lý (Metadata)
        job_data['source'] = self.source
        job_data['crawled_date'] = datetime.now()  # Thời điểm hiện tại

        # B. Kiểm tra sơ bộ (Validation) - đảm bảo có URL và Title
        if 'url' not in job_data or not job_data['url']:
            self.logger.warning("⚠️ Bỏ qua Job thiếu URL")
            return

        # C. Thử lưu vào Database
        try:
            # insert_one: Lệnh của Mongo để thêm 1 bản ghi
            self.collection.insert_one(job_data)
            self.logger.info(f"💾 Đã lưu: {job_data.get('job_title', 'Unknown')} ({job_data['url']})")
        
        except DuplicateKeyError:
            # Nếu trùng URL (do index unique), Mongo sẽ báo lỗi này.
            # Ta bắt lỗi lại và chỉ in ra cảnh báo, không làm sập chương trình.
            self.logger.warning(f"⏩ Đã tồn tại (Bỏ qua): {job_data['url']}")
        
        except Exception as e:
            # Các lỗi khác (sai định dạng, mất mạng...)
            self.logger.error(f"❌ Lỗi khi lưu: {e}")

    @abstractmethod
    def scrape(self):
        """
        Hàm trừu tượng.
        Class cha không viết gì ở đây cả.
        Bắt buộc Class con (Dev A, Dev B) phải tự viết logic cào của riêng họ.
        """
        pass

    def close_connection(self):
        """Đóng kết nối khi chạy xong để giải phóng tài nguyên"""
        self.client.close()
        self.logger.info("Đã đóng kết nối Database.")