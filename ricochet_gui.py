import tkinter as tk
import copy

class RicochetRobotsGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("碰撞機器人 (Ricochet Robots) - GUI版")
        
        self.width = 16
        self.height = 16
        self.cell_size = 40  # 每個格子的像素大小
        
        # 初始位置，用於 Reset
        self.initial_robots = {
            'Red': [1, 1],
            'Blue': [14, 1],
            'Green': [1, 14],
            'Yellow': [14, 14]
        }
        
        # 機器人顏色對應 tkinter 顏色
        self.colors = {
            'Red': 'red',
            'Blue': 'blue',
            'Green': 'green',
            'Yellow': 'yellow'
        }
        
        self.robots = copy.deepcopy(self.initial_robots)
        self.selected_robot = None
        
        self.setup_walls()
        self.setup_ui()
        
    def setup_walls(self):
        # 初始化牆壁 (h_walls[y][x] 表示在 (x,y) 的上方有一道牆)
        self.h_walls = [[False] * self.width for _ in range(self.height)]
        # v_walls[y][x] 表示在 (x,y) 的左方有一道牆
        self.v_walls = [[False] * self.width for _ in range(self.height)]
        
        # 邊界
        for x in range(self.width):
            self.h_walls[0][x] = True
        for y in range(self.height):
            self.v_walls[y][0] = True
            
        # 中間 2x2 障礙物
        self.h_walls[7][7] = True; self.h_walls[7][8] = True
        self.h_walls[9][7] = True; self.h_walls[9][8] = True
        self.v_walls[7][7] = True; self.v_walls[8][7] = True
        self.v_walls[7][9] = True; self.v_walls[8][9] = True
        
        # 隨機幾個內部牆壁
        self.h_walls[3][5] = True; self.v_walls[2][6] = True
        self.h_walls[12][10] = True; self.v_walls[12][10] = True
        
    def setup_ui(self):
        # 狀態列
        self.status_var = tk.StringVar()
        self.status_var.set("請點擊一個機器人來選擇，然後使用鍵盤上下左右移動。")
        self.status_label = tk.Label(self.master, textvariable=self.status_var, font=("Arial", 14))
        self.status_label.pack(pady=5)
        
        # 畫布
        canvas_width = self.width * self.cell_size
        canvas_height = self.height * self.cell_size
        self.canvas = tk.Canvas(self.master, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=20, pady=10)
        
        # 綁定事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.master.bind("<Up>", lambda event: self.move("Up"))
        self.master.bind("<Down>", lambda event: self.move("Down"))
        self.master.bind("<Left>", lambda event: self.move("Left"))
        self.master.bind("<Right>", lambda event: self.move("Right"))
        
        # 底部按鈕
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=5)
        
        reset_btn = tk.Button(btn_frame, text="重來 (Reset)", command=self.reset_game, font=("Arial", 12))
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        self.draw_board()
        
    def draw_board(self):
        self.canvas.delete("all")
        
        # 畫背景網格
        for x in range(self.width):
            for y in range(self.height):
                x0 = x * self.cell_size
                y0 = y * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                
                # 畫基礎方格
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="#e0e0e0")
                
                # 畫中間障礙物
                if 7 <= x <= 8 and 7 <= y <= 8:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="black")

        # 畫牆壁 (加粗線條)
        wall_width = 4
        for y in range(self.height):
            for x in range(self.width):
                x0 = x * self.cell_size
                y0 = y * self.cell_size
                
                if self.h_walls[y][x] or y == 0:
                    self.canvas.create_line(x0, y0, x0 + self.cell_size, y0, fill="black", width=wall_width)
                if self.v_walls[y][x] or x == 0:
                    self.canvas.create_line(x0, y0, x0, y0 + self.cell_size, fill="black", width=wall_width)
                    
        # 右下角邊界補齊
        self.canvas.create_line(0, self.height * self.cell_size, self.width * self.cell_size, self.height * self.cell_size, fill="black", width=wall_width)
        self.canvas.create_line(self.width * self.cell_size, 0, self.width * self.cell_size, self.height * self.cell_size, fill="black", width=wall_width)

        # 畫選取高亮 (如果有的話)
        if self.selected_robot:
            rx, ry = self.robots[self.selected_robot]
            x0 = rx * self.cell_size
            y0 = ry * self.cell_size
            self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill="#d0f0d0", outline="")

        # 畫機器人
        padding = 6
        for name, pos in self.robots.items():
            rx, ry = pos
            x0 = rx * self.cell_size + padding
            y0 = ry * self.cell_size + padding
            x1 = (rx + 1) * self.cell_size - padding
            y1 = (ry + 1) * self.cell_size - padding
            
            color = self.colors[name]
            
            # 如果被選中，加上粗框
            outline_color = "black" if name == self.selected_robot else ""
            outline_width = 3 if name == self.selected_robot else 0
            
            self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=outline_color, width=outline_width)

    def on_click(self, event):
        # 計算點擊的格子座標
        grid_x = event.x // self.cell_size
        grid_y = event.y // self.cell_size
        
        # 檢查是否點擊到機器人
        clicked_robot = None
        for name, pos in self.robots.items():
            if pos[0] == grid_x and pos[1] == grid_y:
                clicked_robot = name
                break
                
        if clicked_robot:
            self.selected_robot = clicked_robot
            self.status_var.set(f"已選擇 {self.selected_robot} 機器人。使用方向鍵移動。")
        else:
            self.selected_robot = None
            self.status_var.set("取消選擇。請點擊一個機器人。")
            
        self.draw_board()

    def get_robot_at(self, x, y):
        for name, pos in self.robots.items():
            if pos[0] == x and pos[1] == y:
                return name
        return None

    def move(self, direction):
        if not self.selected_robot:
            return
            
        dx, dy = 0, 0
        if direction == "Up": dy = -1
        elif direction == "Down": dy = 1
        elif direction == "Left": dx = -1
        elif direction == "Right": dx = 1

        x, y = self.robots[self.selected_robot]
        
        while True:
            # 檢查是否會撞牆
            if dx == 1: # 向右
                if x + 1 >= self.width or self.v_walls[y][x + 1]: break
            elif dx == -1: # 向左
                if x <= 0 or self.v_walls[y][x]: break
            elif dy == 1: # 向下
                if y + 1 >= self.height or self.h_walls[y + 1][x]: break
            elif dy == -1: # 向上
                if y <= 0 or self.h_walls[y][x]: break
                
            next_x, next_y = x + dx, y + dy
            
            # 檢查是否撞到中間黑色障礙物
            if 7 <= next_x <= 8 and 7 <= next_y <= 8:
                break
                
            # 檢查是否撞到其他機器人
            if self.get_robot_at(next_x, next_y):
                break
                
            # 可以移動，更新當前虛擬座標並繼續滑行
            x, y = next_x, next_y
            
        # 更新實際座標
        if self.robots[self.selected_robot] != [x, y]:
            self.robots[self.selected_robot] = [x, y]
            self.status_var.set(f"{self.selected_robot} 移動到了 ({x}, {y})")
            self.draw_board()

    def reset_game(self):
        self.robots = copy.deepcopy(self.initial_robots)
        self.selected_robot = None
        self.status_var.set("遊戲已重置。請點擊一個機器人來選擇。")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    
    # 確保視窗顯示在最上層
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    app = RicochetRobotsGUI(root)
    root.mainloop()
