history = {
  "32501": {
    "action": "opened",
    "actor": "zhanghansong",
    "comment": "",
    "date": "2026-01-08 13:13:12",
    "extra": "",
    "history": [],
    "id": "32501",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  },
  "32538": {
    "action": "edited",
    "actor": "zhanghansong",
    "comment": "12345",
    "date": "2026-01-08 13:58:56",
    "extra": "",
    "history": [
      {
        "action": "32538",
        "diff": "001- <del><p><b>[步骤]</b></del>\n001+ <ins><p><b>[步骤]</b> </p></ins>\n002- <del></p><p> [初始情况]</del>\n002+ <ins><p>[初始情况]</p><...></del>\n010+ <ins><p>[Signal Condition]</p></ins>\n011+ <ins><p>PKG: v0288_0010</p></ins>\n012+ <ins><p><b>[备注]</b></p></ins>",
        "field": "steps",
        "id": "49789",
        "new": "<p><b>[步骤]</b> </p>\n<p>[初始情况]</p>\n<p>[操作/状态]</p>\n<p><b>[结果]</b> </p>\n<p><b>[期望]</b> </p>\n<p><br /></p>\n<p><b>[环境]</b> <...ironmental Condition]</p>\n<p>[Connected Equipment]</p>\n<p>[Signal Condition]</p>\n<p>PKG: v0288_0010</p>\n<p><b>[备注]</b></p>",
        "old": "<p><b>[步骤]</b>\n</p><p> [初始情况]\n</p><p> [操作/状态]\n</p><p></p><p><b>[结果]</b>\n</p><p> </p><p><b>[期望]</b>\n</p><p>\n</p><p> </p>...ntal Condition]\n</p><p> [Connected Equipment]\n</p><p> [Signal Condition]</p><p>PKG: v0288_0010 </p><p><b>[备注]</b></p><p></p>"
      },
      {
        "action": "32538",
        "diff": "",
        "field": "assignedTo",
        "id": "49790",
        "new": "",
        "old": "张寒松"
      }
    ],
    "id": "32538",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  },
  "32705": {
    "action": "commented",
    "actor": "zhanghansong",
    "comment": "备注1",
    "date": "2026-01-08 21:20:04",
    "extra": "",
    "history": [],
    "id": "32705",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  },
  "32706": {
    "action": "commented",
    "actor": "zhanghansong",
    "comment": "备注2",
    "date": "2026-01-08 21:20:15",
    "extra": "",
    "history": [],
    "id": "32706",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  },
  "32707": {
    "action": "commented",
    "actor": "zhanghansong",
    "comment": "备注3",
    "date": "2026-01-08 21:20:22",
    "extra": "",
    "history": [],
    "id": "32707",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  },
  "32923": {
    "action": "edited",
    "actor": "zhanghansong",
    "comment": "",
    "date": "2026-01-09 15:38:56",
    "extra": "",
    "history": [
      {
        "action": "32923",
        "diff": "001- <del>Pseudo Bug11</del>\n001+ <ins>[Test API] 8</ins>",
        "field": "title",
        "id": "50431",
        "new": "[Test API] 8",
        "old": "Pseudo Bug11"
      }
    ],
    "id": "32923",
    "objectID": "3853",
    "objectType": "bug",
    "product": ",44,",
    "project": "0",
    "read": "0"
  }
}


def transfer_single_zentao_history(history_content):
    history_str = (history_content['id'] + ": "
                   + history_content['date'] + ", "
                   + history_content['actor'] + " "
                   + history_content['action'] + ", Comment: "
                   + history_content['comment'])
    return history_str


def show_latest_zentao_history(history_dict):
    latest_history_id = max(history_dict, key=lambda k: int(k))
    latest_history_content = history_dict[latest_history_id]
    history_str = transfer_single_zentao_history(latest_history_content)
    return history_str


def show_all_zentao_history(history_dict):
    history_list = list()
    for history_id, history_content in history_dict.items():
        history_list.append(transfer_single_zentao_history(history_content))
    return history_list
