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
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(11,), dtype=np.float32
        )

    def reset(self):
        print("Environment reset")  # Debug statement
        self.game.reset_game()
        return self._get_observation()

    def step(self, action, current_time):

        print("Action taken:", action)  # Debug statement
        # Only take the action every 150 milliseconds
        if (
            current_time - self.game.last_training_time >= 150
        ):  # 0.1 second = 100 milliseconds
            if action == 1 and self.game.bird.can_jump():
                self.game.bird.jump()
            else:
                self.game.bird.no_jump()

            # Each Step
            self.game.last_training_time = current_time
            self.game.current_steps += 1

        # Update game state
        self.game.update_game(pygame.time.get_ticks())

        done = not self.game.game_active
        reward = self._calculate_reward()

        return self._get_observation(), reward, done, {}

    def _calculate_reward(self):
        reward = 0

        if self.game.pipes:
            reward += self._reward_for_clearing_pipes()
            reward += self._penalty_for_hitting_obstacles()
            reward += self._pentalty_for_being_near_top_or_bottom()
            reward += self._reward_for_being_in_gap()
        else:
            reward += self._reward_for_staying_in_middle_when_no_pipes()

        reward += self._reward_for_survival()

        return reward

    def _reward_for_survival(self):
        return 0.5  # Survival reward

    def _reward_for_clearing_pipes(self):
        reward = 0
        for pipe in self.game.pipes:
            if pipe.scored and not pipe.trained:
                reward += 5  # Extra reward for clearing pipes
                pipe.trained = True
        return reward

    def _reward_for_staying_in_middle_when_no_pipes(self):
        if (
            not self.game.pipes
            and abs(self.game.bird.rect.centery - self.game.height / 2)
            < 0.15 * self.game.height
        ):
            return 0.1
        return 0

    def _penalty_for_hitting_obstacles(self):
        reward = 0
        if pygame.sprite.spritecollideany(self.game.bird, self.game.pipes):
            reward -= 10
            self.game.game_active = False
        if (
            self.game.bird.rect.top <= 0
            or self.game.bird.rect.bottom >= self.game.height
        ):
            reward -= 15
            self.game.game_active = False
        return reward

    def _pentalty_for_being_near_top_or_bottom(self):
        distance_from_border_where_penalty_starts = 0.2 * self.game.height
        penalty_scale_factor = 0.1

        if self.game.bird.rect.top < distance_from_border_where_penalty_starts:
            distance_to_top = distance_from_border_where_penalty_starts - self.game.bird.rect.top
            penalty = -penalty_scale_factor * np.exp(distance_to_top / distance_from_border_where_penalty_starts)
            return penalty

        if self.game.bird.rect.bottom > self.game.height - distance_from_border_where_penalty_starts:
            distance_to_bottom = self.game.bird.rect.bottom - (self.game.height - distance_from_border_where_penalty_starts)
            penalty = -penalty_scale_factor * np.exp(distance_to_bottom / distance_from_border_where_penalty_starts)
            return penalty

        return 0

    def _reward_for_being_in_gap(self):
        if self._is_in_gap():
            return 1
        return 0

    def _get_observation(self):
        bird_y_ratio = self._get_bird_y_ratio()
        bird_velocity = self._get_bird_velocity()
        bird_angle_normalized = self._get_bird_angle_normalized()
        distance_from_top = self._get_distance_to_top()
        distance_from_bottom = self._get_distance_to_bottom()
        pipe_distance_ratio, gap_top_y, gap_bottom_y = self._get_pipe_info()
        time_until_jump_cooldown_over = self._get_time_until_jump_cooldown_over()
        is_in_gap = 1 if self._is_in_gap() else 0

        gap_center_y, bird_y_distance_from_gap_center_y = (
            self._get_gap_center_and_distance(self._get_closest_pipe())
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
                bird_y_distance_from_gap_center_y,
                is_in_gap,
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
        # if no pipe, return middle of screen
        if closest_pipe is None:
            center = 0.5
            # calculate distance from mock gap center
            return center, self.game.bird.rect.centery / self.game.height - center

        gap_top_y = (
            closest_pipe.rect.bottom if closest_pipe.is_top else closest_pipe.rect.y
        ) / self.game.height
        gap_bottom_y = gap_top_y + self.game.pipe_gap / self.game.height
        gap_center_y = (gap_top_y + gap_bottom_y) / 2

        bird_y_distance_from_gap_center_y = (
            self.game.bird.rect.centery / self.game.height - gap_center_y
        )
        return gap_center_y, bird_y_distance_from_gap_center_y

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
            gap_top_y = 0.3  # Default center if no pipe
            gap_bottom_y = 0.7  # Default center if no pipe

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

    def _is_in_gap(self) -> bool:
        bird_y = self.game.bird.rect.centery
        # if bird_y is less than   greater than gap top Y and less than gap bottom Y, return True else False
        pipe_distance_ratio, gap_top_y, gap_bottom_y = self._get_pipe_info()
        
        if bird_y > gap_top_y * self.game.height and bird_y < gap_bottom_y * self.game.height:
            return True 
        return False