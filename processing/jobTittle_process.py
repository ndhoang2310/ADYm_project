import pandas as pd
import re

def standardize_job_title_v3(title):
    if pd.isna(title): return 'Other'
    t = str(title).lower()
    
    if re.search(r'data|ai\b|machine learning|nlp|bi\b|business intelligence|dữ liệu', t): return 'Data & AI'
    if re.search(r'business analyst|ba\b|phân tích|product analyst', t): return 'Business Analyst'
    if re.search(r'project manager|product manager|pm\b|product owner|po\b|scrum master|dự án|project', t): return 'PM/PO'
    if re.search(r'test|qa\b|qc\b|quality|kiểm thử|đảm bảo chất lượng', t): return 'QA/Tester'
    if re.search(r'devops|cloud|system|hệ thống|mạng|network|security|bảo mật|an ninh|infrastructure|redteam|secops', t): return 'System/DevOps/Security'
    if re.search(r'design|thiết kế|đồ họa|đồ hoạ|ui/ux|ui|ux|artist|2d|3d|animator|video|media|compositor|hình ảnh|quảng cáo|sáng tạo|motion', t): return 'Designer'
    if re.search(r'sale|kinh doanh|marketing|comtor|business development|phát triển kinh doanh|tư vấn|khách hàng|account|thu mua|sales|seo\b', t): return 'IT Sales/Marketing'
    if re.search(r'brse|cầu nối|bridge', t): return 'BrSE'
    if re.search(r'lead\b|leader|manager|director|architect|trưởng|giám đốc|cio|cto|head|tổ phó|giải pháp', t): return 'Management/Architect'
    if re.search(r'recruit|nhân sự|tuyển dụng|hr\b|talent|learning & development|human resources', t): return 'HR/Admin'
    
    if re.search(r'frontend|front-end|react|vue|angular', t): return 'Frontend Developer'
    if re.search(r'backend|java\b|python|php|\.net|c#|node|ruby|golang|back-end', t): return 'Backend Developer'
    if re.search(r'mobile|ios|android|flutter|swift|kotlin', t): return 'Mobile Developer'
    if re.search(r'fullstack|full-stack|full stack', t): return 'Fullstack Developer'
    if re.search(r'odoo|sap|erp|crm|salesforce', t): return 'ERP/CRM Developer'
    if re.search(r'embedded|nhúng|iot', t): return 'Embedded Developer'
    
    if re.search(r'helpdesk|support|it staff|nhân viên it|chuyên viên it|công nghệ thông tin|cntt|it officer|it executive|quản trị website|vận hành|kỹ thuật', t): return 'IT Support'
    if re.search(r'developer|engineer|programmer|lập trình|phát triển|phần mềm|software|kỹ sư|coder', t): return 'General Developer'
    
    return 'Other'

def main():
    df = pd.read_csv('data/02_merged_jobs.csv')
    
    df['job_category'] = df['job_title'].apply(standardize_job_title_v3)
    
    other_df = df[df['job_category'] == 'Other']['job_title'].value_counts().reset_index()
    other_df.columns = ['job_title', 'count']
    other_df.to_csv('data/03_unclassified_titles_report.csv', index=False, encoding='utf-8-sig')
    
    df.to_csv('data/03_jobs_with_titles.csv', index=False, encoding='utf-8-sig')
    
    print(f"✅ Đã chuẩn hóa xong. Số lượng rơi vào Other: {other_df['count'].sum()}")
    print("📁 File dữ liệu ML: 03_jobs_with_titles.csv")
    print("📁 File review Other: 03_unclassified_titles_report.csv")

if __name__ == "__main__":
    main()