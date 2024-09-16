import sys
import pygame
import random
from player_bird import PlayerBird
from pipe import Pipe
from text_object import TextObject

class GameLoop:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        self.running = True
        self.game_active = True
        self.all_sprites = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.bird = PlayerBird(50, self.height // 2)
        self.all_sprites.add(self.bird)
        self.pipe_interval = 1500  # milliseconds
        self.last_pipe = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, 48)
        self.game_over_text = TextObject("Game Over", self.font, self.width, self.height, center=True)
        self.gravity = 0.5
        self.pipe_speed = 3
        self.score = 0
        self.score_text = TextObject(f"Score: {self.score}", self.font, 10, 10, center=False)

    def reset_game(self):
        self.game_active = True
        self.all_sprites.empty()
        self.pipes.empty()
        self.bird = PlayerBird(50, self.height // 2)
        self.all_sprites.add(self.bird)
        self.last_pipe = pygame.time.get_ticks()
        self.score = 0
        self.score_text.update_text(f"Score: {self.score}")

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            current_time = pygame.time.get_ticks()
            self.handle_events()
            if self.game_active:
                self.update_game(current_time)
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.game_active:
                    self.bird.jump()
                else:
                    self.reset_game()

    def update_game(self, current_time):
        self.bird.update(self.gravity)
        if current_time - self.last_pipe > self.pipe_interval:
            self.last_pipe = current_time
            pipe_height = random.randint(50, self.height - self.bird.pipe_gap - 50)
            pipe_width = 60  # You can adjust this for wider/narrower pipes
            top_pipe = Pipe(self.width, 0, pipe_width, pipe_height, self.pipe_speed, is_top=True)
            bottom_pipe = Pipe(self.width, pipe_height + self.bird.pipe_gap, pipe_width, self.height - pipe_height - self.bird.pipe_gap, self.pipe_speed, is_top=False)
            self.pipes.add(top_pipe, bottom_pipe)
            self.all_sprites.add(top_pipe, bottom_pipe)

        self.pipes.update()
        self.check_collisions()
        self.check_score()

    def check_collisions(self):
        if pygame.sprite.spritecollideany(self.bird, self.pipes) or self.bird.rect.top < 0 or self.bird.rect.bottom > self.height:
            self.game_active = False

    def check_score(self):
        # Increase score when the bird passes the middle of a pipe pair
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
        pygame.display.flip()