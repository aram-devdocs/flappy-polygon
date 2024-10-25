import gym
from gym import spaces
import numpy as np
import pygame


class FlappyEnv(gym.Env):
    def __init__(self, game):
        super(FlappyEnv, self).__init__()
        self.game = game
        self.action_space = spaces.Discrete(2)  # 0 for no action, 1 for jump
        # Define observation space with detailed, descriptive inputs
        self.observation_space = spaces.Box(low=0, high=1, shape=(9,), dtype=np.float32)

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

        if self.game.pipes:
            reward = 1  # Survival reward

            for pipe in self.game.pipes:
                if pipe.scored:
                    reward += 5  # Extra reward for clearing pipes

            # Penalize for hitting obstacles
            if pygame.sprite.spritecollideany(self.game.bird, self.game.pipes):
                reward -= 10
                done = True
            if (
                self.game.bird.rect.top <= 0
                or self.game.bird.rect.bottom >= self.game.height
            ):
                reward -= 5
                done = True

            # Calculate gap center and bird's distance from it
            closest_pipe = min(
                (
                    pipe
                    for pipe in self.game.pipes
                    if pipe.rect.right > self.game.bird.rect.left
                ),
                key=lambda p: p.rect.right,
                default=None,
            )

            if closest_pipe:
                gap_top_y = (
                    closest_pipe.rect.bottom
                    if closest_pipe.is_top
                    else closest_pipe.rect.y
                ) / self.game.height
                gap_bottom_y = (
                    gap_top_y + self.game.pipe_gap / self.game.height
                )  # Add normalized gap height

                # Apply a small penalty if the bird is far from the gap center
                gap_center_y = (gap_top_y + gap_bottom_y) / 2
                bird_distance_from_gap = abs(
                    self.game.bird.rect.centery / self.game.height - gap_center_y
                )
                if bird_distance_from_gap > 0.1:
                    reward -= 2 * bird_distance_from_gap

        return self._get_observation(), reward, done, {}

    def _get_observation(self):
        # Bird state
        bird_y_ratio = self.game.bird.rect.y / self.game.height
        bird_velocity = self.game.bird.velocity / 10
        bird_angle_normalized = (
            self.game.bird.angle + 90
        ) / 180  # Normalize angle (-90 to +90) -> (0 to 1)

        # Distance from top and bottom
        distance_from_top = bird_y_ratio
        distance_from_bottom = 1 - bird_y_ratio

        # Pipe gap information
        if self.game.pipes:
            next_pipe = min(
                self.game.pipes,
                key=lambda p: (
                    p.rect.right
                    if p.rect.right > self.game.bird.rect.left
                    else float("inf")
                ),
            )
            pipe_distance_ratio = (
                next_pipe.rect.x - self.game.bird.rect.x
            ) / self.game.width

            gap_top_y = (
                (next_pipe.rect.bottom / self.game.height)
                if next_pipe.is_top
                else (next_pipe.rect.y / self.game.height)
            )
            gap_bottom_y = gap_top_y + (self.game.pipe_gap / self.game.height)
        else:
            pipe_distance_ratio = 1.0  # Default to far right if no pipe exists
            gap_top_y = 0.5  # Default center if no pipe
            gap_bottom_y = 0.5

        # Time until next possible jump
        time_until_jump_cooldown_over = (
            max(
                0,
                self.game.bird.jump_cooldown
                - (pygame.time.get_ticks() - self.game.bird.last_jump_time),
            )
            / 1000
        )

        return np.array(
            [
                bird_y_ratio,
                bird_velocity,
                bird_angle_normalized,
                distance_from_top,
                distance_from_bottom,
                pipe_distance_ratio,
                gap_top_y,
                gap_bottom_y,
                time_until_jump_cooldown_over,
            ],
            dtype=np.float32,
        )
