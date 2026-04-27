import numpy as np
from env import TankEnv, Goal, Tank, ROWS, COLS


class TankEnvEx(TankEnv):
    """
    Расширенная среда для экспериментов.

    Дополнительные параметры:
      random_start    — случайная стартовая позиция танка каждый эпизод
      random_goal     — случайная позиция цели каждый эпизод
      goal_move_every — цель прыгает в случайную клетку каждые N шагов (0 = выкл)
      goal_flees      — цель убегает от танка каждый шаг (охотник-жертва)
      seed            — seed для генератора случайных чисел
    """

    def __init__(self, grid=None, tank_start=(1, 1), goal_pos=(8, 8),
                 max_steps=200, rewards=None,
                 random_start=False, random_goal=False,
                 goal_move_every=0, goal_flees=False, seed=0):
        self.random_start    = random_start
        self.random_goal     = random_goal
        self.goal_move_every = goal_move_every
        self.goal_flees      = goal_flees
        self._rng            = np.random.default_rng(seed)
        # free_cells заполним после того как grid известен
        super().__init__(grid=grid, tank_start=tank_start, goal_pos=goal_pos,
                         max_steps=max_steps, rewards=rewards)
        self._free_cells = [(r, c) for r in range(ROWS) for c in range(COLS)
                            if self.grid[r][c] == 0]

    # ------------------------------------------------------------------
    def _random_free(self, exclude=()):
        choices = [c for c in self._free_cells if c not in exclude]
        idx = self._rng.integers(len(choices))
        return choices[idx]

    def reset(self):
        if self.random_start:
            sr, sc = self._random_free()
        else:
            sr, sc = self.tank_start

        if self.random_goal:
            gr, gc = self._random_free(exclude=((sr, sc),))
        else:
            gr, gc = self.goal_pos

        self.tank       = Tank(sr, sc, angle=0)
        self.goal       = Goal(gr, gc)
        self.steps      = 0
        self._prev_dist = self._dist()
        return self._observe()

    def step(self, action):
        obs, reward, done = super().step(action)

        if not done and self.goal_move_every > 0 and self.steps % self.goal_move_every == 0:
            nr, nc = self._random_free(exclude=((self.tank.row, self.tank.col),))
            self.goal = Goal(nr, nc)
            self._prev_dist = self._dist()

        if not done and self.goal_flees:
            self._flee_goal()

        return self._observe(), reward, done

    def _flee_goal(self):
        """Цель уходит в соседнюю клетку максимально далёкую от танка."""
        tr, tc = self.tank.row, self.tank.col
        gr, gc = self.goal.row, self.goal.col
        candidates = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = gr + dr, gc + dc
            if self._is_free(nr, nc):
                candidates.append((abs(nr - tr) + abs(nc - tc), nr, nc))
        if candidates:
            _, nr, nc = max(candidates)
            self.goal = Goal(nr, nc)
            self._prev_dist = self._dist()
