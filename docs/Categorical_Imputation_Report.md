📊 Data Quality Report: Categorical Features Imputation
Dự án: Vietnam IT Market Analysis & Salary Prediction
Giai đoạn: Data Preprocessing & Cleaning (Xử lý dữ liệu khuyết)
File thực thi: processing/handle_categorical_missing.py
Input Dataset: data/final_dataset.csv (Kích thước: 5661 dòng, 17 cột)
Output Dataset: data/dataset_after_categorical_imputing.csv

1. Đánh giá hiện trạng (Pre-Imputation Status)
Sau bước hợp nhất dữ liệu (Merge Data), tập dữ liệu tổng hợp gồm 5661 bản ghi xuất hiện tình trạng khuyết dữ liệu ở một số feature phân loại (Categorical Features) trọng yếu.

Chi tiết tỷ lệ khuyết trước khi xử lý:

    education_level: 39.85%

    contract_type: 24.62%

    tech_stack: 17.49%

    company_name: 0.83%

2. Chiến lược xử lý (Imputation Strategy)
Để bảo toàn vẹn toàn dữ liệu và tránh việc phải drop (xóa) quá nhiều dòng gây hao hụt kích thước tập mẫu, nhóm áp dụng hai phương pháp chính: Constant Imputation (Điền hằng số) và Mode Imputation (Điền giá trị phổ biến nhất dựa trên Domain Knowledge).

Chi tiết từng Feature:

a. education_level

    Tỷ lệ thiếu: 39.85%

    Phương pháp áp dụng: Constant Imputation

    Giá trị điền: "Unknown"

    Giải thích: Lượng thiếu hụt lớn. Việc điền bừa một cấp bậc (VD: Cử nhân) có thể làm sai lệch phân phối học vấn. Gắn nhãn Unknown là an toàn nhất.

b. contract_type

    Tỷ lệ thiếu: 24.62%

    Phương pháp áp dụng: Mode Imputation

    Giá trị điền: "Full-time"

    Giải thích: Đặc thù của thị trường lao động IT là đa số các vị trí tuyển dụng đều là toàn thời gian. Sử dụng Mode (giá trị xuất hiện nhiều nhất) của tập dữ liệu là hợp lý.

c. tech_stack

    Tỷ lệ thiếu: 17.49%

    Phương pháp áp dụng: Constant Imputation

    Giá trị điền: "Not Specified"

    Giải thích: Phục vụ cho bước NLP sau này. Nếu JD không đề cập kỹ năng, giữ nguyên trạng thái không xác định để không làm nhiễu mô hình gợi ý kỹ năng.

d. company_name

    Tỷ lệ thiếu: 0.83%

    Phương pháp áp dụng: Constant Imputation

    Giá trị điền: "Unknown"

    Giải thích: Tỷ lệ thiếu vô cùng nhỏ, không đáng kể. Điền giá trị mặc định để đảm bảo Pipeline không bị lỗi rỗng (Null pointer).

3. Quá trình thực thi (Implementation)
Đoạn code cốt lõi được triển khai trong file handle_categorical_missing.py:


    # 1. Constant Imputation cho Học vấn, Kỹ năng và Tên công ty
    df['education_level'] = df['education_level'].fillna("Unknown")
    df['tech_stack'] = df['tech_stack'].fillna("Not Specified")
    df['company_name'] = df['company_name'].fillna("Unknown")

    # 2. Mode Imputation cho Loại hợp đồng
    df['contract_type'] = df['contract_type'].fillna("Full-time")

    # Xuất dữ liệu
    df.to_csv("data/dataset_after_categorical_imputing.csv", index=False)
    
4. Kết quả nghiệm thu (Post-Imputation Validation)
Quá trình xử lý chạy thành công, bảo toàn nguyên vẹn kích thước tập dữ liệu gốc (5661 dòng).
Tỷ lệ missing values của 4 feature education_level, contract_type, tech_stack, và company_name hiện tại đã giảm xuống mức 0%.