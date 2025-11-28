import board

piece_values = {
    "pawn": 10,
    "knight": 30,
    "bishop": 30,
    "rook": 50,
    "queen": 90,
    "king": 1000
}


# Helper to count bits
def count_bits(n):
    return bin(n).count('1')

# Helper to get set bits indices
def get_set_bits(n):
    while n:
        b = n & (~n + 1)
        yield (b.bit_length() - 1)
        n ^= b

# Flattened tables (Rank 1 to Rank 8, File A to File H)
# Note: The original numpy arrays were defined visually (Rank 8 at top).
# We need to flatten them such that index 0 is a1, 7 is h1, ..., 56 is a8, 63 is h8.
# The original numpy arrays had index 0,0 as a8 (top-left).
# So we need to flip them vertically to match rank 1 at bottom, then flatten.

# PAWN
white_pawn_table = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5,
    0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5,
    0.0, 0.0, 0.0, 6.0, 6.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 1.0, 6.0, 6.0, 1.0, 0.5, 0.5,
    1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0,
    2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

black_pawn_table = list(reversed(white_pawn_table))

# KNIGHT
white_knight_table = [
    -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
    -4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0,
    -3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0,
    -3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0,
    -3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0,
    -3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0,
    -4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0,
    -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0
]

black_knight_table = list(reversed(white_knight_table))

# BISHOP
white_bishop_table = [
    -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
    -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
    -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0,
    -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0,
    -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0,
    -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0,
    -1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0,
    -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0
]

black_bishop_table = list(reversed(white_bishop_table))

# ROOK
white_rook_table = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0
]

black_rook_table = list(reversed(white_rook_table))

# QUEEN
white_queen_table = [
    -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
    -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
    -1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
    -0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
    0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
    -1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
    -1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
    -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0
]

black_queen_table = list(reversed(white_queen_table))

# KING
white_king_table = [
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
    -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
    2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
    2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0
]

black_king_table = list(reversed(white_king_table))

# Eval the board state for white
def eval_white(bitboards):
    score = 0
    
    # PAWNS
    bb = bitboards["WHITE_PAWNS"]
    score += count_bits(bb) * piece_values["pawn"]
    for sq in get_set_bits(bb):
        score += white_pawn_table[sq]
    
    # KNIGHTS
    bb = bitboards["WHITE_KNIGHTS"]
    score += count_bits(bb) * piece_values["knight"]
    for sq in get_set_bits(bb):
        score += white_knight_table[sq]
    
    # BISHOPS
    bb = bitboards["WHITE_BISHOPS"]
    score += count_bits(bb) * piece_values["bishop"]
    for sq in get_set_bits(bb):
        score += white_bishop_table[sq]
    
    # ROOKS
    bb = bitboards["WHITE_ROOKS"]
    score += count_bits(bb) * piece_values["rook"]
    for sq in get_set_bits(bb):
        score += white_rook_table[sq]
    
    # QUEENS
    bb = bitboards["WHITE_QUEEN"]
    score += count_bits(bb) * piece_values["queen"]
    for sq in get_set_bits(bb):
        score += white_queen_table[sq]
    
    # KINGS
    bb = bitboards["WHITE_KING"]
    score += count_bits(bb) * piece_values["king"]
    for sq in get_set_bits(bb):
        score += white_king_table[sq]
    
    return score

# Eval the board state for black
def eval_black(bitboards):
    score = 0
    
    # PAWNS
    bb = bitboards["BLACK_PAWNS"]
    score += count_bits(bb) * piece_values["pawn"]
    for sq in get_set_bits(bb):
        score += black_pawn_table[sq]
    
    # KNIGHTS
    bb = bitboards["BLACK_KNIGHTS"]
    score += count_bits(bb) * piece_values["knight"]
    for sq in get_set_bits(bb):
        score += black_knight_table[sq]
    
    # BISHOPS
    bb = bitboards["BLACK_BISHOPS"]
    score += count_bits(bb) * piece_values["bishop"]
    for sq in get_set_bits(bb):
        score += black_bishop_table[sq]
    
    # ROOKS
    bb = bitboards["BLACK_ROOKS"]
    score += count_bits(bb) * piece_values["rook"]
    for sq in get_set_bits(bb):
        score += black_rook_table[sq]
    
    # QUEENS
    bb = bitboards["BLACK_QUEEN"]
    score += count_bits(bb) * piece_values["queen"]
    for sq in get_set_bits(bb):
        score += black_queen_table[sq]
    
    # KINGS
    bb = bitboards["BLACK_KING"]
    score += count_bits(bb) * piece_values["king"]
    for sq in get_set_bits(bb):
        score += black_king_table[sq]
    
    return score

# Eval total board state (Black POV, Positive is good for black, since black is the bot)
def eval_total(bitboards):
    return eval_black(bitboards) - eval_white(bitboards)