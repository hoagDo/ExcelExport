# main.py
"""
CÔNG CỤ TRÍCH XUẤT CÂU HỎI TỪ VĂN BẢN SANG EXCEL
Phiên bản: 1.0.0
Tác giả: AI Assistant
Ngày: 2024
"""

import sys
import os
import io # <--- Thêm thư viện này

# --- FIX LỖI FONT TIẾNG VIỆT TRÊN WINDOWS CONSOLE ---
# Ép buộc stdout và stderr sử dụng UTF-8
if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# ----------------------------------------------------

from gui import main as gui_main

def check_dependencies():
    """Kiểm tra và cài đặt dependencies"""
    required = ['openpyxl', 'pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("Thiếu các thư viện cần thiết:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nCài đặt bằng lệnh: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Hàm chính"""
    print("=" * 60)
    print("CÔNG CỤ TRÍCH XUẤT CÂU HỎI TỪ VĂN BẢN SANG EXCEL")
    print("Phiên bản: 1.0.0")
    print("=" * 60)
    
    # Kiểm tra dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Tạo thư mục logs nếu chưa tồn tại
    os.makedirs('logs', exist_ok=True)
    
    # Chạy ứng dụng GUI
    try:
        gui_main()
    except Exception as e:
        print(f"Lỗi khởi chạy ứng dụng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()