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
    Gets real-time weather info using wttr.in API (free, no API key needed).
    """
    # Weather description translations
    weather_translations = {
        "Sunny": "晴天",
        "Clear": "晴朗",
        "Partly cloudy": "多雲",
        "Cloudy": "陰天",
        "Overcast": "陰沈",
        "Rainy": "下雨",
        "Light rain": "小雨",
        "Moderate rain": "中雨",
        "Heavy rain": "大雨",
        "Thunderstorm": "雷暴",
        "Snowy": "下雪",
        "Light snow": "小雪",
        "Moderate snow": "中雪",
        "Heavy snow": "大雪",
        "Patchy rain nearby": "附近有小雨",
        "Patchy light rain": "零星小雨",
        "Patchy light drizzle": "零星毛毛雨",
        "Mist": "霧氣",
        "Fog": "濃霧",
        "Drizzle": "毛毛雨",
        "Freezing rain": "冰雨",
        "Sleet": "冷雨",
        "Hail": "冰雹",
        "Windy": "多風"
    }
    
    try:
        url = f"https://wttr.in/{city}?format=j1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        description = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']
        
        translated_desc = weather_translations.get(description, description)
        
        return f"{city}現在的天氣：氣溫 {temp}°C，{translated_desc}，濕度 {humidity}%，風速 {wind_speed} km/h。"
        
    except Exception as e:
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
    except Exception as e:
        return None

def bot_get_google_search(keyword):
    """
    Tries robust DuckDuckGo search first, with a fallback to Google scraping.
    """
    ddg_res = bot_get_ddg_search(keyword)
    if ddg_res and len(ddg_res) > 30:
        return ddg_res

    url = f"https://www.google.com/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
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
    Scrapes Wikipedia for a given keyword with a reasonable timeout.
    """
    if not keyword: return None
        
    url = f"https://zh.wikipedia.org/wiki/{keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # Use a more specific selector for the actual article text
        content_div = soup.select_one(".mw-parser-output")
        if not content_div: return None

        # Find all direct paragraph children to avoid hidden templates
        paragraphs = content_div.find_all('p', recursive=False)
        content = ""
        for p in paragraphs:
            text = p.get_text().strip()
            # Only accept paragraphs that look like actual descriptions (contains Chinese)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            if len(text) > 30 and has_chinese:
                content += text + " "
                if len(content) > 400: break
                    
        if not content or "可以指：" in content or "可以指:" in content:
            return None
            
        return to_traditional(bot_clean_text(content))
    except:
        return None

def bot_enhance_with_gemini(user_input, search_result=""):
    """
    Uses Gemini API to enhance and polish the response.
    """
    try:
        import google.genai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "請在這裡貼上您的API_KEY":
            return search_result if search_result else "我無法提供更多資訊。"
        
        client = genai.Client(api_key=api_key)
        model = 'gemini-flash-latest'
        
        prompt = f"你是一個可愛的機器人助手叫通通。請用簡潔友善的台灣繁體中文回答。問題：{user_input}\n參考資訊：{search_result}\n請回答："
        
        response = client.models.generate_content(model=model, contents=prompt)
        if response.text: return response.text.strip()
        return search_result
    except:
        return search_result

def bot_ask_gemini_direct(user_input, history=None):
    """
    Directly asks Gemini AI, with local fallbacks and conversation context.
    """
    # 1. Local responses for common buttons (Instant)
    local_responses = {
        "你好": "你好呀！我是通通，今天有什麼我可以幫你的嗎？😊",
        "你是誰": "我是通通！您的可愛 AI 助手。無論是查資料、算數學、報天氣還是純聊天，通通都沒問題喔！🤖",
        "心情": "通通今天心情超級好喔！因為可以跟你聊天！✨",
        "推薦": "通通覺得台式料理都很棒喔！像是滷肉飯、牛肉麵或是珍珠奶茶，你喜歡哪一種呢？😋",
        "好吃": "說到好吃的，通通口水都要流下來了！台灣的小吃世界第一，去夜市逛逛準沒錯！",
        "勵志": "成功不是終點，失敗也不是終結，唯有前進的勇氣才是永恆。加油！💪"
    }
    
    for key, val in local_responses.items():
        if key in user_input:
            return val

    # 2. Try AI (Gemini) with history
    try:
        import google.genai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != "請在這裡貼上您的API_KEY":
            client = genai.Client(api_key=api_key)
            
            # Format context from history for Gemini
            context = ""
            if history:
                context = "\n【之前的對話上下文】\n"
                for msg in history[-6:]: # Include last 3 exchanges
                    role = "我 (通通)" if msg['role'] == 'bot' else "你 (使用者)"
                    context += f"{role}: {msg['content']}\n"
            
            prompt = f"""你是一個名叫「通通」的可愛機器人。回答要簡潔、有趣、充滿表情符號。{context}
現在使用者問：{user_input}
請回答："""
            
            try:
                response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                if response.text: return response.text.strip()
            except:
                pass
    except:
        pass

    # 3. Final Fallback: Web Search
    search_res = bot_get_google_search(user_input)
    if search_res and len(search_res) > 30:
        return search_res

    return "通通現在腦袋轉得有點慢（可能是 AI 請求太頻繁了）。請稍等一分鐘再試，或者點擊「你是誰？」來認識我喔！🕒"
