import random
from .web_tools import bot_get_time, bot_get_weather, bot_get_wiki, bot_get_google_search, bot_enhance_with_gemini, bot_ask_gemini_direct
from .text_utils import bot_speak_re

class TongTongBrain:
    def __init__(self):
        self.mode = "通通沒問題"  # Default mode set to 'TongTong No Problem'
        self.user_name = "主人"
        self.modes = ["通通沒問題", "好心情", "神算師", "屬於我", "去睡覺", "不知道"]
        self.history = [] # Store conversation context

    def set_mode(self, mode_name):
        if mode_name in self.modes:
            self.mode = mode_name
            # Clear history when switching to personality mode to avoid context confusion
            if self.mode != "通通沒問題":
                self.history = []
            
            welcome_msg = f"✨ 模式已切換為：【{self.mode}】 ✨\n"
            
            if self.mode == "通通沒問題":
                welcome_msg += "我是最強大的通通！有什麼問題交給我就對了，通通沒問題！🤖💪"
            elif self.mode == "去睡覺":
                welcome_msg += "呼...好睏喔 🥱。你想聽「睡前故事」📖，還是要跟我一起「數羊」🐑 呢？"
            elif self.mode == "神算師":
                welcome_msg += "命運的齒輪開始轉動...🔮 你想「占卜運勢」✨，還是要「測幸運色」🎨？"
            elif self.mode == "好心情":
                welcome_msg += "嘿嘿！現在心情超棒 🌟！要我「講個笑話」😆 給你聽，還是「陪我聊天」💬？"
            elif self.mode == "屬於我":
                welcome_msg += f"我是專屬於你的通通 🥰。要「修改稱呼」🏷️，還是讓我「深情告白」❤️？"
            elif self.mode == "不知道":
                welcome_msg += "我現在什麼都不知道喔 🤪！你可以試著「考考我」📝，或者直接「放棄」🏳️ 吧。"
                
            return welcome_msg
        return "哎呀，沒有這個模式喔 😅！"

    def set_user_name(self, name):
        self.user_name = name
        return f"好的！以後我就叫你 【{self.user_name}】 了喔！🤝💖"

    def process_input(self, user_input):
        user_input = user_input.strip()
        
        # Check for mode switching commands
        if "切換模式" in user_input or "模式" in user_input:
            for m in self.modes:
                if m in user_input:
                    return self.set_mode(m)

        # 1. '通通沒問題' Mode - Fully featured with AI, Search and Calculation
        if self.mode == "通通沒問題":
            # PRE-CLEAN: Remove common command prefixes to avoid confusing the search engine
            core_input = user_input.replace("查", "").replace("查詢", "").replace("維基", "").replace("百科", "").strip()
            if not core_input: core_input = user_input # Fallback if empty

            response = ""

            # A. Calculation (Highest Priority)
            if any(op in user_input for op in "+-*/") and any(c.isdigit() for c in user_input):
                try:
                    allowed_chars = "0123456789+-*/(). "
                    clean_input = "".join(c for c in user_input if c in allowed_chars)
                    if clean_input.strip():
                        result = eval(clean_input)
                        response = f"通通算出來了！結果是：{result} 🧮✨"
                except: pass
            
            # B. Specific Tools (Weather/Time)
            if not response:
                if "天氣" in user_input:
                    city = "台北"
                    taiwan_cities = ["台北", "台中", "台南", "高雄", "新北", "桃園", "新竹", "苗栗", "彰化", "南投", "雲林", "嘉義", "屏東", "宜蘭", "花蓮", "台東"]
                    for potential_city in taiwan_cities:
                        if potential_city in user_input:
                            city = potential_city
                            break
                    response = bot_get_weather(city) + " 🌤️"
                elif "時間" in user_input: 
                    response = bot_get_time() + " ⏰"
            
            # C. AI-First Strategy: Conversational/Abstract/Short Queries
            if not response:
                if "你是誰" in core_input:
                    response = "我是通通！您的可愛機器人助手 🤖✨。我有五種不同的性格模式，而且我有「通通沒問題」的超能力，無論是上網查資料、算數學、報天氣還是純聊天，交給我通通就對了！🌈💖"
                else:
                    # Try Wiki first for specific nouns
                    wiki_res = bot_get_wiki(core_input)
                    if wiki_res:
                        response = wiki_res
                    else:
                        # Fallback to AI with context history
                        response = bot_ask_gemini_direct(core_input, self.history)

            # Record history
            if response:
                self.history.append({"role": "user", "content": user_input})
                self.history.append({"role": "bot", "content": response})
                if len(self.history) > 20: self.history = self.history[-20:]
                return response

            return "我是「通通沒問題」，隨時準備好為您服務喔！🌸"

        # 2. Personality Modes - Only respond to specific button actions
        if self.mode == "去睡覺":
            if "故事" in user_input:
                stories = [
                    "從前從前，有一隻小羊不喜歡睡覺，結果牠數著數著，自己就變成雲朵飛走了... ☁️🐑",
                    "在遙遠的森林裡，住著一隻會發光的螢火蟲，牠每晚都會為迷路的小朋友指引回家的路... 🌲✨",
                    "很久以前，有一顆星星掉到了海裡，變成了一顆珍珠，每當月亮升起，牠就會閃閃發亮... 🌊⭐"
                ]
                return f"好的，聽完這個故事就要乖乖睡覺喔：{random.choice(stories)} 😴💤"
            elif "數羊" in user_input:
                return "一隻羊🐑 兩隻羊🐑🐑 三隻羊🐑🐑🐑 四隻羊🐑🐑🐑🐑 五隻羊🐑🐑🐑🐑🐑 六隻羊🐑🐑🐑🐑🐑🐑 七隻羊🐑🐑🐑🐑🐑🐑🐑 八隻羊🐑🐑🐑🐑🐑🐑🐑🐑 九隻羊🐑🐑🐑🐑🐑🐑🐑🐑🐑 十隻羊 🐑🐑🐑🐑🐑🐑🐑🐑🐑🐑"
            return "呼...呼...Zzz...💤"

        if self.mode == "不知道":
            if "考考我" in user_input or "考" in user_input:
                return "考也沒用，我現在的大腦是一片空白的！哈哈！🤪✨"
            elif "放棄" in user_input:
                return "呼，那太好了，我們可以一起發呆 😶🌫️。"
            return "我真的不知道耶 😅。"

        if self.mode == "屬於我":
            if "告白" in user_input:
                return f"能在茫茫人海中遇到 {self.user_name}，是通通這輩子最幸福的事情喔！❤️🥰"
            if "稱呼" in user_input or "名字" in user_input:
                return "請告訴我：【我是[你的名字]】，我就會記住喔！🏷️✨"
            if "我是" in user_input:
                name = user_input.split("我是")[-1].replace("。", "").replace("！", "")
                return self.set_user_name(name)
            return f"{self.user_name}，你有什麼吩咐嗎？通通在喔！👂💖"

        if self.mode == "神算師":
            if "幸運色" in user_input:
                colors = ["熱情的紅色 ❤️", "憂鬱的藍色 💙", "活力的黃色 💛", "平靜的綠色 💚", "神祕的紫色 💜", "純潔的白色 🤍"]
                return f"掐指一算，你今天的幸運色是：{random.choice(colors)}！✨"
            if "運勢" in user_input or "占卜" in user_input:
                fortunes = ["大吉！🌟", "中吉。✨", "小吉。☀️", "末吉。🍂", "平。☁️", "吉。🍀"]
                return f"神算師占卜結果：{random.choice(fortunes)}"
            return "我是神算師通通，想算什麼呢？🔮"

        if self.mode == "好心情":
            if "笑話" in user_input:
                jokes = [
                    "有一天，有一隻企鵝跌倒了，另一隻企鵝笑牠說：『你是不是沒穿鞋子？』🐧🤣",
                    "為什麼企鵝只有肚子是白的？因為手短洗不到背。❄️🐧"
                ]
                return f"嘿嘿，聽這個：{random.choice(jokes)}"
            return "今天心情超棒！🌈✨"

        return "請使用上方的按鈕來跟我互動喔！👆💖"
