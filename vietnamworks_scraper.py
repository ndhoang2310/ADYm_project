import logging
import time
import random
from datetime import datetime
from base_scraper_new import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class VietnamWorksScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="vietnamworks")
        
    def setup_driver(self):
        options = Options()
        # Bỏ comment lệnh dưới nếu muốn chạy ẩn
        options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        return webdriver.Chrome(options=options)

    def get_job_links_on_page(self, driver, page_url):
        #Lấy tất cả link việc làm trên 1 trang danh sách
        driver.get(page_url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            
            elements = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            links = []
            for elem in elements:
                href = elem.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = "https://www.vietnamworks.com" + href
                    links.append(href)
            return list(set(links))
        except Exception as e:
            self.logger.error(f"⚠️ Lỗi lấy link ở trang danh sách: {e}")
            return []

    def get_text_by_label(self, driver, label_text):
        #Hàm hỗ trợ: Tìm giá trị (thẻ p) dựa trên nhãn (thẻ label)
        try:
            # XPath tìm label chứa text -> lấy thẻ p ngay sau nó
            xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::p"
            element = driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except:
            return None

    def parse_job_detail(self, driver, url):
        """Vào trang chi tiết để lấy toàn bộ thông tin theo Schema chung"""
        driver.get(url)
        time.sleep(random.uniform(1.5, 3)) 
        
        # --- TÌM VÀ CLICK NÚT "XEM THÊM" ---
        try:
            # Tìm nút có chữ "Xem thêm" và click để hiện full thông tin
            see_more_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Xem thêm')]")
            driver.execute_script("arguments[0].click();", see_more_btn)
            time.sleep(1) # Đợi 1 giây để nội dung hiển thị.
        except:
            pass # Nếu không có nút này thì bỏ qua

        # Khởi tạo dictionary theo đúng format của nhóm
        job_data = {
            "source": "vietnamworks",
            "url": url,
            "crawled_date": datetime.now(),
            "skills_tags": []
        }

        try:
            # 1. job_title
            try:
                job_data['job_title'] = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                job_data['job_title'] = "Unknown Title"

            # 2. company_name
            try:
                comp_elem = driver.find_element(By.XPATH, "//a[contains(@href, '/nha-tuyen-dung/')]")
                job_data['company_name'] = comp_elem.text.strip()
            except:
                job_data['company_name'] = "Unknown Company"

            # 3. salary_raw
            try:
                salary_elem = driver.find_element(By.XPATH, "//span[contains(@class, 'cVbwLK')]")
                job_data['salary_raw'] = salary_elem.text.strip()
            except:
                try:
                    job_data['salary_raw'] = driver.find_element(By.XPATH, "//*[contains(text(), 'Thương lượng')]").text
                except:
                    job_data['salary_raw'] = None

            # 4. location_raw
            try:
                locations = [
                    "An Giang", "Bắc Ninh", "Cà Mau", "Cao Bằng", "Điện Biên", "Đắk Lắk", 
                    "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Tĩnh", "Hưng Yên", "Khánh Hòa", 
                    "Lai Châu", "Lạng Sơn", "Lào Cai", "Lâm Đồng", "Nghệ An", "Ninh Bình", 
                    "Phú Thọ", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sơn La", "Tây Ninh", 
                    "Thái Nguyên", "Thanh Hóa", "Cần Thơ", "Đà Nẵng", "Hà Nội", 
                    "Hải Phòng", "Hồ Chí Minh", "Huế", "Tuyên Quang", "Vĩnh Long"
                ]
                #Tạo chuỗi điều kiện OR cho các thành phố
                city_conditions = " or ".join([f"contains(text(), '{city}')" for city in locations])
                full_xpath = f"//*[contains(@class, 'ePOHWr') and ({city_conditions})]"
                location_elem = driver.find_element(By.XPATH, full_xpath)
                job_data['location_raw'] = location_elem.text.strip()
            except:
                job_data['location_raw'] = None

            # 5. posted_date
            job_data['posted_date'] = self.get_text_by_label(driver, "NGÀY ĐĂNG")
            
            # 6. job_level
            job_data['job_level'] = self.get_text_by_label(driver, "CẤP BẬC")
            
            # 7. experience_raw 
            # Tìm theo "KINH NGHIỆM" hoặc "SỐ NĂM KINH NGHIỆM"
            exp = self.get_text_by_label(driver, "KINH NGHIỆM")
            if not exp:
                exp = self.get_text_by_label(driver, "SỐ NĂM") # Fallback cho "SỐ NĂM KINH NGHIỆM TỐI THIỂU"
            job_data['experience_raw'] = exp

            # 8. education_raw (Trình độ học vấn)
            # Map từ "TRÌNH ĐỘ HỌC VẤN" hoặc "TRÌNH ĐỘ HỌC VẤN TỐI THIỂU"
            job_data['education_raw'] = self.get_text_by_label(driver, "HỌC VẤN") 

            # 9. contract_type (Loại hợp đồng) 
            # Lấy từ "LOẠI HÌNH LÀM VIỆC" (Toàn thời gian/Bán thời gian)
            job_data['contract_type'] = self.get_text_by_label(driver, "LOẠI HÌNH LÀM VIỆC")

            # 10. work_type (Làm tại công ty / Remote)
            #Vietnamworks ít ghi rõ, tạm để NULL
            job_data['work_type'] = None

            # 11. english_req 
            #Cũng ít khi ghi rõ, tạm NULL
            job_data['english_req'] = None

            # 12. skills_tags
            skills_str = self.get_text_by_label(driver, "KỸ NĂNG")
            if skills_str:
                job_data['skills_tags'] = [s.strip() for s in skills_str.split(',') if s.strip()]

            # 13. requirements_text (Mô tả công việc)
            try:
                req_elem = driver.find_element(By.XPATH, "//h2[contains(text(), 'Mô tả công việc')]/following-sibling::div")
                job_data['requirements_text'] = req_elem.text.strip()
            except:
                job_data['requirements_text'] = ""

            self.logger.info(f"✅ Đã cào: {job_data['job_title']}")
            return job_data

        except Exception as e:
            self.logger.error(f"❌ Lỗi khi parse trang chi tiết {url}: {e}")
            return None

    def scrape(self):
        self.logger.info("🚀 Bắt đầu cào VietnamWorks")
        driver = self.setup_driver()
        
        base_url = "https://www.vietnamworks.com/viec-lam?g=5&j=35.28.27.31.29.36.34.30.26.32.38"
        total_pages = 5 
        
        try:
            for page in range(1, total_pages + 1):
                current_url = f"{base_url}&page={page}"
                self.logger.info(f"📄 Đang quét trang danh sách số {page}...")
                
                job_links = self.get_job_links_on_page(driver, current_url)
                self.logger.info(f"   -> Tìm thấy {len(job_links)} việc làm.")
                
                for link in job_links:
                    # Kiểm tra xem URL này đã có trong database chưa
                    if self.collection.count_documents({'url': link}, limit=1) > 0:
                        self.logger.info(f"⏩ Đã tồn tại, bỏ qua: {link}")
                        continue # Nhảy sang job tiếp theo ngay, không vào parse nữa

                    try:
                        job_detail = self.parse_job_detail(driver, link)
                        if job_detail:
                            self.save_job(job_detail)
                    except Exception as e:
                        self.logger.error(f"Skipping job: {e}")
        
        except Exception as global_e:
            self.logger.error(f"Global Error: {global_e}")

        finally:
            driver.quit()
            self.logger.info("🎉 Hoàn thành.")

if __name__ == "__main__":
    bot = VietnamWorksScraper()
    bot.scrape()