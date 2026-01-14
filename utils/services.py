import sys
import os


from mjira.const import FIELD_CSC, FIELD_SONY
import mjira.field
from mlogger import LOGGER
import os
import mjira.issue
import mjira.net_sony
import mzentao.trans
import mzentao.net
import mconfig
from openpyxl import load_workbook
from urllib.request import HTTPError

from libmirror.mstr import extract_pr_list


def download_jira_attachments(jira_info, jira_id):
    attachments = mjira.field.get_attachments(jira_info)
    assets_path_list = []
    assets_folder = os.getcwd() + "\\" + jira_id + "\\"
    for attachment_info in attachments:
        mjira.net_sony.download_sony_attachment(
            attachment_info["content"], attachment_info["filename"], assets_folder
        )
        assets_path_list.append(assets_folder + attachment_info["filename"])
    return assets_path_list


def sync_jira_to_zentao(jira_id, zt_pid,zt_assignee):
    try:
        # 获取Jira信息
        sync_result = ""
        input_bug_str = jira_id
        sony_jira_id = ""
        sync_success = "Success"
        sync_fail = "Fail"
        # 是否为DQA Jira Ticket
        input_key_str = mjira.issue.extract_internal_bug_key(input_bug_str)
        if not input_key_str:
            sync_result = jira_id + " - 输入值不为有效的 DQA Jira Ticket"
            return sync_fail, sync_result
        jira_info = mjira.net_sony.get_sony_jira(input_key_str)
        if not input_key_str:
            sync_result = jira_id + " - Sony Jira Center中搜索不到DQA Jira对应的信息"
            return sync_fail, sync_result
        sony_jira_id = input_key_str

        # 转换成Zt参数
        zt_id, zt_params = mzentao.trans.trans_sqa_to_zt_home(zt_pid, zt_assignee, jira_info)
        if zt_id:
            sync_result = jira_id + " - 此票已存在禅道ID: " + zt_id
            return sync_fail, sync_result

        # 获取附件并加载到本地
        assets_path_list = download_jira_attachments(jira_info, sony_jira_id)
        LOGGER.debug("附件列表:" + str(assets_path_list))

        # 创建Zt, 此时应获得Zt Id
        add_result, add_zt_id = mzentao.net.add_bug(zt_params, assets_path_list)
        if not add_result:
            sync_result = "禅道创建失败!"
            if not add_zt_id:
                sync_result = "禅道创建成功, 但获取创建的禅道Id失败!"
            return sync_fail, sync_result
        sync_result = "已创建的禅道：" + add_zt_id
        LOGGER.debug("创建的禅道Id: " + str(add_zt_id))

        chandao_link = mjira.issue.format_chandao_link("禅道-" + add_zt_id)
        update_result = mjira.net_sony.update_sony_jira(
            sony_jira_id, {FIELD_SONY.EXTERNAL_ISSUE_ID: chandao_link}
        )
        if update_result:
            sync_result = "禅道" + add_zt_id + "已更新到Jira的Trd Party Id字段"
            print("已将禅道链接更新到Jira的Trd Party Id字段")
            return sync_success, sync_result
        else:
            sync_result = sync_fail, "禅道" + add_zt_id + "更新到Jira失败!"
            return sync_fail, sync_result
    except Exception as e:
        print(e)
        return sync_fail, str(e)


def sync_excel():
    file_path = mconfig.get_issue_list_file_path()

    # 一份读取值
    wb_data = load_workbook(file_path, data_only=True)
    ws_data = wb_data.active

    # 一份读取公式
    wb = load_workbook(file_path)
    ws = wb.active

    # 处理
    for i, (row_data, row) in enumerate(zip(ws_data.iter_rows(min_row=2, max_col=7),
                                            ws.iter_rows(min_row=2, max_col=7)), start=2):
        jira_id = row_data[0].value  # 读取值
        zt_pid = str(row_data[2].value)  # 读取值
        zt_assignee = str(row_data[3].value) # 读取值

        if not jira_id:
            break

        sync_flg, sync_result = sync_jira_to_zentao(jira_id, zt_pid,zt_assignee)

        row[5].value = sync_flg
        row[6].value = sync_result

    # 保存（保留原始公式）
    wb.save(file_path)


def get_jira_sync_list(jql_text):
    jira_issue_list = []
    # 直接从mconfig获取
    # jql = mconfig.get_issue_list_jql()
    jql = jql_text

    try:
        search_result = mjira.net_sony.search_sony_jira_in_params(jql,mconfig.get_issue_field(),-1)
        #  核心判断：如果返回的是HTTPError异常对象 → 主动抛出，向上传递
        if isinstance(search_result, HTTPError):
            raise search_result
        #  只有返回正常数据，才执行取值和循环逻辑
        jql_result_list = search_result["issues"]
        for result in jql_result_list:
            issue_dict = dict()
            external_issue_link = result['fields']['customfield_17000']
            zentao_id = (
            mjira.issue.extract_chandao_key(external_issue_link.strip()) or ""
            if external_issue_link
            else ""
        )
            issue_dict.update(
                {'jira_key': result['key'],
                 'jira_summary': result['fields']['summary'],
                 'jira_status': result['fields']['status']['name'],
                 'jira_rank': result['fields']['customfield_31801']['value'],
                 'zentao_id':  zentao_id
                 })
            jira_issue_list.append(issue_dict)
        print(jira_issue_list)

    except HTTPError as e:
        #  捕获HTTP异常，直接返回异常对象e，e内包含完整的 e.code + e.reason
        return e
    except Exception as e:
        #  兜底捕获所有其他异常，返回空列表，防止程序卡死
        return []

        #  正常返回数据列表
    return jira_issue_list

def get_jira_with_zentao(jira_issue_list, ui=None):
    if isinstance(jira_issue_list, HTTPError):
        raise jira_issue_list
    zentao_id_list = list()
    for jira_issue in jira_issue_list:
        zentao_id_list.append(jira_issue['zentao_id'])
    total_count = len(zentao_id_list)
    zentao_result_list = mzentao.net.get_bugs_with_ids(
        zentao_id_list,
        # 进度回调函数：实时更新UI气泡进度
        progress_callback=lambda curr, total: ui.run_in_main_thread(
            ui.show_progress_tooltip,
            f"共{total}条数据，解析中 {curr}/{total}"
        ) if ui else None
    )
    result_list = [{**d1, **d2} for d1, d2 in zip(jira_issue_list, zentao_result_list)]
    return result_list