import time
import sys
import random
import math
from datetime import datetime
from playwright.sync_api import sync_playwright
from base_scraper import BaseScraper 

class GlintsScraper(BaseScraper):
    def __init__(self):
        # 1. Kế thừa chuẩn từ Leader
        super().__init__(source_name="glints", db_name="ADYM", collection_name="glints_tnth")
        
        # 2. Đảm bảo Index duy nhất để chặn trùng URL tuyệt đối
        self.collection.create_index("url", unique=True)
        
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    def scrape(self):
        self._crawl_missing_details()
        """Logic chính tích hợp từ main cũ: Chạy vô hạn và chia 2 Phase"""
        keywords = ["Frontend", "Backend", "Java", "Python", "NodeJS", 
                    "Full Stack", "Mobile Developer", "Data Scientist", 
                    "Business Analyst", "Tester", "Project Manager", "AI", "Machine Learning", "IT"]
        while True:
            self.logger.info("🌊 [PHASE 1] BẮT ĐẦU QUÉT METADATA CHO TẤT CẢ TỪ KHÓA...")
            
            for kw in keywords:
                self.logger.info(f"🎯 Target: {kw.upper()}")
                
                for page_num in range(1, 11): 
                    # Lấy danh sách và tổng số trang thực tế
                    jobs, total_pages = self._scrape_list_page(page_num, kw)
                    
                    # Nếu bị chặn (jobs is None), chuyển từ khóa ngay
                    if jobs is None:
                        self.logger.warning(f"⚠️ {kw} bị kẹt ở trang {page_num}. Chuyển mục tiêu.")
                        break
                    
                    # Nếu hết dữ liệu thực tế
                    if len(jobs) == 0:
                        self.logger.info(f"⏹️ Đã hết tin cho '{kw}'.")
                        break
                    
                    self.logger.info(f"📊 Trang {page_num} trả về {len(jobs)} tin")

                    for job in jobs:
                        # Lưu bằng hàm của Leader (tự thêm source, crawled_date)
                        self.save_job(job)
                    
                    # SỬA LỖI: Chỉ dừng khi page_num thực sự lớn hơn hoặc bằng total_pages (với total_pages > 0)
                    if total_pages > 0 and page_num >= total_pages:
                        self.logger.info(f"✅ Đã quét xong tất cả các trang của {kw}")
                        break
                    
                    time.sleep(random.randint(5, 10))

            # --- PHASE 2: VÁ DỮ LIỆU CHI TIẾT ---
            self.logger.info("🧹 [PHASE 2] BẮT ĐẦU VÁ DETAIL...")
            self._crawl_missing_details()

            # --- PHASE 3: NGHỈ NGƠI TỔNG THỂ (15 phút) ---
            self.logger.info(f"😴 Chu kỳ hoàn tất lúc {time.ctime()}. Nghỉ 15 phút...")
            time.sleep(900)

    def _scrape_list_page(self, page_num, keyword):
        """Bóc tách danh sách và tính toán lại total_pages chuẩn xác"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=random.choice(self.ua_list))
            page_obj = context.new_page()
            url = f"https://glints.com/vn/opportunities/jobs/explore?keyword={keyword}&country=VN&page={page_num}"
            
            try:
                def is_search_api(res):
                    return "graphql" in res.url and "searchJobsV3" in res.url and res.status == 200

                with page_obj.expect_response(is_search_api, timeout=30000) as response_info:
                    page_obj.goto(url, wait_until="networkidle", timeout=60000)
                    page_obj.mouse.wheel(0, 500) 
                    time.sleep(2)

                data = response_info.value.json()
                search_data = data.get('data', {}).get('searchJobsV3', {})
                
                # SỬA LỖI TÍNH TRANG: Dùng math.ceil để làm tròn lên chuẩn xác
                total_jobs = search_data.get('totalJobCount', 0)
                total_pages = math.ceil(total_jobs / 30) if total_jobs > 0 else 0
                
                raw_list = search_data.get('jobsInPage', [])
                processed = []
                for r in raw_list:
                    loc = r.get('location', {})
                    parents = loc.get('parents', [])
                    full_loc = f"{loc.get('name', '')}, {parents[0].get('name', '') if parents else ''}".strip(", ")
                    
                    # Cấu trúc Dictionary khớp y hệt hình ảnh Database của bạn
                    processed.append({
                        "url": f"https://glints.com/vn/opportunities/jobs/{r.get('id')}",
                        "job_title": r.get('title'),
                        "company_name": (r.get('company') or {}).get('name'),
                        "salary_raw": "Thỏa thuận",
                        "location_raw": full_loc or "Việt Nam",
                        "work_type": None,
                        "job_level": None,
                        "experience_raw": f"{r.get('minYearsOfExperience', 0)}-{r.get('maxYearsOfExperience', 0)} năm",
                        "education_raw": r.get('educationLevel'),
                        "english_req": None,
                        "requirements_text": None,
                        "skills_tags": [s['skill']['name'] for s in r.get('skills', []) if 'skill' in s],
                        "source": self.source,
                        "posted_date": r.get('createdAt')
                    })
                return processed, total_pages
            except Exception as e:
                self.logger.error(f"❌ Lỗi trang {page_num}: {e}")
                return None, 0
            finally:
                browser.close()

    def _crawl_missing_details(self):
        """Vá dữ liệu chi tiết cho các tin chưa có requirements_text"""
        query = {"source": self.source, "requirements_text": None}
        missing_jobs = list(self.collection.find(query).limit(50)) 

        if not missing_jobs:
            self.logger.info("✅ Database đã đầy đủ thông tin!")
            return

        for job in missing_jobs:
            try:
                job_id = job['url'].split('/')[-1].split('?')[0]
                detail_data = self._scrape_detail_logic(job_id)
                
                if detail_data:
                    self.collection.update_one({"_id": job["_id"]}, {"$set": detail_data})
                    self.logger.info(f"   ✅ Đã vá: {job.get('job_title')}")
                else:
                    self.logger.warning("🛑 Glints chặn vá tin. Nghỉ 15 phút...")
                    time.sleep(900)
                    break 
                
                time.sleep(random.uniform(8, 15)) 
            except Exception as e:
                self.logger.error(f"❌ Lỗi vá ID {job['_id']}: {e}")

    def _scrape_detail_logic(self, job_id):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            url = f"https://glints.com/vn/opportunities/jobs/{job_id}"
            try:
                response = page.goto(url, wait_until="networkidle", timeout=60000)
                if response.status in [403, 400]:
                    return None

                # 1. GTM + DOM metadata
                company_size = "N/A"
                salary_from_dom = "Thỏa thuận"

                gtm_btn = page.locator('.job_details-apply_button').first
                if gtm_btn.count() > 0:
                    company_size = gtm_btn.get_attribute(
                        'data-gtm-company-size'
                    ) or "N/A"

                salary_loc = page.locator(
                    'span[class*="SalaryWrapper"], div[class*="SalaryJobOverview"], .lcEIyF'
                ).first
                if salary_loc.count() > 0:
                    text = salary_loc.inner_text().strip()
                    if "VND" in text or "Tr" in text:
                        salary_from_dom = text.replace("/Tháng", "").strip()

                # 2. DOM DETAIL (nguồn chính)
                title = (
                    page.locator('h1[class*="JobOverViewTitle"]').inner_text().strip()
                    if page.locator('h1[class*="JobOverViewTitle"]').count() > 0
                    else "N/A"
                )

                info_nodes = page.locator(
                    'div[class*="JobOverViewInfo"]'
                ).all_inner_texts()
                c_type, w_type = "N/A", "N/A"
                for text in info_nodes:
                    if " · " in text:
                        parts = text.split(" · ")
                        c_type = parts[0].strip()
                        w_type = parts[1].strip()

                requirements_text = (
                    page.locator('div[class*="JobDescriptionContainer"]')
                    .inner_text()
                    .strip()
                    if page.locator('div[class*="JobDescriptionContainer"]').count() > 0
                    else "N/A"
                )

                return {
                    "job_title": title,
                    "company_size": company_size,
                    "contract_type": c_type,
                    "work_type": w_type,
                    "requirements_text": requirements_text,
                    "salary_raw": salary_from_dom
                }

            except Exception as e:
                print(f"⚠️ Lỗi: {e}")
                return None
            finally:
                browser.close()

if __name__ == "__main__":
    scraper = GlintsScraper()
    try:
        scraper.scrape()
    except KeyboardInterrupt:
        print("\n👋 Đã nhận lệnh dừng. Đang đóng kết nối...")
        scraper.close_connection() # Dùng hàm đóng kết nối của Leader
        sys.exit(0)