import requests

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

    word_dict = {word: {'pos': pos, 'ner': ""} for word, pos in zip(word_list, pos_list)}
    for start, end, ner, word in ner_list:
        if word in word_dict:
            word_dict[word]['ner'] = ner
        else:
            word_dict[word] = {'pos': "", 'ner': ner}

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

    ner_mapping = {"DATE": "Time", "GPE": "Place", "ORG": "Object", "PERSON": "People", "EVENT": "Event"}
    for word, data in word_dict.items():
        ner, pos = data['ner'], data['pos']
        if ner in ner_mapping:
            entities[ner_mapping[ner]].add(word)
        elif pos in {"Na", "Nb", "Nc"}:
            entities["Object"].add(word)

    return entities