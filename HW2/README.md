# Readme - CKIP API Text Processor

## 簡介

本專案使用 CKIP API 來進行詞性標註與命名實體辨識，並將分析結果輸出為 Markdown 格式。

## 環境需求

- Python 3.x
- `requests` 套件

## 安裝方式

請先安裝 `requests` 套件：

```sh
pip install requests
```

## 使用方式

執行 `main.py`，並提供 `.txt` 文章檔案的路徑。

```sh
python main.py <文章路徑> --output=<輸出路徑>
```

### 參數說明

- `article` (必填)：要處理的文章檔案 (`.txt` 格式)
- `--output` (選填)：輸出 Markdown 的 路徑 (`.md` 格式)，預設為 `output.md`

### 自動處理邏輯

- 若 `article` 無 `.txt` 副檔名，則自動補上。
- 若 `--output` 為資料夾，則輸出為 `資料夾/output.md`。
- 若 `--output` 無副檔名，則自動補上 `.md`。

## 範例

```sh
python main.py sample.txt --output result.md
```

或指定資料夾作為輸出：

```sh
python main.py input.txt --output result/
```

結果將儲存於 `result/output.md`。

## 主要功能

1. **API 請求**：向 CKIP API 發送請求，回傳詞性標註與命名實體辨識結果。
2. **實體分類**：
   - `People`：人名
   - `Time`：時間
   - `Place`：地點
   - `Object`：物件、組織
   - `Event`：事件
3. **Markdown 格式輸出**：將結果輸出為 `.md` 檔案。

## 輸出格式範例 (`output.md`)

```md
## People
- 王小明

## Time
- 2024年3月4日

## Place
- 台北

## Object
- 電腦

## Event
- 參加 比賽
```

## 注意事項

- 確保輸入檔案為 `.txt` 格式，以避免錯誤。
