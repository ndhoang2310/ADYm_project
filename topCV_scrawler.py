import time
import random 
from datetime import datetime
from seleniumbase import Driver
from base_scraper import BaseScraper 

class TopCVScraper(BaseScraper):
    def __init__(self, start_url):
        # Khởi tạo với collection riêng của bạn
        super().__init__(source_name="topcv", collection_name="topcv_Hoang_17_2")
        self.base_url = start_url
        print("🚀 Đang khởi động trình duyệt (UC Mode - Enhanced)...")
        self.driver = Driver(uc=True, headless=False)

    def is_url_exists(self, url):
        """Kiểm tra URL đã tồn tại trong MongoDB chưa (Xây dựng tại class này)"""
        return self.collection.find_one({"url": url}) is not None

    def get_text_js(self, selector):
        script = f'var el = document.querySelector("{selector}"); return el ? el.innerText.trim() : null;'
        return self.driver.execute_script(script)

    def get_job_title_safely(self):
        selectors = ["h1[class*='job-detail__info--title']", ".job-detail__info--title", "h1.title"]
        for s in selectors:
            if self.driver.is_element_visible(s):
                text = self.get_text_js(s)
                if text: return text
        return None

    def get_company_name_safely(self):
        selectors = [".company-name-label a.name", ".company-name-label a", "a[href*='/cong-ty/'] .name"]
        for s in selectors:
            if self.driver.is_element_visible(s):
                text = self.get_text_js(s)
                if text: return text
        return None

    def extract_header_summary(self):
        """Lấy Lương, Địa điểm, Kinh nghiệm từ các box icon"""
        results = {"salary_raw": None, "location_raw": "N/A", "experience_raw": None}
        mapping = {"mức lương": "salary_raw", "địa điểm": "location_raw", "kinh nghiệm": "experience_raw"}
        
        sections = self.driver.find_elements(".job-detail__info--section")
        for section in sections:
            try:
                title = section.find_element(by="css selector", value=".job-detail__info--section-content-title").text.lower()
                value = section.find_element(by="css selector", value=".job-detail__info--section-content-value").text.strip()
                for label, key in mapping.items():
                    if label in title: results[key] = value
            except: continue
        return results

    def extract_general_info_dynamic(self):
        """Lấy Cấp bậc, Học vấn, Hình thức làm việc"""
        data = {"job_level": None, "education_raw": None, "work_type": None}
        label_map = {"cấp bậc": "job_level", "học vấn": "education_raw", "hình thức": "work_type"}

        groups = self.driver.find_elements(".box-general-group-info")
        for group in groups:
            try:
                title = group.find_element(by="css selector", value=".box-general-group-info-title").text.lower()
                value = group.find_element(by="css selector", value=".box-general-group-info-value").text.strip()
                for label, key in label_map.items():
                    if label in title: data[key] = value
            except: continue
        return data

    def extract_content_blocks(self):
        """Lấy Mô tả, Yêu cầu và Quyền lợi (Khôi phục đầy đủ)"""
        data = {"job_description": None, "requirements_text": "N/A", "benefits": None}
        blocks = self.driver.find_elements(".job-description__item")
        for block in blocks:
            try:
                title = block.find_element(by="css selector", value="h3").text.lower()
                content = block.find_element(by="css selector", value=".job-description__item--content").text.strip()
                if "mô tả" in title: data["job_description"] = content
                elif "yêu cầu" in title: data["requirements_text"] = content
                elif "quyền lợi" in title: data["benefits"] = content
            except: continue
        return data

    def scrape_job_detail(self, url):
        """Cào chi tiết một công việc"""
        try:
            self.driver.get(url)
            self.driver.wait_for_element("h1[class*='job-detail__info--title']", timeout=12)
            time.sleep(1.5)

            job_title = self.get_job_title_safely()
            company_name = self.get_company_name_safely()
            if not job_title: return None

            item = {
                "url": url,
                "source": "topcv",
                "job_title": job_title,
                "company_name": company_name,
                "crawled_date": datetime.now(),
                "posted_date": self.get_text_js(".job-detail__info--deadline-date")
            }

            # Gom dữ liệu từ các hàm bóc tách
            header_info = self.extract_header_summary()
            general_info = self.extract_general_info_dynamic()
            content_blocks = self.extract_content_blocks()
            
            item.update(header_info)
            item.update(general_info)
            item.update(content_blocks)

            # --- XỬ LÝ SKILL TAGS KỸ LƯỠNG ---
            tags = self.driver.find_elements(".box-category-tag")
            raw_tags = [t.text.strip() for t in tags if t.text.strip()]
            
            # 1. Danh sách loại trừ dựa trên dữ liệu metadata đã lấy
            meta_values = [
                str(item.get('location_raw', '')).lower(),
                str(item.get('work_type', '')).lower(),
                str(item.get('job_level', '')).lower(),
                str(item.get('experience_raw', '')).lower(),
                str(item.get('education_raw', '')).lower()
            ]

            # 2. Blacklist các từ khóa rác thường xuất hiện trong tag của TopCV
            junk_blacklist = [
                'hà nội', 'hồ chí minh', 'đà nẵng', 'hcm', 'toàn quốc', 'miền nam', 'miền bắc',
                'nhân viên', 'trưởng nhóm', 'trưởng phòng', 'giám đốc', 'thực tập', 'fresher', 'junior', 'senior',
                'toàn thời gian', 'bán thời gian', 'tháng', 'năm', 'người', 'triệu', 'vnd', 'usd',
                'thỏa thuận', 'cạnh tranh', 'đại học', 'cao đẳng', 'hạn nộp', 'quy mô', 'vị trí'
            ]

            filtered_skills = []
            for tag in list(set(raw_tags)):
                tag_lower = tag.lower()
                # Kiểm tra xem tag có nằm trong metadata hoặc blacklist không
                is_meta = any(val in tag_lower or tag_lower in val for val in meta_values if val)
                is_junk = any(junk in tag_lower for junk in junk_blacklist)
                
                if not is_meta and not is_junk:
                    filtered_skills.append(tag)

            item['skills_tags'] = filtered_skills
            # ---------------------------------
            
            if item.get('work_type'):
                wt = item['work_type'].lower()
                item['contract_type'] = 'Full-time' if 'toàn thời gian' in wt else ('Part-time' if 'bán thời gian' in wt else item['work_type'])
            
            return item
        except Exception as e:
            print(f"❌ Lỗi khi cào chi tiết {url}: {e}")
            return None

    def scrape(self):
        page_num = 1
        while True:
            current_url = f"{self.base_url}&page={page_num}"
            print(f"\n--- 📄 Đang quét trang {page_num}: {current_url} ---")
            
            self.driver.get(current_url)
            time.sleep(random.uniform(5, 8))

            if self.driver.is_element_visible(".empty-job-list") or self.driver.is_text_visible("Chưa tìm thấy việc làm"):
                break

            links = [el.get_attribute("href") for el in self.driver.find_elements(".job-item-search-result .title a") if el.get_attribute("href")]
            links = list(set(links))
            print(f"✅ Tìm thấy {len(links)} link. Đang lọc trùng...")

            for link in links:
                # Kiểm tra trùng tại đây trước khi cào chi tiết
                if self.is_url_exists(link):
                    print(f"   ⏩ Bỏ qua (Đã tồn tại): {link[:50]}...")
                    continue

                data = self.scrape_job_detail(link)
                if data:
                    self.save_job(data)
                    print(f"   ✔️ Đã lưu: {data['job_title'][:40]}...")
                time.sleep(random.uniform(1, 3))

            page_num += 1
        
        self.driver.quit()
        self.close_connection()

if __name__ == "__main__":
    url_it = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=1"
    bot = TopCVScraper(start_url=url_it)
    bot.scrape()