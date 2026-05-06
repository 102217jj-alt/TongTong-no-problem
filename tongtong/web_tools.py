import requests
from bs4 import BeautifulSoup
import datetime
from .text_utils import to_traditional, bot_clean_text

def bot_get_time():
    """
    Returns the current date and time.
    """
    now = datetime.datetime.now()
    return now.strftime("現在是 %Y 年 %m 月 %d 日，%H 點 %M 分。")

def bot_get_weather(city="台北"):
    """
    Scrapes weather info from Google search (simplified).
    """
    url = f"https://www.google.com/search?q={city}+天氣"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find weather info in Google's special snippet
        temp = soup.find("span", {"id": "wob_tm"})
        cond = soup.find("span", {"id": "wob_dc"})
        
        if temp and cond:
            return f"{city}目前的氣溫是 {temp.text} 度，天氣狀況是 {cond.text}。"
        else:
            # Fallback search result text
            return f"我沒辦法直接看到氣溫，但你可以去 Google 搜尋「{city} 天氣」看看喔！"
    except Exception as e:
        return f"抱歉，查詢天氣時發生錯誤：{e}"

from duckduckgo_search import DDGS

def bot_get_ddg_search(keyword):
    """
    Uses duckduckgo_search library for a robust web query.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(keyword, region='wt-wt', safesearch='moderate', timelimit='y', max_results=3)
            if results:
                # Combine snippets from the top results
                content = " ".join([r['body'] for r in results if 'body' in r])
                if content:
                    return bot_clean_text(to_traditional(content))
        return None
    except Exception as e:
        print(f"DDG Search library error: {e}")
        return None

def bot_get_google_search(keyword):
    """
    Tries robust DuckDuckGo search first, then falls back to basic scraping.
    """
    # 1. Try robust DDG search library
    ddg_res = bot_get_ddg_search(keyword)
    if ddg_res and len(ddg_res) > 30:
        return ddg_res

    # 2. Fallback to Google scraping (if not blocked)
    url = f"https://www.google.com/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        selectors = ["div.VwiC3b", "span.hgKElc", "div.BNeawe"]
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                best_text = max([el.get_text() for el in elements], key=len)
                if len(best_text) > 30:
                    return bot_clean_text(to_traditional(best_text))
        
        return f"我幫你上網找了關於「{keyword}」的資料，但暫時沒辦法直接讀取內容。換個說法試試看？"
    except Exception as e:
        return f"上網找資料時發生了一點問題：{e}"

def bot_get_wiki(keyword):
    """
    Scrapes Wikipedia for a given keyword.
    """
    if not keyword:
        return "請問你想查什麼呢？"
        
    url = f"https://zh.wikipedia.org/wiki/{keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return f"抱歉，維基百科上找不到關於「{keyword}」的資料。"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            return f"我找到了「{keyword}」的頁面，但沒辦法讀取內容。"

        paragraphs = content_div.find_all('p')
        content = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 10:
                content += text + " "
                if len(content) > 300:
                    break
                    
        # If content is empty or looks like a disambiguation page
        if not content or "可以指：" in content or "可以指:" in content:
            # Return None to trigger general web search in brain.py
            return None
            
        content = bot_clean_text(content)
        return to_traditional(content)
    except Exception as e:
        return None # Trigger fallback on error
