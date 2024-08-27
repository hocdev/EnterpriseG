import os
import sys
import shutil
from colorama import Fore, Style, init

init()

def remove_read_only_attribute(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.chmod(file_path, 0o666)
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.chmod(dir_path, 0o777)
    else:
        os.chmod(path, 0o666)

def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Tệp {Fore.GREEN}{file_path}{Style.RESET_ALL} đã được xóa thành công.")
        except Exception as e:
            print(f"Lỗi xảy ra khi xóa tệp {Fore.GREEN}{file_path}{Style.RESET_ALL}: {e}")
    else:
        print(f"Tệp {Fore.GREEN}{file_path}{Style.RESET_ALL} không tồn tại.")

def delete_directory(directory_path):
    if os.path.exists(directory_path):
        try:
            remove_read_only_attribute(directory_path)
            shutil.rmtree(directory_path, ignore_errors=True)
            print(f"Đã xóa thư mục {Fore.GREEN}{directory_path}{Style.RESET_ALL} thành công.")
        except Exception as e:
            print(f"Lỗi xảy ra khi xóa thư mục {Fore.GREEN}{directory_path}{Style.RESET_ALL}: {e}")
    else:
        print(f"Thư mục {Fore.GREEN}{directory_path}{Style.RESET_ALL} không tồn tại.")

def copy_file(src, dst):
    if os.path.exists(src):
        try:
            shutil.copy(src, dst)
            print(f"Tệp {Fore.GREEN}{src}{Style.RESET_ALL} đã được sao chép đến {Fore.GREEN}{dst}{Style.RESET_ALL}.")
        except Exception as e:
            print(f"Lỗi xảy ra khi sao chép tệp {Fore.GREEN}{src}{Style.RESET_ALL} đến {Fore.GREEN}{dst}{Style.RESET_ALL}: {e}")
    else:
        print(f"Tệp nguồn {Fore.GREEN}{src}{Style.RESET_ALL} không tồn tại.")

def copy_directory(src, dst):
    if os.path.exists(src):
        try:
            if not os.path.exists(dst):
                os.makedirs(dst)  # Tạo thư mục đích nếu chưa tồn tại
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"Thư mục {Fore.GREEN}{src}{Style.RESET_ALL} đã được sao chép đến {Fore.GREEN}{dst}{Style.RESET_ALL}.")
        except Exception as e:
            print(f"Lỗi xảy ra khi sao chép thư mục {Fore.GREEN}{src}{Style.RESET_ALL} đến {Fore.GREEN}{dst}{Style.RESET_ALL}: {e}")
    else:
        print(f"Thư mục nguồn {Fore.GREEN}{src}{Style.RESET_ALL} không tồn tại.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: demo.exe <operation> <source_path> <destination_path>")
        print("Operations: delete, copy")
        sys.exit(1)

    operation = sys.argv[1].lower()
    src_path = sys.argv[2]
    if len(sys.argv) == 4:
        dst_path = sys.argv[3]
    else:
        dst_path = None

    if operation == "delete":
        if os.path.isfile(src_path):
            delete_file(src_path)
        elif os.path.isdir(src_path):
            delete_directory(src_path)
        else:
            print(f"{Fore.RED}Đường dẫn {src_path} không hợp lệ.{Style.RESET_ALL}")
    elif operation == "copy":
        if dst_path is None:
            print(f"{Fore.RED}Cần cung cấp đường dẫn đích cho lệnh sao chép.{Style.RESET_ALL}")
            sys.exit(1)
        if os.path.isfile(src_path):
            copy_file(src_path, dst_path)
        elif os.path.isdir(src_path):
            copy_directory(src_path, dst_path)
        else:
            print(f"{Fore.RED}Đường dẫn nguồn {src_path} không hợp lệ.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Hoạt động không hợp lệ. Sử dụng 'delete' hoặc 'copy'.{Style.RESET_ALL}")
