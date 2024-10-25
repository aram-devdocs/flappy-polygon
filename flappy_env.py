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
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)

    def reset(self):
        print("Environment reset")  # Debug statement
        self.game.reset_game()
        return self._get_observation()

    def step(self, action):
        # Only jump if action is 1 and jump cooldown allows it
        if action == 1 and self.game.bird.can_jump():
            self.game.bird.jump()
        else:
            self.game.bird.no_jump()

        # Update game state
        self.game.update_game(pygame.time.get_ticks())

        done = not self.game.game_active
        reward = 0

        # Only give reward if pipes are on screen
        if self.game.pipes:
            reward = 1  # Reward for survival with pipes present

            # Extra reward for clearing pipes
            for pipe in self.game.pipes:
                if pipe.scored:
                    reward += 5

            # Penalize collisions with pipes
            if pygame.sprite.spritecollideany(self.game.bird, self.game.pipes):
                reward -= 10
                done = True

            # Penalize touching top and bottom boundaries
            if self.game.bird.rect.top <= 0:
                reward -= 5
                done = True
            if self.game.bird.rect.bottom >= self.game.height:
                reward -= 5
                done = True

            # Find the closest pipe and calculate the center of its gap
            closest_pipe = min(
                (pipe for pipe in self.game.pipes if pipe.rect.right > self.game.bird.rect.left),
                key=lambda p: p.rect.right,
                default=None
            )

            if closest_pipe:
                # Calculate the center of the gap
                gap_center_y = (closest_pipe.rect.bottom + self.game.pipe_gap / 2) if closest_pipe.is_top else (closest_pipe.rect.top - self.game.pipe_gap / 2)
                bird_distance_from_gap = abs(self.game.bird.rect.centery - gap_center_y) / self.game.height

                # Apply a small penalty if the bird is far from the gap center
                if bird_distance_from_gap > 0.1:  # Allow some leeway around the gap center
                    reward -= 2 * bird_distance_from_gap  # Penalize proportional to distance

        return self._get_observation(), reward, done, {}
    def _get_observation(self):
        # Bird parameters
        bird_y = self.game.bird.rect.y / self.game.height
        bird_velocity = self.game.bird.velocity / 10
        bird_angle = (self.game.bird.angle + 90) / 180  # Normalize angle (-90 to +90) -> (0 to 1)

        # Pipe parameters: distance to next pipe, top and bottom pipe heights
        if self.game.pipes:
            next_pipe = min(
                self.game.pipes,
                key=lambda p: (p.rect.right if p.rect.right > self.game.bird.rect.left else float("inf")),
            )
            pipe_distance = (next_pipe.rect.x - self.game.bird.rect.x) / self.game.width
            top_pipe_height = next_pipe.rect.bottom / self.game.height if next_pipe.is_top else 0
            bottom_pipe_top = next_pipe.rect.y / self.game.height if not next_pipe.is_top else 1
        else:
            pipe_distance = 1.0  # Default to far right if no pipe exists
            top_pipe_height = 0.5  # Center default
            bottom_pipe_top = 0.5  # Center default

        # Additional game settings
        jump_strength = abs(self.game.bird.jump_strength) / 15  # Normalize to 0-1 range
        can_jump = 1 if self.game.bird.can_jump() else 0  # 1 if can jump, else 0

        return np.array(
            [
                bird_y,
                pipe_distance,
                top_pipe_height,
                bottom_pipe_top,
                jump_strength,
                bird_velocity,
                bird_angle,
                can_jump  # New observation for AI to learn jump timing
            ],
            dtype=np.float32,
        )