import customtkinter as ctk
import threading
from dotenv import load_dotenv
from tongtong.brain import TongTongBrain
from tongtong.voice import bot_listen, bot_speak
from tongtong.text_utils import bot_speak_re
from games.gomoku import GomokuGame

# Load environment variables
load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TongTongApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("通通 (TongTong) 語音聊天機器人")
        self.geometry("800x600")

        # Initialize Brain
        self.brain = TongTongBrain()
        self.voice_gender = "female"

        self.setup_ui()

    def setup_ui(self):
        # Configure Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Chat History
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="對話歷史")
        self.chat_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Input Area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="輸入文字或點擊右側麥克風...")
        self.entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda e: self.send_text())

        self.send_button = ctk.CTkButton(self.input_frame, text="發送", width=80, command=self.send_text)
        self.send_button.grid(row=0, column=1, padx=5, pady=10)

        self.mic_button = ctk.CTkButton(self.input_frame, text="🎤 語音", width=80, fg_color="#E74C3C", hover_color="#C0392B", command=self.start_voice_thread)
        self.mic_button.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Control Panel
        self.control_frame = ctk.CTkFrame(self, width=200)
        self.control_frame.grid(row=0, column=1, rowspan=2, padx=(0, 20), pady=20, sticky="ns")

        self.mode_label = ctk.CTkLabel(self.control_frame, text="通通模式", font=("Heiti TC", 16, "bold"))
        self.mode_label.pack(pady=(20, 10))

        self.mode_option = ctk.CTkOptionMenu(self.control_frame, values=self.brain.modes, command=self.change_mode)
        self.mode_option.set("好心情")
        self.mode_option.pack(pady=10)

        self.voice_label = ctk.CTkLabel(self.control_frame, text="語音設定", font=("Heiti TC", 16, "bold"))
        self.voice_label.pack(pady=(20, 10))

        self.voice_option = ctk.CTkOptionMenu(self.control_frame, values=["女聲 (Female)", "男聲 (Male)"], command=self.change_voice)
        self.voice_option.set("女聲 (Female)")
        self.voice_option.pack(pady=10)

        self.game_button = ctk.CTkButton(self.control_frame, text="開啟五子棋", command=self.open_game)
        self.game_button.pack(pady=(40, 10))

    def add_message(self, sender, message, color="white"):
        msg_label = ctk.CTkLabel(self.chat_frame, text=f"[{sender}]: {message}", wraplength=500, justify="left", text_color=color)
        msg_label.pack(anchor="w", padx=10, pady=5)
        # Auto scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def send_text(self):
        text = self.entry.get()
        if text.strip():
            self.entry.delete(0, 'end')
            self.process_interaction(text)

    def start_voice_thread(self):
        self.mic_button.configure(state="disabled", text="正在聽...")
        threading.Thread(target=self.voice_interaction_task, daemon=True).start()

    def voice_interaction_task(self):
        audio_text = bot_listen()
        self.after(0, lambda: self.mic_button.configure(state="normal", text="🎤 語音"))
        
        if audio_text:
            self.after(0, lambda: self.process_interaction(audio_text))
        else:
            self.after(0, lambda: self.add_message("系統", "抱歉，我沒聽清楚。", "gray"))

    def process_interaction(self, user_text):
        self.add_message("您", user_text, "#AED6F1")
        
        # Brain processing
        response = self.brain.process_input(user_text)
        self.add_message("通通", response, "#F9E79F")

        # Speak in a separate thread
        threading.Thread(target=self.speak_task, args=(response,), daemon=True).start()

    def speak_task(self, text):
        cleaned_text = bot_speak_re(text)
        bot_speak(cleaned_text, self.voice_gender)

    def change_mode(self, mode_name):
        res = self.brain.set_mode(mode_name)
        self.add_message("系統", res, "gray")

    def change_voice(self, voice_display):
        if "女" in voice_display:
            self.voice_gender = "female"
        else:
            self.voice_gender = "male"
        self.add_message("系統", f"語音已更換為 {voice_display}", "gray")

    def open_game(self):
        GomokuGame(self)

if __name__ == "__main__":
    app = TongTongApp()
    app.mainloop()
