import pygame

class TrainingUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 24)
        self.progress = 0
        self.observations = {}  # Placeholder for observed values
        self.current_score = 0
        self.total_score = 0
        self.highest_score = 0  # Track the highest score
        self.action_history = []  # Track recent actions for decision insights

    def update_progress(self, current_steps, target_steps):
        self.progress = current_steps / target_steps

    def update_observations(self, observations, current_score, action):
        self.observations = observations
        self.current_score = current_score
        self.action_history.append(action)
        if len(self.action_history) > 10:  # Limit history to last 10 actions
            self.action_history.pop(0)

    def update_scores(self, reward, done):
        """Update scores based on rewards and reset when episode ends."""
        self.current_score += reward
        if done:
            # End of episode: update highest score if current score exceeds it
            self.highest_score = max(self.highest_score, self.current_score)
            self.total_score += self.current_score  # Add current score to total score
            self.current_score = 0  # Reset current score for next episode

    def draw(self, screen):
        # Draw training progress bar
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, self.width - 100, 30))  # Background bar
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, (self.width - 100) * self.progress, 30))  # Progress fill
        progress_text = self.font.render(f"Training Progress: {self.progress * 100:.2f}%", True, (255, 255, 255))
        screen.blit(progress_text, (50, 90))

        # Display observations
        y_offset = 140
        for key, value in self.observations.items():
            obs_text = self.font.render(f"{key}: {value:.3f}", True, (255, 255, 255))
            screen.blit(obs_text, (50, y_offset))
            y_offset += 30

        # Display score metrics
        score_text = self.font.render(f"Current Score: {self.current_score}", True, (255, 255, 255))
        screen.blit(score_text, (50, y_offset))
        y_offset += 30
        total_score_text = self.font.render(f"Total Score: {self.total_score}", True, (255, 255, 255))
        screen.blit(total_score_text, (50, y_offset))
        y_offset += 30
        highest_score_text = self.font.render(f"Highest Score: {self.highest_score}", True, (255, 255, 255))
        screen.blit(highest_score_text, (50, y_offset))
        y_offset += 30

        # Display recent action history
        action_text = self.font.render(f"Recent Actions: {self.action_history}", True, (255, 255, 255))
        screen.blit(action_text, (50, y_offset))