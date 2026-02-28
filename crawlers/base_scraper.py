import logging
import os 
from abc import ABC, abstractmethod
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import certifi
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class BaseScraper(ABC):
    def __init__(self, source_name, db_name="ADYM", collection_name="raw_jobs"):
        self.source = source_name
        self.logger = logging.getLogger(self.source)

       
        
        try:
            self.client = MongoClient(
                os.getenv("MONGO_URI"),
                tlsCAFile=certifi.where()
            )
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            
            # Ping thử để chắc chắn kết nối thành công
            self.client.admin.command('ping')
            self.logger.info(f"✅ Đã kết nối MongoDB Atlas thành công!")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi kết nối MongoDB: {e}")
            raise e

    def save_job(self, job_data):
        # ... (Phần còn lại giữ nguyên như cũ) ...
        job_data['source'] = self.source
        job_data['crawled_date'] = datetime.now()

        if 'url' not in job_data or not job_data['url']:
            self.logger.warning("⚠️ Bỏ qua Job thiếu URL")
            return

        try:
            self.collection.insert_one(job_data)
            self.logger.info(f"💾 Đã lưu: {job_data.get('job_title', 'Unknown')}")
        except DuplicateKeyError:
            self.logger.warning(f"⏩ Đã tồn tại: {job_data['url']}")
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi lưu: {e}")

    @abstractmethod
    def scrape(self):
        pass

    def close_connection(self):
        self.client.close()


class MyScraper(BaseScraper):
    def scrape(self):
        self.logger.info(f"Starting scrape for {self.source}")
        # Implement scraping logic here

if __name__ == "__main__":
    # Instantiate the concrete subclass instead of the abstract BaseScraper
    scraper = MyScraper("ITViec")
    scraper.scrape()


