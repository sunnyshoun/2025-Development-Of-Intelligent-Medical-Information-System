import requests
import argparse
from pathlib import Path

def fetch_CKIP_api(sent, token):
    """向 CKIP API 發送請求，回傳詞性標註與實體辨識結果"""
    try:
        res = requests.post("http://140.116.245.157:2001", data={"data": sent, "token": token})
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
        "Event": set()
    }

    if not response or 'ws' not in response:
        print("無法解析 API 回應")
        return entities

    word_list = response['ws'][0]
    pos_list = response['pos'][0]
    ner_list = response['ner'][0]

    # 建立詞性與 NER 對應表
    word_dict = {word: {'pos': pos, 'ner': ""} for word, pos in zip(word_list, pos_list)}

    for start, end, ner, word in ner_list:
        if word in word_dict:
            word_dict[word]['ner'] = ner
        else:
            word_dict[word] = {'pos': "", 'ner': ner}

    # 使役動詞與事件詞過濾條件
    causative_verbs = {"讓", "使", "叫", "迫使", "促使"}
    noun_pos_filter = {"Na", "Nc", "VE"}
    
    i = 0
    while i < len(word_list):
        word, pos = word_list[i], pos_list[i]

        if pos == "VH":
            i += 1
            continue

        if word in causative_verbs and i + 3 < len(word_list):
            next_word, next_pos = word_list[i + 1], pos_list[i + 1]
            verb_word, verb_pos = word_list[i + 2], pos_list[i + 2]
            target_word, target_pos = word_list[i + 3], pos_list[i + 3]

            if next_pos in {"Na", "Np", "Nh"} and verb_pos.startswith("V") and target_pos in {"Na", "Np", "Nc"}:
                entities["Event"].add(f"{word} {next_word} {verb_word} {target_word}")
                i += 4
                continue

        if pos.startswith("V"):
            event_words = [word]
            
            j = i + 1
            while j < len(word_list) and pos_list[j] in noun_pos_filter:
                event_words.append(word_list[j])
                j += 1

            if len(event_words) > 1:
                entities["Event"].add(" ".join(event_words))
            i = j
            continue

        if pos.startswith("V") and i + 1 < len(word_list):
            next_word, next_pos = word_list[i + 1], pos_list[i + 1]
            if next_word != "人" and word not in causative_verbs and next_pos in {"Na", "Np", "Nc"}:
                entities["Event"].add(f"{word} {next_word}")
                i += 2
                continue
        
        i += 1

    ner_mapping = {
        "DATE": "Time",
        "GPE": "Place",
        "ORG": "Object",
        "PERSON": "People",
        "EVENT": "Event"
    }

    for word, data in word_dict.items():
        ner, pos = data['ner'], data['pos']
        if ner in ner_mapping:
            entities[ner_mapping[ner]].add(word)
        elif pos in {"Na", "Nb", "Nc"}:
            entities["Object"].add(word)

    return {key: list(value) for key, value in entities.items()}


def dict_to_markdown(data: dict, output_path: Path):
    """將字典轉換為 Markdown 格式輸出"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in data.items():
            f.write(f"## {key}\n\n")
            if value:
                for item in value:
                    f.write(f"- {item}\n")
            else:
                f.write("_無資料_\n")
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("article", type=str, help="文章 (*.txt) 的路徑")
    parser.add_argument("--output", type=str, default="output.md", help="輸出檔案 (*.md) 的路徑")

    args = parser.parse_args()

    article_path = Path(args.article)
    if article_path.suffix == "":
        article_path = article_path.with_suffix(".txt")

    output_path = Path(args.output)
    if output_path.suffix == "":
        if output_path.exists() and output_path.is_dir():
            output_path = output_path / "output.md"
        else:
            output_path = output_path.with_suffix(".md")
    elif output_path.suffix != ".md":
        output_path = output_path.with_suffix(".md")
    
    print(f"讀取文章 {article_path}")
    with open(F"{article_path}", "r", encoding='UTF-8') as f:
        sent = "".join(f.readlines()).replace("\n", "")
    
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODI1LCJzZXJ2aWNlX2lkIjoiMSIsImV4cCI6MTc1NjE4NjgxMywic3ViIjoiIiwidXNlcl9pZCI6IjUyNSIsInZlciI6MC4xLCJzY29wZXMiOiIwIiwiYXVkIjoid21ta3MuY3NpZS5lZHUudHciLCJuYmYiOjE3NDA2MzQ4MTMsImlhdCI6MTc0MDYzNDgxMywiaXNzIjoiSldUIn0.tYXhqeJSDM1XAOEFndDhB_vOVPjgG82yMoBsaIVlH4G3A763iTIosXeqw-8TRS8rQzdNL4zYw_kf-agJVaQkD_8YUN_qdxKiu1qn9BIV0dC133msvCczjXGxxYBDtoGIfjWc6T9nemK-0FnSlXns-N0QssgCLPR04HtdS2WIV7Y"
    response = fetch_CKIP_api(sent, token)
    if response:
        entities = extract_entities(response)
        dict_to_markdown(entities, output_path)
        print(f"分類完成，結果已存入 {output_path}")
