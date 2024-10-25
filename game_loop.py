import sys
import pygame
import random
from player_bird import PlayerBird
from pipe import Pipe
from text_object import TextObject
from settings_menu import SettingsMenu
from stable_baselines3 import PPO
from flappy_env import FlappyEnv
from training_ui import TrainingUI
import random

class GameLoop:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.game_active = True
        self.all_sprites = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.gravity = 0.5
        self.default_jump_strength = -7.8
        self.default_pipe_speed = 2.4

        # Initialize pipe_speed and pipe_interval
        self.pipe_speed = self.default_pipe_speed
        self.base_pipe_interval = 1500
        self.pipe_interval = self.calculate_pipe_interval()

        # Pipe gap
        self.pipe_gap = 150

        self.bird = PlayerBird(50, self.height // 2, self.default_jump_strength)
        self.all_sprites.add(self.bird)
        self.last_pipe = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 48)
        self.game_over_text = TextObject(
            "Game Over", self.font, self.width // 2, self.height // 2, center=True
        )
        self.score = 0
        self.score_text = TextObject(
            f"Score: {self.score}", self.font, 10, 10, center=False
        )

        # Instructions text
        self.instructions_text = TextObject(
            "Press 'S' for Settings",
            self.font,
            self.width // 2,
            self.height - 30,
            center=True,
        )

        # Settings menu and Training UI
        self.settings_menu = SettingsMenu(
            self.width,
            self.height,
            abs(self.bird.jump_strength),
            abs(self.pipe_speed),
            training_mode=False,
        )
        self.settings_active = False
        self.training_active = False
        self.training_ui = TrainingUI(self.width, self.height)

        # Initialize PPO Model
        self.env = FlappyEnv(self)
        self.model = PPO("MlpPolicy", self.env, verbose=1)
        self.training_steps = 10000
        self.current_steps = 0

    def calculate_pipe_interval(self):
        base_speed = 3
        interval = self.base_pipe_interval * (base_speed / self.pipe_speed)
        return interval

    def reset_game(self):
        self.game_active = True
        self.all_sprites.empty()
        self.pipes.empty()
        self.bird = PlayerBird(50, self.height // 2, self.bird.jump_strength)
        self.all_sprites.add(self.bird)
        self.last_pipe = pygame.time.get_ticks()
        self.score = 0
        self.score_text.update_text(f"Score: {self.score}")

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            current_time = pygame.time.get_ticks()
            self.handle_events()

            if self.training_active:
                self.train_and_update_game(current_time)
            elif self.game_active and not self.settings_active:
                self.update_game(current_time)

            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.settings_active:
                self.settings_menu.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.settings_active = False
                    # Unpack values from settings menu
                    (
                        jump_strength,
                        pipe_speed,
                        training_mode,
                        training_steps,
                        learning_rate,
                    ) = self.settings_menu.get_values()

                    # Apply jump strength and pipe speed settings
                    self.bird.jump_strength = -jump_strength
                    self.pipe_speed = pipe_speed
                    self.pipe_interval = self.calculate_pipe_interval()

                    # Check if training mode has changed
                    if training_mode != self.training_active:
                        self.training_active = training_mode
                        self.reset_game()  # Reset game state

                    # Apply training parameters
                    self.training_steps = int(training_steps)
                    self.model.learning_rate = learning_rate
                elif (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_k
                ):  # Save the model when 'K' is pressed
                    self.settings_menu.save_training_results(self.model)

                elif (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_l
                ):  # Load the model when 'L' is pressed
                    self.settings_menu.load_training_results(self.model)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_active:
                            self.bird.jump()
                        else:
                            self.reset_game()
                    elif event.key == pygame.K_s:
                        self.settings_active = True

    def update_game(self, current_time):
        self.bird.update(self.gravity)
        self.pipe_interval = self.calculate_pipe_interval()
        if current_time - self.last_pipe > self.pipe_interval:
            self.last_pipe = current_time
            pipe_height = random.randint(50, self.height - self.pipe_gap - 50)
            pipe_width = 60
            top_pipe = Pipe(
                self.width, 0, pipe_width, pipe_height, self.pipe_speed, is_top=True
            )
            bottom_pipe = Pipe(
                self.width,
                pipe_height + self.pipe_gap,
                pipe_width,
                self.height - pipe_height - self.pipe_gap,
                self.pipe_speed,
                is_top=False,
            )
            self.pipes.add(top_pipe, bottom_pipe)
            self.all_sprites.add(top_pipe, bottom_pipe)
        self.pipes.update()
        self.check_collisions()
        self.check_score()

    def check_collisions(self):
        if (
            pygame.sprite.spritecollideany(self.bird, self.pipes)
            or self.bird.rect.top < 0
            or self.bird.rect.bottom > self.height
        ):
            self.game_active = False

    def check_score(self):
        for pipe in self.pipes:
            if (
                not pipe.scored
                and pipe.rect.right < self.bird.rect.left
                and pipe.is_top
            ):
                pipe.scored = True
                self.score += 1
                self.score_text.update_text(f"Score: {self.score}")

    def train_and_update_game(self, current_time):
        obs = self.env._get_observation()
        
        # Action selection with exploration
        if self.current_steps < 1000:
            action = random.choice([0, 1])
        else:
            action, _ = self.model.predict(obs, deterministic=False)

        _, reward, done, _ = self.env.step(action)

        # Debug output for action and reward
        print(f"Action: {'Jump' if action == 1 else 'No Jump'}, Reward: {reward}, Done: {done}")

        # Reward and score tracking
        self.training_ui.current_score += reward

        if done:
            self.training_ui.total_score += self.training_ui.current_score
            self.training_ui.current_score = 0
            self.env.reset()
        
        # Update training UI with observations
        observation_labels = {
            "Bird Height": obs[0],
            "Pipe Distance": obs[1],
            "Top Pipe Height": obs[2],
            "Bottom Pipe Top": obs[3],
            "Jump Strength": obs[4],
            "Velocity": obs[5],
            "Angle": obs[6],
        }
        self.training_ui.update_observations(observation_labels, self.training_ui.current_score, action)

    def draw(self):
        self.screen.fill((135, 206, 235))
        if self.training_active:
            self.all_sprites.draw(self.screen)
            self.score_text.draw(self.screen)
            self.training_ui.draw(self.screen)  # Display training progress
        elif self.game_active:
            self.all_sprites.draw(self.screen)
            self.score_text.draw(self.screen)
        else:
            self.game_over_text.draw(self.screen)
            self.score_text.draw_center(self.screen, y_offset=50)

        if not self.settings_active:
            self.instructions_text.draw(self.screen)
        if self.settings_active:
            self.settings_menu.draw(self.screen)
        pygame.display.flip()
