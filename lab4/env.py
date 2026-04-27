import os
import numpy as np
import pygame

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

pygame.init()

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
CELL   = 40
ROWS   = 10
COLS   = 10
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL

C_BG    = (30,  30,  30)
C_WALL  = (80,  80,  80)
C_FREE  = (200, 200, 200)
C_TANK  = (50,  180, 50)
C_GOAL  = (220, 50,  50)
C_ARROW = (255, 255, 255)

# ---------------------------------------------------------------------------
# Карта по умолчанию (0 — проход, 1 — стена)
# ---------------------------------------------------------------------------
DEFAULT_MAP = np.array([
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,0,0,0,0,0,1],
    [1,1,1,0,0,0,1,0,0,1],
    [1,0,0,0,1,0,0,0,1,1],
    [1,0,0,0,1,0,0,0,0,1],
    [1,1,0,1,1,0,0,1,0,1],
    [1,0,0,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
], dtype=np.int8)

# ---------------------------------------------------------------------------
# Объекты
# ---------------------------------------------------------------------------
class Tank:
    def __init__(self, row, col, angle=0):
        self.row   = row
        self.col   = col
        self.angle = angle   # 0=вверх, 90=вправо, 180=вниз, 270=влево

    def center_px(self):
        return (self.col * CELL + CELL // 2,
                self.row * CELL + CELL // 2)


class Goal:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def center_px(self):
        return (self.col * CELL + CELL // 2,
                self.row * CELL + CELL // 2)


# ---------------------------------------------------------------------------
# Среда
# ---------------------------------------------------------------------------
class TankEnv:
    """
    2D клетчатая среда: танк должен добраться до цели.

    Действия:
    0 — вперёд
    1 — назад
    2 — поворот влево  (-90°)
    3 — поворот вправо (+90°)

    Наблюдение: (row, col, angle_idx, goal_row, goal_col)
      angle_idx = angle // 90  →  0..3
    """

    ACTIONS = {0: 'вперёд', 1: 'назад', 2: 'влево', 3: 'вправо'}

    DEFAULT_REWARDS = {
        'step':    -1,
        'wall':   -10,
        'closer': +10,
        'farther': -5,
        'goal':  +100,
    }

    def __init__(self, grid=None, tank_start=(1, 1), goal_pos=(8, 8),
                 max_steps=200, rewards=None):
        self.grid       = grid if grid is not None else DEFAULT_MAP.copy()
        self.tank_start = tank_start
        self.goal_pos   = goal_pos
        self.max_steps  = max_steps
        self.rewards    = {**self.DEFAULT_REWARDS, **(rewards or {})}
        self.surface    = pygame.Surface((WIDTH, HEIGHT))
        self.reset()

    # ------------------------------------------------------------------
    def reset(self):
        self.tank       = Tank(*self.tank_start, angle=0)
        self.goal       = Goal(*self.goal_pos)
        self.steps      = 0
        self._prev_dist = self._dist()
        return self._observe()

    # ------------------------------------------------------------------
    def step(self, action):
        self.steps += 1
        reward = self.rewards['step']
        done   = False

        if action == 2:
            self.tank.angle = (self.tank.angle - 90) % 360
        elif action == 3:
            self.tank.angle = (self.tank.angle + 90) % 360
        else:
            dr, dc = self._direction()
            if action == 1:
                dr, dc = -dr, -dc
            nr = self.tank.row + dr
            nc = self.tank.col + dc
            if self.grid[nr][nc] == 1:
                reward += self.rewards['wall']
            else:
                self.tank.row = nr
                self.tank.col = nc

        dist = self._dist()
        if dist < self._prev_dist:
            reward += self.rewards['closer']
        elif dist > self._prev_dist:
            reward += self.rewards['farther']
        self._prev_dist = dist

        if self.tank.row == self.goal.row and self.tank.col == self.goal.col:
            reward += self.rewards['goal']
            done = True

        if self.steps >= self.max_steps:
            done = True

        return self._observe(), reward, done

    # ------------------------------------------------------------------
    def _direction(self):
        return {0: (-1, 0), 90: (0, 1), 180: (1, 0), 270: (0, -1)}[self.tank.angle % 360]

    def _dist(self):
        return abs(self.tank.row - self.goal.row) + abs(self.tank.col - self.goal.col)

    def _is_free(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == 0

    def _observe(self):
        return (self.tank.row, self.tank.col, self.tank.angle // 90,
                self.goal.row, self.goal.col)

    # ------------------------------------------------------------------
    def render(self):
        """Рисует кадр, возвращает RGB numpy-массив (H×W×3)."""
        s = self.surface
        s.fill(C_BG)

        for r in range(ROWS):
            for c in range(COLS):
                rect  = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                color = C_WALL if self.grid[r][c] == 1 else C_FREE
                pygame.draw.rect(s, color, rect)
                pygame.draw.rect(s, C_BG, rect, 1)

        pygame.draw.circle(s, C_GOAL, self.goal.center_px(), CELL // 3)

        tx, ty = self.tank.center_px()
        tank_rect = pygame.Rect(tx - CELL//3, ty - CELL//3, CELL*2//3, CELL*2//3)
        pygame.draw.rect(s, C_TANK, tank_rect, border_radius=4)

        dr, dc = self._direction()
        ex = tx + dc * (CELL // 2 - 4)
        ey = ty + dr * (CELL // 2 - 4)
        pygame.draw.line(s, C_ARROW, (tx, ty), (ex, ey), 3)

        font = pygame.font.SysFont(None, 22)
        txt  = font.render(f'step {self.steps}', True, (255, 255, 255))
        s.blit(txt, (4, 4))

        return pygame.surfarray.array3d(s).transpose(1, 0, 2)
