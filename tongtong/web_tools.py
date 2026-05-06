import requests
from bs4 import BeautifulSoup
import datetime
import os
from dotenv import load_dotenv
from .text_utils import to_traditional, bot_clean_text

# Load environment variables
load_dotenv()

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
    Uses duckduckgo_search library with strict regional settings for Taiwan/Traditional Chinese.
    """
    try:
        # Append "中文" to help force language if it's not a common term
        search_query = f"{keyword} 中文"
        with DDGS() as ddgs:
            # region='tw-tzh' for Taiwan Traditional Chinese
            results = ddgs.text(search_query, region='tw-tzh', safesearch='moderate', timelimit='y', max_results=3)
            if results:
                # Filter out results that are purely English if possible, or just take the best one
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

def bot_enhance_with_gemini(user_input, search_result=""):
    """
    Uses Gemini API to enhance and polish the response.
    Returns enhanced response or original search result if API fails.
    """
    try:
        import google.genai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "請在這裡貼上您的API_KEY":
            print("Warning: GEMINI_API_KEY not configured in .env file")
            return search_result if search_result else "我無法提供更多資訊。"
        
        client = genai.Client(api_key=api_key)
        model = 'gemini-2.5-flash'
        
        # Create a prompt to enhance the response
        prompt = f"""使用者問題：{user_input}

搜尋到的資訊：{search_result if search_result else "無"}

請用簡潔、友善的台灣繁體中文回答，不超過200字："""
        
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        if response.text:
            return response.text.strip()
        return search_result
        
    except ImportError:
        print("Warning: google-genai not installed")
        return search_result
    except Exception as e:
        print(f"Gemini API error: {e}")
        return search_result

def bot_ask_gemini_direct(user_input):
    """
    Directly asks Gemini AI when search fails.
    Used as a fallback when Wikipedia and Google searches don't work.
    """
    try:
        import google.genai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "請在這裡貼上您的API_KEY":
            return "抱歉，我的資料庫目前無法存取。不過你可以試試其他方式來問我喔！"
        
        client = genai.Client(api_key=api_key)
        model = 'gemini-2.5-flash'
        
        prompt = f"""使用者問題：{user_input}

請用簡潔、友善、有趣的台灣繁體中文回答，不超過200字。如果不確定，可以說不知道："""
        
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        if response.text:
            return response.text.strip()
        return "我需要想一下呢...請等等喔！"
        
    except ImportError:
        return "抱歉，我的智能模組暫時無法使用。試試問我時間或天氣吧！"
    except Exception as e:
        print(f"Gemini direct ask error: {e}")
        return "哎呀，我出了點小問題。再問我一次試試看？"
