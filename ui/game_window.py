import os
import pygame
from game.poker_game import PokerGame
from game.logger import game_logger
import logging

class GameWindow:
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GOLD = (218, 165, 32)
    GRAY = (128, 128, 128)
    
    def __init__(self, screen, game: PokerGame):
        self.logger = logging.getLogger('game_window')
        self.logger.setLevel(logging.DEBUG)
        self.screen = screen
        self.game = game
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Card dimensions
        self.CARD_WIDTH = 100
        self.CARD_HEIGHT = 145
        self.CORNER_RADIUS = 10
        
        # Load suit images
        self.suit_images = {}
        self.load_suit_images()
        
        # Calculate card positions
        self.CARD_SPACING = 20
        total_width = (self.CARD_WIDTH * 5) + (self.CARD_SPACING * 4)
        start_x = (self.width - total_width) // 2
        self.card_positions = [(start_x + i * (self.CARD_WIDTH + self.CARD_SPACING), 200) 
                              for i in range(5)]
        
        # Button dimensions
        self.button_width = 100
        self.button_height = 40
        self.hold_button_height = 30
        
        # Hold buttons
        self.hold_buttons = [None] * 5  # Initialize array for hold button rectangles
        
        # Initialize fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 36)
        self.text_font = pygame.font.SysFont('Arial', 24)
        self.card_font = pygame.font.SysFont('Arial', 40)  # For card ranks
        self.big_font = pygame.font.SysFont('Arial', 48)  # For big announcements
        
        # Win message
        self.show_win_message = False
        self.win_message = ""
        
        # Endurance test mode
        self.endurance_mode = False
        self.hands_played = 0
        self.total_hands = 0
        self.starting_credits = 0
        
    def load_suit_images(self):
        cards_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'cards')
        
        # Load suit images
        for suit in ['heart', 'diamond', 'club', 'spade']:
            filepath = os.path.join(cards_dir, f'suit-{suit}.png')
            image = pygame.image.load(filepath)
            # Scale suit image smaller for sharper appearance
            scaled_size = (self.CARD_WIDTH // 4, self.CARD_WIDTH // 4)  
            self.suit_images[suit] = pygame.transform.scale(image, scaled_size)
            
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        
    def draw_card(self, card, x, y, face_up=True, card_index=None):
        self.logger.debug(f"Drawing card {card_index+1}: {card} at position ({x}, {y})")
        
        # Draw card background
        card_rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        if not face_up:
            # Draw card back
            self.draw_rounded_rect(self.screen, self.BLUE, card_rect, self.CORNER_RADIUS)
            # Add pattern to card back
            pattern_rect = card_rect.inflate(-20, -20)
            pygame.draw.rect(self.screen, self.WHITE, pattern_rect, 2, border_radius=self.CORNER_RADIUS)
            return
            
        # Draw white card face with black border
        self.draw_rounded_rect(self.screen, self.WHITE, card_rect, self.CORNER_RADIUS)
        pygame.draw.rect(self.screen, self.BLACK, card_rect, 2, border_radius=self.CORNER_RADIUS)
        
        # Set color based on suit
        color = self.RED if card.suit in ['♥', '♦'] else self.BLACK
        
        # Draw rank in corners
        rank_text = self.card_font.render(card.rank, True, color)
        small_rank = self.text_font.render(card.rank, True, color)
        
        # Top-left rank
        self.screen.blit(rank_text, (x + 5, y + 5))
        
        # Bottom-right rank (upside down)
        rotated_rank = pygame.transform.rotate(small_rank, 180)
        self.screen.blit(rotated_rank, (x + self.CARD_WIDTH - 25, y + self.CARD_HEIGHT - 25))
        
        # Map card suit to image key
        suit_map = {'♠': 'spade', '♥': 'heart', '♦': 'diamond', '♣': 'club'}
        suit_key = suit_map[card.suit]
        suit_image = self.suit_images[suit_key]
        
        # Draw suit image in center (slightly smaller)
        suit_rect = suit_image.get_rect()
        suit_rect.center = (x + self.CARD_WIDTH // 2, y + self.CARD_HEIGHT // 2)
        self.screen.blit(suit_image, suit_rect)
        
        # Draw small suits in corners (even smaller for corners)
        small_suit = pygame.transform.scale(suit_image, 
                                         (suit_image.get_width() // 3,  
                                          suit_image.get_height() // 3))
        
        # Top-left suit
        self.screen.blit(small_suit, (x + 5, y + 30))
        
        # Bottom-right suit (rotated)
        rotated_suit = pygame.transform.rotate(small_suit, 180)
        self.screen.blit(rotated_suit, 
                        (x + self.CARD_WIDTH - 15 - small_suit.get_width(),  
                         y + self.CARD_HEIGHT - 45))
        
        # Draw hold button if in holding state
        if self.game.game_state == "holding" and card_index is not None:
            hold_rect = pygame.Rect(x, y + self.CARD_HEIGHT + 10, self.CARD_WIDTH, 30)
            self.hold_buttons[card_index] = hold_rect  # Store the hold button rect for click detection
            color = self.RED if self.game.hand[card_index].held else self.GRAY
            pygame.draw.rect(self.screen, color, hold_rect)
            hold_text = self.text_font.render("HOLD", True, self.WHITE)
            text_rect = hold_text.get_rect(center=hold_rect.center)
            self.screen.blit(hold_text, text_rect)
            self.logger.debug(f"Drew HOLD text for card {card_index+1}")
            
    def draw(self):
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw title
        if self.endurance_mode:
            title = self.title_font.render("Endurance Test Mode", True, self.RED)
            stats = self.text_font.render(f"Hand {self.hands_played}/{self.total_hands}", True, self.WHITE)
            profit_loss = self.game.credits - self.starting_credits
            profit_color = self.GREEN if profit_loss >= 0 else self.RED
            profit_text = self.text_font.render(f"Profit/Loss: {profit_loss}", True, profit_color)
            
            self.screen.blit(title, ((self.width - title.get_width()) // 2, 20))
            self.screen.blit(stats, ((self.width - stats.get_width()) // 2, 60))
            self.screen.blit(profit_text, ((self.width - profit_text.get_width()) // 2, 90))
        else:
            title = self.title_font.render("Jacks or Better", True, self.GOLD)
            self.screen.blit(title, ((self.width - title.get_width()) // 2, 20))
        
        self.draw_credits_and_bet()
        
        # Initialize hold buttons array
        self.hold_buttons = [None] * 5
        
        # Draw cards
        for i, card in enumerate(self.game.hand):
            card_x, card_y = self.card_positions[i]
            self.draw_card(card, card_x, card_y, self.game.face_up[i], card_index=i)
                
        # Draw buttons based on game state
        if self.game.game_state == "betting":
            # Draw bet buttons in a row
            bet_start_x = (self.width - (5 * 120)) // 2
            for i in range(5):
                # Only allow changing bet if no bet is placed yet
                button_active = i+1 <= self.game.credits and self.game.current_bet == 0
                self.draw_button(str(i+1), bet_start_x + i*120, self.height - 150, 100, 40, button_active)
            
            # Draw Deal button below bet buttons (only active if bet is placed)
            self.draw_button("Deal", self.width//2 - 50, self.height - 80, 100, 40,
                           self.game.current_bet > 0)
        elif self.game.game_state == "holding":
            self.draw_button("Draw", self.width//2 - 50, self.height - 80, 100, 40)
            
        # Draw win message if active
        if self.show_win_message:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill(self.BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # Draw the message in a larger font with a background
            message_surface = self.big_font.render(self.win_message, True, self.WHITE)
            message_rect = message_surface.get_rect(center=(self.width // 2, self.height // 2))
            
            # Draw a background box
            bg_rect = message_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, self.BLUE, bg_rect)
            pygame.draw.rect(self.screen, self.GOLD, bg_rect, 3)  # Gold border
            
            self.screen.blit(message_surface, message_rect)
            
        pygame.display.flip()
        
    def draw_credits_and_bet(self):
        # Draw credits
        credits_text = f"Credits: {self.game.credits}"
        credits_surface = self.text_font.render(credits_text, True, self.WHITE)
        self.screen.blit(credits_surface, (10, 10))

        # Draw current bet if there is one
        if self.game.current_bet > 0:
            bet_text = f"Bet: {self.game.current_bet}"
            bet_surface = self.text_font.render(bet_text, True, self.WHITE)
            self.screen.blit(bet_surface, (10, 40))

        # Draw profit/loss statistics
        stats = self.game.get_profit_stats()
        profit_color = self.GREEN if stats['net_profit'] >= 0 else self.RED
        profit_text = f"Profit/Loss: {stats['net_profit']} ({stats['profit_percentage']:.1f}%)"
        profit_surface = self.text_font.render(profit_text, True, profit_color)
        self.screen.blit(profit_surface, (200, 100))  # Just below Jacks or Better text

        # Draw session high/low
        high_low_text = f"Session High: {stats['max_credits']} | Low: {stats['min_credits']}"
        high_low_surface = self.text_font.render(high_low_text, True, self.WHITE)
        self.screen.blit(high_low_surface, (200, 125))  # Below profit/loss text

    def handle_draw_button(self):
        if self.game.game_state == "holding":
            self.game.draw_new_cards()
            self.game.reveal_cards()  # Make sure all cards are face up
            hand_type, winnings = self.game.evaluate_hand()
            
            if winnings > 0:
                self.show_win_message = True
                self.win_message = f"{hand_type}! You won {winnings} credits!"
            else:
                self.show_win_message = True
                self.win_message = "No Win. Better luck next time!"
                
            self.draw()  # Update display to show final hand
            pygame.display.flip()  # Make sure changes are shown
            pygame.time.delay(2000)  # Show final hand for 2 seconds
            
            self.game.collect_winnings(winnings)  # This will also reset for next hand
            self.show_win_message = False  # Clear the win message after collecting winnings
            
    def handle_event(self, event):
        """Handle pygame events. Returns True if the event caused a state change that requires redrawing."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle betting buttons
            if self.height - 150 <= mouse_pos[1] <= self.height - 110:
                if self.game.game_state == "betting":
                    bet_start_x = (self.width - (5 * 120)) // 2
                    for i in range(5):
                        if (bet_start_x + i*120 <= mouse_pos[0] <= bet_start_x + i*120 + 100 and 
                            i+1 <= self.game.credits):
                            self.game.place_bet(i+1)
                            return True
            
            # Handle Deal/Draw button
            draw_button_rect = pygame.Rect(self.width//2 - 50, self.height - 80, self.button_width, self.button_height)
            if draw_button_rect.collidepoint(mouse_pos):
                if self.game.game_state == "betting" and self.game.current_bet > 0:
                    if self.game.deal_initial_hand():
                        return True
                elif self.game.game_state == "holding":
                    self.handle_draw_button()
                    return True
            
            # Check for hold buttons
            if self.game.game_state == "holding":
                for i in range(5):
                    if self.hold_buttons[i] and self.hold_buttons[i].collidepoint(mouse_pos):
                        self.game.hold_card(i)
                        return True
            
            # Check for card holds (clicking the card itself)
            if self.game.game_state == "holding":
                for i, (x, y) in enumerate(self.card_positions):
                    card_rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
                    if card_rect.collidepoint(mouse_pos):
                        self.game.hold_card(i)
                        return True
        
        elif event.type == pygame.USEREVENT:
            # Reset game after win message
            if self.show_win_message:
                self.show_win_message = False
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
                return True
        
        return False  # No redraw needed

    def draw_button(self, text, x, y, width, height, active=True):
        color = self.BLUE if active else self.GRAY
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        text_surface = self.text_font.render(text, True, self.WHITE)
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
