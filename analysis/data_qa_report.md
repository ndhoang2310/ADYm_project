
# Báo Cáo Đánh Giá Chất Lượng Dữ Liệu (Data Quality Assessment)

## 1. Phân Tích Giá Trị Thiếu (Missing Values Analysis)

| Cột dữ liệu     | Tỷ lệ thiếu | Đánh giá             | Đề xuất xử lý                                               |
| --------------- | ----------- | -------------------- | ----------------------------------------------------------- |
| salary_range    | 63.01%      | Thiếu rất nhiều      | Có thể tạo lại từ `salary_min` và `salary_max` hoặc loại bỏ |
| salary_min      | 62.20%      | Thiếu rất nhiều      | Cần xem xét phương pháp điền giá trị (imputation)           |
| salary_max      | 58.43%      | Thiếu rất nhiều      | Cần xem xét phương pháp điền giá trị (imputation)           |
| education_level | 39.85%      | Thiếu nhiều          | Có thể điền `"Unknown"`                                     |
| contract_type   | 24.62%      | Thiếu mức trung bình | Có thể điền theo dạng category                              |
| tech_stack      | 17.49%      | Thiếu mức trung bình | Có thể điền `"Not Specified"`                               |
| company_name    | 0.83%       | Thiếu rất ít         | Chấp nhận được                                              |
| url             | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| is_manager      | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| work_method     | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| job_title       | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| language_req    | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| exp_years       | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| source          | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| job_level       | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| location        | 0%          | Không thiếu          | Dữ liệu sạch                                                |
| is_shift_work   | 0%          | Không thiếu          | Dữ liệu sạch                                                |

### Nhận xét chính

* Các cột liên quan đến **salary có tỷ lệ thiếu rất cao (>50%)**.
* Hầu hết các cột mô tả công việc (**job metadata**) đều đầy đủ.
* `salary_range` có thể **bị dư thừa** nếu đã có `salary_min` và `salary_max`.

---

# 2. Phát Hiện Giá Trị Ngoại Lai (Outlier Detection)

Các outlier được phát hiện bằng **phương pháp IQR (Interquartile Range)**.

### Công thức

IQR = Q3 − Q1

Lower Bound = Q1 − 1.5 × IQR

Upper Bound = Q3 + 1.5 × IQR

---

## Tóm tắt Outlier của Salary

| Cột dữ liệu | Lower Bound | Upper Bound | Số lượng Outlier |
| ----------- | ----------- | ----------- | ---------------- |
| salary_min  | -12.5       | 47.5        | 101              |
| salary_max  | -22.5       | 77.5        | 75               |

### Diễn giải

* Giá trị **lower bound âm** xuất hiện do cách tính thống kê của IQR, nhưng **mức lương thực tế không thể âm**.
* Một số tin tuyển dụng có thể chứa **mức lương quá cao hoặc bất thường**.
* Các giá trị này cần **được kiểm tra lại trước khi dùng cho phân tích hoặc mô hình hóa**.

---

# 3. Các Vấn Đề Chất Lượng Dữ Liệu

| Vấn đề                     | Ảnh hưởng                   | Hướng xử lý                        |
| -------------------------- | --------------------------- | ---------------------------------- |
| Thiếu nhiều dữ liệu salary | Khó phân tích mức lương     | Điền giá trị hoặc lọc bớt dữ liệu  |
| Outliers trong salary      | Làm lệch thống kê lương     | Kiểm tra hoặc cắt ngưỡng (capping) |
| Thiếu education_level      | Ảnh hưởng phân tích kỹ năng | Điền `"Unknown"`                   |

