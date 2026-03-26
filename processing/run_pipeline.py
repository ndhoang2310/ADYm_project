import sys
import subprocess
import argparse
import time
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

def print_banner(text):
    print("\n" + "="*70)
    print(f"🚀 {text}")
    print("="*70 + "\n")

def run_script(script_name):
    script_path = os.path.join(CURRENT_DIR, script_name)
    print(f"▶️ Bắt đầu chạy: {script_name}...")
    start_time = time.time()
    
    result = subprocess.run([sys.executable, script_path], cwd=PROJECT_ROOT)
    
    elapsed = time.time() - start_time
    if result.returncode == 0:
        print(f"✅ Hoàn thành: {script_name} (Thời gian: {elapsed:.2f}s)\n")
    else:
        print(f"❌ LỖI KHI CHẠY: {script_name}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="Chạy Pipeline Xử lý Dữ liệu ADYm")
    parser.add_argument("--skip-fetch", action="store_true", help="Bỏ qua bước tải dữ liệu từ MongoDB (fetch_data.py)")
    args = parser.parse_args()

    print_banner("BẮT ĐẦU PIPELINE XỬ LÝ DỮ LIỆU ADYm")

    pipeline_steps = [
        ("fetch_data.py", not args.skip_fetch),
        ("clean_salary.py", True),
        ("clean_skills.py", True),
        ("merge.py", True),
        ("jobTittle_process.py", True),
        ("handle_categorical_misssing.py", True),
        ("salary_calculate.py", True),
    ]

    for script_name, should_run in pipeline_steps:
        if should_run:
            run_script(script_name)
        else:
            print(f"⏭️ Bỏ qua: {script_name}\n")

    print_banner("PIPELINE HOÀN TẤT THÀNH CÔNG 🎉")
    final_output = os.path.join(PROJECT_ROOT, 'data', '05_final_dataset.csv')
    print(f"Dữ liệu ML cuối cùng đã sẵn sàng tại:\n👉 {final_output}\n")

if __name__ == "__main__":
    main()
