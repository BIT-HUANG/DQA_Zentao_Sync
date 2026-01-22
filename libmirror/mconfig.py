__API_VERSION = 1

from mlogger import LOGGER
import json
import os
import logging
from mio import get_json_from_file


print("1. 运行工作目录(CWD):", os.getcwd())  # 相对路径的基准
print("2. 代码文件所在目录:", os.path.dirname(os.path.abspath(__file__)))  # 代码文件位置
print("3. .config实际解析路径:", os.path.abspath(".config"))  # 相对路径最终指向的位置
CONFIG_FILE_PATH = os.path.abspath(".config")

DEFAULT_CONFIG = {
    # 基础字符串配置
    "ngrok_auth_token": "",
    "sony_jira_token": "",
    "zt_url": "",
    "zt_http_basic": "",
    "zt_username": "",
    "zt_password": "",
    "db_manager": "",
    "host_zt": "",
    "issue_list_jql": "",
    "issue_list_jql_test": "",
    "issue_list_file_path": "",
    "host_sony": "",

    # 布尔类型配置
    "trans_artifacts": False,
    "trans_descriptions": False,

    # 列表类型配置
    "issue_field": [],

    # 复杂列表字典类型（核心配置）
    "create_zentao_map": [],
    "jira_project_name_list": []
}


def load_all_config():
    """
    通用方法：读取配置文件中的所有配置（一次性加载全部）
    返回：完整的配置字典（缺失字段会用默认值填充）
    """
    try:
        if not os.path.exists(CONFIG_FILE_PATH):
            logging.warning(f"配置文件不存在，使用默认配置：{CONFIG_FILE_PATH}")
            return DEFAULT_CONFIG.copy()

        # 每次读取都重新打开文件，确保获取最新内容
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            user_config = json.load(f)

        # 合并用户配置和默认配置（确保缺失字段有默认值）
        full_config = DEFAULT_CONFIG.copy()
        full_config.update(user_config)
        return full_config

    except Exception as e:
        logging.error(f"读取配置文件失败：{str(e)}")
        return DEFAULT_CONFIG.copy()


# 保留原有单个配置读取方法（兼容旧代码）
def get_create_zentao_map():
    """读取禅道模块配置（兼容旧逻辑）"""
    all_config = load_all_config()
    return all_config.get("create_zentao_map", [])


def get_jira_project_list():
    """读取Jira项目配置（兼容旧逻辑）"""
    all_config = load_all_config()
    return all_config.get("jira_project_list", [])


# 新增：获取任意配置项的通用方法
def get_config_item(key, default=None):
    """获取单个配置项（通用）"""
    all_config = load_all_config()
    return all_config.get(key, default)


try:
    __CONFIG_JSON = get_json_from_file(".config")
except Exception as e:
    LOGGER.error(f"读取配置文件失败: {e}")

__CONFIG_KEY_ISSUE_LIST_FILE_PATH = "issue_list_file_path"
__CONFIG_VALUE_ISSUE_LIST_FILE_PATH = None

def get_issue_list_file_path() -> str:
    global __CONFIG_VALUE_ISSUE_LIST_FILE_PATH
    if __CONFIG_VALUE_ISSUE_LIST_FILE_PATH == None:
        if __CONFIG_KEY_ISSUE_LIST_FILE_PATH not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ISSUE_LIST_FILE_PATH}"到.config\n')
        __CONFIG_VALUE_ISSUE_LIST_FILE_PATH = __CONFIG_JSON[__CONFIG_KEY_ISSUE_LIST_FILE_PATH]
    return __CONFIG_VALUE_ISSUE_LIST_FILE_PATH
    
__CONFIG_KEY_SONY_JIRA_TOKEN = "sony_jira_token"
__CONFIG_VALUE_SONY_JIRA_TOKEN = None

def get_sony_jira_token() -> str:
    global __CONFIG_VALUE_SONY_JIRA_TOKEN
    if __CONFIG_VALUE_SONY_JIRA_TOKEN == None:
        if __CONFIG_KEY_SONY_JIRA_TOKEN not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_SONY_JIRA_TOKEN}"到.config\n')
        __CONFIG_VALUE_SONY_JIRA_TOKEN = __CONFIG_JSON[__CONFIG_KEY_SONY_JIRA_TOKEN]
    return __CONFIG_VALUE_SONY_JIRA_TOKEN


__CONFIG_KEY_ZT_URL = "zt_url"
__CONFIG_VALUE_ZT_URL = None

def get_zt_url() -> str:
    global __CONFIG_VALUE_ZT_URL
    if __CONFIG_VALUE_ZT_URL == None:
        if __CONFIG_KEY_ZT_URL not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ZT_URL}"到.config\n')
        __CONFIG_VALUE_ZT_URL = __CONFIG_JSON[__CONFIG_KEY_ZT_URL]
    return __CONFIG_VALUE_ZT_URL


__CONFIG_KEY_ZT_HTTP_BASIC = "zt_http_basic"
__CONFIG_VALUE_ZT_HTTP_BASIC = None

def get_zt_http_basic() -> str:
    global __CONFIG_VALUE_ZT_HTTP_BASIC
    if __CONFIG_VALUE_ZT_HTTP_BASIC == None:
        if __CONFIG_KEY_ZT_HTTP_BASIC not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ZT_HTTP_BASIC}"到.config\n')
        __CONFIG_VALUE_ZT_HTTP_BASIC = __CONFIG_JSON[__CONFIG_KEY_ZT_HTTP_BASIC]
    return __CONFIG_VALUE_ZT_HTTP_BASIC


__CONFIG_KEY_ZT_USERNAME = "zt_username"
__CONFIG_VALUE_ZT_USERNAME = None

def get_zt_username() -> str:
    global __CONFIG_VALUE_ZT_USERNAME
    if __CONFIG_VALUE_ZT_USERNAME == None:
        if __CONFIG_KEY_ZT_USERNAME not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ZT_USERNAME}"到.config\n')
        __CONFIG_VALUE_ZT_USERNAME = __CONFIG_JSON[__CONFIG_KEY_ZT_USERNAME]
    return __CONFIG_VALUE_ZT_USERNAME


__CONFIG_KEY_ZT_PASSWORD = "zt_password"
__CONFIG_VALUE_ZT_PASSWORD = None

def get_zt_password() -> str:
    global __CONFIG_VALUE_ZT_PASSWORD
    if __CONFIG_VALUE_ZT_PASSWORD == None:
        if __CONFIG_KEY_ZT_PASSWORD not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ZT_PASSWORD}"到.config\n')
        __CONFIG_VALUE_ZT_PASSWORD = __CONFIG_JSON[__CONFIG_KEY_ZT_PASSWORD]
    return __CONFIG_VALUE_ZT_PASSWORD


__CONFIG_KEY_ZT_URL = "host_zt"
__CONFIG_VALUE_ZT_URL = None


def get_host_zt() -> str:
    global __CONFIG_VALUE_ZT_URL
    if __CONFIG_VALUE_ZT_URL == None:
        if __CONFIG_KEY_ZT_URL not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ZT_URL}"到.config\n')
        __CONFIG_VALUE_ZT_URL = __CONFIG_JSON[__CONFIG_KEY_ZT_URL]
    return __CONFIG_VALUE_ZT_URL


__CONFIG_KEY_DB_MANAGER = "db_manager"
__CONFIG_VALUE_DB_MANAGER = None


def get_db_manager() -> str:
    global __CONFIG_VALUE_DB_MANAGER
    if __CONFIG_VALUE_DB_MANAGER == None:
        if __CONFIG_KEY_DB_MANAGER not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_DB_MANAGER}"到.config\n')
        __CONFIG_VALUE_DB_MANAGER = __CONFIG_JSON[__CONFIG_KEY_DB_MANAGER]
    return __CONFIG_VALUE_DB_MANAGER


__CONFIG_KEY_TO_ZT_BUG_SECTION_PARENT = "to_zt_bug_section"
__CONFIG_KEY_TO_ZT_BUG_SECTION_PICKED = "picked"
__CONFIG_VALUE_TO_BUG_SECTION = None


def get_to_zt_bug_section() -> str:
    global __CONFIG_VALUE_TO_BUG_SECTION
    #if __CONFIG_VALUE_TO_BUG_SECTION == None:
    #    if __CONFIG_KEY_TO_ZT_BUG_SECTION_PARENT not in __CONFIG_JSON:
    #        LOGGER.error(
    #            f'请补充配置"{__CONFIG_KEY_TO_ZT_BUG_SECTION_PARENT}"到.config'
    #        )
    #    if (
    #        __CONFIG_KEY_TO_ZT_BUG_SECTION_PICKED
    #        not in __CONFIG_JSON[__CONFIG_KEY_TO_ZT_BUG_SECTION_PARENT]
    #    ):
    #        LOGGER.error(
    #            f'请补充配置"{__CONFIG_KEY_TO_ZT_BUG_SECTION_PICKED}"到.config'
    #        )
    #    __CONFIG_VALUE_TO_BUG_SECTION = __CONFIG_JSON[
    #        __CONFIG_KEY_TO_ZT_BUG_SECTION_PARENT
    #    ][__CONFIG_KEY_TO_ZT_BUG_SECTION_PICKED]
    return __CONFIG_VALUE_TO_BUG_SECTION


__CONFIG_KEY_TRANS_ARTIFACTS = "trans_artifacts"
__CONFIG_VALUE_TRANS_ARTIFACTS = None


def get_trans_artifacts() -> bool:
    global __CONFIG_VALUE_TRANS_ARTIFACTS
    if __CONFIG_VALUE_TRANS_ARTIFACTS == None:
        if __CONFIG_KEY_TRANS_ARTIFACTS not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_TRANS_ARTIFACTS}"到.config')
        __CONFIG_VALUE_TRANS_ARTIFACTS = __CONFIG_JSON[__CONFIG_KEY_TRANS_ARTIFACTS]
    return __CONFIG_VALUE_TRANS_ARTIFACTS


__CONFIG_KEY_TRANS_DESCRIPTIONS = "trans_descriptions"
__CONFIG_VALUE_TRANS_DESCRIPTIONS = None


def get_trans_descriptions() -> bool:
    global __CONFIG_VALUE_TRANS_DESCRIPTIONS
    if __CONFIG_VALUE_TRANS_DESCRIPTIONS == None:
        if __CONFIG_KEY_TRANS_DESCRIPTIONS not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_TRANS_DESCRIPTIONS}"到.config\n')
        __CONFIG_VALUE_TRANS_DESCRIPTIONS = __CONFIG_JSON[
            __CONFIG_KEY_TRANS_DESCRIPTIONS
        ]
    return __CONFIG_VALUE_TRANS_DESCRIPTIONS


__CONFIG_KEY_HOST_SONY = "host_sony"
__CONFIG_VALUE_HOST_SONY = None


def get_host_sony() -> bool:
    global __CONFIG_VALUE_HOST_SONY
    if __CONFIG_VALUE_HOST_SONY == None:
        if __CONFIG_KEY_HOST_SONY not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_HOST_SONY}"到.config\n')
        __CONFIG_VALUE_HOST_SONY = __CONFIG_JSON[__CONFIG_KEY_HOST_SONY]
    return __CONFIG_VALUE_HOST_SONY


__CONFIG_KEY_HOST_CSC = "host_csc"
__CONFIG_VALUE_HOST_CSC = None


__CONFIG_KEY_HOST_TAPD = "host_tapd"
__CONFIG_VALUE_HOST_TAPD = None


def get_host_tapd() -> bool:
    global __CONFIG_VALUE_HOST_TAPD
    if __CONFIG_VALUE_HOST_TAPD == None:
        if __CONFIG_KEY_HOST_TAPD not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_HOST_TAPD}"到.config\n')
        __CONFIG_VALUE_HOST_TAPD = __CONFIG_JSON[__CONFIG_KEY_HOST_TAPD]
    return __CONFIG_VALUE_HOST_TAPD


__CONFIG_KEY_GERRIT_SUBMIT_REPO = "gerrit_submit_repo"
__CONFIG_VALUE_GERRIT_SUBMIT_REPO = None


def get_gerrit_submit_repo() -> bool:
    global __CONFIG_VALUE_GERRIT_SUBMIT_REPO
    if __CONFIG_VALUE_GERRIT_SUBMIT_REPO == None:
        if __CONFIG_KEY_GERRIT_SUBMIT_REPO not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_GERRIT_SUBMIT_REPO}"到.config\n')
        __CONFIG_VALUE_GERRIT_SUBMIT_REPO = __CONFIG_JSON[
            __CONFIG_KEY_GERRIT_SUBMIT_REPO
        ]
    return __CONFIG_VALUE_GERRIT_SUBMIT_REPO


__CONFIG_KEY_GERRIT_SUBMIT_REPO_T6Y = "gerrit_submit_repo_t6y"
__CONFIG_VALUE_GERRIT_SUBMIT_REPO_T6Y = None


def get_gerrit_submit_repo_t6y() -> bool:
    global __CONFIG_VALUE_GERRIT_SUBMIT_REPO_T6Y
    if __CONFIG_VALUE_GERRIT_SUBMIT_REPO_T6Y == None:
        if __CONFIG_KEY_GERRIT_SUBMIT_REPO_T6Y not in __CONFIG_JSON:
            LOGGER.error(
                f'请补充配置"{__CONFIG_KEY_GERRIT_SUBMIT_REPO_T6Y}"到.config\n'
            )
        __CONFIG_VALUE_GERRIT_SUBMIT_REPO_T6Y = __CONFIG_JSON[
            __CONFIG_KEY_GERRIT_SUBMIT_REPO_T6Y
        ]
    return __CONFIG_VALUE_GERRIT_SUBMIT_REPO_T6Y


__CONFIG_KEY_HOST_CSC_CONFLUENCE = "host_csc_confluence"
__CONFIG_VALUE_HOST_CSC_CONFLUENCE = None


def get_host_csc_confluence() -> bool:
    global __CONFIG_VALUE_HOST_CSC_CONFLUENCE
    if __CONFIG_VALUE_HOST_CSC_CONFLUENCE == None:
        if __CONFIG_KEY_HOST_CSC_CONFLUENCE not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_HOST_CSC_CONFLUENCE}"到.config\n')
        __CONFIG_VALUE_HOST_CSC_CONFLUENCE = __CONFIG_JSON[
            __CONFIG_KEY_HOST_CSC_CONFLUENCE
        ]
    return __CONFIG_VALUE_HOST_CSC_CONFLUENCE


__CONFIG_KEY_HOST_REMOTE = "host_remote"
__CONFIG_VALUE_HOST_REMOTE = None


def get_host_remote() -> bool:
    global __CONFIG_VALUE_HOST_REMOTE
    if __CONFIG_VALUE_HOST_REMOTE == None:
        if __CONFIG_KEY_HOST_REMOTE not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_HOST_REMOTE}"到.config\n')
        __CONFIG_VALUE_HOST_REMOTE = __CONFIG_JSON[__CONFIG_KEY_HOST_REMOTE]
    return __CONFIG_VALUE_HOST_REMOTE


__CONFIG_KEY_GITHUB_OWNERE = "github_owner"
__CONFIG_VALUE_GITHUB_OWNERE = None


def get_github_owner() -> bool:
    global __CONFIG_VALUE_GITHUB_OWNERE
    if __CONFIG_VALUE_GITHUB_OWNERE == None:
        if __CONFIG_KEY_GITHUB_OWNERE not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_GITHUB_OWNERE}"到.config\n')
        __CONFIG_VALUE_GITHUB_OWNERE = __CONFIG_JSON[__CONFIG_KEY_GITHUB_OWNERE]
    return __CONFIG_VALUE_GITHUB_OWNERE


__CONFIG_KEY_SYNC_JIRA_CONFIG = "sync_jira_config"
__CONFIG_VALUE_SYNC_JIRA_CONFIG = None


def get_sync_jira_config() -> dict:
    global __CONFIG_VALUE_SYNC_JIRA_CONFIG
    if __CONFIG_VALUE_SYNC_JIRA_CONFIG == None:
        if __CONFIG_KEY_SYNC_JIRA_CONFIG not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_SYNC_JIRA_CONFIG}"到.config\n')
        __CONFIG_VALUE_SYNC_JIRA_CONFIG = __CONFIG_JSON[__CONFIG_KEY_SYNC_JIRA_CONFIG]
    return __CONFIG_VALUE_SYNC_JIRA_CONFIG


__CONFIG_KEY_JIRA_USERS = "jira_users"
__CONFIG_VALUE_JIRA_USERS = None


def get_jira_users() -> dict:
    global __CONFIG_VALUE_JIRA_USERS
    if __CONFIG_VALUE_JIRA_USERS == None:
        if __CONFIG_KEY_JIRA_USERS not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_JIRA_USERS}"到.config\n')
        __CONFIG_VALUE_JIRA_USERS = __CONFIG_JSON[__CONFIG_KEY_JIRA_USERS]
    return __CONFIG_VALUE_JIRA_USERS


__CONFIG_KEY_WORKLOG_CONFIG = "worklog_config"
__CONFIG_VALUE_WORKLOG_CONFIG = None


def get_worklog_config() -> dict:
    global __CONFIG_VALUE_WORKLOG_CONFIG
    if __CONFIG_VALUE_WORKLOG_CONFIG == None:
        if __CONFIG_KEY_WORKLOG_CONFIG not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_WORKLOG_CONFIG}"到.config\n')
        __CONFIG_VALUE_WORKLOG_CONFIG = __CONFIG_JSON[__CONFIG_KEY_WORKLOG_CONFIG]
    return __CONFIG_VALUE_WORKLOG_CONFIG


__CONFIG_KEY_MODULES_INFO = "modules_info"
__CONFIG_VALUE_MODULES_INFO = None


def get_modules_info() -> dict:
    global __CONFIG_VALUE_MODULES_INFO
    if __CONFIG_VALUE_MODULES_INFO == None:
        if __CONFIG_KEY_MODULES_INFO not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_MODULES_INFO}"到.config\n')
        __CONFIG_VALUE_MODULES_INFO = __CONFIG_JSON[__CONFIG_KEY_MODULES_INFO]
    return __CONFIG_VALUE_MODULES_INFO


__CONFIG_KEY_PROJECTS_INFO = "projects_info"
__CONFIG_VALUE_PROJECTS_INFO = None


def get_projects_info() -> dict:
    global __CONFIG_VALUE_PROJECTS_INFO
    if __CONFIG_VALUE_PROJECTS_INFO == None:
        if __CONFIG_KEY_PROJECTS_INFO not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_PROJECTS_INFO}"到.config\n')
        __CONFIG_VALUE_PROJECTS_INFO = __CONFIG_JSON[__CONFIG_KEY_PROJECTS_INFO]
    return __CONFIG_VALUE_PROJECTS_INFO



__CONFIG_KEY_ISSUE_LIST_JQL = "issue_list_jql"
__CONFIG_VALUE_ISSUE_LIST_JQL = None


def get_issue_list_jql() -> str:
    global __CONFIG_VALUE_ISSUE_LIST_JQL
    if __CONFIG_VALUE_ISSUE_LIST_JQL is None:
        if __CONFIG_KEY_ISSUE_LIST_JQL not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ISSUE_LIST_JQL}"到.config\n')
        __CONFIG_VALUE_ISSUE_LIST_JQL = __CONFIG_JSON[__CONFIG_KEY_ISSUE_LIST_JQL]
    return __CONFIG_VALUE_ISSUE_LIST_JQL



__CONFIG_KEY_ISSUE_FIELD = "issue_field"
__CONFIG_VALUE_ISSUE_FIELD = []


def get_issue_field() -> list:
    global __CONFIG_VALUE_ISSUE_FIELD
    if not __CONFIG_VALUE_ISSUE_FIELD:
        if __CONFIG_KEY_ISSUE_FIELD not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_ISSUE_FIELD}"到.config\n')
        __CONFIG_VALUE_ISSUE_FIELD = __CONFIG_JSON[__CONFIG_KEY_ISSUE_FIELD]
    return __CONFIG_VALUE_ISSUE_FIELD


# ========== 读取.config中的禅道创建模块映射 create_zentao_map ==========
__CONFIG_KEY_CREATE_ZENTAO_MAP = "create_zentao_map"
__CONFIG_VALUE_CREATE_ZENTAO_MAP = None

def get_create_zentao_map() -> list:
    """读取禅道创建模块映射（新格式：List[Dict]）"""
    global __CONFIG_VALUE_CREATE_ZENTAO_MAP
    if __CONFIG_VALUE_CREATE_ZENTAO_MAP is None:
        if __CONFIG_KEY_CREATE_ZENTAO_MAP not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_CREATE_ZENTAO_MAP}"到.config\n')
            __CONFIG_VALUE_CREATE_ZENTAO_MAP = []  # 改为空列表（原是空dict）
        else:
            # 读取新格式：List[Dict]
            __CONFIG_VALUE_CREATE_ZENTAO_MAP = __CONFIG_JSON[__CONFIG_KEY_CREATE_ZENTAO_MAP]
            # 兼容校验：确保格式正确
            if not isinstance(__CONFIG_VALUE_CREATE_ZENTAO_MAP, list):
                LOGGER.error(f'配置"{__CONFIG_KEY_CREATE_ZENTAO_MAP}"格式错误，应为List[Dict]，已重置为空列表')
                __CONFIG_VALUE_CREATE_ZENTAO_MAP = []
            else:
                # 过滤有效项（必须包含zt_pname/zt_pid/zt_assignee）
                valid_items = []
                for item in __CONFIG_VALUE_CREATE_ZENTAO_MAP:
                    if isinstance(item, dict) and all(k in item for k in ["zt_pname", "zt_pid", "zt_assignee"]):
                        valid_items.append(item)
                    else:
                        LOGGER.warning(f'过滤无效配置项：{item}（需包含zt_pname/zt_pid/zt_assignee字段）')
                __CONFIG_VALUE_CREATE_ZENTAO_MAP = valid_items
    return __CONFIG_VALUE_CREATE_ZENTAO_MAP

# ========== 新增：兼容原有Dict格式的辅助方法（防止其他代码依赖） ==========
def get_create_zentao_map_dict() -> dict:
    """兼容原有逻辑：将List[Dict]转回双层Dict格式"""
    zentao_list = get_create_zentao_map()
    zentao_map = {}
    for item in zentao_list:
        pname = item.get("zt_pname")
        if pname:
            zentao_map[pname] = {
                "zt_pid": item.get("zt_pid"),
                "zt_assignee": item.get("zt_assignee")
            }
    return zentao_map

# ========== 新增：获取项目名称列表（适配UI下拉框） ==========
def get_zentao_project_names() -> list:
    """提取所有zt_pname值，用于UI下拉框"""
    zentao_list = get_create_zentao_map()
    return [item.get("zt_pname") for item in zentao_list if item.get("zt_pname")]

# ========== 读取.config中的Jira项目名称映射 jira_project_name_list ==========
__CONFIG_KEY_JIRA_PROJECT_NAME_LIST = "jira_project_name_list"
__CONFIG_VALUE_JIRA_PROJECT_NAME_LIST = None

def get_jira_project_name_list() -> list:
    """读取Jira项目名称映射（新格式：List[Dict]）"""
    global __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST
    if __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST is None:
        if __CONFIG_KEY_JIRA_PROJECT_NAME_LIST not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_JIRA_PROJECT_NAME_LIST}"到.config\n')
            __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST = []  # 改为空列表（原是空dict）
        else:
            # 读取新格式：List[Dict]
            __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST = __CONFIG_JSON[__CONFIG_KEY_JIRA_PROJECT_NAME_LIST]
            # 兼容校验：确保格式正确（防止配置写错）
            if not isinstance(__CONFIG_VALUE_JIRA_PROJECT_NAME_LIST, list):
                LOGGER.error(f'配置"{__CONFIG_KEY_JIRA_PROJECT_NAME_LIST}"格式错误，应为List[Dict]，已重置为空列表')
                __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST = []
            else:
                # 过滤无效元素（只保留 Dict 类型）
                valid_items = []
                for item in __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST:
                    if isinstance(item, dict) and len(item) == 1:  # 确保是单键值对Dict
                        valid_items.append(item)
                    else:
                        LOGGER.warning(f'过滤无效配置项：{item}（需为单键值对Dict）')
                __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST = valid_items
    return __CONFIG_VALUE_JIRA_PROJECT_NAME_LIST

def get_jira_project_name_values() -> list:
    """从List[Dict]中提取所有value值（兼容原有ui.py的使用方式）"""
    project_list = get_jira_project_name_list()
    value_list = []
    for item in project_list:
        # 取Dict中唯一的value值
        for v in item.values():
            value_list.append(v)
            break  # 确保只取第一个value（单键值对）
    return value_list


# ========== 读取.config中的ngrok auth token ==========
__CONFIG_KEY_NGROK_AUTH_TKOEN = "ngrok_auth_token"
__CONFIG_VALUE_NGROK_AUTH_TKOEN = None

def get_ngrok_auth_token() -> str:
    global __CONFIG_VALUE_NGROK_AUTH_TKOEN
    if __CONFIG_VALUE_NGROK_AUTH_TKOEN is None:
        if __CONFIG_KEY_NGROK_AUTH_TKOEN not in __CONFIG_JSON:
            LOGGER.error(f'请补充配置"{__CONFIG_KEY_NGROK_AUTH_TKOEN}"到.config\n')
        __CONFIG_VALUE_NGROK_AUTH_TKOEN = __CONFIG_JSON[__CONFIG_KEY_NGROK_AUTH_TKOEN]
    return __CONFIG_VALUE_NGROK_AUTH_TKOEN