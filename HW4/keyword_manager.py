import random
from ckip_tool import fetch_CKIP_api, extract_entities

def generate_keywords(all_news_data, used_keywords, token, min_keywords_per_round, sample_articles):
    """從現有資料生成新關鍵字"""
    if not all_news_data:
        print("無資料可供斷詞")
        return []

    print("關鍵字已用完，隨機選取上一輪部分文章進行斷詞...")
    sampled_news = random.sample(all_news_data[-len(all_news_data):], min(sample_articles, len(all_news_data)))
    sampled_titles = "，".join([item['Title'] for item in sampled_news])
    
    response = fetch_CKIP_api(sampled_titles, token)
    if not response:
        print("CKIP API 提取失敗")
        return []
    
    entities = extract_entities(response)
    keywords = list(set(entities["People"]) - used_keywords)
    
    if len(keywords) < min_keywords_per_round:
        remaining_count = min_keywords_per_round - len(keywords)
        other_entities = []
        for category in ["Event", "Place", "Object", "Time"]:
            new_items = list(set(entities[category]) - used_keywords)
            other_entities.extend(new_items)
            if len(keywords) + len(other_entities) >= min_keywords_per_round:
                break
        keywords.extend(other_entities[:remaining_count])
    
    keywords = list(set([kw.strip() for kw in keywords if kw.strip() and len(kw) > 1]) - used_keywords)
    
    return keywords