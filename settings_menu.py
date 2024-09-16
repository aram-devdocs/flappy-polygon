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
        self.handle_rect.x = self.rect.x + ratio * (self.rect.width - self.handle_rect.width)
        self.handle_rect.y = self.rect.y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_rect.x = max(self.rect.x, min(event.pos[0] - self.handle_rect.width / 2, self.rect.x + self.rect.width - self.handle_rect.width))
                ratio = (self.handle_rect.x - self.rect.x) / (self.rect.width - self.handle_rect.width)
                self.value = self.min_value + ratio * (self.max_value - self.min_value)
                self.value = round(self.value, 2)  # Round for cleaner values
                self.update_handle_position()

    def draw(self, surface):
        # Draw the slider bar
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        # Draw the handle
        pygame.draw.rect(surface, (100, 100, 100), self.handle_rect)
        # Draw the label and value
        label_surface = self.font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        surface.blit(label_surface, (self.rect.x, self.rect.y - 25))

class SettingsMenu:
    def __init__(self, width, height, bird_jump_strength, pipe_speed):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 48)
        self.title_surface = self.font.render("Settings", True, (0, 0, 0))
        self.title_rect = self.title_surface.get_rect(center=(self.width // 2, 50))
        # Initialize sliders
        self.jump_strength_slider = Slider(100, 150, 200, 5, 15, abs(bird_jump_strength), "Jump Strength")
        self.pipe_speed_slider = Slider(100, 250, 200, 1, 10, pipe_speed, "Pipe Speed")
        self.sliders = [self.jump_strength_slider, self.pipe_speed_slider]
        self.active = False

    def handle_event(self, event):
        for slider in self.sliders:
            slider.handle_event(event)

    def draw(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))  # White with alpha transparency
        surface.blit(overlay, (0, 0))
        # Draw the title
        surface.blit(self.title_surface, self.title_rect)
        # Draw sliders
        for slider in self.sliders:
            slider.draw(surface)
        # Draw instructions
        instructions_font = pygame.font.SysFont(None, 24)
        instructions_surface = instructions_font.render("Press 'Esc' to return", True, (0, 0, 0))
        instructions_rect = instructions_surface.get_rect(center=(self.width // 2, self.height - 30))
        surface.blit(instructions_surface, instructions_rect)

    def get_values(self):
        return self.jump_strength_slider.value, self.pipe_speed_slider.value