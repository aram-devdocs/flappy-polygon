import os
import pygame


class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.handle_rect = pygame.Rect(0, 0, 10, 20)
        self.update_handle_position()
        self.dragging = False
        self.font = pygame.font.SysFont(None, 24)

    def update_handle_position(self):
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        self.handle_rect.x = self.rect.x + ratio * (
            self.rect.width - self.handle_rect.width
        )
        self.handle_rect.y = self.rect.y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_rect.x = max(
                    self.rect.x,
                    min(
                        event.pos[0] - self.handle_rect.width / 2,
                        self.rect.x + self.rect.width - self.handle_rect.width,
                    ),
                )
                ratio = (self.handle_rect.x - self.rect.x) / (
                    self.rect.width - self.handle_rect.width
                )
                self.value = self.min_value + ratio * (self.max_value - self.min_value)
                self.value = round(self.value, 2)
                self.update_handle_position()

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.handle_rect)
        label_surface = self.font.render(
            f"{self.label}: {self.value:.2f}", True, (0, 0, 0)
        )
        surface.blit(label_surface, (self.rect.x, self.rect.y - 25))


class Toggle:
    def __init__(self, x, y, label, initial_state=False):
        self.rect = pygame.Rect(x, y, 40, 20)
        self.state = initial_state
        self.label = label
        self.font = pygame.font.SysFont(None, 24)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 255, 0) if self.state else (255, 0, 0), self.rect)
        label_surface = self.font.render(
            f"{self.label}: {'On' if self.state else 'Off'}", True, (0, 0, 0)
        )
        surface.blit(label_surface, (self.rect.x + 50, self.rect.y))


class SettingsMenu:
    def __init__(
        self,
        width,
        height,
        bird_jump_strength,
        pipe_speed,
        training_steps,
        learning_rate,
        training_mode=False,
    ):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 48)
        self.title_surface = self.font.render("Settings", True, (0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(self.width // 2, 50))

        # Initialize sliders
        self.jump_strength_slider = Slider(
            100, 150, 200, 5, 15, abs(bird_jump_strength), "Jump Strength"
        )
        self.pipe_speed_slider = Slider(100, 250, 200, 1, 10, pipe_speed, "Pipe Speed")
        self.training_steps_slider = Slider(
            100, 350, 200, 1000, 50000, training_steps, "Training Steps"
        )
        # learning rate for PPO
        self.learning_rate_slider = Slider(
            100, 450, 200, 0.0001, 0.1, learning_rate, "Learning Rate"
        )

        # Training mode toggle
        self.training_mode_toggle = Toggle(
            100, 550, "Training Mode", initial_state=training_mode
        )

        self.sliders = [
            self.jump_strength_slider,
            self.pipe_speed_slider,
            self.training_steps_slider,
            self.learning_rate_slider,
        ]
        self.active = False

    def handle_event(self, event):
        for slider in self.sliders:
            slider.handle_event(event)
        self.training_mode_toggle.handle_event(event)

    def draw(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))
        surface.blit(overlay, (0, 0))

        # Draw the title
        surface.blit(self.title_surface, self.title_rect)

        # Draw sliders and toggle
        for slider in self.sliders:
            slider.draw(surface)
        self.training_mode_toggle.draw(surface)

        instructions_font = pygame.font.SysFont(None, 16)
        instructions_surface = instructions_font.render(
            "Press 'Esc' to return", True, (0, 0, 0)
        )
        instructions_rect = instructions_surface.get_rect(
            center=(self.width // 2, self.height - 30)
        )
        surface.blit(instructions_surface, instructions_rect)

    def get_values(self):
        return (
            self.jump_strength_slider.value,
            self.pipe_speed_slider.value,
            self.training_mode_toggle.state,
            self.training_steps_slider.value,
            self.learning_rate_slider.value,
        )

    def save_training_results(self, model, file_path="ppo_flappy.zip"):
        model.save(file_path)
        print(f"Training results saved to {file_path}")

    def load_training_results(self, model, file_path="ppo_flappy.zip"):
        if os.path.exists(file_path):
            model.load(file_path)
            print(f"Training results loaded from {file_path}")
        else:
            print(f"File {file_path} not found. Starting fresh.")
