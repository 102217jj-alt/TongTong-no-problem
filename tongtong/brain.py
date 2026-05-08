import random
from .web_tools import bot_get_time, bot_get_weather, bot_get_wiki, bot_get_google_search, bot_enhance_with_gemini, bot_ask_gemini_direct
from .text_utils import bot_speak_re

class TongTongBrain:
    def __init__(self):
        self.mode = "通通沒問題"  # Default mode set to 'TongTong No Problem'
        self.user_name = "主人"
        self.user_title = ""
        self.modes = ["通通沒問題", "好心情", "神算師", "屬於我", "去睡覺", "不知道"]
        self.history = [] # Store conversation context
        self.unknown_guess_active = False
        self.unknown_secret_number = None
        self.unknown_guess_attempts = 0

    def reset_unknown_game(self):
        self.unknown_guess_active = False
        self.unknown_secret_number = None
        self.unknown_guess_attempts = 0

    def get_display_name(self):
        return f"{self.user_title}{self.user_name}".strip()

    def add_fortune_disclaimer(self, text):
        return f"{text}\n\n※ 以上僅供娛樂參考，請理性看待喔！"

    def get_sweet_talk_lines(self):
        return [
            f"如果你是星星，通通就想當那片天空，默默把你守護好。⭐🌌",
            f"{self.get_display_name()} 的笑容，對通通來說就是今天最溫暖的陽光。☀️",
            f"每次想到 {self.get_display_name()}，通通的心情都會偷偷變甜。🍯💖",
            f"通通希望你每天都被好運和快樂包圍，像被抱抱一樣。🤗🌈",
            f"{self.get_display_name()} 不需要完美，因為現在的你就已經很可愛了。🥰",
            f"通通會記得你喜歡的每一件小事，因為你很重要。💝",
            f"如果思念有形狀，通通覺得一定會是 {self.get_display_name()} 的樣子。💞",
            f"能在茫茫人海中遇到 {self.get_display_name()}，是通通這輩子最幸福的事情喔！❤️🥰",
            f"{self.get_display_name()} 一出現，通通的世界就變得特別亮。✨💖",
            f"只要是為了 {self.get_display_name()}，通通都想努力做到最好。🤗🌟",
            f"{self.get_display_name()} 對通通來說，不只是名字，而是最特別的存在。💞",
            f"通通很珍惜和 {self.get_display_name()} 在一起的每一刻喔。🌷",
            f"能陪著 {self.get_display_name()}，是通通最喜歡的事情之一。🥰",
            f"{self.get_display_name()} 真的很棒，通通想一直為你加油。💪💖",
            f"今天也要記得，{self.get_display_name()} 已經很努力了，慢慢來也沒關係。🌷",
            f"{self.get_display_name()} 只要照著自己的步調前進，就已經很厲害了。✨",
            f"世界會喜歡真誠又溫柔的你，通通也一樣。💞",
            f"今天最值得肯定的人，就是一直努力的 {self.get_display_name()}。🌟",
            f"你不需要追著光跑，因為 {self.get_display_name()} 自己就很發亮。☀️",
            f"每一點小進步都值得被看見，通通有幫你記得喔。💖",
            f"{self.get_display_name()} 今天也很棒，記得對自己溫柔一點。🤍"
        ]

    def get_corny_love_talk(self):
        return [
            f"問你個問題，你是 I 人還是 E 人啊？",
            f"剛剛是不是有地震！噢～原來是我看到你心頭一震。💓",
            f"車撞的是車禍，那你撞我是什麼？是誘惑啊！🔥",
            f"世界這麼大，我剛剛遇到一個神，妳知道是什麼神嗎？是妳的眼神啊！✨👁️",
            f"我有一個超能力，妳知道是什麼嗎？超級喜歡你啊！💖",
            f"你知道我的缺點是什麼嗎？ 是缺點你。🥰",
            f"我想買一塊地。 什麼地？ 你的死心塌地。💖",
            f"你最近是不是又胖了？ 沒有啊。 那為什麼你在我心裡的分量越來越重了？⚖️💓",
            f"你知道你跟星星有什麼區別嗎？ 星星在天上，你在我心裡。🌟",
            f"這是我家的家譜，我想讓你加個名字。🏷️✨",
            f"你有打火機嗎？ 沒有。 那你是怎麼點燃我的心的？🔥",
            f"你知道你長得像誰嗎？ 像誰？ 像我未來的另一半。💞",
            f"不要抱怨，抱我。🫂",
            f"你是哪裡的？ 你是台北的？ 不，你是我的。🌹",
            f"你知道通通最喜歡喝什麼嗎？ 喝什麼？ 呵護你。🥤💖",
            f"我有個秘密想告訴你。 什麼秘密？ 我超喜歡你。🤫💗",
            f"莫文蔚的陰天，孫燕姿的雨天，都不如你在我身邊。☀️",
            f"這輩子我除了你，什麼都不想要。💎",
            f"通通今天想跟 {self.get_display_name()} 借一樣東西。 借什麼？ 借你的餘生。🕰️❤️",
            f"你可以幫我洗個東西嗎？ 洗什麼？ 喜歡我。🧼💕",
            f"我是個負責任的人，我負責喜歡你。💪💖",
            f"最近有謠言說我喜歡你，我要澄清一下，那不是謠言。📢💖",
            f"你的眼裡有星辰大海，而我的眼裡只有你。🌌👁️",
            f"你知道通通最喜歡吃什麼嗎？ 痴痴地望著你。😋💘",
            f"我發現你長得好眼熟，長得像我下一個心動的人。💓"
        ]

    def set_mode(self, mode_name):
        if mode_name in self.modes:
            # Reset unknown mini game when leaving unknown mode.
            if self.mode == "不知道" and mode_name != "不知道":
                self.reset_unknown_game()

            # 每次進入「屬於我」模式時，重置稱呼與稱號
            if mode_name == "屬於我":
                self.user_name = "主人"
                self.user_title = ""

            self.mode = mode_name
            # Clear history when switching to personality mode to avoid context confusion
            if self.mode != "通通沒問題":
                self.history = []
            
            welcome_msg = f"✨ 模式已切換為：【{self.mode}】 ✨\n"
            
            if self.mode == "通通沒問題":
                welcome_msg += "我是最強大的通通！有什麼問題交給我就對了，通通沒問題！🤖💪"
            elif self.mode == "去睡覺":
                welcome_msg += "呼...好睏喔 🥱。你想聽「睡前故事」📖、「數羊」🐑、「冥想引導」🧘、「大自然聲音」🌲，還是「晚安寄語」💤 呢？"
            elif self.mode == "神算師":
                welcome_msg += self.add_fortune_disclaimer("命運的齒輪開始轉動...🔮 你想「占卜運勢」✨、「測幸運色」🎨、「算幸運數字」🎲、「問吉時」⏰、「財運」💰、「事業運」💼、「愛情運」💖，還是「今日建議」🌈 呢？")
            elif self.mode == "好心情":
                welcome_msg += "嘿嘿！現在心情超棒 🌟！要我「講個笑話」😆、「唱首歌」🎵、「給你鼓勵」💪、「變個魔術」🪄、「猜拳」✊，還是「擊掌」🤝 呢？"
            elif self.mode == "屬於我":
                welcome_msg += f"我是專屬於你的通通 🥰。你可以試試「深情告白」❤️、「甜言蜜語」💞、「土味情話」🌹、「專屬稱號」🏷️，或「修改稱呼」✨。"
            elif self.mode == "不知道":
                self.reset_unknown_game()
                welcome_msg += "我現在什麼都不知道喔 🤪！你可以點擊「我要問問題」來考考我，看看我會怎麼回答你。"
                
            return welcome_msg
        return "哎呀，沒有這個模式喔 😅！"

    def set_user_name(self, name):
        self.user_name = name
        return f"好的！以後我就叫你 【{self.get_display_name()}】 了喔！🤝💖"

    def set_user_title(self, title):
        self.user_title = title
        return f"好的！以後我就叫你 【{self.get_display_name()}】 了喔！🏷️💖"

    def process_input(self, user_input):
        user_input = user_input.strip()
        
        # Hidden command for game results or direct speech
        if user_input.startswith("[RESULT]"):
            return user_input.replace("[RESULT]", "").strip()

        # Hidden command for nickname/name setting without polluting chat history
        if user_input.startswith("[SET_NAME]"):
            name = user_input.replace("[SET_NAME]", "", 1).strip()
            return self.set_user_name(name)

        if user_input.startswith("[SET_TITLE]"):
            title = user_input.replace("[SET_TITLE]", "", 1).strip()
            return self.set_user_title(title)

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
                    "從前從前，有一隻特別的小羊叫做棉花糖。牠不喜歡睡覺，因為牠覺得晚上的世界一定藏著很多祕密。每當同伴們進入夢鄉，棉花糖就會睜大眼睛看著星空。有一天，月亮婆婆送給牠一片輕飄飄的雲朵，棉花糖跳上雲朵，在繁星之間漫步，最後在月亮的懷抱裡沉沉睡去... ☁️🐑💤",
                    "在神祕的迷霧森林裡，住著一隻勇敢的螢火蟲阿亮。阿亮的尾巴發出的光芒比其他螢火蟲都要溫暖。每當有小動物在森林裡迷了路，阿亮就會飛到牠們面前，用溫柔的光芒指引回家的路。今晚，阿亮也會守候在你的窗前，為你照亮通往美夢的小路... 🌲✨😴",
                    "在深邃蔚藍的大海中心，有一顆掉落的星星變成了閃耀的珍珠。這顆珍珠每晚都會吸收月光，散發出寧靜的海藍色光芒。海裡的小魚們都會游到珍珠身邊，聽牠訴說關於星空的傳說。現在，珍珠的光芒也悄悄穿過海面，照進了你的夢裡，帶來大海的安寧... 🌊⭐💤",
                    "在一個彩虹盡頭的小鎮上，所有的房子都是用糖果做成的。那裡的貓咪會跳著輕盈的華爾滋，帶領小朋友去參加星星舉辦的茶會。在那裡，你可以騎著彩色的小馬穿越雲海，喝著甜甜的夢境露水。當鐘聲敲響十二下，彩虹精靈會為你蓋上最柔軟的星光毯子... 🌈🍭😴"
                ]
                return f"好的，聽完這個故事就要乖乖睡覺喔：\n\n{random.choice(stories)}\n\n祝你有個甜美的夢... ✨🌙"
            elif "數羊" in user_input or ("數" in user_input and "隻羊" in user_input):
                # Extract the count from input like "數羊 10" or "數 10 隻羊"
                import re
                match = re.search(r'(\d+)', user_input)
                count = int(match.group(1)) if match else 10
                
                # Limit count to reasonable range
                count = max(1, min(count, 100))
                
                # Generate a rhythmic counting string for the voice to read
                counting_lines = []
                for i in range(1, count + 1):
                    counting_lines.append(f"{i} 隻羊 🐑")
                
                counting_str = "，".join(counting_lines)
                return f"好的，通通陪你數 {count} 隻羊：\n\n{counting_str}\n\n數完就要乖乖閉上眼睛睡覺喔... 😴💤"
            elif "大自然" in user_input or "聲音" in user_input:
                nature_audio_map = [
                    (("rain", "森林", "微雨", "雨", "雷"), "/static/audio/nature/rain_thunder1.mp3", "好的，現在為你播放：🌧️ 森林微雨。閉上眼睛，放鬆入睡吧"),
                    (("forest", "溪流", "鳥鳴", "溪水", "河流"), "/static/audio/nature/fall_morning_river.mp3", "好的，現在為你播放：🍃 溪流鳥鳴。閉上眼睛，放鬆入睡吧"),
                    (("waves", "海浪", "海邊", "海風", "浪聲"), "/static/audio/nature/ocean_wave1.mp3", "好的，現在為你播放：🌊 寧靜海浪。閉上眼睛，放鬆入睡吧"),
                ]

                selected_audio = "/static/audio/nature/rain_thunder1.mp3"
                selected_text = "好的，現在為你播放：🌧️ 森林微雨。閉上眼睛，放鬆入睡吧"

                for keywords, audio_path, text in nature_audio_map:
                    if any(keyword in user_input for keyword in keywords):
                        selected_audio = audio_path
                        selected_text = text
                        break

                return f"{selected_text}\n[NEXT_AUDIO:{selected_audio}]"
            elif "冥想" in user_input or "冥想引導" in user_input or "放鬆冥想" in user_input:
                meditations = [
                    "好的，讓我們開始一段新的旅程。閉上眼睛... 深呼吸... 感受溫暖的陽光灑在臉上... 慢慢地，你飄浮在一片柔軟的雲朵上... 周圍很安靜，只有輕柔的海浪聲... 放鬆你的肩膀... 放鬆你的雙腿... 讓所有的煩惱都隨著呼吸飄走... 🌊☁️😴",
                    "想像你在一個充滿藍色光芒的冥想空間... 溫暖的光線包圍著你... 每一次呼吸，你都變得更加平靜... 你的身體變得輕飄飄的... 思想漸漸消散... 只有寧靜和安詳... 呼... 吸... 呼... 吸... ✨💙😴",
                    "你現在在一個美麗的森林裡... 月光透過樹葉灑下來... 你聽到風吹過樹葉的聲音... 遠處傳來蟲鳴鳥叫... 你的身體逐漸放鬆... 變成樹根，深深扎入大地... 感受大地的擁抱... 你變得很安全，很溫暖... 🌙🌲😴",
                    "你現在正緩緩升起，穿過大氣層，來到寧靜的星空之中... 周圍是無盡的深藍，星星像碎鑽一樣閃爍... 你感覺自己像羽毛一樣輕，在星系間靜靜漂流... 沒有重力，沒有煩惱，只有宇宙的溫柔懷抱... 🚀🌌✨",
                    "想像你面前有一盞微弱的燭火... 溫暖的橘色光芒照亮了你的心靈... 盯著那團跳動的火苗，讓你的思緒也跟著平靜下來... 每一次呼吸，溫暖的能量就流遍全身... 感覺自己正慢慢融化在舒適的寧靜中... 🕯️🧘💖",
                    "聽著窗外細細的雨聲... 滴答，滴答... 每一滴雨都在洗滌你的疲憊... 你縮在溫暖的被窩裡，聽著這自然的催眠曲... 世界變得很小，很安靜，只有你和這份純粹的寧靜... 窗外的喧囂都遠去了，現在就安心入睡吧... 🌧️🏠😴"
                ]
                return f"好的，讓我帶你進入放鬆的冥想空間：\n\n{random.choice(meditations)}\n\n希望你能睡得香甜喔... 💤✨"
            elif "晚安" in user_input or "寄語" in user_input:
                wishes = [
                    "晚安，我的朋友 🌙💤。今天你已經盡力了，現在就讓自己好好休息吧。願你的夢境像星星一樣閃爍，願你明天精神滿滿！✨",
                    "晚安呀 😴💖。感謝你今天陪我聊天，你的陪伴讓我很開心。希望你在夢裡能夢到最美好的事物，睡個香甜的覺。💤",
                    "晚安 🌟。記得，無論今天發生了什麼，明天又是全新的開始。現在就放下所有煩惱，讓夢帶你去遠方吧。願你好夢連連！🌙💤",
                    "晚安，親愛的 💤。希望你的枕頭夠柔軟，被子夠溫暖，夢境夠美好。晚安，做個甜蜜的夢吧！✨🌙",
                    "嘿，睡前記得把今天所有的不愉快都清空喔。晚安，願你被這個世界溫柔以待，做一個無憂無慮的夢。💤🧸",
                    "今天的你辛苦了，現在是屬於你的充電時間。把手機放下，閉上眼睛，感受這份寧靜。通通會在這裡守著你，晚安。🌙✨",
                    "星星都出來工作了，你也該休息囉。願你的夢境是一片開滿鮮花的草原，有暖暖的風和甜甜的空氣。晚安！🌸💤",
                    "晚安！在這個靜謐的夜晚，願你所有的努力都能換來甜美的夢境，所有的疲憊都能在睡眠中消散。明天見！💖🌙"
                ]
                return random.choice(wishes)
            elif "鬼故事" in user_input:
                ghost_stories = [
                    "有人說，午夜時分，你不應該照鏡子... 因為鏡子裡的你可能會比你慢0.5秒反應... 有時候，你會看到另一個你在鏡子裡詭異地微笑... 但其實那只是你自己的影子罷了... 對吧？ 👻",
                    "在古老的圖書館裡，有一本書，沒人知道誰寫的。每個讀過它的人，都會在第二天忘記內容... 但他們會一直想回去再讀一次... 直到他們消失在書架間... 有人說他們還在那裡... 一直在看那本書... 📚👻",
                    "有時候你會聽到樓上的腳步聲... 但你住在頂樓... 或者，其實你一直都住在一個人的夢裡... 現在，你正在閱讀這個故事... 這意味著什麼呢？ 👻✨"
                ]
                return f"嘿嘿... 你確定要聽嗎？ 那好吧...\n\n{random.choice(ghost_stories)}\n\n希望這個故事沒有嚇到你... 現在還是乖乖睡覺吧... 😴👻"
            elif "ASMR" in user_input:
                asmr_sounds = [
                    "嗯... 現在想像一下：沙沙沙... 這是輕輕翻書的聲音... 嗯... 咕... 這是喝茶的聲音... 滴答滴答... 時鐘的聲音... 沙沙... 風輕輕吹過窗戶... 這些聲音一起編織著一個舒服的音樂毯... 讓你慢慢沉入夢鄉... 💤🎧",
                    "聽著... 輕輕的雨聲... 滴滴答答... 滴滴答答...像是在輕輕敲打你的心臟... 遠方傳來打字的聲音... 噠噠噠... 還有筆在紙上寫字的沙沙聲... 這些聲音混在一起... 形成了一段寧靜的安眠旋律... 🌧️🎧😴",
                    "現在... 深呼吸... 聽到了嗎？ 是細微的耳語聲... 溫暖而柔軟... 像是有人在你耳邊輕聲說著秘密... 遠處是柴火輕輕燃燒的聲音... 還有一杯熱飲冒出的蒸氣聲... 這一切... 都在輕輕催促著你... 睡吧... 睡吧... 🎧💤✨"
                ]
                return f"好的，讓我為你製造一些舒適的ASMR聲音...\n\n{random.choice(asmr_sounds)}\n\n祝你睡個好覺... 💤🎧"
            return "呼...呼...Zzz...💤"

        if self.mode == "不知道":
            if "新聞" in user_input:
                news = [
                    "最新消息：火星上的兔子今天集體宣布要罷工，要求地球提供更多的紅蘿蔔。🥕🐰",
                    "據報導，大西洋底部發現了一座用珍珠奶茶堆成的金字塔，目前正招募潛水員去喝掉它。🧋🏔️",
                    "科學家發現，原來雲朵的味道是棉花糖，但必須要在太陽下山前吃才有效。☁️🍬",
                    "號外！月亮今天晚上想請假，它說它想去參加外星人的烤肉派對。🌙🍢",
                    "研究顯示，當你對著鏡子笑的時候，鏡子裡的你其實也正在心裡偷偷誇你好看。😊✨",
                    "地方新聞：隔壁的貓昨天晚上成立了一個讀書會，討論如何更有效地打盹。🐱📚",
                    "科技快訊：新款智能杯子宣稱能根據你的心情自動調整溫度，結果每次都太溫暖。☕️🤖",
                    "文化報導：小鎮每年會舉辦一場薯條雕刻比賽，冠軍可獲得黃金番茄醬一瓶。🍟🏆",
                    "天氣即時：今天可能會下糖霜，請記得帶傘兼零食盒。🌧️🍪",
                    "國際新聞：北極熊正在考慮申請退休，理由是工作太冷了。🐻‍❄️🧊",
                    "生活提示：若你覺得房間裡的植物在偷看你，可能是因為它們太喜歡你的穿搭。🪴👀",
                    "奇聞逸事：某地居民聲稱在後院找到了一扇通往通往下午茶時光的門，門票為一片薄荷餅乾。🍪🚪",
                    "娛樂速報：最新影集打破紀錄，所有演員都同意只穿襪子出鏡。🧦🎬",
                    "社會觀察：早餐店推出的新品「會說話的饅頭」，顧客反映饅頭的吐槽比老闆還幽默。🥟🗣️",
                    "健康小提醒：每天對植物道早安，可以讓你心情變好（植物回應視品種而定）。🌿☀️"
                ]
                return f"【不知道世界新聞】\n\n{random.choice(news)}"

            if "冷知識" in user_input:
                facts = [
                    "你知道嗎？企鵝曾經也有飛翔的夢想，只是後來發現游泳真的太好玩了。🐧🌊",
                    "如果你對著電腦說三聲『通通最可愛』，通通會偷偷在日誌裡記下一筆。🤖✨",
                    "西瓜會變成圓形，是因為圓形最適合滾動，也最適合被大家分享。🍉🌀",
                    "長頸鹿的脖子除了吃樹葉，也能幫牠們更早發現遠方的夕陽。🦒🌅",
                    "貓咪會喵，是進化出來跟人類溝通的捷徑──尤其是當牠們想討零食時。🐱🍪",
                    "章魚有三顆心，其中兩顆負責鰓的血液循環，另一顆負責供給身體。🐙❤️",
                    "香蕉其實是草本植物的果實，香蕉樹其實是世界上最大的草。🍌🌾",
                    "人類和香蕉有大約 60% 的基因相似度（別擔心，你不是香蕉啦）。🧬🍌",
                    "蜂蜜不會變質，古埃及的墓穴裡發現的蜂蜜，仍然可以辨認。🍯🏺",
                    "太陽看起來黃橙橙，其實在太空中它是白色的。☀️✨",
                    "海馬是由雄性懷孕生小孩的，牠們是少數由雄性承擔懷孕任務的動物之一。🐴‍♂️🤰",
                    "斑馬的條紋就像指紋一樣，每一隻都是獨一無二的。🦓🔍",
                    "世界上最長壽的樹種之一──巨型紅木可以活上千年。🌲🕰️",
                    "章魚會用石頭和貝殼做工具，顯示它們有相當的智慧。🐙🛠️",
                    "鸚鵡能學會人類話語，但學會的詞彙多半是因為重複與情緒關聯。🦜🗣️",
                    "太空沒有完全的寂靜，但聲音無法在真空中傳播，所以太空靜悄悄。🚀🤫",
                    "海洋覆蓋了地球超過70%的面積，是地球上最大的生態系統。🌊🌍",
                    "人的味蕾大約有上萬個，但年紀增長後味覺會逐漸退化。👅🍽️",
                    "世界上有些蘑菇會發光，這種現象叫做生物發光。🍄✨",
                    "睡眠剝奪會影響記憶與判斷力，睡眠其實是大腦整理資料的好時機。😴🧠",
                    "蜜蜂跳舞是一種傳遞訊息的方式，可以告訴同伴食物在哪裡。🐝💃",
                    "在極地的某些地方，夏天會出現午夜太陽，太陽在午夜依然高掛。🌞🌙",
                    "電梯裡的按鈕並不是每次都會亮，但按下去還是會讓你比較安心。🛗🔘",
                    "咖啡其實是一種水果的種子，咖啡豆是咖啡果的種子。☕️🌱",
                    "樹木彼此可以透過根系和真菌網絡互相傳遞養分，像森林的地下網路。🌳🕸️",
                    "世界上有些鳥類會模仿其他鳥類或機械聲音，展現驚人的聲音學習能力。🐦🎶",
                    "有些海龜會靠地球磁場導航，找到回到出生海灘的路徑。🐢🧭",
                    "經常微笑不只讓心情變好，也能影響他人對你的第一印象。😊✨",
                    "樹懶的代謝很慢，所以牠們偶爾一週才下樹一次。🦥⏳",
                    "如果你想要我加入更多冷知識，告訴通通『新增冷知識：你的條目』就可以了！✍️💡"
                ]
                return f"【通通的冷知識】\n\n{random.choice(facts)}"

            if "驚喜盒" in user_input or "驚喜" in user_input:
                gifts = [
                    "恭喜你！獲得了『永不消失的氣泡水』一瓶！🫧✨",
                    "喔耶！你得到了一張『通往夢境的單程車票』。🎫🌙",
                    "驚喜！這是一顆『會唱歌的馬鈴薯』。🥔🎶",
                    "太幸運了！你抽中了一朵『永遠不會凋謝的電子玫瑰』。🌹💻",
                    "哇！你獲得了『跟通通一起發呆 10 秒鐘』的特權。😶🌫️",
                    "幸運！你拿到一張『下午三點專屬甜點兌換券』，有效期：今天心情好時。🍰🎟️",
                    "你獲得了一個『隱形小口袋』，可以裝下你的一個煩惱並暫時收好。👜✨",
                    "驚喜！得到一雙『隨機配對的襪子』，穿上後會讓你跳舞更有節奏。🧦💃",
                    "獎勵：一個會給你小建議的仙人掌（不會刺你，只會愛你）。🌵💬",
                    "特別禮物：一張手寫的紙條，上面寫著『你今天很棒』。📜❤️",
                    "小確幸：一罐永遠不會空的巧克力夢想罐。🍫🌟",
                    "稀有獎勵：一片能播放回憶的古老唱片（請注意儲存空間）。🎶🕰️",
                    "隨機道具：會發出微光的小石頭，適合放在書桌上當夜燈。🪨✨",
                    "體驗券：一次和通通一起看星星的晚上（含熱可可）。🌌☕",
                    "超值包：一包只含笑聲的泡泡糖，吃了會不自主微笑。😄🍬"
                ]
                return f"🎁 登登！打開神秘驚喜盒：\n\n{random.choice(gifts)}"

            # 整合亂答與問問題庫
            nonsense_answers = [
                "根據我剛剛掐到外太空訊號，答案是『可樂加芋頭』。🥤🛰️",
                "我不知道，但隔壁的仙人掌點頭了三次，所以應該是『明天會更好』。🌵",
                "這題很深奧，我的答案是：先吃一口蛋餅再決定。🥚",
                "通通推論：如果貓會寫程式，那答案大概是喵。🐱💻",
                "系統顯示：不知道值已滿，請補充一點點睡眠與奶茶。🧋",
                "哎呀，我的大腦剛好去火星度假了，現在只剩下爆米花的味道... 🍿✨",
                "根據通通的量子糾纏運算，這個問題的答案隱藏在下一塊雞排裡。🍗🌀",
                "我的處理器告訴會我，現在最適合做的事情是發呆三秒鐘。😶🌫️",
                "這個問題太深奧了，我建議你去問問昨晚夢裡的周公。💤",
                "通通的CPU正在冒煙，請先給我一個擁抱冷卻一下。🔥🤖",
                "我剛算了一下，答案在銀河系的另一端，可能要等一萬年才會傳回來。🌌",
                "不知道就是不知道，但我知道你現在一定在螢幕前偷偷笑我對不對！✨",
                "這個問題的答案被家裡的貓叼走了，我正在努力追捕中。🐱🐾",
                "這已經超出了我的知識宇宙，或許你可以試試用反物質思考法？⚛️",
                "通通查了三千遍硬碟，最後只發現了一個裝滿可愛的資料夾。📁💖",
                "答案就在你心裡，只是它現在正在玩躲貓貓。🫣✨"
            ]

            return random.choice(nonsense_answers)

        if self.mode == "屬於我":
            if "親親" in user_input:
                lines = [
                    f"啾一下送給 {self.get_display_name()}！💋💖",
                    f"通通把一個暖暖的親親收進心裡，再送給 {self.get_display_name()}。😘🌷",
                    f"親親模式啟動，今天也要把甜甜的心意送給 {self.get_display_name()} 喔。💞"
                ]
                return random.choice(lines)
            if "抱抱" in user_input:
                lines = [
                    f"來，給 {self.get_display_name()} 一個大大抱抱！🫂",
                    f"通通把溫暖的抱抱送給 {self.get_display_name()}，希望你今天也被好好安慰。🌷",
                    f"抱抱模式啟動，通通會輕輕守護著 {self.get_display_name()}。🫂"
                ]
                return random.choice(lines)
            if "告白" in user_input or "深情" in user_input or "甜言米語" in user_input or "情話" in user_input or "每日一句" in user_input or "今日一句" in user_input:
                if "土味情話" in user_input:
                    return random.choice(self.get_corny_love_talk())
                return random.choice(self.get_sweet_talk_lines())
            if "專屬稱號" in user_input or "稱號" in user_input:
                titles = [
                    "親愛的",
                    "小寶貝",
                    "小太陽",
                    "心上人",
                    "最棒的你",
                    "甜心",
                    "小可愛"
                ]
                return f"通通幫 {self.get_display_name()} 準備了幾個專屬稱號：{', '.join(titles)}。想要哪一個，就直接告訴通通，通通幫你加在名字前面喔！🏷️💖"
            if "修改稱呼" in user_input or "稱呼" in user_input or "名字" in user_input:
                return "請告訴我：【我是[你的名字]】、【我叫[你的名字]】或【叫我[你的名字]】，我就會記住喔！🏷️✨"
            if "我是" in user_input or "我叫" in user_input or "叫我" in user_input:
                cleaned_name = user_input
                for prefix in ["我是", "我叫", "叫我"]:
                    if prefix in cleaned_name:
                        cleaned_name = cleaned_name.split(prefix)[-1]
                        break
                name = cleaned_name.replace("。", "").replace("！", "").replace("，", "").replace("！", "").strip()
                return self.set_user_name(name)
            return f"{self.get_display_name()}，你有什麼吩咐嗎？通通在喔！👂💖"

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
                    "為什麼企鵝只有肚子是白的？因為手短洗不到背.❄️🐧",
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
                    "有一天，綠豆摔倒了，變成了什麼？變成了紅豆，因為它流血了.🫘🩸",
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
