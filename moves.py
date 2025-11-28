import board
from board import get_empty, get_all_white, get_all_black
from utils import squares_in, sq_to_bb



def get_own_pieces(color, bb=None):
    """Get bitboard of all pieces of the given color."""
    if bb is None:
        bb = board.bb
    if color == "white":
        return get_all_white(bb)
    else:
        return get_all_black(bb)


def is_square_attacked(square, by_color, bb=None):
    """
    Check if a square is attacked by any piece of the given color.
    """
    if bb is None:
        bb = board.bb

    # 1. Check for pawn attacks
    # If we want to know if 'square' is attacked by a pawn of 'by_color',
    # we can pretend there is a pawn of the OPPOSITE color at 'square'
    # and see if it can capture a pawn of 'by_color'.
    # Alternatively, just look at the pawn capture logic.
    
    if by_color == "white":
        # White pawns attack from lower ranks (sq-9, sq-7)
        # So if we are at 'square', we look at square-7 and square-9
        # Check down-left (sq-9)
        if square >= 9 and (square % 8) > 0:
            if (1 << (square - 9)) & bb["WHITE_PAWNS"]:
                return True
        # Check down-right (sq-7)
        if square >= 7 and (square % 8) < 7:
            if (1 << (square - 7)) & bb["WHITE_PAWNS"]:
                return True
    else: # black
        # Black pawns attack from higher ranks (sq+7, sq+9)
        # Check up-left (sq+7)
        if square <= 56 and (square % 8) > 0:
             if (1 << (square + 7)) & bb["BLACK_PAWNS"]:
                return True
        # Check up-right (sq+9)
        if square <= 54 and (square % 8) < 7:
            if (1 << (square + 9)) & bb["BLACK_PAWNS"]:
                return True

    # 2. Check for knight attacks
    # We can use the knight move generation logic or precomputed offsets
    knight_offsets = [17, 15, 10, 6, -17, -15, -10, -6]
    enemy_knights = bb["WHITE_KNIGHTS"] if by_color == "white" else bb["BLACK_KNIGHTS"]
    
    for off in knight_offsets:
        target = square + off
        if 0 <= target <= 63:
            # Check file wrapping
            f1, f2 = square % 8, target % 8
            if abs(f1 - f2) <= 2:
                if (1 << target) & enemy_knights:
                    return True

    # 3. Check for king attacks
    king_offsets = [8, -8, 1, -1, 9, 7, -7, -9]
    enemy_king = bb["WHITE_KING"] if by_color == "white" else bb["BLACK_KING"]
    
    for off in king_offsets:
        target = square + off
        if 0 <= target <= 63:
            f1, f2 = square % 8, target % 8
            if abs(f1 - f2) <= 1:
                if (1 << target) & enemy_king:
                    return True

    # 4. Check for sliding pieces (Rook/Queen) - Orthogonal
    enemy_rooks_queens = (bb["WHITE_ROOKS"] | bb["WHITE_QUEEN"]) if by_color == "white" else (bb["BLACK_ROOKS"] | bb["BLACK_QUEEN"])
    orth_dirs = [8, -8, 1, -1]
    
    for d in orth_dirs:
        curr = square
        while True:
            curr += d
            if curr < 0 or curr > 63:
                break
            # Wrap checks
            if d == 1 and curr % 8 == 0: break
            if d == -1 and curr % 8 == 7: break
            
            bb_curr = 1 << curr
            if bb_curr & enemy_rooks_queens:
                return True
            if bb_curr & (get_all_white(bb) | get_all_black(bb)):
                # Blocked by any piece
                break

    # 5. Check for sliding pieces (Bishop/Queen) - Diagonal
    enemy_bishops_queens = (bb["WHITE_BISHOPS"] | bb["WHITE_QUEEN"]) if by_color == "white" else (bb["BLACK_BISHOPS"] | bb["BLACK_QUEEN"])
    diag_dirs = [9, 7, -7, -9]
    
    for d in diag_dirs:
        curr = square
        while True:
            curr += d
            if curr < 0 or curr > 63:
                break
            # Wrap checks
            if d in (9, -7) and curr % 8 == 0: break
            if d in (7, -9) and curr % 8 == 7: break
            
            bb_curr = 1 << curr
            if bb_curr & enemy_bishops_queens:
                return True
            if bb_curr & (get_all_white(bb) | get_all_black(bb)):
                break
                
    return False

def white_checkmate(bb=None):
    if bb is None:
        bb = board.bb
    
    if generate_all_legal_moves_white(bb) == []:
        return True
    return False

def black_checkmate(bb=None):
    if bb is None:
        bb = board.bb
    
    if generate_all_legal_moves_black(bb) == []:
        return True
    return False

def is_in_check(color, bb=None):
    """
    Check if the king of the given color is currently in check.
    """
    if bb is None:
        bb = board.bb

    king_bb = bb["WHITE_KING"] if color == "white" else bb["BLACK_KING"]
    if king_bb == 0:
        return False # Should not happen in a valid game
        
    king_sq = king_bb.bit_length() - 1
    opponent = "black" if color == "white" else "white"
    
    return is_square_attacked(king_sq, opponent, bb)


def can_castle(color, side, bb=None):
    """
    Check if castling is legal for the given color and side.
    side: "king" or "queen"
    """
    if bb is None:
        bb = board.bb
        
    rights = bb.get("CASTLING_RIGHTS", 0)
    
    # Check rights
    if color == "white":
        if side == "king":
            if not (rights & 1): return False
            # Check path clear (f1, g1) -> 5, 6
            if (1 << 5) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 6) & (get_all_white(bb) | get_all_black(bb)): return False
            # Check not in check and path not attacked
            if is_in_check("white", bb): return False
            if is_square_attacked(5, "black", bb): return False
            if is_square_attacked(6, "black", bb): return False
            return True
        else: # queen side
            if not (rights & 2): return False
            # Check path clear (b1, c1, d1) -> 1, 2, 3
            if (1 << 1) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 2) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 3) & (get_all_white(bb) | get_all_black(bb)): return False
            # Check not in check and path not attacked (c1, d1)
            # Note: b1 can be attacked, King doesn't pass through it (King moves e1->c1)
            # Wait, standard rules: King passes through d1 to get to c1.
            # King moves from 4 to 2. Passes through 3 (d1).
            if is_in_check("white", bb): return False
            if is_square_attacked(3, "black", bb): return False
            if is_square_attacked(2, "black", bb): return False
            return True
            
    else: # black
        if side == "king":
            if not (rights & 4): return False
            # Check path clear (f8, g8) -> 61, 62
            if (1 << 61) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 62) & (get_all_white(bb) | get_all_black(bb)): return False
            # Check not in check and path not attacked
            if is_in_check("black", bb): return False
            if is_square_attacked(61, "white", bb): return False
            if is_square_attacked(62, "white", bb): return False
            return True
        else: # queen side
            if not (rights & 8): return False
            # Check path clear (b8, c8, d8) -> 57, 58, 59
            if (1 << 57) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 58) & (get_all_white(bb) | get_all_black(bb)): return False
            if (1 << 59) & (get_all_white(bb) | get_all_black(bb)): return False
            # Check not in check and path not attacked
            if is_in_check("black", bb): return False
            if is_square_attacked(59, "white", bb): return False
            if is_square_attacked(58, "white", bb): return False
            return True
    
    return False


# PAWNS
def generate_pawn_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Determine if this is a white or black pawn
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves
    
    pawn_bb = 1 << square
    opponent_pieces = get_all_black(bb) if color == "white" else get_all_white(bb)
    
    if color == "white":
        # White pawns move up (positive direction)
        # single push
        single = (pawn_bb << 8) & get_empty(bb)
        sq = single.bit_length() - 1
        if single != 0:
            moves.append((square, sq))
        
        # double push (only from rank 2, and only if single push square is also empty)
        if square // 8 == 1:  # rank 2 (white starting rank)
            # Check that both the square in front AND two squares in front are empty
            if single != 0:  # single push must be possible
                double = (pawn_bb << 16) & get_empty(bb) & 0x00000000FF000000
                sq = double.bit_length() - 1
                if double != 0:
                    moves.append((square, sq))
        
        # diagonal captures (left and right)
        file = square % 8
        
        # capture left diagonal (up-left)
        if file > 0:  # not on left edge
            capture_left = (pawn_bb << 7) & opponent_pieces
            sq = capture_left.bit_length() - 1
            if capture_left != 0:
                moves.append((square, sq))
        
        # capture right diagonal (up-right)
        if file < 7:  # not on right edge
            capture_right = (pawn_bb << 9) & opponent_pieces
            sq = capture_right.bit_length() - 1
            if capture_right != 0:
                moves.append((square, sq))
    
    else:  # black
        # Black pawns move down (negative direction)
        # single push
        single = (pawn_bb >> 8) & get_empty(bb)
        sq = single.bit_length() - 1
        if single != 0:
            moves.append((square, sq))
        
        # double push (only from rank 7, and only if single push square is also empty)
        if square // 8 == 6:  # rank 7 (black starting rank)
            # Check that both the square in front AND two squares in front are empty
            if single != 0:  # single push must be possible
                double = (pawn_bb >> 16) & get_empty(bb) & 0x000000FF00000000
                sq = double.bit_length() - 1
                if double != 0:
                    moves.append((square, sq))
        
        # diagonal captures (left and right)
        file = square % 8
        
        # capture left diagonal (down-left)
        if file > 0:  # not on left edge
            capture_left = (pawn_bb >> 9) & opponent_pieces
            sq = capture_left.bit_length() - 1
            if capture_left != 0:
                moves.append((square, sq))
        
        # capture right diagonal (down-right)
        if file < 7:  # not on right edge
            capture_right = (pawn_bb >> 7) & opponent_pieces
            sq = capture_right.bit_length() - 1
            if capture_right != 0:
                moves.append((square, sq))
    
    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# KNIGHTS
def generate_knight_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Get the color of the knight
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves

    # knight offsets
    offsets = [
        17, 15, 10, 6,   # positive direction moves
        -17, -15, -10, -6
    ]

    for off in offsets:
        sq = square + off

        # off board
        if sq < 0 or sq > 63:
            continue

        # file wrapping rules
        file_from = square % 8
        file_to = sq % 8
        file_diff = abs(file_from - file_to)

        # knight can only move 1 or 2 files; anything else is wrap
        if file_diff > 2:
            continue

        dest = 1 << sq

        # cannot land on own piece
        if dest & get_own_pieces(color, bb):
            continue

        moves.append((square, sq))

    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# ROOKS
def generate_rook_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Get the color of the rook
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves
    
    opponent_pieces = get_all_black(bb) if color == "white" else get_all_white(bb)

    directions = [8, -8, 1, -1]

    for d in directions:
        sq = square

        while True:
            sq += d

            # bounds
            if sq < 0 or sq > 63:
                break

            # horizontal wrap
            if d == 1 and sq % 8 == 0:
                break
            if d == -1 and sq % 8 == 7:
                break

            dest = 1 << sq

            if dest & get_own_pieces(color, bb):
                break

            moves.append((square, sq))

            if dest & opponent_pieces:
                break

    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# BISHOPS
def generate_bishop_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Get the color of the bishop
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves
    
    opponent_pieces = get_all_black(bb) if color == "white" else get_all_white(bb)

    # diagonal directions: NE(+9), NW(+7), SE(-7), SW(-9)
    directions = [9, 7, -7, -9]

    for d in directions:
        sq = square

        while True:
            sq += d

            # off board
            if sq < 0 or sq > 63:
                break

            # diagonal wrap checks
            # moving right (positive file)
            if d in (9, -7) and sq % 8 == 0:
                break

            # moving left (negative file)
            if d in (7, -9) and sq % 8 == 7:
                break

            dest = 1 << sq

            if dest & get_own_pieces(color, bb):
                break

            moves.append((square, sq))

            if dest & opponent_pieces:
                break

    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# QUEEN
def generate_queen_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Get the color of the queen
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves
    
    opponent_pieces = get_all_black(bb) if color == "white" else get_all_white(bb)

    # rook dirs + bishop dirs
    directions = [
        8, -8, 1, -1,      # rook directions
        9, 7, -7, -9       # bishop directions
    ]

    for d in directions:
        sq = square

        while True:
            sq += d

            if sq < 0 or sq > 63:
                break

            # horizontal wrap (rook-like)
            if d == 1 and sq % 8 == 0:
                break
            if d == -1 and sq % 8 == 7:
                break

            # diagonal wrap (bishop-like)
            if d in (9, -7) and sq % 8 == 0:
                break
            if d in (7, -9) and sq % 8 == 7:
                break

            dest = 1 << sq

            if dest & get_own_pieces(color, bb):
                break

            moves.append((square, sq))

            if dest & opponent_pieces:
                break

    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# KING
def generate_king_moves(square, bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    
    # Get the color of the king
    color, _ = board.get_piece(square, bb)
    if color is None:
        return moves

    # king offsets: 8 surrounding squares
    offsets = [8, -8, 1, -1, 9, 7, -7, -9]

    for off in offsets:
        sq = square + off

        # off board
        if sq < 0 or sq > 63:
            continue

        # horizontal wrap rules
        file_from = square % 8
        file_to = sq % 8
        file_diff = abs(file_from - file_to)

        # king can only move 1 file horizontally
        if file_diff > 1:
            continue

        dest = 1 << sq

        # cannot land on own piece
        if dest & get_own_pieces(color, bb):
            continue

        moves.append((square, sq))

    # Castling Moves
    if color == "white":
        if square == 4: # e1
            if can_castle("white", "king", bb):
                moves.append((4, 6)) # e1 -> g1
            if can_castle("white", "queen", bb):
                moves.append((4, 2)) # e1 -> c1
    else: # black
        if square == 60: # e8
            if can_castle("black", "king", bb):
                moves.append((60, 62)) # e8 -> g8
            if can_castle("black", "queen", bb):
                moves.append((60, 58)) # e8 -> c8

    # Filter illegal moves
    legal_moves = []
    
    for m in moves:
        start, end = m
        # Simulate move
        temp_bb = bb.copy()
        if board.move_piece(start, end, temp_bb):
            if not is_in_check(color, temp_bb):
                legal_moves.append(m)
            
    return legal_moves

# ALL LEGAL MOVES for WHITE
def generate_all_legal_moves_white(bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    for sq in range(64):
        color, piece = board.get_piece(sq, bb)
        if color != "white":
            continue
        
        if piece == "pawn":
            moves.extend(generate_pawn_moves(sq, bb))
        elif piece == "rook":
            moves.extend(generate_rook_moves(sq, bb))
        elif piece == "knight":
            moves.extend(generate_knight_moves(sq, bb))
        elif piece == "bishop":
            moves.extend(generate_bishop_moves(sq, bb))
        elif piece == "queen":
            moves.extend(generate_queen_moves(sq, bb))
        elif piece == "king":
            moves.extend(generate_king_moves(sq, bb))
    
    return moves

# ALL LEGAL MOVES for BLACK
def generate_all_legal_moves_black(bb=None):
    moves = []
    if bb is None:
        bb = board.bb
    for sq in range(64):
        color, piece = board.get_piece(sq, bb)
        if color != "black":
            continue
        
        if piece == "pawn":
            moves.extend(generate_pawn_moves(sq, bb))
        elif piece == "rook":
            moves.extend(generate_rook_moves(sq, bb))
        elif piece == "knight":
            moves.extend(generate_knight_moves(sq, bb))
        elif piece == "bishop":
            moves.extend(generate_bishop_moves(sq, bb))
        elif piece == "queen":
            moves.extend(generate_queen_moves(sq, bb))
        elif piece == "king":
            moves.extend(generate_king_moves(sq, bb))
    
    return moves

# IS GAME OVER
def is_game_over(bb=None):
    if bb is None:
        bb = board.bb
    if is_in_check("white", bb) and not any(generate_all_legal_moves_white(bb)):
        return True
    if is_in_check("black", bb) and not any(generate_all_legal_moves_black(bb)):
        return True
    return False

