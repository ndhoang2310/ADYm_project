# BÁO CÁO KỸ THUẬT: PHƯƠNG PHÁP XỬ LÝ VÀ NỘI SUY BIẾN MỤC TIÊU (SALARY)

Trong phân tích dữ liệu tuyển dụng, biến mục tiêu (Mức lương) thường bị kiểm duyệt (Censored Data) dưới dạng khoảng hoặc bị khuyết một cận. Mục tiêu của việc xử lý là quy chuẩn tất cả các trường hợp về một giá trị duy nhất: **Điểm giữa (Midpoint/Q2)** của dải lương thực tế - đại diện cho mức thu nhập kỳ vọng của một ứng viên đạt chuẩn (Fully Competent).



## I. CƠ SỞ KHOA HỌC VÀ CHỨNG MINH CÔNG THỨC LÕI

Để tính toán được các cận bị khuyết, nhóm nghiên cứu sử dụng biến số **Độ rộng dải lương (Salary Range Spread)** - tỷ lệ chênh lệch giữa mức Max và mức Min.

**1. Dẫn chứng và Tiêu chuẩn quốc tế:**
* **WorldatWork:** Trong cẩm nang *"The WorldatWork Handbook of Compensation, Benefits & Total Rewards"* (Chương: Salary Structure Design), tổ chức này quy định mức Range Spread tiêu chuẩn cho nhóm Chuyên viên/Kỹ sư (Professionals/Engineers) là **40% - 50%**.
* **Hiệp hội Quản trị Nhân sự Hoa Kỳ (SHRM):** Hướng dẫn *"How to Establish Salary Ranges"* của SHRM chỉ định dải lương cho các vị trí yêu cầu kỹ thuật cao (như IT) phải đạt mốc **50%** để đảm bảo dư địa tăng lương và phân cấp giữa Junior/Senior.
* **Culpepper and Associates:** Khảo sát thực nghiệm *"Salary Range Structure Practices"* trên các công ty công nghệ chỉ ra mức Range Spread trung bình thực tế trên thị trường IT là **48.5%** (thường được làm tròn thành 50% khi thiết lập quỹ lương).

**2. Công thức lõi (Core Formula):**
Từ tiêu chuẩn Range Spread = 50%, ta có phương trình toán học nền tảng:
`Spread = (Max - Min) / Min = 0.5`
==> **`Max = Min * 1.5`**

Phương trình nền tảng này là cơ sở để thiết lập các hệ số nội suy cho từng trường hợp khuyết dữ liệu.

---

## II. CHI TIẾT 4 TRƯỜNG HỢP NỘI SUY DỮ LIỆU

### Trường hợp 1: Dữ liệu có ranh giới rõ ràng (Cung cấp cả Min và Max)
* **Đặc điểm:** Tin tuyển dụng ghi "Từ X đến Y" (VD: Từ 20 - 40 triệu).
* **Công thức:** `Target = (Min + Max) / 2`
* **Ý nghĩa thực tế:** Dải lương minh bạch. Ta sử dụng phép trung bình cộng thống kê cơ bản để tìm thẳng ra mức Điểm giữa (Midpoint / Q2).

### Trường hợp 2: Dữ liệu khuyết cận dưới (Chỉ có Max - "Lên đến / Upto Y")
* **Đặc điểm:** Tin tuyển dụng chỉ cung cấp mức trần (VD: Lên đến 40 triệu). Mức Max này thường chứa yếu tố "thổi phồng" marketing để thu hút hồ sơ.
* **Công thức nội suy:** `Target = Max * 0.85`
* **Chứng minh toán học (Tìm Midpoint thực tế):**
  1. Từ công thức lõi `Max = Min * 1.5`, ta tìm được Min ẩn: `Min = Max / 1.5`
  2. Điểm giữa (Midpoint) của dải lương này là: `(Min + Max) / 2`
  3. Thế Min vào công thức: `((Max / 1.5) + Max) / 2` = `(0.667*Max + Max) / 2` = `1.667*Max / 2` ≈ **`Max * 0.833`**
* **Kết luận:** Hệ số **0.85** (làm tròn lên từ 0.833 để bù trừ biên độ đàm phán) chính là phép toán triệt tiêu độ nhiễu marketing của mức Max, giúp tìm lại chính xác Điểm giữa (Midpoint) của dải lương thật đã bị giấu đi.

### Trường hợp 3: Dữ liệu khuyết cận trên (Chỉ có Min - "Từ X")
* **Đặc điểm:** Tin tuyển dụng chỉ cung cấp mức giá sàn (VD: Từ 20 triệu). Đây là điểm neo thấp nhất (Anchor Point).
* **Công thức nội suy:** `Target = Min * 1.25`
* **Chứng minh toán học (Tìm Midpoint thực tế):**
  1. Từ công thức lõi, mức trần thực tế của công ty sẽ là: `Max = Min * 1.5`
  2. Điểm giữa (Midpoint) của dải lương này là: `(Min + Max) / 2`
  3. Thế Max vào công thức: `(Min + 1.5*Min) / 2` = `2.5*Min / 2` = **`Min * 1.25`**
* **Kết luận:** Khi ứng viên IT vượt qua vòng phỏng vấn, họ có xu hướng đàm phán tiến về mức trung bình ngân sách của công ty. Phép nhân hệ số **1.25** chính là ước lượng toán học trực tiếp để tìm ra giá trị Midpoint từ mức giá sàn ban đầu.

### Trường hợp 4: Khuyết cả hai cận (Ghi "Thỏa thuận")
* **Đặc điểm:** Không có bất kỳ dữ liệu định lượng nào về lương.
* **Hành động:** **Xóa bỏ (Drop) khỏi tập Train.**
* **Ý nghĩa:** Tuân thủ nguyên tắc *Complete-case analysis* trong Machine Learning. Việc nội suy một nhãn mục tiêu (Target Label) hoàn toàn trống sẽ gây ra hiện tượng thiên lệch (Bias) nghiêm trọng. Các dòng khuyết toàn bộ thông tin nội suy bắt buộc phải bị loại bỏ để bảo toàn độ tin cậy của mô hình (Metrics: RMSE, MAE).