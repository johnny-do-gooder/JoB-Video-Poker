import os
import sys
import time
import random
from game.poker_game import PokerGame
from game.logger import game_logger

def should_hold_card(card, hand):
    """Basic strategy for holding cards"""
    # Count pairs and potential straights/flushes
    ranks = [c.rank for c in hand]
    suits = [c.suit for c in hand]
    
    # Always hold pairs of jacks or better
    if card.rank in ['J', 'Q', 'K', 'A'] and ranks.count(card.rank) >= 2:
        return True
    
    # Always hold three of a kind or better
    if ranks.count(card.rank) >= 3:
        return True
    
    # Hold high cards (jack or better)
    if card.rank in ['J', 'Q', 'K', 'A']:
        return True
        
    # Otherwise, don't hold
    return False

def simulate_game(num_hands=25):
    """Run an endurance test of the game without graphical display"""
    game = PokerGame()
    
    # Track statistics
    hands_played = 0
    starting_credits = game.credits
    min_credits = starting_credits
    max_credits = starting_credits
    total_bets = 0
    total_winnings = 0
    winning_hands = 0
    hand_types = {}
    
    game_logger.info(f"Starting endurance test with {num_hands} hands")
    game_logger.info(f"Initial credits: {starting_credits}")
    
    bet_amount = 5  # Fixed bet for testing
    
    while hands_played < num_hands:
        # Place bet
        if game.place_bet(bet_amount):
            total_bets += bet_amount
            hands_played += 1
            game_logger.info(f"\nHand {hands_played}: Placed bet of {bet_amount} credits")
            
            # Deal initial hand
            game.deal_initial_hand()
            initial_hand = [str(card) for card in game.hand]
            game_logger.info(f"Initial hand: {initial_hand}")
            
            # Make hold decisions
            held_cards = []
            for i, card in enumerate(game.hand):
                if should_hold_card(card, game.hand):
                    game.hold_card(i)
                    held_cards.append(str(card))
            
            game_logger.info(f"Held cards: {held_cards}")
            
            # Draw new cards
            game.draw_new_cards()
            final_hand = [str(card) for card in game.hand]
            game_logger.info(f"Final hand: {final_hand}")
            
            # Evaluate hand
            hand_type, winnings = game.evaluate_hand()
            if winnings > 0:
                winning_hands += 1
                total_winnings += winnings
                hand_types[hand_type] = hand_types.get(hand_type, 0) + 1
            
            # Log hand details
            game_logger.info(f"Hand type: {hand_type}")
            game_logger.info(f"Winnings: {winnings}")
            
            # Collect winnings and update stats
            game.collect_winnings(winnings)
            current_credits = game.credits
            min_credits = min(min_credits, current_credits)
            max_credits = max(max_credits, current_credits)
            
            # Get current profit stats
            stats = game.get_profit_stats()
            game_logger.info(f"Current credits: {current_credits}")
            game_logger.info(f"Current profit/loss: {stats['net_profit']} ({stats['profit_percentage']:.1f}%)")
            game_logger.info(f"Session high: {stats['max_credits']}, Session low: {stats['min_credits']}")
    
    # Final statistics
    net_profit = game.credits - starting_credits
    win_rate = (winning_hands / hands_played) * 100 if hands_played > 0 else 0
    return_rate = (total_winnings / total_bets) * 100 if total_bets > 0 else 0
    
    game_logger.info("\n=== Endurance Test Results ===")
    game_logger.info(f"Hands played: {hands_played}")
    game_logger.info(f"Starting credits: {starting_credits}")
    game_logger.info(f"Final credits: {game.credits}")
    game_logger.info(f"Minimum credits: {min_credits}")
    game_logger.info(f"Maximum credits: {max_credits}")
    game_logger.info(f"Net profit/loss: {net_profit}")
    game_logger.info(f"Total bets: {total_bets}")
    game_logger.info(f"Total winnings: {total_winnings}")
    game_logger.info(f"Winning hands: {winning_hands}")
    game_logger.info(f"Win rate: {win_rate:.1f}%")
    game_logger.info(f"Return rate: {return_rate:.1f}%")
    game_logger.info("\nHand type breakdown:")
    for hand_type, count in hand_types.items():
        game_logger.info(f"{hand_type}: {count} times")
    
    return hands_played, game.credits

if __name__ == "__main__":
    hands_played, final_credits = simulate_game(25)  # Run 25 hands
    print(f"\nEndurance test complete!")
    print(f"Hands played: {hands_played}")
    print(f"Final credits: {final_credits}")
