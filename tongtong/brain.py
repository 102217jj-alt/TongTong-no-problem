import random
from .web_tools import bot_get_time, bot_get_weather, bot_get_wiki, bot_get_google_search, bot_enhance_with_gemini, bot_ask_gemini_direct
from .text_utils import bot_speak_re

class TongTongBrain:
    def __init__(self):
        self.mode = "通通沒問題"  # Default mode set to 'TongTong No Problem'
        self.user_name = "主人"
        self.modes = ["通通沒問題", "好心情", "神算師", "屬於我", "去睡覺", "不知道"]
        self.history = [] # Store conversation context

    def add_fortune_disclaimer(self, text):
        return f"{text}\n\n※ 以上僅供娛樂參考，請理性看待喔！"

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
                welcome_msg += self.add_fortune_disclaimer("命運的齒輪開始轉動...🔮 你想「占卜運勢」✨、「測幸運色」🎨、「算幸運數字」🎲、「問吉時」⏰、「財運」💰、「事業運」💼、「愛情運」💖，還是「今日建議」🌈 呢？")
            elif self.mode == "好心情":
                welcome_msg += "嘿嘿！現在心情超棒 🌟！要我「講個笑話」😆、「唱首歌」🎵、「給你鼓勵」💪、「變個魔術」🪄、「猜拳」✊，還是「擊掌」🤝 呢？"
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
        
        # Hidden command for game results or direct speech
        if user_input.startswith("[RESULT]"):
            return user_input.replace("[RESULT]", "").strip()

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
            
            # Check if user explicitly requested search (with "查" or "查詢" prefix)
            is_explicit_search = any(prefix in user_input for prefix in ["查", "查詢", "維基", "百科"])

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
            
            # C. Search-First for explicit search queries (with "查" prefix), then polish with AI
            if not response and is_explicit_search:
                search_res = bot_get_google_search(core_input)
                if search_res and len(search_res) > 30:
                    # Polish search result with AI for better presentation
                    response = bot_enhance_with_gemini(core_input, search_res)
                else:
                    # If search fails, try AI as backup
                    response = bot_ask_gemini_direct(core_input, self.history)
            
            # D. AI-First for conversational queries (without "查" prefix) for better answer quality
            if not response:
                if "你是誰" in core_input:
                    response = "我是通通！您的可愛機器人助手 🤖✨。我有五種不同的性格模式，而且我有「通通沒問題」的超能力，無論是上網查資料、算數學、報天氣還是純聊天，交給我通通就對了！🌈💖"
                else:
                    # Try AI first for better answer quality
                    response = bot_ask_gemini_direct(core_input, self.history)
                    
                    # If AI fails with fallback message, try web search as backup
                    if response and "腦袋轉得有點慢" in response:
                        search_res = bot_get_google_search(core_input)
                        if search_res and len(search_res) > 30:
                            response = search_res

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
                return self.add_fortune_disclaimer(f"掐指一算，你今天的幸運色是：{random.choice(colors)}！✨")
            if "幸運數字" in user_input or "幸運號碼" in user_input or "數字" in user_input:
                lucky_numbers = random.sample(range(1, 50), 5)
                return self.add_fortune_disclaimer(f"神諭降臨！你今天的幸運數字是：{', '.join(map(str, lucky_numbers))} 🎲✨")
            if "吉時" in user_input or "幸運時間" in user_input:
                lucky_times = ["上午 9:00 - 10:00", "中午 12:00 - 13:00", "下午 3:00 - 4:00", "晚上 7:00 - 8:00", "晚上 9:00 - 10:00"]
                return self.add_fortune_disclaimer(f"我看見了時之河流... 你的吉時是：{random.choice(lucky_times)} ⏰🔮")
            if "財運" in user_input:
                fortunes = [
                    "今天的財運像慢慢升起的太陽，穩穩累積就會看見成果。🌞💰",
                    "很適合做出對自己有幫助的小決定，錢包會因為你的細心而更安心。🪙✨",
                    "有機會遇到意料之外的小驚喜，保持開放心情，收穫會比你想像更多。🌟💵",
                    "今天的財氣偏向穩健成長，越重視規劃，越容易把好運留住。📈💚",
                    "如果你正在整理財務，今天會是很順手的一天，做越多整理越有成就感。📒✨",
                    "今天很適合檢查自己的收支，越有條理，財運就越容易越來越穩。🧾🌈",
                    "小小的節制會帶來大大的安心，今天是讓財務慢慢變漂亮的好日子。💎📊"
                ]
                return self.add_fortune_disclaimer(f"財運卦象：{random.choice(fortunes)}")
            if "事業運" in user_input or "工作運" in user_input:
                fortunes = [
                    "今天很適合把手上的事情一件件完成，你的效率會比自己想像的更好。💼✨",
                    "靈感和行動力都在線，適合開始一個你原本想很久的計畫。🚀📈",
                    "工作上容易出現願意幫你的人，主動說明需求，進展會更順。🤝🌟",
                    "這是適合穩穩發光的一天，先完成再優化，你會越做越有信心。✨💪",
                    "今天的工作運很適合突破卡點，只要踏出第一步，後面就會慢慢打開。🔓🌈",
                    "你今天的專注力很不錯，適合處理需要耐心的任務，越做越順手。🎯💼",
                    "很容易在工作中找到新的節奏，今天只要穩穩向前，就會有好結果。🛤️✨"
                ]
                return self.add_fortune_disclaimer(f"事業運卦象：{random.choice(fortunes)}")
            if "愛情運" in user_input or "戀愛運" in user_input:
                fortunes = [
                    "今天的愛情運很溫柔，真誠表達自己就會散發很迷人的光。💘✨",
                    "適合傳一個貼心訊息，簡單的關心就能讓彼此更靠近。🌷💕",
                    "感情氛圍偏甜，只要多一點理解與耐心，關係就會更舒服。💞🌈",
                    "桃花能量正在慢慢靠近，保持自然和笑容，魅力會更明顯。🌸😊",
                    "如果你正在等回應，今天很適合先照顧好自己的心情，好的互動也會跟著來。💖🌟",
                    "今天適合多一點真誠與溫暖，輕輕的一句話也可能讓心靠得更近。💗🌙",
                    "關係的美好正在慢慢累積，今天是讓彼此更懂彼此的好時機。🤝💐"
                ]
                return self.add_fortune_disclaimer(f"愛情運卦象：{random.choice(fortunes)}")
            if "運勢" in user_input or "占卜" in user_input:
                fortunes = [
                    "大吉！🌟 今天很適合行動，越主動越有收穫。",
                    "中吉。✨ 事情會順順推進，耐心一點更漂亮。",
                    "小吉。☀️ 先做好眼前的小事，運氣會慢慢跟上。",
                    "末吉。🍂 先別硬衝，整理思緒後再出手更穩。",
                    "平。☁️ 今天維持節奏就好，別急著下結論。",
                    "吉。🍀 有機會遇到小驚喜，記得留意細節。"
                ]
                return self.add_fortune_disclaimer(f"神算師占卜結果：{random.choice(fortunes)}")
            if "今日建議" in user_input or "建議" in user_input or "今天適合" in user_input:
                advices = [
                    "今天是充滿好運的一天，勇敢開始就會有漂亮的收穫。🌟",
                    "你的節奏會越來越順，保持微笑，事情會朝好的方向前進。✨",
                    "很適合帶著期待出發，今天的小努力都會慢慢變成大成果。🌈",
                    "只要照著自己的步調前進，驚喜和好消息就會悄悄靠近。💖"
                ]
                return self.add_fortune_disclaimer(f"神算師建議：{random.choice(advices)}")
            return self.add_fortune_disclaimer("我是神算師通通，想算什麼呢？🔮")

        if self.mode == "好心情":
            if "笑話" in user_input:
                jokes = [
                    "有一天，有一隻企鵝跌倒了，另一隻企鵝笑牠說：『你是不是沒穿鞋子？』🐧🤣",
                    "為什麼企鵝只有肚子是白的？因為手短洗不到背。❄️🐧",
                    "小明跟媽媽說：『我不想去上學！』媽媽說：『不行，你必須去，因為你已經是校長了。』🏫😆",
                    "為什麼電腦很冷？因為它有很多視窗（window）。💻❄️",
                    "有一天，小豬去買藥，老闆問：『你要什麼藥？』小豬說：『我要豬古力（巧克力）。』🍫🐷",
                    "咖啡跟可樂誰比較長壽？答案是咖啡，因為咖啡可以續杯（續命）。☕️🥤",
                    "為什麼魚不能在陸地上走路？因為牠沒有腳踏實地。🐟💨",
                    "有一天，紅豆跟綠豆吵架，紅豆大罵：『你這個綠豆！』綠豆回罵：『你才紅豆咧！』結果他們都變成了大紅大紫。🫘✨",
                    "螃蟹出門為什麼不看紅綠燈？因為牠橫行霸道。🦀🚦",
                    "為什麼吸血鬼不吃大蒜？因為那是他的大『蒜』命。🧛‍♂️🧄",
                    "有一天，麵包走在路上覺得肚子餓了，於是牠就把自己吃了。🍞😋",
                    "為什麼衛生紙不能過馬路？因為它會被捲走。🧻🚗",
                    "為什麼螞蟻不去看醫生？因為牠們有螞蟻（免疫）系統。🐜💉",
                    "有一天，皮卡丘走路不小心跌倒了，變成了什麼？變成了皮卡丘（皮卡、揪一聲）。⚡️🥴",
                    "為什麼海是藍色的？因為魚一直在裡面吐泡泡（Blue Blue Blue）。🐟🌊",
                    "有一天，綠豆摔倒了，變成了什麼？變成了紅豆，因為它流血了。🫘🩸",
                    "為什麼手機不能去健身房？因為它會變『機』肉男。📱💪",
                    "有一天，大福和饅頭吵架，結果饅頭輸了，因為大福很有『料』。🥯✨",
                    "為什麼香蕉不用防曬？因為它會自己脫皮。🍌☀️",
                    "有一天，有一隻老虎去抓兔子，結果沒抓到，因為老虎說：『我還沒準老虎（備好）呢！』🐯🐰",
                    "為什麼月亮不跟星星玩？因為星星會『眨』眼，月亮會『臉』紅。🌙⭐"
                ]
                return f"嘿嘿，聽這個：{random.choice(jokes)}"
            
            if "唱首歌" in user_input:
                songs = [
                    "拉~拉~拉~🎶 我是快樂的小機器人~🤖 每天都要開開心心~🌈",
                    "兩隻老虎~🐯 兩隻老虎~🐯 跑得快~💨 跑得快~💨",
                    "小星星~✨ 亮晶晶~⭐ 滿天都是小眼睛~👁️👁️",
                    "通通沒問題~💪 通通沒問題~💪 我是最棒的通通~🏆✨"
                ]
                return f"好喔！通通獻醜了：{random.choice(songs)}"
                
            if "給我鼓勵" in user_input:
                cheers = [
                    "你是最棒的！通通永遠支持你！加油加油！💪💖",
                    "別忘了，你比你想像中更勇敢，也比你表現出來的更強大喔！🌟",
                    "通通送你一個大大的擁抱！🤗 今天的你也很努力呢！✨",
                    "不管發生什麼事，通通都會陪在你身邊，為你加油打氣！🤖💕"
                ]
                return random.choice(cheers)

                
            if "變個魔術" in user_input:
                magics = [
                    "看我的厲害！✨ 嗶嗶—— 🎩 把你的煩惱都變不見了！🪄🌈",
                    "注意看喔！👀 手中有一顆紅豆... 🫘 變！現在變成一朵花送給你！🌹✨",
                    "通通現在要表演讀心術... 🧠 我猜你現在一定覺得通通很可愛對不對！😜💖"
                ]
                return random.choice(magics)
                
            if "猜拳" in user_input:
                choices = ["剪刀 ✌️", "石頭 ✊", "布 🖐️"]
                bot_choice = random.choice(choices)
                return f"好啊！來挑戰吧！通通出：{bot_choice}！你出什麼呢？😜✨"
                
            if "擊掌" in user_input:
                return "啪！✋✨ 合作愉快！我們是最棒的夥伴喔！🤝💖"

            return "今天心情超棒！🌈✨"

        return "請使用上方的按鈕來跟我互動喔！👆💖"
