import pygame
from game_loop import GameLoop

def main():
    pygame.init()
    WIDTH, HEIGHT = 400, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game = GameLoop(screen, clock)
    game.run()

if __name__ == "__main__":
    main()