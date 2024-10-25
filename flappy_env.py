import gym
from gym import spaces
import numpy as np
import pygame

class FlappyEnv(gym.Env):
    def __init__(self, game):
        super(FlappyEnv, self).__init__()
        self.game = game
        self.action_space = spaces.Discrete(2)  # 0 for no action, 1 for jump
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(4,), dtype=np.float32
        )  # Example shape; adjust as needed for your observations

    def reset(self):
        print("Environment reset")  # Debug statement
        self.game.reset_game()
        return self._get_observation()

    def step(self, action):
        if action == 1:
            self.game.bird.jump()

        self.game.update_game(pygame.time.get_ticks())
        
        done = not self.game.game_active
        reward = 1 if self.game.game_active else -10  # Positive reward for survival, negative for game over

        return self._get_observation(), reward, done, {}

    def _get_observation(self):
        bird_y = self.game.bird.rect.y / self.game.height
        bird_velocity = self.game.bird.velocity / 10
        # Check if there are pipes, and set pipe_x to screen width if empty
        if self.game.pipes:
            pipe_x = min(pipe.rect.x for pipe in self.game.pipes) / self.game.width
            pipe_gap_y = (self.game.pipes.sprites()[0].rect.bottom + self.game.pipe_gap / 2) / self.game.height
        else:
            pipe_x = 1.0  # Default to the right edge of the screen
            pipe_gap_y = 0.5  # Center of the screen

        return np.array([bird_y, bird_velocity, pipe_x, pipe_gap_y], dtype=np.float32)

