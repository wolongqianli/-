import tkinter as tk
from tkinter import ttk
import numpy as np
import math

class Go:
    def __init__(self, board_size=16):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = 1  
        self.passes = 0  

    def place_stone(self, x, y):
        if self.board[x, y] != 0:
            return False

        self.board[x, y] = self.current_player
        
        captured = self.check_capture(x, y)
        if captured:
            self.remove_captured_stones(captured)
        else:
            if not self.has_liberty(x, y):
                self.board[x, y] = 0
                return False

        self.current_player = 3 - self.current_player
        self.passes = 0
        return True

    def check_capture(self, x, y):
        opponent = 3 - self.current_player
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        captured = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx, ny] == opponent:
                group = self.get_connected_group(nx, ny)
                if not any(self.has_liberty(gx, gy) for gx, gy in group):
                    captured.extend(group)

        return captured if captured else None

    def remove_captured_stones(self, stones):
        for x, y in stones:
            self.board[x, y] = 0

    def get_connected_group(self, x, y):
        color = self.board[x, y]
        group = []
        visited = set()

        def dfs(x, y):
            if (x, y) in visited or self.board[x, y] != color:
                return
            visited.add((x, y))
            group.append((x, y))
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    dfs(nx, ny)

        dfs(x, y)
        return group

    def has_liberty(self, x, y):
        color = self.board[x, y]
        visited = set()
        
        def dfs(x, y):
            if (x, y) in visited:
                return False
            visited.add((x, y))
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.board[nx, ny] == 0:
                        return True
                    if self.board[nx, ny] == color and dfs(nx, ny):
                        return True
            return False

        return dfs(x, y)

    def pass_turn(self):
        self.passes += 1
        self.current_player = 3 - self.current_player

    def is_game_over(self):
        return self.passes >= 2

    def score(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == 2)
        empty = np.sum(self.board == 0)
        black_score += empty // 2
        white_score += empty // 2
        if empty % 2 != 0:
            black_score += 1 if self.current_player == 1 else 0
        return black_score, white_score

    def display_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] == 1:
                    print("○", end=" ")
                elif self.board[i, j] == 2:
                    print("●", end=" ")
                else:
                    print(".", end=" ")
            print()

class GoGUI:
    def __init__(self, master):
        self.master = master
        self.game = Go(board_size=16)
        
        self.master.geometry("600x600")
        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Configure>", self.resize_board)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        self.control_panel = tk.Frame(self.frame)
        self.control_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.pass_button = ttk.Button(self.control_panel, text="PASS", command=self.pass_turn)
        self.pass_button.pack(side=tk.LEFT, padx=5)
        
        self.score_label = ttk.Label(self.control_panel, text="Score: Black - 0, White - 0")
        self.score_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(self.control_panel, text=f"Current Player: Black")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.preview_stone = None
        self.draw_board()

    def resize_board(self, event):
        if event.widget == self.canvas:
            self.canvas.delete("all")
            self.draw_board()

    def draw_board(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        board_size = min(canvas_width, canvas_height)
        
        cell_size = board_size / (self.game.board_size + 1)
        
        start_x = (canvas_width - board_size) / 2 + cell_size
        start_y = (canvas_height - board_size) / 2 + cell_size
        
        for i in range(self.game.board_size + 1):
            x = start_x + cell_size * i
            y = start_y + cell_size * i
            self.canvas.create_line(start_x, y, start_x + cell_size * (self.game.board_size - 1), y)
            self.canvas.create_line(x, start_y, x, start_y + cell_size * (self.game.board_size - 1))
        
        for i in range(self.game.board_size):
            for j in range(self.game.board_size):
                if self.game.board[i, j] == 1:
                    self.canvas.create_oval(start_x + j * cell_size - 10, start_y + i * cell_size - 10, 
                                            start_x + j * cell_size + 10, start_y + i * cell_size + 10, fill="black")
                elif self.game.board[i, j] == 2:
                    self.canvas.create_oval(start_x + j * cell_size - 10, start_y + i * cell_size - 10, 
                                            start_x + j * cell_size + 10, start_y + i * cell_size + 10, fill="white")

    def on_mouse_move(self, event):
        if self.preview_stone:
            self.canvas.delete(self.preview_stone)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        board_size = min(canvas_width, canvas_height)
        
        cell_size = board_size / (self.game.board_size + 1)
        
        start_x = (canvas_width - board_size) / 2 + cell_size
        start_y = (canvas_height - board_size) / 2 + cell_size
        
        x = min(self.game.board_size - 1, max(0, round((event.x - start_x) / cell_size)))
        y = min(self.game.board_size - 1, max(0, round((event.y - start_y) / cell_size)))
        
        if self.game.board[y, x] == 0:
            color = "black" if self.game.current_player == 1 else "white"
            self.preview_stone = self.canvas.create_oval(start_x + x * cell_size - 10, start_y + y * cell_size - 10, 
                                                         start_x + x * cell_size + 10, start_y + y * cell_size + 10, 
                                                         fill=color, outline=color, stipple="gray25")

    def on_board_click(self, event):
        if self.preview_stone:
            self.canvas.delete(self.preview_stone)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        board_size = min(canvas_width, canvas_height)
        
        cell_size = board_size / (self.game.board_size + 1)
        
        start_x = (canvas_width - board_size) / 2 + cell_size
        start_y = (canvas_height - board_size) / 2 + cell_size
        
        x = min(self.game.board_size - 1, max(0, round((event.x - start_x) / cell_size)))
        y = min(self.game.board_size - 1, max(0, round((event.y - start_y) / cell_size)))
        
        if self.game.place_stone(y, x):
            self.update_display()
        else:
            print("Invalid move. Try again.")

    def pass_turn(self):
        self.game.pass_turn()
        self.update_display()

    def update_display(self):
        self.canvas.delete("all")
        self.draw_board()
        black_score, white_score = self.game.score()
        self.score_label.config(text=f"Score: Black - {black_score}, White - {white_score}")
        player_name = "Black" if self.game.current_player == 1 else "White"
        self.status_label.config(text=f"Current Player: {player_name}")
        if self.game.is_game_over():
            self.status_label.config(text=f"Game Over! Black: {black_score}, White: {white_score}")
            self.pass_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    gui = GoGUI(root)
    root.mainloop()
