import json
import random
from pathlib import Path
from ckiptagger import WS
from opencc import OpenCC

# 設定模型路徑
MODEL_PATH = "./model"  # 你的 CKIPtagger 模型資料夾位置
ws = WS(MODEL_PATH)

# 設定字典路徑
DICT_PATH = "./chinese_dictionary.txt"
with open(DICT_PATH, "r", encoding="utf-8") as f:
    custom_dict = set(line.strip() for line in f)

# 讀取 "活網缺愛複製文" json檔
with open("HuoWang_copypasta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

#建立 result folder
Path("./result").mkdir(parents=True, exist_ok=True)

# 隨機抽選一條複製文
selected_text = random.choice(data)["content"]
with open("./result/select_text.txt", "w", encoding="UTF-8") as f:
    f.write(selected_text)

# 簡體轉繁體
cc = OpenCC('s2twp')
traditional_text = cc.convert(selected_text)
with open("./result/cc_convert.txt", "w", encoding="UTF-8") as f:
    f.write(traditional_text)

# 斷句
seg = traditional_text.replace("\r\n","\n").split('\n')

# CKIPtagger 分詞
seg_result = ws(seg, segment_delimiter_set=custom_dict)
with open("./result/WS_result.txt", "w", encoding="UTF-8") as f:
    for sentence in seg_result:
        f.write(" / ".join(sentence) + "\n")  # 每行句子換行

