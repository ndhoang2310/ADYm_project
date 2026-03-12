# Exploratory Data Analysis (EDA)

## Phân tích dữ liệu mức lương ngành IT tại Việt Nam

---

# 1. Mục tiêu phân tích

Mục tiêu của bước **Exploratory Data Analysis (EDA)** là khám phá và hiểu rõ cấu trúc của bộ dữ liệu tuyển dụng ngành IT tại Việt Nam.

Cụ thể, phân tích này nhằm:

* Khám phá **phân bố mức lương trong ngành IT**
* So sánh **mức lương giữa các thành phố công nghệ lớn**
* Phân tích **mối quan hệ giữa kinh nghiệm và mức lương**
* Phát hiện **các giá trị ngoại lai (outliers)** trong dữ liệu

Thông qua EDA, chúng ta có thể hiểu rõ hơn về **xu hướng lương và thị trường việc làm IT tại Việt Nam**.

---

# 2. Tổng quan về dữ liệu


## Các biến chính trong dataset

Các cột quan trọng bao gồm:

* `job_title` – vị trí công việc
* `company` – công ty tuyển dụng
* `location` – địa điểm làm việc
* `salary_min` – mức lương tối thiểu
* `salary_max` – mức lương tối đa
* `exp_years` – số năm kinh nghiệm yêu cầu

---

## Kiểm tra dữ liệu ban đầu

Một số bước kiểm tra dữ liệu được thực hiện trước khi phân tích:

* `df.info()` để kiểm tra kiểu dữ liệu
* `df.count()` để kiểm tra số lượng giá trị không bị thiếu
* Thống kê mô tả cho các cột lương bằng:
`salary_stats = df[['salary_min','salary_max']].describe()`

Để đảm bảo tính chính xác của phân tích, các dòng có giá trị thiếu ở các cột sau đã được loại bỏ:

**salary_min**

**salary_max**

**exp_years**

Dataset được kiểm tra các bản ghi trùng lặp bằng hàm duplicated().

---

## Kỹ thuật đặc trưng
Vì dataset cung cấp mức lương dưới dạng **khoảng lương**, một biến mới được tạo ra để đại diện cho mức lương trung bình của mỗi tin tuyển dụng:

[
salary = \frac{salary_min + salary_max}{2}
]


# 3. Phân bố mức lương

## Histogram phân bố lương

Histogram được sử dụng để quan sát **phân bố tổng thể của mức lương trong dataset**.

### Insight

* Phần lớn mức lương trong ngành IT tại Việt Nam nằm trong khoảng:

**15 – 40 triệu VND / tháng**

* Phân bố lương có xu hướng **lệch phải (right-skewed)**:

  * nhiều công việc có mức lương trung bình
  * một số ít vị trí có mức lương rất cao


---

# 4. Phân bố công việc theo thành phố

Dataset bao gồm nhiều địa điểm khác nhau.
Để phân tích rõ ràng hơn, dữ liệu được tập trung vào ba trung tâm công nghệ lớn tại Việt Nam:

* **Ho Chi Minh City**
* **Ha Noi**
* **Da Nang**


### Insight

* **Ho Chi Minh City** và **Ha Noi** chiếm phần lớn số lượng tin tuyển dụng.
* **Da Nang** có số lượng tin tuyển dụng ít hơn đáng kể.

Điều này cho thấy phần lớn cơ hội việc làm IT tập trung tại **hai trung tâm kinh tế lớn nhất của Việt Nam**.

---

# 5. So sánh mức lương giữa các thành phố

Một **box plot** được sử dụng để so sánh phân bố lương giữa các thành phố.

Box plot giúp thể hiện:

* **Median salary (mức lương trung vị)**
* **Phạm vi phân bố lương (salary range)**
* **Outliers**

Ngoài ra, trên biểu đồ còn hiển thị **các điểm dữ liệu riêng lẻ (màu hồng)** đại diện cho **từng tin tuyển dụng (job postings)**.


### Insight

* **Ho Chi Minh City** có xu hướng có **median salary cao hơn** so với các thành phố còn lại.
* **Ha Noi** có phân bố lương tương đối tương tự nhưng thấp hơn một chút.
* **Da Nang** có phạm vi lương hẹp hơn.

Tuy nhiên cần lưu ý rằng số lượng tin tuyển dụng tại **Da Nang tương đối ít**, nên kết quả so sánh có thể bị hạn chế.

---

# 6. Mối quan hệ giữa kinh nghiệm và mức lương

Phân tích được thực hiện giữa:

* `exp_years`
* `salary`


### Insight

* Mối quan hệ giữa **kinh nghiệm và lương là dương**
* Tuy nhiên mức tương quan **không quá mạnh**

Điều này cho thấy:

Kinh nghiệm có ảnh hưởng đến mức lương nhưng **không phải là yếu tố duy nhất**.

Các yếu tố khác có thể ảnh hưởng bao gồm:

* kỹ năng chuyên môn
* công nghệ sử dụng
* quy mô công ty
* loại vị trí công việc

---

# 7. Outliers

Outliers trong dữ liệu lương được phát hiện bằng **phương pháp Interquartile Range (IQR)**.

Các giá trị này có thể đại diện cho:

* Senior Engineers
* Technical Leads
* Highly specialized positions

Outliers là yếu tố quan trọng vì chúng có thể **ảnh hưởng đáng kể đến các thống kê trung bình của dữ liệu**.

---

# 8. Kết luận chính

Từ phân tích EDA, có thể rút ra một số kết luận quan trọng:

1️. Phần lớn mức lương ngành IT tại Việt Nam nằm trong khoảng
**15 – 40 triệu VND / tháng**
2️. **Ho Chi Minh City và Ha Noi là hai trung tâm tuyển dụng IT lớn nhất**
3️. **Mức lương có xu hướng tăng theo kinh nghiệm**, nhưng mối quan hệ không quá mạnh
4️. **Ho Chi Minh City có xu hướng có mức lương cao hơn so với các thành phố khác**
5️.  Dataset tồn tại **một số mức lương rất cao**, chủ yếu thuộc về các vị trí senior

---
# 9. Hạn chế của phân tích

Phân tích này vẫn tồn tại một số hạn chế:

- Dữ liệu dựa trên tin tuyển dụng, không phải mức lương thực tế sau khi tuyển dụng.
- Một số thành phố có số lượng dữ liệu nhỏ.
- Dataset chưa bao gồm các yếu tố quan trọng khác như:

**kỹ năng**
**tech stack**
**cấp độ vị trí**
**quy mô công ty**

Trong các bước phân tích tiếp theo, có thể mở rộng nghiên cứu sang:
- phân tích kỹ năng (skill analysis)
- phân tích nhu cầu công nghệ
- dự đoán mức lương

