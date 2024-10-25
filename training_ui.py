

import pygame

class TrainingUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 36)
        self.progress = 0

    def update_progress(self, current_steps, target_steps):
        self.progress = current_steps / target_steps

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.width - 100, 30))  # Background bar
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, (self.width - 100) * self.progress, 30))  # Progress fill
        progress_text = self.font.render(f"Training Progress: {self.progress * 100:.2f}%", True, (255, 255, 255))