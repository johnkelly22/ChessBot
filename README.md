<!-- Ctrl-Shift-V to view read me -->

# ChessBot

A chess engine implemented in Python using Pygame and Bitboards.

## Overview

This project is a fully functional chess game featuring a strong algorithmic opponent. It uses **bitboards** for efficient board representation and move generation, and implements a sophisticated **Minimax** search algorithm with **Alpha-Beta Pruning** and several advanced optimizations to play at a high level.

## Features

- **Algorithmic Opponent**: A custom chess engine that searches 5+ moves ahead using deterministic logic.
- **Bitboard Representation**: Extremely fast move generation using bitwise operations.
- **Move Validation**: Complete legal move generation including pins and checks.
- **Checkmate Detection**: Automatically detects checkmate and declares the winner.

## Technical Deep Dive: The Engine

The core of the chess bot is a **Minimax** algorithm enhanced with several standard chess programming optimizations. It does not use machine learning or neural networks; instead, it relies on a brute-force search of the game tree with smart pruning.

### 1. Minimax Algorithm

The bot uses the Minimax algorithm to determine the best move. It recursively explores the game tree, simulating all possible moves for both white and black.

- **Maximizing Player (Black)**: The engine (Black) tries to maximize the evaluation score.
- **Minimizing Player (White)**: The engine assumes the opponent (White) will try to minimize the evaluation score.

This creates a tree of possibilities where the engine assumes "perfect play" from both sides to find the optimal path.

### 2. Alpha-Beta Pruning

To make the search feasible, we use Alpha-Beta Pruning. This optimization allows the engine to stop evaluating a branch as soon as it finds a move that proves the branch is worse than a previously examined move.

- **Alpha**: The best score the maximizing player can guarantee so far.
- **Beta**: The best score the minimizing player can guarantee so far.
- If `beta <= alpha`, the branch is "pruned" (discarded), saving massive amounts of computation time because we know this path will not be chosen by a rational player.

### 3. Transposition Table

We use a **Transposition Table (TT)** to cache the results of board evaluations.

- **Why**: In chess, different move sequences often lead to the same board position (transposition).
- **How**: We store the evaluation, depth, and best move for each visited position in a hash map.
- **Benefit**: If the engine encounters a position it has already analyzed (even from a different move order), it retrieves the result instantly instead of re-calculating.

### 4. Iterative Deepening

Instead of searching directly to a fixed depth (e.g., Depth 5), the engine searches to Depth 1, then Depth 2, then Depth 3, and so on.

- **Synergy**: This works perfectly with the Transposition Table. The "Best Move" found at Depth `N-1` is stored in the TT and tried _first_ at Depth `N`.
- **Result**: This perfect move ordering makes the deeper searches significantly faster.

## Board Representation: Bitboards

The board is represented using **64-bit integers (Bitboards)**. Each piece type has its own bitboard where a `1` represents the presence of a piece and `0` represents an empty square.

```python
bb = {
    "WHITE_PAWNS": 0b00000000...01111111100000000,
    "BLACK_KINGS": ...
}
```

This allows us to use bitwise operators (`&`, `|`, `~`, `<<`, `>>`) to generate moves and validate board states in nanoseconds. For example, to find all pawn attacks, we can simply shift the pawn bitboard diagonally.

## Evaluation Function

The evaluation function determines how "good" a board position is from the perspective of the engine (Black). It is a static analysis of the board state.

### Material Value

The base score is calculated from the material difference:

- **Pawn**: 10
- **Knight/Bishop**: 30
- **Rook**: 50
- **Queen**: 90
- **King**: 1000

### Piece-Square Tables

We use **Piece-Square Tables (PSTs)** to encourage positional play. These tables assign a bonus or penalty to pieces based on their location on the board.

- **Knights**: Rewarded for being in the center (controlling more squares).
- **Pawns**: Rewarded for advancing towards promotion.
- **Kings**: Penalized for being in the center during the opening/middlegame (safety).

The total evaluation is: `(Black Material + Black Positional Bonus) - (White Material + White Positional Bonus)`.

## Game Loop

The `main.py` file handles the game loop using Pygame:

1.  **Event Handling**: Listens for mouse clicks to select and move pieces.
2.  **Rendering**: Draws the board, pieces, and highlights using the bitboard state.
3.  **Turn Management**:
    - **White (User)**: Moves are validated against the legal move generator.
    - **Black (Engine)**: The `find_best_move` function is called, which triggers the Minimax search.

## Running the Game

Ensure you have Python and Pygame installed.

```bash
pip install pygame
python main.py
```

### Controls

- **Click** a piece to select it.
- **Click** a valid destination square to move.
- **Castling**: Select your King and click on your Rook (or the destination square).
