import sys
import pygame
import random
from player_bird import PlayerBird
from pipe import Pipe
from text_object import TextObject
from settings_menu import SettingsMenu

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
        self.default_jump_strength = -10
        self.default_pipe_speed = 3

        # Initialize pipe_speed
        self.pipe_speed = self.default_pipe_speed
        self.base_pipe_interval = 1500  # Base interval in milliseconds
        self.pipe_interval = self.calculate_pipe_interval()

        self.bird = PlayerBird(50, self.height // 2, self.default_jump_strength)
        self.all_sprites.add(self.bird)
        self.last_pipe = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 48)
        self.game_over_text = TextObject("Game Over", self.font, self.width, self.height, center=True)
        self.score = 0
        self.score_text = TextObject(f"Score: {self.score}", self.font, 10, 10, center=False)

        # Instructions text
        self.instructions_text = TextObject("Press 'S' for Settings", self.font, self.width // 2, self.height - 30, center=True)

        # Settings menu
        self.settings_menu = SettingsMenu(
            self.width,
            self.height,
            abs(self.bird.jump_strength),
            abs(self.pipe_speed)
        )
        self.settings_active = False

    def calculate_pipe_interval(self):
        # Adjust interval inversely proportional to pipe speed
        base_speed = 3  # The default pipe speed
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
            if self.game_active and not self.settings_active:
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
                    # Apply new settings
                    jump_strength_value, pipe_speed_value = self.settings_menu.get_values()
                    self.bird.jump_strength = -jump_strength_value  # Negate to get negative value
                    self.pipe_speed = pipe_speed_value
                    # Recalculate pipe interval with new speed
                    self.pipe_interval = self.calculate_pipe_interval()
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
        # Recalculate pipe_interval in case pipe_speed has changed
        self.pipe_interval = self.calculate_pipe_interval()
        if current_time - self.last_pipe > self.pipe_interval:
            self.last_pipe = current_time
            pipe_height = random.randint(50, self.height - self.bird.pipe_gap - 50)
            pipe_width = 60
            top_pipe = Pipe(
                self.width,
                0,
                pipe_width,
                pipe_height,
                self.pipe_speed,
                is_top=True
            )
            bottom_pipe = Pipe(
                self.width,
                pipe_height + self.bird.pipe_gap,
                pipe_width,
                self.height - pipe_height - self.bird.pipe_gap,
                self.pipe_speed,
                is_top=False
            )
            self.pipes.add(top_pipe, bottom_pipe)
            self.all_sprites.add(top_pipe, bottom_pipe)

        self.pipes.update()
        self.check_collisions()
        self.check_score()

    def check_collisions(self):
        if pygame.sprite.spritecollideany(self.bird, self.pipes) or self.bird.rect.top < 0 or self.bird.rect.bottom > self.height:
            self.game_active = False

    def check_score(self):
        for pipe in self.pipes:
            if not pipe.scored and pipe.rect.right < self.bird.rect.left and pipe.is_top:
                pipe.scored = True
                self.score += 1
                self.score_text.update_text(f"Score: {self.score}")

    def draw(self):
        self.screen.fill((135, 206, 235))
        if self.game_active:
            self.all_sprites.draw(self.screen)
            self.score_text.draw(self.screen)
        else:
            self.game_over_text.draw(self.screen)
            self.score_text.draw_center(self.screen, y_offset=50)
        # Draw instructions
        if not self.settings_active:
            self.instructions_text.draw(self.screen)
        if self.settings_active:
            self.settings_menu.draw(self.screen)
        pygame.display.flip()