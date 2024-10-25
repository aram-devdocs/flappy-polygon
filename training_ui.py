import pygame

class TrainingUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 24)
        self.progress = 0
        # Placeholder for observed values
        self.observations = {}

    def update_progress(self, current_steps, target_steps):
        self.progress = current_steps / target_steps

    def update_observations(self, observations):
        # Accepts an observation dictionary
        self.observations = observations

    def draw(self, screen):
        # Draw training progress bar
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.width - 100, 30))  # Background bar
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, (self.width - 100) * self.progress, 30))  # Progress fill
        progress_text = self.font.render(f"Training Progress: {self.progress * 100:.2f}%", True, (255, 255, 255))
        screen.blit(progress_text, (50, 90))

        # Display each observation parameter
        y_offset = 140
        for key, value in self.observations.items():
            obs_text = self.font.render(f"{key}: {value:.3f}", True, (255, 255, 255))
            screen.blit(obs_text, (50, y_offset))
            y_offset += 30