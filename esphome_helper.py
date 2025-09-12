import os
import glob
import subprocess
import platform
import sys
from datetime import datetime

try:
    # This library is needed to auto-detect COM ports.
    import serial.tools.list_ports
except ImportError:
    print("错误: 'pyserial' 模块未安装。")
    print("它是自动检测 COM 端口所必需的。")
    try:
        install_choice = input("是否现在尝试使用 'pip install pyserial' 来安装它? (y/n): ").lower()
        if install_choice == 'y':
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyserial'], check=True)
            print("\n'pyserial' 安装成功! 请重新运行此脚本。")
        else:
            print("请手动运行 'pip install pyserial' 后再试。")
    except Exception as e:
        print(f"自动安装失败: {e}")
        print("请手动运行 'pip install pyserial' 后再试。")
    exit()


def clear_screen():
    """Clears the console screen."""
    command = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(command)

def get_yaml_files():
    """Gets a list of .yaml files in the current directory, excluding secrets.yaml."""
    all_yaml_files = glob.glob('*.yaml')
    return [f for f in all_yaml_files if f.lower() != 'secrets.yaml']

def select_config_file():
    """Displays a menu to select a .yaml file and returns the selection."""
    clear_screen()
    print("请选择要操作的设备配置文件:\n")
    files = get_yaml_files()
    if not files:
        print("错误: 在当前目录下未找到任何 .yaml 配置文件。")
        return None

    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")

    print("\n  0. 返回主菜单")

    try:
        choice = int(input("\n请输入选项编号: "))
        if 0 < choice <= len(files):
            return files[choice - 1]
        elif choice == 0:
            return None
        else:
            print("无效的选择。")
            return None
    except ValueError:
        print("无效的输入，请输入数字。")
        return None

def select_com_port():
    """Lists available COM ports and lets the user select one."""
    clear_screen()
    print("正在检测可用的 COM 端口...\n")
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("错误: 未检测到任何 COM 端口。")
        print("请确保您的设备已通过 USB 正确连接。")
        return None

    print("请选择要操作的 COM 端口:\n")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")

    print("\n  0. 返回主菜单")

    try:
        choice = int(input("\n请输入选项编号: "))
        if 0 < choice <= len(ports):
            return ports[choice - 1].device
        elif choice == 0:
            return None
        else:
            print("无效的选择。")
            return None
    except ValueError:
        print("无效的输入，请输入数字。")
        return None

def run_command(command, capture_output=False):
    """Runs a command and waits for it to complete."""
    try:
        full_command = [sys.executable, '-m'] + command
        print(f"\n>>> 正在执行命令: {' '.join(full_command)}\n")
        
        if capture_output:
            result = subprocess.run(full_command, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            return result.stdout
        else:
            subprocess.run(full_command, check=True)
            return "SUCCESS"
            
    except subprocess.CalledProcessError as e:
        print(f"\n--- 命令执行失败，返回码: {e.returncode} ---")
        if capture_output and e.stderr:
            print("--- 错误信息 ---")
            print(e.stderr)
        return "ERROR"
    except FileNotFoundError:
        print(f"\n--- 命令未找到: {sys.executable} ---")
        print("错误: 无法找到 Python 解释器。请确保 Python 已正确安装。")
        return "ERROR"
    except Exception as e:
        print(f"\n--- 发生未知错误: {e} ---")
        return "ERROR"


def main_menu():
    """Displays the main menu and handles user choices."""
    while True:
        clear_screen()
        print("==================================================")
        print(" ESPHome 刷机助手 (Python版)")
        print("==================================================")
        print("\n--- ESPHome ---")
        print("  1. 编译、刷机并查看日志 (有线/OTA)")
        print("  2. 仅编译")
        print("  3. 查看设备日志")
        print("  4. 验证配置文件")
        print("\n--- ESPTool (自动检测Flash大小) ---")
        print("  5. 备份固件 (并可选验证)")
        print("  6. 还原固件")
        print("  7. 查看设备 Flash 大小")
        print("\n  0. 退出")

        choice = input("\n请输入操作编号: ")

        if choice in ('1', '2', '3', '4'):
            config_file = select_config_file()
            if not config_file:
                continue
            
            actions = {
                '1': ['esphome', 'run', config_file],
                '2': ['esphome', 'compile', config_file],
                '3': ['esphome', 'logs', config_file],
                '4': ['esphome', 'validate', config_file]
            }
            run_command(actions[choice])

        elif choice == '5': # Backup Firmware
            port = select_com_port()
            if not port:
                continue

            print("\n--- 步骤 1: 正在自动检测 Flash 大小 ---")
            flash_id_output = run_command(['esptool', '--port', port, 'flash_id'], capture_output=True)

            if flash_id_output == "ERROR" or not flash_id_output:
                print("\n无法自动检测 Flash 大小。请检查设备连接并重试。")
                continue

            flash_size_str = None
            for line in flash_id_output.splitlines():
                if "Detected flash size:" in line:
                    flash_size_str = line.split(":")[-1].strip()
                    break
            
            if not flash_size_str:
                print("\n无法从 esptool 输出中解析 Flash 大小。可能是非标准的输出格式。")
                continue

            size_map = {
                "512KB": "0x80000", "1MB": "0x100000", "2MB": "0x200000",
                "4MB": "0x400000", "8MB": "0x800000", "16MB": "0x1000000"
            }
            flash_size_hex = size_map.get(flash_size_str)

            if not flash_size_hex:
                print(f"\n检测到不支持或未知的 Flash 大小: {flash_size_str}")
                continue
                
            print(f"\n--- 步骤 2: 检测到 Flash 大小为 {flash_size_str} ---")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"firmware_backup_{flash_size_str}_{timestamp}.bin"
            print(f"\n--- 步骤 3: 固件将备份到: {backup_file} ---")
            print("备份过程需要一些时间，请耐心等待...")
            
            backup_result = run_command(['esptool', '--port', port, 'read_flash', '0x0', flash_size_hex, backup_file])
            
            if backup_result != "ERROR":
                print(f"\n固件备份成功！文件已保存为: {backup_file}")
                verify_choice = input("\n是否立即校验备份文件的完整性? (y/n): ").lower().strip()
                if verify_choice == 'y':
                    print("\n--- 步骤 4: 正在校验固件 ---")
                    print("校验过程将重新读取一次闪存，请耐心等待...")
                    run_command(['esptool', '--port', port, 'verify_flash', '0x0', backup_file])

        elif choice == '6': # Restore Firmware
            port = select_com_port()
            if not port:
                continue
            firmware_file = input("请输入要还原的固件文件名 (例如 firmware.bin): ").strip()
            if os.path.exists(firmware_file):
                run_command(['esptool', '--port', port, 'write_flash', '0x0', firmware_file])
            else:
                print(f"\n错误: 固件文件 '{firmware_file}' 不存在。")

        elif choice == '7': # Check Flash Size
            port = select_com_port()
            if not port:
                continue
            run_command(['esptool', '--port', port, 'flash_id'])
        
        elif choice == '0':
            print("正在退出...")
            break
        else:
            print("无效的选择，请输入菜单中的编号。")

        print("\n操作完成。按 Enter 键返回主菜单...")
        input()

if __name__ == "__main__":
    main_menu()