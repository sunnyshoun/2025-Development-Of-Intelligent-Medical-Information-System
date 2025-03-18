import feedparser
import time
import random
import urllib.parse

BASE_URL = "https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&num=100"

def crawl_keywords(keywords, existing_links, current_count, target_count):
    """爬取 Google News RSS，若提供 existing_links 則過濾重複"""
    new_news_data = []
    query_num = 1
    
    for keyword in keywords:
        print(f"正在查詢關鍵字 ({query_num}/{len(keywords)}): {keyword}")
        encoded_query = urllib.parse.quote(keyword.strip())
        url = BASE_URL.format(query=encoded_query)
        feed = feedparser.parse(url)
        entries = feed.entries

        for entry in entries:
            link = entry.link
            if link not in existing_links:
                new_news_data.append({
                    'Title': entry.title,
                    'Link': link,
                    'Source': entry.source.title if 'source' in entry else 'Unknown'
                })
                existing_links.add(link)
                if current_count + len(new_news_data) >= target_count:
                    print(f"本輪爬取 {len(new_news_data)} 筆資料，已達目標數量，中止爬取")
                    return new_news_data, existing_links
        query_num += 1
        time.sleep(random.uniform(0.2, 1))
    
    print(f"本輪爬取 {len(new_news_data)} 筆資料")
    return new_news_data, existing_links