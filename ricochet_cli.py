import os

class RicochetRobotsCLI:
    def __init__(self):
        self.width = 16
        self.height = 16
        
        # Robots and their coordinates (x, y) where 0,0 is top-left
        self.robots = {
            'R': [1, 1],
            'B': [14, 1],
            'G': [1, 14],
            'Y': [14, 14]
        }
        
        # Walls storage: lists of (x, y) representing a wall
        # h_walls[y][x] == True means there is a horizontal wall ABOVE cell (x, y)
        self.h_walls = [[False] * self.width for _ in range(self.height)]
        # v_walls[y][x] == True means there is a vertical wall to the LEFT of cell (x, y)
        self.v_walls = [[False] * self.width for _ in range(self.height)]
        
        self.setup_walls()

    def setup_walls(self):
        # Outer borders
        for x in range(self.width):
            self.h_walls[0][x] = True # Top border
        for y in range(self.height):
            self.v_walls[y][0] = True # Left border
            
        # Center 2x2 obstacle (7,7 to 8,8)
        self.h_walls[7][7] = True; self.h_walls[7][8] = True
        self.h_walls[9][7] = True; self.h_walls[9][8] = True
        self.v_walls[7][7] = True; self.v_walls[8][7] = True
        self.v_walls[7][9] = True; self.v_walls[8][9] = True
        
        # Add a few random inner walls just to make it interesting
        self.h_walls[3][5] = True; self.v_walls[2][6] = True
        self.h_walls[12][10] = True; self.v_walls[12][10] = True

    def draw_board(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== 碰撞機器人 (Ricochet Robots) ===")
        print("機器人: [R]紅 [B]藍 [G]綠 [Y]黃")
        print("操作方式: 輸入 '機器人 方向'，例如 'R w' (紅往上), 'B d' (藍往右)")
        print("方向鍵: w(上) s(下) a(左) d(右), 輸入 q 退出\n")

        # Create inverse lookup for robots
        robot_pos = {tuple(pos): name for name, pos in self.robots.items()}

        for y in range(self.height):
            # Draw horizontal walls
            row_top = "+"
            for x in range(self.width):
                if self.h_walls[y][x] or y == 0:
                    row_top += "---+"
                else:
                    row_top += "   +"
            print(row_top)

            # Draw cells and vertical walls
            row_cells = ""
            for x in range(self.width):
                if self.v_walls[y][x] or x == 0:
                    row_cells += "|"
                else:
                    row_cells += " "
                
                # Check for robot or center obstacle
                if (x, y) in robot_pos:
                    row_cells += f" {robot_pos[(x, y)]} "
                elif 7 <= x <= 8 and 7 <= y <= 8:
                    row_cells += "XXX" # Center block
                else:
                    row_cells += " . "
            
            # Right border
            row_cells += "|"
            print(row_cells)

        # Draw bottom border
        print("+---" * self.width + "+")

    def get_robot_at(self, x, y):
        for name, pos in self.robots.items():
            if pos[0] == x and pos[1] == y:
                return name
        return None

    def move_robot(self, robot_name, direction):
        if robot_name not in self.robots:
            return False
            
        dx, dy = 0, 0
        if direction == 'w': dy = -1
        elif direction == 's': dy = 1
        elif direction == 'a': dx = -1
        elif direction == 'd': dx = 1
        else: return False

        x, y = self.robots[robot_name]
        
        while True:
            # Check walls
            if dx == 1: # Moving right
                if x + 1 >= self.width or self.v_walls[y][x + 1]: break
            elif dx == -1: # Moving left
                if x <= 0 or self.v_walls[y][x]: break
            elif dy == 1: # Moving down
                if y + 1 >= self.height or self.h_walls[y + 1][x]: break
            elif dy == -1: # Moving up
                if y <= 0 or self.h_walls[y][x]: break
                
            next_x, next_y = x + dx, y + dy
            
            # Check center block
            if 7 <= next_x <= 8 and 7 <= next_y <= 8:
                break
                
            # Check other robots
            if self.get_robot_at(next_x, next_y):
                break
                
            x, y = next_x, next_y
            
        self.robots[robot_name] = [x, y]
        return True

    def play(self):
        while True:
            self.draw_board()
            
            user_input = input("\n請輸入指令 (例: R d): ").strip().lower()
            
            if user_input == 'q':
                print("遊戲結束！")
                break
                
            parts = user_input.split()
            if len(parts) == 2:
                robot = parts[0].upper()
                direction = parts[1]
                
                if robot in self.robots and direction in ['w', 's', 'a', 'd']:
                    self.move_robot(robot, direction)
                else:
                    input("無效的機器人或方向！按 Enter 繼續...")
            else:
                input("格式錯誤！請輸入 '機器人 方向' (例如 R w)。按 Enter 繼續...")

if __name__ == "__main__":
    game = RicochetRobotsCLI()
    game.play()
