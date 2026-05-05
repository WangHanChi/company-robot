import copy
import random
from collections import deque

CENTER_BLOCK = {(x, y) for x in (7, 8) for y in (7, 8)}

ROBOT_COLORS = ['Red', 'Blue', 'Green', 'Yellow']
COLOR_ZH = {'Red': '紅', 'Blue': '藍', 'Green': '綠', 'Yellow': '黃'}
ZH_TO_COLOR = {v: k for k, v in COLOR_ZH.items()}


class Board:
    def __init__(self, width=16, height=16):
        self.width = width
        self.height = height
        self.h_walls = []
        self.v_walls = []
        self.all_targets = []
        self.current_target = None
        self.initial_robots = {}
        self.robots = {}
        self.moves = 0
        self.won = False
        self.selected_robot = None
        self.show_optimal = False
        self.optimal_steps = -1
        self.solution_path = []
        self.calculating = False
        self._bfs = None
        self.generate_random_board()

    def generate_random_board(self):
        self.all_targets = []
        colors = ROBOT_COLORS * 4
        wall_types = ['TR', 'TL', 'BR', 'BL']

        used_pos = set(CENTER_BLOCK)

        for color in colors:
            while True:
                tx = random.randint(1, self.width - 2)
                ty = random.randint(1, self.height - 2)
                valid = True
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if (tx + dx, ty + dy) in used_pos:
                            valid = False
                            break
                    if not valid:
                        break
                if valid:
                    used_pos.add((tx, ty))
                    self.all_targets.append((color, tx, ty, random.choice(wall_types)))
                    break

        self.extra_h_walls = []
        self.extra_v_walls = []
        for _ in range(8):
            if random.choice([True, False]):
                x = random.randint(2, self.width - 3)
                y = random.choice([1, self.height - 1])
                self.extra_v_walls.append((x, y))
            else:
                x = random.choice([1, self.width - 1])
                y = random.randint(2, self.height - 3)
                self.extra_h_walls.append((x, y))

        self.initial_robots = {}
        for c in ROBOT_COLORS:
            while True:
                rx = random.randint(0, self.width - 1)
                ry = random.randint(0, self.height - 1)
                if (rx, ry) not in used_pos:
                    used_pos.add((rx, ry))
                    self.initial_robots[c] = [rx, ry]
                    break

        self._setup_walls()
        self.select_next_target()

    def _setup_walls(self):
        self.h_walls = [[False] * self.width for _ in range(self.height)]
        self.v_walls = [[False] * self.width for _ in range(self.height)]

        for x in range(self.width):
            self.h_walls[0][x] = True
        for y in range(self.height):
            self.v_walls[y][0] = True

        self.h_walls[7][7] = True; self.h_walls[7][8] = True
        self.h_walls[9][7] = True; self.h_walls[9][8] = True
        self.v_walls[7][7] = True; self.v_walls[8][7] = True
        self.v_walls[7][9] = True; self.v_walls[8][9] = True

        for x, y in self.extra_v_walls:
            if y == 1:
                self.v_walls[0][x] = True
            else:
                self.v_walls[self.height - 1][x] = True

        for x, y in self.extra_h_walls:
            if x == 1:
                self.h_walls[y][0] = True
            else:
                self.h_walls[y][self.width - 1] = True

        for color, x, y, walls in self.all_targets:
            if 'T' in walls: self.h_walls[y][x] = True
            if 'B' in walls: self.h_walls[y + 1][x] = True
            if 'L' in walls: self.v_walls[y][x] = True
            if 'R' in walls: self.v_walls[y][x + 1] = True

    def select_next_target(self):
        self.current_target = random.choice(self.all_targets)
        self.moves = 0
        self.won = False
        self.robots = copy.deepcopy(self.initial_robots)
        self.selected_robot = None
        self.show_optimal = False
        self.optimal_steps = -1
        self.solution_path = []
        self.calculating = True
        self.solve_bfs_init()

    def reset_robots(self):
        self.robots = copy.deepcopy(self.initial_robots)
        self.moves = 0
        self.won = False
        self.selected_robot = None

    def predict(self, color, dx, dy, robots=None):
        robots = robots if robots is not None else self.robots
        x, y = robots[color]
        others = {tuple(p) for k, p in robots.items() if k != color}
        while True:
            if dx == 1 and (x + 1 >= self.width or self.v_walls[y][x + 1]): break
            if dx == -1 and (x <= 0 or self.v_walls[y][x]): break
            if dy == 1 and (y + 1 >= self.height or self.h_walls[y + 1][x]): break
            if dy == -1 and (y <= 0 or self.h_walls[y][x]): break
            nx, ny = x + dx, y + dy
            if (nx, ny) in CENTER_BLOCK: break
            if (nx, ny) in others: break
            x, y = nx, ny
        return x, y

    def apply_move(self, color, dx, dy):
        sx, sy = self.robots[color]
        ex, ey = self.predict(color, dx, dy)
        if (sx, sy) == (ex, ey):
            return None
        self.robots[color] = [ex, ey]
        self.moves += 1
        won = False
        tc, tx, ty, _ = self.current_target
        if color == tc and ex == tx and ey == ty:
            self.won = True
            won = True
        return {
            'color': color,
            'start': (sx, sy),
            'end': (ex, ey),
            'dir': (dx, dy),
            'won': won,
        }

    def get_robot_at(self, x, y):
        for name, pos in self.robots.items():
            if pos[0] == x and pos[1] == y:
                return name
        return None

    def solve_bfs_init(self):
        tc, tx, ty, _ = self.current_target
        start_state = tuple(tuple(self.initial_robots[c]) for c in ROBOT_COLORS)
        self._bfs = {
            'queue': deque([(start_state, [])]),
            'visited': {start_state},
            'target_idx': ROBOT_COLORS.index(tc),
            'target_pos': (tx, ty),
        }
        self.optimal_steps = -1
        self.solution_path = []

    def solve_bfs_step(self, budget=1500):
        """Process up to `budget` BFS states. Returns True if BFS finished."""
        if self._bfs is None:
            return True
        s = self._bfs
        queue = s['queue']
        visited = s['visited']
        target_idx = s['target_idx']
        target_pos = s['target_pos']
        directions = [(0, -1, '上'), (0, 1, '下'), (-1, 0, '左'), (1, 0, '右')]
        max_depth = 20
        max_states = 100_000

        for _ in range(budget):
            if not queue:
                self.optimal_steps = -1
                self.solution_path = []
                self._bfs = None
                return True
            if len(visited) > max_states:
                self.optimal_steps = -1
                self.solution_path = []
                self._bfs = None
                return True
            state, path = queue.popleft()
            if len(path) >= max_depth:
                continue
            for i, c in enumerate(ROBOT_COLORS):
                others = {state[j] for j in range(4) if j != i}
                for dx, dy, dn in directions:
                    cx, cy = state[i]
                    while True:
                        if dx == 1 and (cx + 1 >= self.width or self.v_walls[cy][cx + 1]): break
                        if dx == -1 and (cx <= 0 or self.v_walls[cy][cx]): break
                        if dy == 1 and (cy + 1 >= self.height or self.h_walls[cy + 1][cx]): break
                        if dy == -1 and (cy <= 0 or self.h_walls[cy][cx]): break
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) in CENTER_BLOCK: break
                        if (nx, ny) in others: break
                        cx, cy = nx, ny
                    if (cx, cy) != state[i]:
                        new_state = list(state)
                        new_state[i] = (cx, cy)
                        new_state = tuple(new_state)
                        if new_state not in visited:
                            new_path = path + [(COLOR_ZH[c], dn)]
                            if i == target_idx and (cx, cy) == target_pos:
                                self.solution_path = new_path
                                self.optimal_steps = len(new_path)
                                self._bfs = None
                                return True
                            visited.add(new_state)
                            queue.append((new_state, new_path))
        return False
