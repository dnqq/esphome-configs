# ESPHome 智能家居配置合集

本仓库包含了一系列我个人使用的 ESPHome 配置文件，以及一个为简化 ESPHome 设备刷机和管理流程而编写的 Python 助手脚本。

## 仓库内容

1.  **ESPHome 配置文件 (.yaml)**
    *   `orvibo-ct30w-xxxx.yaml`: 适用于**欧瑞博 (Orvibo) CT30W Wi-Fi 红外遥控器**。
        *   主要用于控制空调，包含开机、关机红外码。
        *   实现特殊的“两步关机”逻辑，用于在关机后触发空调的自动干燥/清洁功能。
        *   巧妙地利用 `GPIO0` 和内部上拉电阻，为设备集成了 `DHT22` 温湿度传感器，无需额外焊接上拉电阻。
    *   `philips-spb9010w-xxxx.yaml`: 适用于**飞利浦 (Philips) SPB9010W 智能排插/插座**的系列配置。

2.  **ESPHome 刷机助手 (`esphome_helper.py`)**
    *   这是一个基于命令行的 Python 脚本，旨在提供一个统一、便捷的界面来操作本仓库中的 ESPHome 设备。

## `esphome_helper.py` 助手脚本功能

- **菜单驱动**: 提供清晰的操作选项，无需手动输入冗长的命令。
- **自动发现**: 自动查找当前目录下的 `.yaml` 配置文件和可用的 COM 端口。
- **ESPHome 集成**:
    -   一键完成 **编译、刷写和查看日志** (`run`)。
    -   单独执行 **编译** (`compile`)、**查看日志** (`logs`) 或 **验证配置** (`validate`)。
- **ESPTool 集成**:
    -   **备份固件**: 自动检测设备的 Flash 大小，并根据大小和时间戳生成备份文件名 (`firmware_backup_4MB_20231027_103000.bin`)。
    -   **校验固件**: 备份后可选择立即校验备份文件的完整性。
    -   **还原固件**: 从指定的 `.bin` 文件恢复设备固件。
    -   **查看 Flash 信息**: 快速获取连接设备的 Flash ID 和大小。

## 使用方法

### 1. 准备环境

-   确保你已经安装了 [ESPHome](https://esphome.io/guides/getting_started_command_line.html)。
-   确保你的电脑上安装了 Python。
-   安装助手脚本所需的依赖库 (主要用于自动检测 COM 端口):
    ```bash
    pip install pyserial
    ```

### 2. 配置凭据

所有 `.yaml` 文件都使用 `secrets.yaml` 来管理敏感信息。请在仓库根目录创建一个 `secrets.yaml` 文件，并填入你的信息，格式如下：

```yaml
# WiFi
wifi_ssid: "你的WiFi名称"
wifi_password: "你的WiFi密码"

# OTA (空中升级)
ota_password: "设置一个OTA密码"
```

### 3. 运行助手脚本

直接运行 Python 脚本即可启动菜单。

```bash
python esphome_helper.py
```

之后，根据屏幕提示选择对应的配置文件和操作即可。

## 文件结构

```
.
├── .gitignore               # Git 忽略文件配置
├── esphome_helper.py        # ESPHome 刷机助手脚本
├── orvibo-ct30w-xxxx.yaml   # 欧瑞博红外遥控器配置
├── philips-spb9010w-xxxx.yaml # 飞利浦智能排插配置
└── README.md                # 本说明文件