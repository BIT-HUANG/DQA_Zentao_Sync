import os
import json

# ========== table data transfer ==========
def transfer_single_zentao_history(history_content):
    history_str = (history_content['id'] + ": "
                    + history_content['date'] + ", "
                    + history_content['actor'] + " "
                   + history_content['action'] + ", Comment: "
                   + history_content['comment'])
    return history_str

def show_latest_zentao_history(history_dict):
    if not history_dict:
        return ""
    latest_history_id = max(history_dict, key=lambda k: int(k))
    latest_history_content = history_dict[latest_history_id]
    history_str = transfer_single_zentao_history(latest_history_content)
    return history_str

def show_all_zentao_history(history_dict):
    history_list = list()
    for history_id, history_content in history_dict.items():
        history_list.append(transfer_single_zentao_history(history_content))
    return history_list

def save_data_to_json(data_list, file_name="table_data_temp.json"):
    """
    通用方法：将列表数据保存为JSON文件到项目根目录
    :param data_list: 要保存的列表数据（表格的原始数据列表）
    :param file_name: 保存的文件名，默认 table_data_temp.json
    :return: 布尔值+描述信息 (成功True/失败False, 提示文本)
    """
    try:
        # 1. 获取项目根目录（适配任意运行路径，精准定位到项目根目录）
        # 从utils目录，向上回退一级，就是项目根目录
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(utils_dir)
        json_file_path = os.path.join(root_dir, file_name)

        # 2. 写入JSON文件，确保中文正常显示+格式化排版
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

        # 3. 成功返回
        return True, f" 数据已保存至项目根目录：{file_name}，共{len(data_list)}条数据"

    except Exception as e:
        # 失败返回异常信息
        return False, f"保存JSON文件失败：{str(e)}"

def get_jira_brief_result(raw_data):
    print(raw_data)
    brief_result = {}

    sw_project_list = [item.get("value", "") for item in raw_data.get("jira_detected_sw_project", []) if
                       item.get("value")]
    jira_detected_sw_project_str = ",".join(sw_project_list) if sw_project_list else "无"

    fix_version_list = [item.get("name", "") for item in raw_data.get("jira_fix_version", []) if item.get("name")]
    jira_fix_version_str = ",".join(fix_version_list) if fix_version_list else "无"

    brief_result['Summary'] = raw_data.get('jira_summary','无')
    brief_result['Status'] = raw_data.get('jira_status', '无')
    brief_result['Defect Rank'] = raw_data.get('jira_rank', '无')
    brief_result['Detected SW Project'] = jira_detected_sw_project_str #列表处理
    brief_result['Assignee'] = raw_data.get('jira_assignee', '无')
    brief_result['Resolution'] = raw_data.get('jira_resolution', '无')
    brief_result['Fix Version'] = jira_fix_version_str #列表处理
    brief_result['Release Version'] = raw_data.get('jira_released_package_version', '无')
    brief_result['Resolved Version'] = raw_data.get('jira_resolved_version', '无')
    brief_result['Defect Info'] = raw_data.get('jira_defect_info', '无')
    return brief_result


class ConfigManager:
    """配置文件管理器：全程 JSON 原生读写，保持 list/dict 等类型不变（对齐项目根目录路径）"""

    def __init__(self, config_file_name=".config"):
        # ========== 核心修改：复用项目根目录路径逻辑 ==========
        # 1. 获取utils目录（当前文件所在目录）
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        # 2. 向上回退一级 → 项目根目录（和table_data_temp.json同目录）
        root_dir = os.path.dirname(utils_dir)
        # 3. 拼接配置文件的绝对路径
        self.config_path = os.path.join(root_dir, config_file_name)

        # 加载配置
        self.config = self._load_config()

    def _load_config(self):
        """加载配置：不存在则创建空 JSON，存在则读取并保持原生类型"""
        if not os.path.exists(self.config_path):
            default_config = {}
            self._save_config(default_config)
            return default_config
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            # 配置损坏，返回空配置并备份原文件
            if os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.bak"
                os.rename(self.config_path, backup_path)
                print(f"配置文件损坏，已备份至：{backup_path}")
            return {}

    def _save_config(self, data):
        """保存配置：直接写 JSON，不转字符串，保持原生结构"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败：{str(e)}")
            raise  # 抛出异常，让上层感知保存失败

    def get(self, key, default=None):
        """读取配置：支持嵌套 key 如 "a.b.c"，返回原生类型"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """设置配置：支持嵌套 key 如 "a.b.c"，value 可以是 list/dict/str/int 等"""
        keys = key.split(".")
        current = self.config
        # 逐层创建字典（如果不存在）
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        # 赋值（保持原生类型）
        current[keys[-1]] = value
        self._save_config(self.config)

    def reload(self):
        """重新加载配置（外部修改后）"""
        self.config = self._load_config()

    def get_config_path(self):
        """获取配置文件的绝对路径（用于调试/日志）"""
        return self.config_path