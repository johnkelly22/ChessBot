turn = "white"

bb = {
    "WHITE_PAWNS"   : 0b0000000000000000000000000000000000000000000000001111111100000000,
    "WHITE_ROOKS"   : 0b0000000000000000000000000000000000000000000000000000000010000001,
    "WHITE_KNIGHTS" : 0b0000000000000000000000000000000000000000000000000000000001000010,
    "WHITE_BISHOPS" : 0b0000000000000000000000000000000000000000000000000000000000100100,
    "WHITE_QUEEN"   : 0b0000000000000000000000000000000000000000000000000000000000001000,
    "WHITE_KING"    : 0b0000000000000000000000000000000000000000000000000000000000010000,
    "BLACK_PAWNS"   : 0b0000000011111111000000000000000000000000000000000000000000000000,
    "BLACK_ROOKS"   : 0b1000000100000000000000000000000000000000000000000000000000000000,
    "BLACK_KNIGHTS" : 0b0100001000000000000000000000000000000000000000000000000000000000,
    "BLACK_BISHOPS" : 0b0010010000000000000000000000000000000000000000000000000000000000,
    "BLACK_QUEEN"   : 0b0000100000000000000000000000000000000000000000000000000000000000,
    "BLACK_KING"    : 0b0001000000000000000000000000000000000000000000000000000000000000,
    "CASTLING_RIGHTS": 0b1111, # Bit 0: WK, Bit 1: WQ, Bit 2: BK, Bit 3: BQ
}

fp = [
	"white-pawn.png",
	"white-rook.png",
	"white-knight.png",
	"white-bishop.png",
	"white-queen.png",
	"white-king.png",
	"black-pawn.png",
	"black-rook.png",
	"black-knight.png",
	"black-bishop.png",
	"black-queen.png",
	"black-king.png",
]

def get_all_white(board=None):
    """Calculate bitboard of all white pieces."""
    if board is None:
        board = bb
    return (board["WHITE_PAWNS"] | board["WHITE_KNIGHTS"] | board["WHITE_BISHOPS"] |
            board["WHITE_ROOKS"] | board["WHITE_QUEEN"]  | board["WHITE_KING"])

def get_all_black(board=None):
    """Calculate bitboard of all black pieces."""
    if board is None:
        board = bb
    return (board["BLACK_PAWNS"] | board["BLACK_KNIGHTS"] | board["BLACK_BISHOPS"] |
            board["BLACK_ROOKS"] | board["BLACK_QUEEN"]  | board["BLACK_KING"])

def get_empty(board=None):
    """Calculate bitboard of all empty squares."""
    return ~(get_all_white(board) | get_all_black(board)) & 0xFFFFFFFFFFFFFFFF

def get_piece(sq, board=None):
    """
    Get the piece at a given square.
    Returns: (color, piece_type) tuple or (None, None) if empty.
    """
    if board is None:
        board = bb

    sq_bb = 1 << sq
    
    # Check white pieces
    if board["WHITE_PAWNS"] & sq_bb:
        return ("white", "pawn")
    if board["WHITE_ROOKS"] & sq_bb:
        return ("white", "rook")
    if board["WHITE_KNIGHTS"] & sq_bb:
        return ("white", "knight")
    if board["WHITE_BISHOPS"] & sq_bb:
        return ("white", "bishop")
    if board["WHITE_QUEEN"] & sq_bb:
        return ("white", "queen")
    if board["WHITE_KING"] & sq_bb:
        return ("white", "king")
    
    # Check black pieces
    if board["BLACK_PAWNS"] & sq_bb:
        return ("black", "pawn")
    if board["BLACK_ROOKS"] & sq_bb:
        return ("black", "rook")
    if board["BLACK_KNIGHTS"] & sq_bb:
        return ("black", "knight")
    if board["BLACK_BISHOPS"] & sq_bb:
        return ("black", "bishop")
    if board["BLACK_QUEEN"] & sq_bb:
        return ("black", "queen")
    if board["BLACK_KING"] & sq_bb:
        return ("black", "king")
    
    return (None, None)

def move_piece(from_sq, to_sq, board=None):
    """
    Move a piece from one square to another.
    Updates the bitboards accordingly, handling captures and castling.
    """
    if board is None:
        board = bb

    # Get the piece being moved
    color, piece_type = get_piece(from_sq, board)
    if color is None:
        return False  # No piece to move
    
    # Check for castling attempt via "King takes own Rook"
    dest_color, dest_piece = get_piece(to_sq, board)
    is_castling_attempt = False
    
    if piece_type == "king" and dest_piece == "rook" and color == dest_color:
        # This is a castling attempt by clicking King then Rook
        # Transform to standard King move (2 squares)
        if color == "white":
            if to_sq == 7: # H1 -> g1
                to_sq = 6
            elif to_sq == 0: # A1 -> c1
                to_sq = 2
        else: # black
            if to_sq == 63: # H8 -> g8
                to_sq = 62
            elif to_sq == 56: # A8 -> c8
                to_sq = 58
        is_castling_attempt = True
        # Note: We don't return here, we proceed with the modified to_sq
        # But we need to be careful not to capture the rook yet, logic below handles it

    # Build the bitboard key
    piece_key = f"{color.upper()}_{piece_type.upper()}S" if piece_type == "pawn" else f"{color.upper()}_{piece_type.upper()}"
    
    # Handle special case for pluralization
    if piece_type in ["rook", "knight", "bishop"]:
        piece_key = f"{color.upper()}_{piece_type.upper()}S"
    elif piece_type == "queen":
        piece_key = f"{color.upper()}_QUEEN"
    elif piece_type == "king":
        piece_key = f"{color.upper()}_KING"
    
    # Handle Castling Move (King moves 2 squares)
    if piece_type == "king" and abs(from_sq - to_sq) == 2:
        # Determine side
        if to_sq > from_sq: # King side
            rook_from = from_sq + 3
            rook_to = from_sq + 1
        else: # Queen side
            rook_from = from_sq - 4
            rook_to = from_sq - 1
            
        # Move Rook
        rook_key = f"{color.upper()}_ROOKS"
        board[rook_key] &= ~(1 << rook_from)
        board[rook_key] |= (1 << rook_to)

    # Remove any piece at destination square (capture)
    # If we converted a "King takes Rook" click to a castle move, dest_piece is now empty (usually)
    # unless we are castling onto a square occupied by opponent (impossible for valid castle)
    # But we need to re-check dest because to_sq might have changed
    dest_color, dest_piece = get_piece(to_sq, board)
    
    if dest_color is not None:
        dest_key = f"{dest_color.upper()}_{dest_piece.upper()}S" if dest_piece == "pawn" else f"{dest_color.upper()}_{dest_piece.upper()}"
        if dest_piece in ["rook", "knight", "bishop"]:
            dest_key = f"{dest_color.upper()}_{dest_piece.upper()}S"
        elif dest_piece == "queen":
            dest_key = f"{dest_color.upper()}_QUEEN"
        elif dest_piece == "king":
            dest_key = f"{dest_color.upper()}_KING"
        
        # Clear the captured piece
        board[dest_key] &= ~(1 << to_sq)
        
        # Update castling rights if a rook is captured
        if dest_piece == "rook":
            if to_sq == 7: board["CASTLING_RIGHTS"] &= ~1 # WK
            elif to_sq == 0: board["CASTLING_RIGHTS"] &= ~2 # WQ
            elif to_sq == 63: board["CASTLING_RIGHTS"] &= ~4 # BK
            elif to_sq == 56: board["CASTLING_RIGHTS"] &= ~8 # BQ
    
    # Clear the piece from the source square
    board[piece_key] &= ~(1 << from_sq)
    
    # Set the piece at the destination square
    board[piece_key] |= (1 << to_sq)
    
    # Update Castling Rights
    if piece_type == "king":
        if color == "white":
            board["CASTLING_RIGHTS"] &= ~3 # Clear WK and WQ
        else:
            board["CASTLING_RIGHTS"] &= ~12 # Clear BK and BQ
            
    if piece_type == "rook":
        if from_sq == 7: board["CASTLING_RIGHTS"] &= ~1 # WK
        elif from_sq == 0: board["CASTLING_RIGHTS"] &= ~2 # WQ
        elif from_sq == 63: board["CASTLING_RIGHTS"] &= ~4 # BK
        elif from_sq == 56: board["CASTLING_RIGHTS"] &= ~8 # BQ
    
    return board

# Copy the current board
def copy_current_board(bb):
    return bb.copy()




