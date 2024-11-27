import pygame
import sys
import logging
from game.poker_game import PokerGame
from ui.game_window import GameWindow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_poker_ui.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('main')

def main():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Jacks or Better Video Poker")

    # Initialize game components
    game = PokerGame()
    game_window = GameWindow(screen, game)

    # Main game loop
    clock = pygame.time.Clock()
    needs_redraw = True  # Flag to track if redraw is needed
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_window.handle_event(event):  # Returns True if event caused state change
                needs_redraw = True

        if needs_redraw:
            screen.fill((0, 0, 0))  # Clear screen before drawing
            game_window.draw()
            pygame.display.flip()
            needs_redraw = False
            
        clock.tick(30)  # Reduce to 30 FPS since this is a card game

if __name__ == "__main__":
    main()
