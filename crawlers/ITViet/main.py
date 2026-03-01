import json
import re
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from base_scraper import BaseScraper 

class ITViecScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="itviec", collection_name="it_viec_nt__")

    # ---------- PHASE 1: LẤY URL (GIỮ NGUYÊN TUYỆT ĐỐI) ----------
    def scrape_job_urls(self, page):
        urls = set()
        for page_num in range(1, 61):
            try:
                page.goto(f"https://itviec.com/it-jobs?page={page_num}", wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                # Lấy slug từ data attribute chuẩn theo image_8eb7b6.png
                slugs = page.locator("div.job-card").evaluate_all(
                    "els => els.map(el => el.getAttribute('data-search--job-selection-job-slug-value'))"
                )
                for slug in slugs:
                    if slug: urls.add(f"https://itviec.com/it-jobs/{slug}")
            except: break
        return list(urls)

    # ---------- PHASE 2: CÀO CHI TIẾT (FIX EXPERTISE & DOMAIN) ----------
    def scrape_job_detail(self, page, url):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            json_str = page.evaluate('() => document.querySelector(\'script[type="application/ld+json"]\')?.innerText')
            if not json_str: return None
            
            data = json.loads(json_str)
            node = data[0] if isinstance(data, list) else data

            # 1. XỬ LÝ SKILLS (Giới hạn vùng .bg-it-white để tránh lấy nhầm job gợi ý)
            skills = []
            skills_raw = node.get('skills', "")
            if skills_raw and isinstance(skills_raw, str):
                skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            
            if not skills:
                # Chỉ lấy tag trong vùng nội dung chính
                ui_skills = page.locator(".bg-it-white .tag-list a, .bg-it-white .igap-2 a").all_text_contents()
                skills = list(set([s.strip() for s in ui_skills if s.strip()]))

            # 2. XỬ LÝ LOCATION (Ghép Quận + Thành phố)
            addr = node.get('jobLocation', [{}])[0].get('address', {})
            full_location = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}".strip(", ")

            # 3. FIX LỖI EXPERTISE & DOMAIN (CHỈ SỬA PHẦN NÀY)
            # Thêm tiền tố .bg-it-white để Playwright không 'vơ' nhầm Expertise rác ở dưới
            expertise = page.locator(".bg-it-white div:has-text('Job Expertise:') + div a").all_text_contents()
            domain = page.locator(".bg-it-white div:has-text('Job Domain:') + div div.itag").all_text_contents()

            # 4. XỬ LÝ REQUIREMENTS (Lấy cả Job description & Your skills and experience)
            req_content = page.evaluate("""() => {
                const sections = Array.from(document.querySelectorAll('.imy-5.paragraph'));
                return sections
                    .filter(s => {
                        const h2 = s.querySelector('h2');
                        return h2 && (h2.innerText.includes('Job description') || h2.innerText.includes('Your skills and experience'));
                    })
                    .map(s => s.innerText)
                    .join('\\n\\n');
            }""")

            # 5. PARSE SALARY (Dữ liệu thô từ JSON-LD)
            salary = "Thỏa thuận"
            val = node.get('baseSalary', {}).get('value', {})
            min_v = val.get('minValue')
            max_v = val.get('maxValue')
            
            # Chỉ ghép chuỗi nếu có ít nhất một giá trị lương cụ thể
            if min_v or max_v:
                salary = f"{min_v if min_v else ''} - {max_v if max_v else ''} {node.get('baseSalary', {}).get('currency', 'USD')}"
            elif "Sign in to view salary" in page.content() or "You'll love it" in page.content():
                # Nhận diện trạng thái ẩn lương trên giao diện
                salary = "Thỏa thuận"
            return {
                "url": url,
                "job_title": node.get('title'),
                "company_name": node.get('hiringOrganization', {}).get('name'),
                "salary_raw": salary,
                "location_raw": full_location,
                "job_domain": [d.strip() for d in domain if d.strip()],
                "job_expertise": [e.strip() for e in expertise if e.strip()],
                "experience_months": node.get('experienceRequirements', {}).get('monthsOfExperience'),
                "requirements_text": req_content.strip() or self.safe_text(page, ".job-description__content"),
                "skills_tags": skills,
                "source": "itviec",
                "posted_date": node.get('datePosted'),
                "crawled_date": datetime.utcnow()
            }
        except Exception as e:
            self.logger.error(f"Lỗi cào chi tiết {url}: {e}")
            return None

    def scrape(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()

            urls = self.scrape_job_urls(page)
            self.logger.info(f"✅ Đã tìm thấy {len(urls)} jobs. Bắt đầu Phase 2...")

            for i, url in enumerate(urls):
                detail_page = context.new_page()
                try:
                    data = self.scrape_job_detail(detail_page, url)
                    if data:
                        self.save_job(data)
                        # Log giờ đây sẽ hiện Expertise chuẩn (1-3 cái) thay vì 80+
                        print(f"[{i+1}/{len(urls)}] ✅ Lưu: {data['job_title']} | Expertise: {len(data['job_expertise'])} | Skills: {len(data['skills_tags'])}")
                finally:
                    detail_page.close()
                time.sleep(random.uniform(1.5, 3.0))
            browser.close()

if __name__ == "__main__":
    ITViecScraper().scrape()