import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

PATH_RAW = os.path.join(ROOT_DIR, 'data', '00_raw_jobs.csv')
PATH_NLP = os.path.join(CURRENT_DIR, 'artifacts', '01_clean_skills.csv')
PATH_STRUCT = os.path.join(CURRENT_DIR, 'artifacts', '01_clean_salary.csv')
PATH_FINAL = os.path.join(ROOT_DIR, 'data', '02_merged_jobs.csv')

def process_and_merge():
    df_raw = pd.read_csv(PATH_RAW)
    df_nlp = pd.read_csv(PATH_NLP)
    df_struct = pd.read_csv(PATH_STRUCT)

    df_merged = pd.merge(df_nlp, df_struct, on='url', how='inner')

    df_raw_subset = df_raw[['url', 'company_name', 'source', 'education_raw', 'job_description']].drop_duplicates(subset=['url'])
    df_final = pd.merge(df_merged, df_raw_subset, on='url', how='left')

    df_final['company_name_clean'] = df_final['company_name'].str.strip().str.upper()

    df_final['source'] = df_final['source'].str.lower()

    df_final['education_level'] = np.where(df_final['education_raw'].str.contains('Đại học|Bachelor', case=False, na=False), 'Bachelor',
                                  np.where(df_final['education_raw'].str.contains('Cao đẳng|College', case=False, na=False), 'College', 'None'))

    df_final['is_shift_work'] = np.where(df_final['job_description'].str.contains(r'ca xoay|theo ca|làm đêm|shift', case=False, na=False), 1, 0)

    df_final.drop(columns=['education_raw', 'job_description', 'company_name'], inplace=True)
    df_final.rename(columns={'company_name_clean': 'company_name'}, inplace=True)

    df_final = df_final.drop_duplicates(subset=['job_title', 'company_name'], keep='first')

    df_final.to_csv(PATH_FINAL, index=False, encoding='utf-8-sig')
    print(f"✅ Đã gộp, xử lý feature mới và lưu thành công tại: {PATH_FINAL}")

if __name__ == "__main__":
    process_and_merge()