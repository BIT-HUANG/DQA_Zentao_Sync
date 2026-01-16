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