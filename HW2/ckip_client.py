import requests

def fetch_CKIP_api(sent, token):
    """向 CKIP API 發送請求，回傳詞性標註與實體辨識結果"""
    try:
        res = requests.post("http://140.116.245.157:2001", data={"data": sent, "token": token})
        res.raise_for_status()  # 確保回應成功
        return res.json()
    except requests.RequestException as e:
        print(f"API 請求錯誤: {e}")
        return None

def extract_entities(response):
    """根據 API 回傳結果，分類不同詞性與命名實體"""
    entities = {
        "People": set(),
        "Time": set(),
        "Place": set(),
        "Object": set(),
        "Event": set()  # 儲存事件
    }

    if not response or 'ws' not in response:
        print("無法解析 API 回應")
        return entities
    
    word_list = response['ws'][0]
    pos_list = response['pos'][0]
    ner_list = response['ner'][0]

    # 建立詞性與命名實體對應的字典
    word_dict = {}
    wp_pair = list(zip(word_list, pos_list))
    for word, pos in wp_pair:
        word_dict[word] = {'pos': pos, 'ner': ""}

    # 將 NER 資訊補充到詞典中
    for start, end, ner, word in ner_list:
        if word in word_dict:
            word_dict[word]['ner'] = ner
        else:
            word_dict[word] = {'pos': "", 'ner': ner}

    # 事件辨識 (V + Na/Np/Nh/Ncd) 或 (V + Na + Na) 或 (使役動詞 + N + V + 目標)
    causative_verbs = {"讓", "使", "叫", "迫使", "促使"}  # 使役動詞

    for i in range(len(word_list) - 1):
        word, pos = word_list[i], pos_list[i]
        next_word, next_pos = word_list[i + 1], pos_list[i + 1]

        # 動詞 + 名詞 (受詞)
        if pos.startswith("V") and next_pos in ["Na", "Np", "Nh", "Ncd"]:
            event = f"{word} {next_word}"
            entities["Event"].add(event)

        # 三詞組合：V + Na + Na
        if i < len(word_list) - 2:
            next_next_word, next_next_pos = word_list[i + 2], pos_list[i + 2]
            if pos.startswith("V") and next_pos == "Na" and next_next_pos == "Na":
                event = f"{word} {next_word} {next_next_word}"
                entities["Event"].add(event)

        # 使役動詞 + N + V + N (讓人攻進國會)
        if word in causative_verbs and next_pos in ["Na", "Np", "Nh"]:  # 使役動詞 + 受詞
            if i + 2 < len(word_list):
                verb_word, verb_pos = word_list[i + 2], pos_list[i + 2]  # 主要動作
                if verb_pos.startswith("V") and i + 3 < len(word_list):
                    target_word, target_pos = word_list[i + 3], pos_list[i + 3]  # 目標
                    if target_pos in ["Na", "Np", "Nh", "Ncd"]:  # 目標應為名詞
                        event = f"{word} {next_word} {verb_word} {target_word}"
                        entities["Event"].add(event)

    # NER 與詞性分類
    for word, word_data in word_dict.items():
        ner, pos = word_data['ner'], word_data['pos']
        print(word, ner, pos)

        if ner == "DATE":
            entities['Time'].add(word)
        elif ner == "GPE" and pos != "Nb":
            entities['Place'].add(word)
        elif ner == "ORG":
            entities['Object'].add(word)  # 政黨、組織等
        elif ner == "PERSON":
            entities['People'].add(word)
        elif pos.startswith("N") or pos.startswith("V"):
            entities['Object'].add(word)

    # 轉回列表
    for key in entities:
        entities[key] = list(entities[key])

    return entities

def dict_to_markdown(data: dict, filename: str = "output.md"):
    """將字典轉換為 Markdown 格式輸出"""
    with open(filename, "w", encoding="utf-8") as f:
        for key, value in data.items():
            f.write(f"## {key}\n\n")  # 標題
            if value:
                for item in value:
                    f.write(f"- {item}\n")
            else:
                f.write("_無資料_\n")  # 若無對應資料，顯示「無資料」
            f.write("\n")

if __name__ == "__main__":
    with open("article.txt", "r", encoding='UTF-8') as f:
        sent = "".join(f.readlines()).replace("\n", "")
    
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODI1LCJzZXJ2aWNlX2lkIjoiMSIsImV4cCI6MTc1NjE4NjgxMywic3ViIjoiIiwidXNlcl9pZCI6IjUyNSIsInZlciI6MC4xLCJzY29wZXMiOiIwIiwiYXVkIjoid21ta3MuY3NpZS5lZHUudHciLCJuYmYiOjE3NDA2MzQ4MTMsImlhdCI6MTc0MDYzNDgxMywiaXNzIjoiSldUIn0.tYXhqeJSDM1XAOEFndDhB_vOVPjgG82yMoBsaIVlH4G3A763iTIosXeqw-8TRS8rQzdNL4zYw_kf-agJVaQkD_8YUN_qdxKiu1qn9BIV0dC133msvCczjXGxxYBDtoGIfjWc6T9nemK-0FnSlXns-N0QssgCLPR04HtdS2WIV7Y"
    response = fetch_CKIP_api(sent, token)
    if response:
        entities = extract_entities(response)
        dict_to_markdown(entities)
        print("分類完成，結果已存入 output.md")
