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
        # Use wttr.in API - supports cities worldwide
        url = f"https://wttr.in/{city}?format=j1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract current weather
        current = data['current_condition'][0]
        temp = current['temp_C']
        description = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']
        
        # Translate weather description
        translated_desc = weather_translations.get(description, description)
        
        return f"{city}現在的天氣：氣溫 {temp}°C，{translated_desc}，濕度 {humidity}%，風速 {wind_speed} km/h。"
        
    except requests.exceptions.Timeout:
        return f"查詢 {city} 天氣超時，請稍後再試。"
    except requests.exceptions.ConnectionError:
        return f"無法連接到天氣服務，請檢查網路連線。"
    except (KeyError, ValueError):
        return f"找不到 {city} 的天氣資料，請試試其他城市名稱。"
    except Exception as e:
        return f"查詢天氣時出錯：{str(e)}"

from duckduckgo_search import DDGS

def bot_get_ddg_search(keyword):
    """
    Uses duckduckgo_search library with strict regional settings and short timeout.
    """
    try:
        search_query = f"{keyword} 中文"
        with DDGS() as ddgs:
            # Short timelimit to speed up
            results = ddgs.text(search_query, region='tw-tzh', safesearch='moderate', timelimit='m', max_results=3)
            if results:
                content = " ".join([r['body'] for r in results if 'body' in r])
                if content:
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
        # Added strict 2s timeout
        response = requests.get(url, headers=headers, timeout=2)
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
    Scrapes Wikipedia for a given keyword with a short timeout.
    """
    if not keyword: return None
        
    url = f"https://zh.wikipedia.org/wiki/{keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # Added strict 2s timeout
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code != 200: return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div: return None

        paragraphs = content_div.find_all('p')
        content = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 10:
                content += text + " "
                if len(content) > 300: break
                    
        if not content or "可以指：" in content or "可以指:" in content:
            return None
            
        return to_traditional(bot_clean_text(content))
    except:
        return None

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
        model = 'gemini-flash-latest'  # 使用最穩定的最新 Flash 模型
        
        # Create a prompt to enhance the response
        prompt = f"""你是一个可愛且專業的機器人助手、名字叫通通。你適用繁體中文回答，推謝簡潔、清的表達，回答時常常加入有趣的表情符號。

使用者問題：{user_input}

搜尋到的資訊：{search_result if search_result else "無"}

請用通通的身份回答，不超過200字："""
        
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
    Directly asks Gemini AI, with local fallbacks and a final web search backup.
    """
    # 1. Quick Local Fallback for common topics
    local_responses = {
        "你好": "你好呀！我是通通，今天有什麼我可以幫你的嗎？😊",
        "你是誰": "我是通通！您的可愛 AI 助手。🤖",
        "心情": "通通今天心情超級好喔！因為可以跟你聊天！✨",
        "推薦": "通通覺得台式料理都很棒喔！像是滷肉飯、牛肉麵或是珍珠奶茶，你喜歡哪一種呢？😋",
        "好吃": "說到好吃的，通通口水都要流下來了！台灣的小吃世界第一，去夜市逛逛準沒錯！",
        "勵志": "成功不是終點，失敗也不是終結，唯有前進的勇氣才是永恆。加油！💪"
    }
    
    for key, val in local_responses.items():
        if key in user_input:
            return val

    # 2. Try Gemini AI
    try:
        import google.genai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "請在這裡貼上您的API_KEY":
            return "抱歉，我的大腦模組還沒裝好金鑰。你可以先問我時間或天氣喔！"
        
        client = genai.Client(api_key=api_key)
        model = 'gemini-1.5-flash' 
        prompt = f"你是一個名叫「通通」的可愛機器人。回答要簡潔、有趣、充滿表情符號。使用者問：{user_input}"
        
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            if response.text: return response.text.strip()
        except:
            # If 1.5 fails, try flash-latest
            response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
            if response.text: return response.text.strip()
            
    except Exception as e:
        print(f"Gemini API error, falling back to web: {e}")

    # 3. Final Fallback: If AI fails, try one last quick web search
    search_res = bot_get_google_search(user_input)
    if search_res and len(search_res) > 20:
        return search_res

    return "通通現在腦袋有點打結... 你可以試著問我「台北天氣」或「現在幾點」，這些我最拿手了！"
