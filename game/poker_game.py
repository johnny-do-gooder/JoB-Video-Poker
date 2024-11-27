import random
from typing import List, Tuple
from collections import Counter  # Import Counter from collections module
from .logger import game_logger

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.held = False

    def __str__(self):
        return f"{self.rank}{self.suit}"

class PokerGame:
    SUITS = ['♠', '♥', '♦', '♣']  # Unicode symbols for card suits
    SUITS_UNICODE = {
        '♠': '♠',  # U+2660 BLACK SPADE SUIT
        '♥': '♥',  # U+2665 BLACK HEART SUIT
        '♦': '♦',  # U+2666 BLACK DIAMOND SUIT
        '♣': '♣'   # U+2663 BLACK CLUB SUIT
    }
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self):
        self.deck = []  # All cards not in player's hand
        self.hand = []  # Current player's hand (5 cards)
        self.initial_hand = []  # Store the initial hand before draws
        self.face_up = [False] * 5
        self.credits = 100
        self.starting_credits = 100  # Track initial credits
        self.max_credits = 100  # Track highest balance
        self.min_credits = 100  # Track lowest balance
        self.current_bet = 0
        self.initial_bet = 0  # Store the initial bet for endurance mode
        self.game_state = "betting"
        self.show_result = False  # Initialize the flag
        game_logger.info("Game initialized with 100 credits")
        self.initialize_deck()

    def initialize_deck(self):
        # Create a fresh 52-card deck
        self.deck = [Card(suit, rank) for suit in self.SUITS for rank in self.RANKS]
        self.shuffle_remaining_cards()
        game_logger.debug("New deck initialized and shuffled")
        
    def shuffle_remaining_cards(self):
        # Continuously shuffle cards not in player's hand
        random.shuffle(self.deck)
        game_logger.debug(f"Shuffled remaining {len(self.deck)} cards")
        
    def deal_initial_hand(self):
        if self.current_bet <= 0:
            game_logger.warning("Attempted to deal without a bet")
            return False
            
        game_logger.info(f"Dealing initial hand with bet: {self.current_bet}")
        
        # Start fresh with all 52 cards
        self.initialize_deck()
        self.hand = []
        self.initial_hand = []  # Clear initial hand
        self.face_up = [True] * 5  # Make cards face up immediately
            
        # Deal 5 cards from deck
        for _ in range(5):
            card = self.deck.pop()
            self.hand.append(card)
            game_logger.debug(f"Dealt card: {card}")
            
        # Store initial hand
        self.initial_hand = [Card(card.suit, card.rank) for card in self.hand]
            
        # Shuffle remaining 47 cards
        self.shuffle_remaining_cards()
        
        game_logger.info(f"Initial hand: {[str(card) for card in self.hand]}")
        self.game_state = "holding"
        return True
        
    def reveal_cards(self):
        self.face_up = [True] * 5
        game_logger.info("Cards revealed")
        
    def hold_card(self, index: int):
        if 0 <= index < len(self.hand) and self.face_up[index] and self.game_state == "holding":
            self.hand[index].held = not self.hand[index].held
            game_logger.info(f"Card {index} ({'held' if self.hand[index].held else 'unheld'}): {self.hand[index]}")
            
    def draw_new_cards(self):
        game_logger.info("Drawing new cards")
        
        held_cards = []
        for i, card in enumerate(self.hand):
            if card.held:
                held_cards.append(str(card))
            else:
                # Return non-held cards to deck and shuffle
                self.deck.append(self.hand[i])
                self.shuffle_remaining_cards()
        
        game_logger.info(f"Held cards: {held_cards}")
        
        # Draw new cards from the continuously shuffled deck
        for i in range(len(self.hand)):
            if not self.hand[i].held:
                new_card = self.deck.pop()
                game_logger.debug(f"Replacing card {i} ({self.hand[i]}) with {new_card}")
                self.hand[i] = new_card
                self.face_up[i] = True
            self.hand[i].held = False
            
        game_logger.info(f"Final hand: {[str(card) for card in self.hand]}")
        game_logger.debug(f"Cards remaining in deck: {len(self.deck)}")
        self.game_state = "evaluating"
            
    def evaluate_hand(self) -> Tuple[str, int]:
        game_logger.info("Evaluating hand")
        ranks = [self.RANKS.index(card.rank) for card in self.hand]
        suits = [card.suit for card in self.hand]
        
        # Sort ranks for easier evaluation
        ranks.sort()
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = False
        if len(set(ranks)) == 5:  # All ranks must be different for a straight
            sorted_ranks = sorted(ranks)
            # Check for Ace-low straight (A,2,3,4,5)
            if sorted_ranks == [0, 1, 2, 3, 12]:  # 12 is Ace
                is_straight = True
            # Check for regular straight (including Ace-high)
            elif sorted_ranks == [i for i in range(min(ranks), max(ranks) + 1)]:
                is_straight = True
        
        # Count rank frequencies
        rank_counts = Counter(ranks)
        max_count = max(rank_counts.values())
        
        # Evaluate hand
        hand_type = "No Win"
        winnings = 0
        
        if is_straight and is_flush:
            if ranks == [8, 9, 10, 11, 12]:  # Royal Flush
                hand_type = "Royal Flush"
                winnings = self.current_bet * 800
            else:  # Straight Flush
                hand_type = "Straight Flush"
                winnings = self.current_bet * 50
        elif max_count == 4:
            hand_type = "Four of a Kind"
            winnings = self.current_bet * 25
        elif sorted(rank_counts.values()) == [2, 3]:
            hand_type = "Full House"
            winnings = self.current_bet * 9
        elif is_flush:
            hand_type = "Flush"
            winnings = self.current_bet * 6
        elif is_straight:
            hand_type = "Straight"
            winnings = self.current_bet * 4
        elif max_count == 3:
            hand_type = "Three of a Kind"
            winnings = self.current_bet * 3
        elif list(rank_counts.values()).count(2) == 2:
            hand_type = "Two Pair"
            winnings = self.current_bet * 2
        elif max_count == 2:
            pair_rank = max(rank_counts.items(), key=lambda x: (x[1], x[0]))[0]
            if pair_rank >= self.RANKS.index('J'):  # Jacks or Better
                hand_type = "Jacks or Better"
                winnings = self.current_bet
        
        game_logger.info(f"Hand evaluation: {hand_type}, Winnings: {winnings}")
        self.show_result = True  # Add this flag to indicate we should show the result
        return hand_type, winnings
        
    def get_profit_stats(self):
        """Get current profit/loss statistics"""
        net_profit = self.credits - self.starting_credits
        profit_percentage = (net_profit / self.starting_credits) * 100 if self.starting_credits > 0 else 0
        return {
            'net_profit': net_profit,
            'profit_percentage': profit_percentage,
            'max_credits': self.max_credits,
            'min_credits': self.min_credits,
            'current_credits': self.credits
        }

    def collect_winnings(self, amount: int):
        # First subtract the bet
        self.credits -= self.current_bet
        
        if amount > 0:
            self.credits += amount
            game_logger.info(f"Collected winnings: {amount}, New credits: {self.credits}")
        else:
            # Just log the loss since we already subtracted the bet
            game_logger.info(f"No winnings. Lost bet of {self.current_bet}. Credits: {self.credits}")
            
        # Update min/max credit tracking
        self.min_credits = min(self.min_credits, self.credits)
        self.max_credits = max(self.max_credits, self.credits)
        
        # In endurance mode, preserve the initial bet
        saved_bet = self.initial_bet
        self.current_bet = 0
        self.reset_for_new_hand()
        # Restore the initial bet if we're in endurance mode
        if saved_bet > 0:
            self.current_bet = saved_bet
            
    def reset_for_new_hand(self):
        game_logger.info(f"Reset for new hand. Credits: {self.credits}")
        # Don't reset the bet amount - keep it consistent for the session
        self.hand = []
        self.initial_hand = []  # Clear initial hand
        self.face_up = [False] * 5
        self.game_state = "betting"
        self.show_result = False
        self.initialize_deck()
        
    def place_bet(self, amount: int):
        if self.game_state != "betting":
            game_logger.warning(f"Attempted to bet {amount} in invalid state: {self.game_state}")
            return False
            
        if 1 <= amount <= 5 and amount <= self.credits:
            self.current_bet = amount
            # Don't subtract credits here anymore, we'll do it in collect_winnings
            game_logger.info(f"Bet placed: {amount}, Credits remaining: {self.credits}")
            return True
            
        game_logger.warning(f"Invalid bet amount: {amount}, Credits: {self.credits}")
        return False
