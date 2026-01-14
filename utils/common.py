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