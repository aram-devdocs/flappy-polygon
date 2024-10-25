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
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)

    def reset(self):
        print("Environment reset")  # Debug statement
        self.game.reset_game()
        return self._get_observation()

    def step(self, action):
        # Only jump if action is 1 and jump cooldown allows it
        print("Action taken:", action)  # Debug statement
        if action == 1 and self.game.bird.can_jump():
            self.game.bird.jump()
        else:
            self.game.bird.no_jump()

        # Update game state
        self.game.update_game(pygame.time.get_ticks())

        done = not self.game.game_active
        reward = self._calculate_reward()

        return self._get_observation(), reward, done, {}

    def _calculate_reward(self):
        reward = 0

        if self.game.pipes:
            reward += self._reward_for_survival()
            reward += self._reward_for_clearing_pipes()
            reward += self._penalty_for_hitting_obstacles()
            reward += self._penalty_for_distance_from_gap_and_edges()

        return reward

    def _reward_for_survival(self):
        return 1  # Survival reward

    def _reward_for_clearing_pipes(self):
        reward = 0
        for pipe in self.game.pipes:
            if pipe.scored:
                reward += 5  # Extra reward for clearing pipes
        return reward

    def _penalty_for_hitting_obstacles(self):
        reward = 0
        if pygame.sprite.spritecollideany(self.game.bird, self.game.pipes):
            reward -= 10
            self.game.game_active = False
        if (
            self.game.bird.rect.top <= 0
            or self.game.bird.rect.bottom >= self.game.height
        ):
            reward -= 50
            self.game.game_active = False
        return reward

    def _penalty_for_distance_from_gap_and_edges(self):
        reward = 0
        closest_pipe = self._get_closest_pipe()
        if closest_pipe:
            gap_center_y, bird_distance_from_gap = self._get_gap_center_and_distance(
                closest_pipe
            )
            if bird_distance_from_gap > 0.05:
                reward -= 5 * bird_distance_from_gap
            else:
                reward += 1  # Small positive reward for staying centered

        distance_to_top = self._get_distance_to_top()
        distance_to_bottom = self._get_distance_to_bottom()

        if distance_to_top < 0.1:
            reward -= 5 * (0.1 - distance_to_top)
        if distance_to_bottom < 0.1:
            reward -= 5 * (0.1 - distance_to_bottom)

        return reward

    def _get_observation(self):
        bird_y_ratio = self._get_bird_y_ratio()
        bird_velocity = self._get_bird_velocity()
        bird_angle_normalized = self._get_bird_angle_normalized()
        distance_from_top = self._get_distance_to_top()
        distance_from_bottom = self._get_distance_to_bottom()
        pipe_distance_ratio, gap_top_y, gap_bottom_y = self._get_pipe_info()
        time_until_jump_cooldown_over = self._get_time_until_jump_cooldown_over()

        gap_center_y, bird_distance_from_gap = self._get_gap_center_and_distance(
            self._get_closest_pipe()
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
                bird_distance_from_gap,
            ],
            dtype=np.float32,
        )

    def _get_bird_y_ratio(self):
        return self.game.bird.rect.y / self.game.height

    def _get_bird_velocity(self):
        return self.game.bird.velocity / 10

    def _get_bird_angle_normalized(self):
        return (self.game.bird.angle + 90) / 180

    def _get_closest_pipe(self):
        return min(
            (
                pipe
                for pipe in self.game.pipes
                if pipe.rect.right > self.game.bird.rect.left
            ),
            key=lambda p: p.rect.right,
            default=None,
        )

    def _get_gap_center_and_distance(self, closest_pipe):
        gap_top_y = (
            closest_pipe.rect.bottom if closest_pipe.is_top else closest_pipe.rect.y
        ) / self.game.height
        gap_bottom_y = gap_top_y + self.game.pipe_gap / self.game.height
        gap_center_y = (gap_top_y + gap_bottom_y) / 2
        bird_distance_from_gap = abs(
            self.game.bird.rect.centery / self.game.height - gap_center_y
        )
        return gap_center_y, bird_distance_from_gap

    def _get_pipe_info(self):
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

        return pipe_distance_ratio, gap_top_y, gap_bottom_y

    def _get_time_until_jump_cooldown_over(self):
        return (
            max(
                0,
                self.game.bird.jump_cooldown
                - (pygame.time.get_ticks() - self.game.bird.last_jump_time),
            )
            / 1000
        )

    def _get_distance_to_top(self):
        return self.game.bird.rect.top / self.game.height

    def _get_distance_to_bottom(self):
        return (self.game.height - self.game.bird.rect.bottom) / self.game.height
