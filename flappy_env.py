import gym
from gym import spaces
import numpy as np
import pygame

class FlappyEnv(gym.Env):
    def __init__(self, game):
        super(FlappyEnv, self).__init__()
        self.game = game
        self.action_space = spaces.Discrete(2)  # 0 for no action, 1 for jump
        # Define observation space with new inputs:
        # bird height, distance to next pipe, top and bottom pipe heights, jump strength, velocity, and angle
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(7,), dtype=np.float32
        )

    def reset(self):
        print("Environment reset")  # Debug statement
        self.game.reset_game()
        return self._get_observation()

    def step(self, action):
        # Apply action
        if action == 1:
            self.game.bird.jump()
        else:
            self.game.bird.no_jump()
        
        # Update game state
        self.game.update_game(pygame.time.get_ticks())
        
        # Calculate rewards and penalties
        done = not self.game.game_active
        reward = 1  # Reward for staying alive

        # Penalty if the bird hits a pipe
        if pygame.sprite.spritecollideany(self.game.bird, self.game.pipes):
            reward -= 10

        # Penalty for touching the top of the screen
        if self.game.bird.rect.top <= 0:
            reward -= 5
            done = True  # End the episode if it touches the top

        # Penalty for touching the bottom of the screen
        if self.game.bird.rect.bottom >= self.game.height:
            reward -= 5
            done = True  # End the episode if it touches the bottom

        # Return new observation, reward, and done flag
        return self._get_observation(), reward, done, {}

    def _get_observation(self):
        # Bird parameters
        bird_y = self.game.bird.rect.y / self.game.height
        bird_velocity = self.game.bird.velocity / 10
        bird_angle = (self.game.bird.angle + 90) / 180  # Normalize angle (-90 to +90) -> (0 to 1)

        # Pipe parameters: distance to next pipe, top and bottom pipe heights
        if self.game.pipes:
            next_pipe = min(self.game.pipes, key=lambda p: p.rect.right if p.rect.right > self.game.bird.rect.left else float('inf'))
            pipe_distance = (next_pipe.rect.x - self.game.bird.rect.x) / self.game.width
            top_pipe_height = next_pipe.rect.bottom / self.game.height if next_pipe.is_top else 0
            bottom_pipe_top = next_pipe.rect.y / self.game.height if not next_pipe.is_top else 1
        else:
            pipe_distance = 1.0  # Default to far right if no pipe exists
            top_pipe_height = 0.5  # Center default
            bottom_pipe_top = 0.5  # Center default

        # Additional game settings
        jump_strength = abs(self.game.bird.jump_strength) / 15  # Normalize to 0-1 range

        return np.array([
            bird_y,
            pipe_distance,
            top_pipe_height,
            bottom_pipe_top,
            jump_strength,
            bird_velocity,
            bird_angle
        ], dtype=np.float32)