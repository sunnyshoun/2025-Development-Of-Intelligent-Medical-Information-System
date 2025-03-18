import os
import pandas as pd
from crawler import crawl_keywords
from keyword_manager import generate_keywords
from dotenv import load_dotenv

def news_search(output_csv, token, target_count=10000, min_keywords_per_round=20, sample_articles=20, keywords=["台灣"]):
    all_news_data = []
    existing_links = set()
    used_keywords = set()
    round_num = 1

    while len(all_news_data) < target_count and keywords:
        keywords = list(set(keywords) - used_keywords)
        if not keywords and len(all_news_data) < target_count:
            keywords = generate_keywords(all_news_data, used_keywords, token, min_keywords_per_round, sample_articles)
            if not keywords:
                print("無新關鍵字可供下一輪爬取，停止程式。")
                break

        print(f"\n=== 第 {round_num} 輪爬取開始，關鍵字數量：{len(keywords)} ===")
        new_news, existing_links = crawl_keywords(keywords, existing_links, len(all_news_data), target_count)
        all_news_data.extend(new_news)
        
        current_df = pd.DataFrame(all_news_data)
        current_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"目前總計 {len(all_news_data)} 筆資料，已更新至 {output_csv}")

        if len(all_news_data) >= target_count:
            print(f"\n已達目標 {target_count} 筆資料，爬取結束。")
            break

        used_keywords.update(keywords)
        round_num += 1

    print(f"\n爬取完成，總計 {len(all_news_data)} 筆資料已儲存至 {output_csv}")
    if len(all_news_data) < target_count:
        print(f"注意：未達目標 {target_count} 筆，可能已無新資料或新關鍵字可爬取。")

if __name__ == "__main__":
    load_dotenv(override=True)
    CKIP_API_TOKEN = os.getenv("CKIP_API_TOKEN")
    output_csv = "news_result.csv"
    
    news_search(output_csv, CKIP_API_TOKEN, sample_articles=50)