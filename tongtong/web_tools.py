import requests
from bs4 import BeautifulSoup
import datetime
import os
import random
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
    Gets real-time weather info using wttr.in API (free, no API key needed).
    """
    weather_translations = {
        "Sunny": "晴天", "Clear": "晴朗", "Partly cloudy": "多雲", "Cloudy": "陰天",
        "Overcast": "陰沈", "Rainy": "下雨", "Light rain": "小雨", "Moderate rain": "中雨",
        "Heavy rain": "大雨", "Thunderstorm": "雷暴", "Snowy": "下雪", "Light snow": "小雪",
        "Moderate snow": "中雪", "Heavy snow": "大雪", "Mist": "霧氣", "Fog": "濃霧",
        "Drizzle": "毛毛雨", "Windy": "多風"
    }
    
    try:
        url = f"https://wttr.in/{city}?format=j1"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        description = current['weatherDesc'][0]['value']
        translated_desc = weather_translations.get(description, description)
        return f"{city}現在的天氣：氣溫 {temp}°C，{translated_desc}，濕度 {current['humidity']}%。"
    except:
        return f"查詢天氣時出錯了呢，你可以試著直接問我其他問題喔！"

from duckduckgo_search import DDGS

def bot_get_ddg_search(keyword):
    """
    Uses duckduckgo_search library with strict regional settings and safer timeouts.
    """
    try:
        search_query = f"{keyword} 介紹"
        with DDGS() as ddgs:
            results = ddgs.text(search_query, region='tw-tzh', safesearch='moderate', timelimit='y', max_results=5)
            if results:
                valid_bodies = [r['body'] for r in results if 'body' in r and len(r['body']) > 30]
                if valid_bodies:
                    content = " ".join(valid_bodies[:2])
                    return bot_clean_text(to_traditional(content))
        return None
    except:
        return None

def bot_get_google_search(keyword):
    """
    Tries robust DuckDuckGo search first, with a fallback to Google scraping.
    """
    ddg_res = bot_get_ddg_search(keyword)
    if ddg_res and len(ddg_res) > 30:
        return ddg_res

    url = f"https://www.google.com/search?q={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        selectors = ["div.VwiC3b", "span.hgKElc", "div.BNeawe"]
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                best_text = max([el.get_text() for el in elements], key=len)
                if len(best_text) > 30:
                    return bot_clean_text(to_traditional(best_text))
        return None
    except:
        return None

def bot_get_wiki(keyword):
    """
    Scrapes Wikipedia with robust selector and longer timeout.
    """
    if not keyword: return None
    url = f"https://zh.wikipedia.org/wiki/{keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.select_one(".mw-parser-output")
        if not content_div: return None
        
        # Find all paragraphs (allow nested)
        paragraphs = content_div.find_all('p')
        content = ""
        for p in paragraphs:
            text = p.get_text().strip()
            # Filter meta paragraphs
            if len(text) > 40 and any('\u4e00' <= char <= '\u9fff' for char in text):
                if "導覽" in text[:10] or "目錄" in text[:10]: continue
                content += text + " "
                if len(content) > 500: break
        
        if not content or "可以指：" in content: return None
        return to_traditional(bot_clean_text(content))
    except:
        return None

def bot_enhance_with_gemini(user_input, search_result=""):
    """
    Uses Gemini API to enhance the response.
    """
    try:
        import google.genai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "請在這裡貼上您的API_KEY":
            return search_result
        client = genai.Client(api_key=api_key)
        prompt = f"你是一個可愛機器人通通。用簡潔友善的台灣繁體中文回答。問題：{user_input}\n資訊：{search_result}"
        response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
        return response.text.strip() if response.text else search_result
    except:
        return search_result

def bot_ask_gemini_direct(user_input, history=None):
    """
    Directly asks Gemini AI, with local fallbacks and a robust error message.
    """
    local_responses = {
        "你好": "你好呀！我是通通，今天有什麼我可以幫你的嗎？😊",
        "你是誰": "我是通通！您的可愛 AI 助手。🤖💖",
        "推薦": "通通覺得滷肉飯和珍珠奶茶超棒！😋",
        "勵志": random.choice(["加油！你是最棒的！💪✨", "明天會更好喔！🌟"]),
    }
    
    for key, val in local_responses.items():
        if key in user_input: return val

    try:
        import google.genai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != "請在這裡貼上您的API_KEY":
            client = genai.Client(api_key=api_key)
            context = ""
            if history:
                context = "\n【上下文】\n" + "\n".join([f"{'我' if m['role']=='bot' else '你'}: {m['content']}" for m in history[-4:]])
            prompt = f"你是一個名叫「通通」的可愛機器人。回答要簡潔有趣。{context}\n現在問：{user_input}"
            try:
                response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                if response.text: return response.text.strip()
            except: pass
    except: pass

    # Last resort search
    search_res = bot_get_google_search(user_input)
    if search_res and len(search_res) > 30: return search_res

    return "通通現在腦袋有點打結...可能是網路太慢或 AI 忙碌中。請一分鐘後再點一次「查 台灣歷史」，我一定會幫你找到的！💪✨"
