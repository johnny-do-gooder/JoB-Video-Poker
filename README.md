# Jacks or Better Video Poker

A classic video poker simulator implementing the "Jacks or Better" variant with authentic casino-style gameplay.

## Features

- Authentic poker hand evaluation and payouts
- Classic video poker machine interface
- Real-time credit tracking
- Variable betting (1-5 credits)
- Card holding functionality
- Cross-platform compatibility (Windows/Linux)

## Requirements

- Python 3.7+
- Pygame 2.5.2
- Numpy 1.24.3

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## How to Play

1. Place your bet (1-5 credits) using the number buttons
2. Click "Deal" to receive your initial hand
3. Click cards you want to hold (they will be marked as "HELD")
4. Click "Draw" to replace non-held cards
5. Winning hands will automatically add credits to your balance

## Game Mathematics

### Betting and Credits
- Starting credits: 100
- Bet range: 1-5 credits per hand
- Credits are deducted when hands are evaluated
- Winnings are added immediately after hand evaluation

### Expected Returns
- Base return rate: ~99.54% with optimal play
- Maximum theoretical return: ~800x bet (Royal Flush)
- Minimum return: 0x (loss of bet)
- Common returns: 1x-2x (Jacks or Better, Two Pair)

### Profit/Loss Tracking
The game tracks your performance in two ways:
1. Session tracking (Regular mode):
   - Net profit/loss from starting credits
   - Highest credit balance achieved
   - Lowest credit balance reached
   - Current credit balance

2. Endurance test mode:
   - Runs 100 hands automatically
   - Tracks total profit/loss
   - Shows performance statistics
   - Uses optimal play strategy

### Paytable (multiplied by bet amount)

- Royal Flush: 800x
- Straight Flush: 50x
- Four of a Kind: 25x
- Full House: 9x
- Flush: 6x
- Straight: 4x
- Three of a Kind: 3x
- Two Pair: 2x
- Jacks or Better: 1x

## Game Modes

### Regular Mode
- Standard video poker gameplay
- Real-time profit/loss tracking
- Unlimited hands
- Manual card selection
- Practice your strategy

### Endurance Test Mode
- Automated 100-hand session
- Uses basic strategy for holds
- Detailed performance metrics
- Great for understanding game mathematics
- Shows theoretical return rates

## Strategy Tips

1. Always hold:
   - Royal Flush, Straight Flush, Four of a Kind
   - Full House, Flush, Straight
   - Three of a Kind
   - Any pair of Jacks or better

2. Sometimes hold:
   - Low pairs (depending on other cards)
   - Four cards to a Royal Flush
   - Four cards to a Straight Flush

3. Never hold:
   - Single low cards (below Jack)
   - Unsuited, non-sequential high cards

The game's mathematics are designed to closely match real casino video poker machines, providing an authentic gambling experience without real money risk.
