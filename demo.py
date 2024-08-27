import os
import shutil
import configparser
import subprocess
import sys
import re
import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("Reconstruct Windows 10/11 Enterprise G - V1.2")

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        # Không phải admin, yêu cầu chạy với quyền admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def main_menu():
    clear_screen()
    if not os.path.exists("install.wim"):
        global architecture_info, build_info
        architecture_info = "Chưa có"
        build_info = "Chưa có"
    else:
        architecture_info = run_wimlib_imagex("install.wim", "info", info_type="architecture")
        build_info = run_wimlib_imagex("install.wim", "info", info_type="build")
    print("")
    print(f" \033[92mKiến trúc của WIM:\033[0m \033[91m{architecture_info}\033[0m")
    print(f" \033[92mThông tin build:\033[0m \033[91m{build_info}\033[0m")
    print("")
    print(" +====================================Lựa chọn====================================+")
    print(" |                                                                                |")
    print(" |           1. Tiêu chuẩn                                                        |")
    print(" |           2. Nâng cao (cập nhật)                                               |")
    print(" |           3. Thoát                                                             |")
    print(" |                                                                                |")
    print(" +================================================================================+")

mount_dir = r'libs\mount'
temp_dir = r'libs\temp'
wim_file = "install.wim"
config = configparser.ConfigParser()
config.read('config.ini')

# Các tập tin hoặc tham số mẫu
unattend_file = r'libs\sxs\1.xml'
package_file = r'libs\lp\update.mum'
product_key = "YYVX9-NTFWV-6MDM3-9PT4T-4M68B"
edition = "EnterpriseG"

def is_mounted(mount_dir):
    try:
        dism_command = f"dism /get-mountedwiminfo"
        result = subprocess.run(dism_command, shell=True, capture_output=True, text=True, check=True)
        if mount_dir.lower() in result.stdout.lower():
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi kiểm tra mount: {e}\033[0m")
        return False
    except Exception as e:
        print(f" \033[91mLỗi không xác định: {e}\033[0m")
        return False

def taothumuc():
    clear_screen()
    if is_mounted(mount_dir):
        print("")
        print(f" Thư mục \033[92m{mount_dir}\033[0m đã mount")
        print(f" \033[91mĐang tiến hành unmount...\033[0m")
        print("")
        run_dism_unmount(mount_dir)
        input("Press Enter to continue...")
    # else:
        # print(f"The directory {mount_dir} is not mounted.")
    
    folders = ['libs/mount', 'libs/temp', 'libs/logs', 'libs/lp', 'libs/sxs']
    
    # Sau khi kiểm tra xong, tiến hành xóa và tạo lại các thư mục khác
    for folder in folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)  # Xóa thư mục và nội dung bên trong
                os.mkdir(folder)  # Tạo thư mục nếu chưa tồn tại
            except Exception as e:
                print(f" \033[91mLỗi khi xóa và tạo lại {folder}: {e}\033[0m")
        else:
            try:
                os.mkdir(folder)  # Tạo thư mục nếu chưa tồn tại
            except Exception as e:
                print(f" \033[91mLỗi khi tạo {folder}: {e}\033[0m")

def get_choice():
    print("")
    choice = input(" Vui lòng chọn: ")
    return choice.strip()  # Xóa bỏ các ký tự trắng ở hai đầu nếu có

# Hàm chính của chương trình
def main():
    while True:
        main_menu()
        choice = get_choice()

        if not os.path.isfile(wim_file):
            print(f" Tệp \033[91m{wim_file}\033[0m không tồn tại. Vui lòng kiểm tra lại.")
            input(" Nhấn Enter để tiếp tục...")
            continue

        if choice == '1':
            buoc1()
            buoc3()
            input("Press Enter to continue...")
            break
        elif choice == '2':
            buoc1()
            run_dism_update(mount_dir, temp_dir)
            buoc3()
            input(" Press Enter to continue...")
        elif choice == '3':
            print(" Exiting program...")
            break
        else:
            clear_screen()
            print(" Lỗi lựa chọn. Vui lòng chỉ chọn từ 1 đến 4")

def buoc1():
    clear_screen()
    print(" =============================================================================================")
    print(f" Thông tin bản build: \033[91m{build_info}\033[0m")
    sxs_path = f"libs\\esd\\{'win10' if build_info == '19041' else 'win11'}\\{'x64' if architecture_info == 'x86_64' else 'x86'}"
    language_pack_file = f"Microsoft-Windows-Client-LanguagePack-Package{'-amd64' if architecture_info == 'x86_64' else ''}-en-us.esd"
    
    if not run_wimlib_imagex(f"{sxs_path}\\sxs.wim", "libs\\sxs"):
        return False
    if not run_wimlib_imagex(f"{sxs_path}\\{language_pack_file}", "libs\\lp"):
        return False
    if not run_wimlib_imagex(f"{sxs_path}\\Microsoft-Windows-EditionSpecific-EnterpriseG-Package.esd", "libs\\sxs"):
        return False
    
    print(" =============================================================================================")
    print(f" \033[92minstall.wim\033[0m đang được mount...")
    index = 1
    if not run_dism_mount(wim_file, index, mount_dir):
        return False

    print(" =============================================================================================")
    source_path = r'libs\mount\Windows\System32\en-US\Licenses'
    destination_path = r'libs\temp\Licenses'
    copy_directory(source_path, destination_path)

    # Đổi thư mục Professional thành EnterpriseG
    print(" =============================================================================================")
    base_directory = r'libs\temp\Licenses'
    old_directory_name = 'Professional'
    new_directory_name = 'EnterpriseG'
    rename_directories(base_directory, old_directory_name, new_directory_name)
    
    # Sao chép OEMDefaultAssociations
    print(" =============================================================================================")
    system32_directory = r'libs\mount\Windows\System32'
    filenames = ['OEMDefaultAssociations.xml', 'OEMDefaultAssociations.dll']
    copy_files(system32_directory, filenames, temp_dir)

    # Thực thi scratchdir
    print(" =============================================================================================")
    print(f" Đang \033[92mscratchdir\033[0m...")
    run_dism_scratchdir(mount_dir, temp_dir, "apply-unattend", unattend_file)
    run_dism_scratchdir(mount_dir, temp_dir, "add-package", package_file)
    run_dism_scratchdir(mount_dir, temp_dir, "set-productkey", product_key)
    run_dism_scratchdir(mount_dir, temp_dir, "set-edition", edition)
    run_dism_scratchdir(mount_dir, temp_dir, "get-currentedition")
    
    # Sao chép EnterpriseGEdition
    print(" =============================================================================================")
    file1 = r'libs\mount\Windows\servicing\Editions\EnterpriseGEdition.xml'
    file1_out = r'libs\mount\Windows\EnterpriseG.xml'
    shutil.copy(file1, file1_out)
    print(f" Đã sao chép \033[92mEnterpriseGEdition\033[0m thành \033[92mEnterpriseG\033[0m")

    # Xóa Professional.xml
    print(" =============================================================================================")
    delete_professional = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\Professional.xml"
    try:
        subprocess.run(delete_professional, shell=True, capture_output=True, text=True, check=True)
        print(f" Đã xóa tệp \033[92mlibs/mount/Windows/Professional.xml\033[0m")
    except subprocess.CalledProcessError as e:
        print(f" Error executing command: {e}")

def buoc3():
    # Xóa thư mục Licenses từ mount
    print(" =============================================================================================")
    delete_edgedev = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\SystemApps\Microsoft.MicrosoftEdgeDevToolsClient_8wekyb3d8bbwe"
    delete_edge = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\SystemApps\Microsoft.MicrosoftEdge_8wekyb3d8bbwe"
    delete_xbox = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\SystemApps\Microsoft.XboxGameCallableUI_cw5n1h2txyewy"
    # delete_sechealthui = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\SystemApps\Microsoft.Windows.SecHealthUI_cw5n1h2txyewy"
    # delete_defender_protection = r"bin\PowerRun_x64.exe cli delete libs\mount\Program Files\Windows Defender Advanced Threat Protection"
    # delete_defender = r"bin\PowerRun_x64.exe cli delete libs\mount\Program Files\Windows Defender"
    delete_licenses = r"bin\PowerRun_x64.exe cli delete libs\mount\Windows\System32\en-US\Licenses"
    copy_licenses = r"bin\PowerRun_x64.exe cli copy libs\temp\Licenses libs\mount\Windows\System32\en-US\Licenses"
    copy_oem_xml = r"bin\PowerRun_x64.exe cli copy libs\temp\OEMDefaultAssociations.xml libs\mount\Windows\System32"
    copy_oem_dll = r"bin\PowerRun_x64.exe cli copy libs\temp\OEMDefaultAssociations.dll libs\mount\Windows\System32"
    copy_scripts = r"bin\PowerRun_x64.exe cli copy bin\Scripts libs\mount\Windows\Setup\Scripts"
    try:
        edge_delete = config.get('Settings', 'edge_delete', fallback='0')
        if edge_delete == '1':
            subprocess.run(delete_edgedev, shell=True, capture_output=True, text=True, check=True)
            subprocess.run(delete_edge, shell=True, capture_output=True, text=True, check=True)
            subprocess.run(delete_xbox, shell=True, capture_output=True, text=True, check=True)
        print(f" Đã xóa \033[92mứng dụng mặc định của windows\033[0m")
        subprocess.run(delete_licenses, shell=True, capture_output=True, text=True, check=True)
        print(f" Đã xóa thư mục \033[92mlibs/mount/Windows/System32/en-US/Licenses\033[0m")
        subprocess.run(copy_licenses, shell=True, capture_output=True, text=True, check=True)
        print(f" Sao chép thư mục \033[92mlibs/temp/Licenses\033[0m tới \033[92mlibs/mount/Windows/System32/en-US/Licenses\033[0m")
        subprocess.run(copy_oem_xml, shell=True, capture_output=True, text=True, check=True)
        print(f" Sao chép tệp \033[92mlibs/temp/OEMDefaultAssociations.xml\033[0m tới \033[92mlibs/mount/Windows/System32\033[0m")
        subprocess.run(copy_oem_dll, shell=True, capture_output=True, text=True, check=True)
        print(f" Sao chép tệp \033[92mlibs/temp/OEMDefaultAssociations.dll\033[0m tới \033[92mlibs/mount/Windows/System32\033[0m")
        subprocess.run(copy_scripts, shell=True, capture_output=True, text=True, check=True)
        print(f" Sao chép thư mục \033[92mbin/Scripts\033[0m tới \033[92mlibs/mount/Windows/Setup/Scripts\033[0m")
    except subprocess.CalledProcessError as e:
        print(f" Error executing command: {e}")

    # Xóa danh sách app
    print(" =============================================================================================")
    regedit_add(f'libs\\commands_{"win10" if build_info == "19041" else "win11"}.ini')
    print(" =============================================================================================")
    packages_ini(f'libs\\packages_{"win10" if build_info == "19041" else "win11"}.ini', architecture_info, mount_dir, temp_dir)
    print(" =============================================================================================")
    run_dism_resetbase(mount_dir)
    print(" =============================================================================================")
    run_dism_unmount(mount_dir)
    print(" =============================================================================================")
    run_wimlib_imagex("install.wim", "optimize")
    # print(" =============================================================================================")
    # operation1 = '1 --image-property NAME="" --image-property DESCRIPTION="" --image-property DISPLAYNAME="" --image-property DISPLAYDESCRIPTION=""  --image-property WINDOWS/EDITIONID="" --image-property FLAGS=""'
    # run_wimlib_imagex("install.wim", "info", operation1)
    print(" =============================================================================================")
    # operation2 = '1 --image-property NAME="Windows 10 Enterprise G" --image-property DESCRIPTION="Windows 10 Enterprise G" --image-property DISPLAYNAME="Windows 10 Enterprise G" --image-property DISPLAYDESCRIPTION="Windows 10 Enterprise G"  --image-property WINDOWS/EDITIONID="EnterpriseG" --image-property FLAGS="EnterpriseG"'
    operation2 = f'1 --image-property NAME="Windows {"10" if build_info == "19041" else "11"} Enterprise G" --image-property DESCRIPTION="Windows {"10" if build_info == "19041" else "11"} Enterprise G" --image-property DISPLAYNAME="Windows {"10" if build_info == "19041" else "11"} Enterprise G" --image-property DISPLAYDESCRIPTION="Windows {"10" if build_info == "19041" else "11"} Enterprise G" --image-property WINDOWS/EDITIONID="EnterpriseG" --image-property FLAGS="EnterpriseG"'
    run_wimlib_imagex("install.wim", "info", operation2)
    shutil.rmtree(r'libs\lp')
    shutil.rmtree(r'libs\sxs')
    shutil.rmtree(r'libs\temp')

def packages_ini(ini_filename, architecture_info, mount_dir, temp_dir):
    with open(ini_filename, 'r') as file:
        package_names = [
            line.strip() for line in file 
            if line.strip() and not line.strip().startswith('#')
        ]
    
    if architecture_info == "x86":
        package_names = [pkg.replace("_x64__", "_x86__") for pkg in package_names]
    
    for package_name in package_names:
        run_dism_scratchdir(mount_dir, temp_dir, "remove-provisionedappxpackage", package_name)
        sys.stdout.flush()

def extract_with_progress(filename, current_directory):
    if not os.path.exists(current_directory):
        os.makedirs(current_directory)
    command = f'bin\\7z e "{filename}" "sources/install.wim" -o"{current_directory}" -bso0 -y'
    subprocess.run(command, shell=True)
    print(f" {filename} đã giải nén thành công\n")
    
def run_wimlib_imagex(image_file, operation, operation_params=None, info_type=None):
    try:
        image_filename = os.path.basename(image_file)
        wimlib_executable = "bin\\wimlib-imagex"
        
        if operation == "optimize":
            full_command = f"{wimlib_executable} optimize {image_file}"
        elif operation == "info":
            if operation_params:
                full_command = f"{wimlib_executable} info {image_file} {operation_params}"
            else:
                full_command = f"{wimlib_executable} info {image_file}"
        else:
            full_command = f"{wimlib_executable} apply {image_file} {operation}"
        
        result = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if operation == "optimize":
            print(f" \033[92m{image_filename}\033[0m đã được optimize thành công")
        elif operation == "info":
            if operation_params:
                print(f" \033[92m{image_filename}\033[0m đã được info thành công")
            else:
                output = result.stdout
                if info_type == "architecture":
                    arch_match = re.search(r'Architecture\s*:\s*(.*)', output)
                    return arch_match.group(1).strip() if arch_match else "Không xác định"
                elif info_type == "build":
                    build_match = re.search(r'Build\s*:\s*(.*)', output)
                    return build_match.group(1).strip() if build_match else "Không xác định"
                else:
                    return "Loại thông tin không hợp lệ"
        else:
            print(f" \033[92m{image_filename}\033[0m đã được thực thi thành công")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi thực thi lệnh: {e}\033[0m")
        return False
    except Exception as e:
        print(f" \033[91mCó lỗi xảy ra: {e}\033[0m")
        return False
        
def run_dism_mount(wim_file, index, mount_dir):
    try:
        full_command = f"dism /mount-wim /wimfile:\"{wim_file}\" /index:{index} /mountdir:\"{mount_dir}\""
        subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f" \033[92m{os.path.basename(wim_file)}\033[0m đã được mount thành công")
        return True
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi thực thi lệnh: {e}\033[0m")
        return False
    except Exception as e:
        print(f" \033[91mCó lỗi xảy ra: {e}\033[0m")
        return False


def run_dism_unmount(mount_dir, commit=True):
    try:
        # dism /cleanup-wim
        commit_option = "/commit" if commit else "/discard"
        full_command = f"dism /unmount-wim /mountdir:\"{mount_dir}\" {commit_option}"
        
        # Execute the DISM command
        subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print success message
        print(f" Đã unmount \033[92m{mount_dir}\033[0m thành công và {'lưu thay đổi' if commit else 'không lưu thay đổi'}")
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi thực thi lệnh: {e}\033[0m")
    except Exception as e:
        print(f" \033[91mCó lỗi xảy ra: {e}\033[0m")
        
def run_dism_update(mount_dir, temp_dir):
    lcu_dir = fr"libs\lcu\{'win10' if build_info == '19041' else 'win11'}\{'x64' if architecture_info == 'x86_64' else 'x86'}"
    lcu_txt = r'libs\lcu.txt'
    lcu_files = os.listdir(lcu_dir)
    lcu_txt_exists = os.path.exists(lcu_txt)
    with open(lcu_txt, 'w' if not lcu_txt_exists else 'a') as f:
        if not lcu_txt_exists:
            for file_name in lcu_files:
                f.write(file_name + '\n')
        else:
            f.truncate(0)
            for file_name in lcu_files:
                f.write(file_name + '\n')

    print(" =============================================================================================")
    print(f" \033[93mThêm tệp update\033[0m")
    try:
        with open(lcu_txt, 'r') as f:
            lcu_files = [line.strip() for line in f if line.strip()]
        for file_name in lcu_files:
            full_command = f"dism /image:{mount_dir} /add-package:{os.path.join(lcu_dir, file_name)} /scratchdir:{temp_dir}"
            subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f" \033[92m{file_name}\033[0m đã được thêm thành công")

        return True
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi thực thi lệnh: {e}\033[0m")
        return False
    except Exception as e:
        print(f" \033[91mCó lỗi xảy ra: {e}\033[0m")
        return False

def run_dism_resetbase(mount_dir):
    try:
        full_command = f"dism /image:\"{mount_dir}\" /Cleanup-Image /StartComponentCleanup /ResetBase"
        subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f" \033[92m{mount_dir}\033[0m đã được resetbase thành công")
        return True
    except subprocess.CalledProcessError as e:
        print(f" \033[91mLỗi khi thực thi lệnh: {e}\033[0m")
        return False
    except Exception as e:
        print(f" \033[91mCó lỗi xảy ra: {e}\033[0m")
        return False


def run_dism_scratchdir(mount_dir, temp_dir, action, parameter=None):
    try:
        if action == "apply-unattend":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /apply-unattend:{parameter}"
        elif action == "add-package":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /add-package:{parameter}"
        elif action == "set-productkey":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /set-productkey:{parameter}"
        elif action == "set-edition":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /Set-Edition:{parameter}"
        elif action == "get-currentedition":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /get-currentedition"
        elif action == "remove-provisionedappxpackage":
            command = f"dism /scratchdir:{temp_dir} /image:{mount_dir} /remove-provisionedappxpackage /packagename:{parameter}"
        else:
            raise ValueError("Hành động không được hỗ trợ")

        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

        if action == "remove-provisionedappxpackage":
            print(f" \033[92m{action} {parameter}\033[0m")
        else:
            print(f" \033[92m{action}:{parameter}\033[0m")

    except subprocess.CalledProcessError as e:
        print(f" Lỗi khi thực thi lệnh DISM: {e}")
    except ValueError as ve:
        print(f" Lỗi: {ve}")
    except Exception as e:
        print(f" Có lỗi xảy ra khi thực thi lệnh DISM: {e}")

def copy_directory(source, destination):
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f" Sao chép từ \033[92m{source}\033[0m đến \033[92m{destination}\033[0m thành công")
    except FileExistsError:
        print(f" Thư mục đích '{destination}' đã tồn tại.")
    except Exception as e:
        print(f" Lỗi khi sao chép từ '{source}' đến '{destination}': {e}")

def copy_files(source_dir, filenames, destination_dir):
    for filename in filenames:
        source_path = os.path.join(source_dir, filename)
        destination_path = os.path.join(destination_dir, filename)
        try:
            shutil.copy(source_path, destination_path)
            print(f" Sao chép thành công \033[92m{filename}\033[0m")
        except IOError as e:
            print(f" Lỗi khi sao chép \033[91m{filename}\033[0m: {str(e)}")
  
def rename_directories(base_dir, old_name, new_name):
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name == old_name:
                old_path = os.path.join(root, dir_name)
                new_path = os.path.join(root, new_name)
                try:
                    shutil.move(old_path, new_path)
                    print(f" Đổi tên thư mục \033[92m{old_path}\033[0m thành \033[92m{new_path}\033[0m")
                except Exception as e:
                    print(f" Lỗi khi đổi tên thư mục \033[92m{old_name}\033[0m: {str(e)}")

def regedit_add(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        command = line.strip()
        if command and not command.startswith('#'):
            full_command = f'bin\\PowerRun_x64.exe /SW:0 "Reg.exe" {command}'
            try:
                subprocess.run(full_command, shell=True, check=True)
                print(f"\033[92m {command}\033[0m")
            except subprocess.CalledProcessError:
                print(f"\033[91m {command}\033[0m")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def check_iso():
    try:
        current_directory = os.getcwd()
        pattern = re.compile(r'^19041.*\.iso$', re.IGNORECASE)

        for filename in os.listdir(current_directory):
            if pattern.match(filename):
                print(f" \033[93mTìm thấy:\033[0m \033[92m{filename}\033[0m")
                choice = input(f" \033[93mCó muốn giải nén không?\033[0m (yes/no): ").strip().lower()

                if choice == 'yes' or choice == 'y':
                    extract_with_progress(filename, current_directory)
                elif choice == 'no' or choice == 'n':
                    print(f" {filename} đã bỏ qua\n")
                else:
                    print(" Invalid choice. Skipping...\n")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

def quickedit(enabled=1):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        if enabled:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x40|0x100))
        else:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x00|0x100))



if __name__ == "__main__":
    run_as_admin() 
    quickedit(0)
    taothumuc()
    clear_screen()
    check_iso()
    main()
