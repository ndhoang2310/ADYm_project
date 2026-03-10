import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    # Tìm vị trí chính xác của file processing/handle_categorical_misssing.py 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lùi ra 1 cấp để đứng ở thư mục gốc 
    project_root = os.path.dirname(current_dir)
    
    # Trỏ thẳng tới file final_dataset.csv trong thư mục data
    input_path = os.path.join(project_root,'data', 'final_dataset_title.csv')
    
    # Tạo tên file output mới để không ghi đè mất file gốc (đề phòng cần rollback)
    output_path = os.path.join(project_root, 'data', 'dataset_after_categorical_imputing.csv')
    
    logging.info(f"Đang nạp bộ dataset tổng: {input_path}")
    
    try:
        df = pd.read_csv(input_path)
        logging.info(f"Kích thước bộ dữ liệu (Shape): {df.shape}")
    except FileNotFoundError:
        logging.error(f"❌ Không tìm thấy file tại '{input_path}'.")
        exit()
        
    # 2. Bắt đầu "lấp lỗ hổng" (Imputation) cho các feature
    logging.info("Đang xử lý Missing Values cho các cột Categorical...")
    
    # Điền "Unknown" cho Học vấn (khuyết ~39.85%)
    if 'education_level' in df.columns:
        df['education_level'] = df['education_level'].fillna("Unknown")
        
    # Điền "Full-time" cho Loại hợp đồng (khuyết ~24.62%) - Mode Imputation
    if 'contract_type' in df.columns:
        df['contract_type'] = df['contract_type'].fillna("Full-time")
        
    # Điền "Not Specified" cho Tech Stack (khuyết ~17.49%)
    if 'tech_stack' in df.columns:
        df['tech_stack'] = df['tech_stack'].fillna("Not Specified")
        
    # Điền "Unknown" cho Tên công ty (khuyết ~0.83%)
    if 'company_name' in df.columns:
        df['company_name'] = df['company_name'].fillna("Unknown")
        
    # 3. Báo cáo nghiệm thu
    cols_to_check = ['education_level', 'contract_type', 'tech_stack', 'company_name']
    existing_cols = [c for c in cols_to_check if c in df.columns]
    
    missing_after = df[existing_cols].isnull().sum()
    logging.info(f"Số ô trống còn lại của các feature vừa xử lý:\n{missing_after}")
    
    # 4. Xuất mẻ dữ liệu mới
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logging.info(f"✅ Hoàn tất! Đã lưu file sạch vào: {output_path}")