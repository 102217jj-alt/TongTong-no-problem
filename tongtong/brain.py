import random
from .web_tools import bot_get_time, bot_get_weather, bot_get_wiki, bot_get_google_search, bot_enhance_with_gemini, bot_ask_gemini_direct
from .text_utils import bot_speak_re

class TongTongBrain:
    def __init__(self):
        self.mode = "原本的通通"  # Default mode set to 'Original'
        self.user_name = "主人"
        self.modes = ["原本的通通", "好心情", "神算師", "屬於我", "去睡覺", "不知道"]

    def set_mode(self, mode_name):
        if mode_name in self.modes:
            self.mode = mode_name
            welcome_msg = f"模式已切換為：{self.mode}。\n"
            
            if self.mode == "原本的通通":
                welcome_msg += "我是最專業的通通！你可以直接問我任何問題，我會幫你上網查資料喔。"
            elif self.mode == "去睡覺":
                welcome_msg += "呼...好睏喔。你想聽「睡前故事」，還是要跟我一起「數羊」呢？"
            elif self.mode == "神算師":
                welcome_msg += "命運的齒輪開始轉動...你想「占卜運勢」，還是要「測幸運色」？"
            elif self.mode == "好心情":
                welcome_msg += "嘿嘿！現在心情超棒！要我「講個笑話」給你聽，還是「陪我聊天」？"
            elif self.mode == "屬於我":
                welcome_msg += f"我是專屬於你的通通。要「修改稱呼」，還是讓我「深情告白」？"
            elif self.mode == "不知道":
                welcome_msg += "我現在什麼都不知道喔！你可以試著「考考我」，或者直接「放棄」吧。"
                
            return welcome_msg
        return "沒有這個模式喔！"

    def set_user_name(self, name):
        self.user_name = name
        return f"好的，以後我就叫你 {self.user_name} 了！"

    def process_input(self, user_input):
        user_input = user_input.strip()
        
        # Check for mode switching commands
        if "切換模式" in user_input or "模式" in user_input:
            for m in self.modes:
                if m in user_input:
                    return self.set_mode(m)

        # 1. '原本的通通' Mode - Fully featured with Search and Calculation
        if self.mode == "原本的通通":
            # A. Calculation
            if any(op in user_input for op in "+-*/") and any(c.isdigit() for c in user_input):
                try:
                    allowed_chars = "0123456789+-*/(). "
                    clean_input = "".join(c for c in user_input if c in allowed_chars)
                    if clean_input.strip():
                        result = eval(clean_input)
                        return f"專業通通算出來了，結果是：{result}"
                except: pass
            
            # B. Specific Tools
            if "天氣" in user_input: return bot_get_weather()
            if "時間" in user_input: return bot_get_time()
            
            # C. Basic Greetings (Optional, to prevent searching "你好")
            greetings = ["你好", "嗨", "哈囉", "hello", "hi"]
            if any(g == user_input.lower() for g in greetings):
                return "你好，我是原始版本的通通，有什麼想查詢的知識嗎？可以直接輸入關鍵字喔！"
            
            # D. Automatic Wiki Search (Default) with Google Fallback and Gemini Direct
            keyword = user_input.replace("查", "").replace("維基", "").replace("百科", "").strip()
            if keyword:
                # Try Wiki first
                wiki_res = bot_get_wiki(keyword)
                if wiki_res and "找不到" not in wiki_res and "沒辦法讀取" not in wiki_res:
                    # Enhance with Gemini for better quality
                    enhanced = bot_enhance_with_gemini(user_input, wiki_res)
                    return enhanced
                
                # Fallback to general web search
                search_res = bot_get_google_search(keyword)
                
                # Check if search failed (returns error message)
                if "暫時沒辦法直接讀取內容" in search_res or "上網找資料時發生" in search_res:
                    # Use Gemini to answer directly when search fails
                    gemini_res = bot_ask_gemini_direct(user_input)
                    return gemini_res
                else:
                    # Enhance successful search results with Gemini
                    enhanced = bot_enhance_with_gemini(user_input, search_res)
                    return enhanced

            return "我是原本的通通，隨時準備好為您服務。"

        # 2. Personality Modes - Only respond to specific button actions
        if self.mode == "去睡覺":
            if "故事" in user_input:
                stories = [
                    "從前從前，有一隻小羊不喜歡睡覺，結果牠數著數著，自己就變成雲朵飛走了...",
                    "在遙遠的森林裡，住著一隻會發光的螢火蟲，牠每晚都會為迷路的小朋友指引回家的路...",
                    "很久以前，有一顆星星掉到了海裡，變成了一顆珍珠，每當月亮升起，牠就會閃閃發亮..."
                ]
                return f"好的，聽完這個故事就要乖乖睡覺喔：{random.choice(stories)}"
            elif "數羊" in user_input:
                return "一隻羊...兩隻羊...三隻羊...（通通的聲音越來越小）...四隻羊...Zzz..."
            return "呼...呼...Zzz..."

        if self.mode == "不知道":
            if "考考我" in user_input or "考" in user_input:
                return "考也沒用，我現在的大腦是一片空白的！哈哈！"
            elif "放棄" in user_input:
                return "呼，那太好了，我們可以一起發呆。"
            return "我不知道耶。"

        if self.mode == "屬於我":
            if "告白" in user_input:
                return f"能在茫茫人海中遇到 {self.user_name}，是通通這輩子最幸福的事情喔！❤️"
            if "稱呼" in user_input or "名字" in user_input:
                return "請告訴我：我是[你的名字]，我就會記住喔！"
            if "我是" in user_input:
                name = user_input.split("我是")[-1].replace("。", "").replace("！", "")
                return self.set_user_name(name)
            return f"{self.user_name}，你有什麼吩咐嗎？"

        if self.mode == "神算師":
            if "幸運色" in user_input:
                colors = ["熱情的紅色", "憂鬱的藍色", "活力的黃色", "平靜的綠色", "神祕的紫色", "純潔的白色"]
                return f"掐指一算，你今天的幸運色是：{random.choice(colors)}！"
            if "運勢" in user_input or "占卜" in user_input:
                fortunes = ["大吉！", "中吉。", "小吉。", "末吉。", "平。", "吉。"]
                return f"神算師占卜結果：{random.choice(fortunes)}"
            return "我是神算師通通，想算什麼？"

        if self.mode == "好心情":
            if "笑話" in user_input:
                jokes = [
                    "有一天，有一隻企鵝跌倒了，另一隻企鵝笑牠說：『你是不是沒穿鞋子？』",
                    "為什麼企鵝只有肚子是白的？因為手短洗不到背。"
                ]
                return f"嘿嘿，聽這個：{random.choice(jokes)}"
            return "今天心情超棒！"

        return "請使用上方的按鈕來跟我互動喔！"
