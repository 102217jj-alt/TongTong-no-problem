import customtkinter as ctk
from tkinter import messagebox

class GomokuGame(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("通通遊戲專區 - 五子棋")
        self.geometry("650x700")
        self.grid_size = 15
        self.cell_size = 40
        self.current_player = 1  # 1 for Black, 2 for White
        self.board = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        self.setup_ui()

    def setup_ui(self):
        self.canvas = ctk.CTkCanvas(self, width=600, height=600, bg="#DEB887")
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.draw_board()
        
        self.info_label = ctk.CTkLabel(self, text="輪到：黑棋 (Black)", font=("Heiti TC", 16))
        self.info_label.pack()
        
        self.reset_button = ctk.CTkButton(self, text="重新開始", command=self.reset_game)
        self.reset_button.pack(pady=10)

    def draw_board(self):
        for i in range(self.grid_size):
            # Horizontal lines
            self.canvas.create_line(20, 20 + i * self.cell_size, 20 + (self.grid_size - 1) * self.cell_size, 20 + i * self.cell_size)
            # Vertical lines
            self.canvas.create_line(20 + i * self.cell_size, 20, 20 + i * self.cell_size, 20 + (self.grid_size - 1) * self.cell_size)

    def on_click(self, event):
        x = (event.x - 20 + self.cell_size // 2) // self.cell_size
        y = (event.y - 20 + self.cell_size // 2) // self.cell_size
        
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if self.board[y][x] == 0:
                self.place_piece(x, y)

    def place_piece(self, x, y):
        self.board[y][x] = self.current_player
        color = "black" if self.current_player == 1 else "white"
        
        px = 20 + x * self.cell_size
        py = 20 + y * self.cell_size
        self.canvas.create_oval(px - 15, py - 15, px + 15, py + 15, fill=color)
        
        if self.check_win(x, y):
            winner = "黑棋" if self.current_player == 1 else "白棋"
            messagebox.showinfo("遊戲結束", f"恭喜 {winner} 獲勝！")
            self.reset_game()
            return

        self.current_player = 3 - self.current_player
        player_text = "黑棋 (Black)" if self.current_player == 1 else "白棋 (White)"
        self.info_label.configure(text=f"輪到：{player_text}")

    def check_win(self, x, y):
        player = self.board[y][x]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            # Check one direction
            tx, ty = x + dx, y + dy
            while 0 <= tx < self.grid_size and 0 <= ty < self.grid_size and self.board[ty][tx] == player:
                count += 1
                tx += dx
                ty += dy
            
            # Check opposite direction
            tx, ty = x - dx, y - dy
            while 0 <= tx < self.grid_size and 0 <= ty < self.grid_size and self.board[ty][tx] == player:
                count += 1
                tx -= dx
                ty -= dy
                
            if count >= 5:
                return True
        return False

    def reset_game(self):
        self.board = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.canvas.delete("all")
        self.draw_board()
        self.current_player = 1
        self.info_label.configure(text="輪到：黑棋 (Black)")
