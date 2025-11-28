import pygame
import sys
import board
import moves
from eval import eval_white
from utils import squares_in, to_xy
from minimax import minimax, find_best_move

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.font.init() 
font = pygame.font.SysFont("Times New Roman", 100) 
font = pygame.font.SysFont("Times New Roman", 100)

# Set up the display
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess Bot")
icon = pygame.image.load("black-queen.png")
pygame.display.set_icon(icon)
move_sound = pygame.mixer.Sound("move-self.mp3")

def close_game():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                pygame.quit()
                sys.exit()

def check_game_over():
    if moves.white_checkmate():
        draw_all()
        draw_centered_text("Black Wins", font, (255, 255, 255), (0, 0, 0))
        pygame.display.flip()
        close_game()
    elif moves.black_checkmate():
        draw_all()
        draw_centered_text("White Wins", font, (255, 255, 255), (0, 0, 0))
        pygame.display.flip()
        close_game()

def draw_all():
        screen.fill(BLACK)

        # Draw Grid
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(screen, LIGHT, (i * 100, j * 100, 100, 100))
                else:
                    pygame.draw.rect(screen, DARK, (i * 100, j * 100, 100, 100))
        
        # Highlight selected square
        if is_selected:
            x_from = last_selected_sq % 8
            y_from = 7 - (last_selected_sq // 8)
            pygame.draw.rect(screen, WHITE_HIGHLIGHT_FROM, (x_from * 100, y_from * 100, 100, 100), 5)
            x_to = square % 8
            y_to = 7 - (square // 8)
            pygame.draw.rect(screen, WHITE_HIGHLIGHT_TO, (x_to * 100, y_to * 100, 100, 100), 5)


        if board.turn == "white":
            x_from = best_move_from % 8
            y_from = 7 - (best_move_from // 8)
            pygame.draw.rect(screen, BLACK_HIGHLIGHT_FROM, (x_from * 100, y_from * 100, 100, 100), 5)
            x_to = best_move_to % 8
            y_to = 7 - (best_move_to // 8)
            pygame.draw.rect(screen, BLACK_HIGHLIGHT_TO, (x_to * 100, y_to * 100, 100, 100), 5)

        # Draw pieces from bitboard
        draw_pieces()

        # Update the display
        pygame.display.flip()

# Load piece images once at startup
piece_images = {}
piece_names = ["white-pawn", "white-rook", "white-knight", "white-bishop", "white-queen", "white-king",
               "black-pawn", "black-rook", "black-knight", "black-bishop", "black-queen", "black-king"]
for name in piece_names:
    img = pygame.image.load(f"{name}.png")
    piece_images[name] = pygame.transform.scale_by(img, 0.78)

# Helper Functions
def draw_centered_text(text, font, color, outline_color, offset=2):
    text_surf = font.render(text, True, color)
    outline_surf = font.render(text, True, outline_color)
    x = width // 2 - text_surf.get_width() // 2
    y = height // 2 - text_surf.get_height() // 2
    
    # Draw outline
    screen.blit(outline_surf, (x - offset, y + offset))
    screen.blit(outline_surf, (x - offset, y - offset))
    screen.blit(outline_surf, (x + offset, y + offset))
    screen.blit(outline_surf, (x + offset, y - offset))
    
    # Draw text
    screen.blit(text_surf, (x, y))

def draw_pieces():
    """Draw all pieces on the board."""
    for p in squares_in(board.bb['WHITE_PAWNS']):
        screen.blit(piece_images['white-pawn'], to_xy(p))
    for p in squares_in(board.bb['WHITE_ROOKS']):
        screen.blit(piece_images['white-rook'], to_xy(p))
    for p in squares_in(board.bb['WHITE_KNIGHTS']):
        screen.blit(piece_images['white-knight'], to_xy(p))
    for p in squares_in(board.bb['WHITE_BISHOPS']):
        screen.blit(piece_images['white-bishop'], to_xy(p))
    for p in squares_in(board.bb['WHITE_QUEEN']):
        screen.blit(piece_images['white-queen'], to_xy(p))
    for p in squares_in(board.bb['WHITE_KING']):
        screen.blit(piece_images['white-king'], to_xy(p))
    for p in squares_in(board.bb['BLACK_PAWNS']):
        screen.blit(piece_images['black-pawn'], to_xy(p))
    for p in squares_in(board.bb['BLACK_ROOKS']):
        screen.blit(piece_images['black-rook'], to_xy(p))
    for p in squares_in(board.bb['BLACK_KNIGHTS']):
        screen.blit(piece_images['black-knight'], to_xy(p))
    for p in squares_in(board.bb['BLACK_BISHOPS']):
        screen.blit(piece_images['black-bishop'], to_xy(p))
    for p in squares_in(board.bb['BLACK_QUEEN']):
        screen.blit(piece_images['black-queen'], to_xy(p))
    for p in squares_in(board.bb['BLACK_KING']):
        screen.blit(piece_images['black-king'], to_xy(p))

# Global Variables
depth = 4 #DIFFICULTY: HIGHER IS SLOWER
is_selected = False
last_selected_sq = 0
square = 0
move_count = 0
best_move_from = -1
best_move_to = -1

# Define colors
BLACK = (0, 0, 0)
LIGHT = (252, 225, 202)
DARK = (112, 88, 74)
WHITE_HIGHLIGHT_FROM = (152, 227, 200)
WHITE_HIGHLIGHT_TO = (152, 227, 150)
BLACK_HIGHLIGHT_FROM = (237, 116, 85)
BLACK_HIGHLIGHT_TO = (207, 62, 25)


# Main Game Loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse click position
            click_x, click_y = event.pos
            x = click_x // 100
            y = abs(7 - click_y // 100)    
            square = (y * 8 + x)

            # User Movement
            if not is_selected:
                # First click - select a piece
                color, piece_type = board.get_piece(square)
                if color == board.turn:  # Only select if it's the player's turn
                    last_selected_sq = square
                    is_selected = True
            else:
                # Second click - try to move
                color, piece_type = board.get_piece(last_selected_sq)
                
                if color is None:
                    # No piece at selected square, deselect
                    is_selected = False
                else:
                    # Generate moves for the selected piece
                    user_moves = []
                    if piece_type == "pawn":
                        user_moves = moves.generate_pawn_moves(last_selected_sq)
                    elif piece_type == "knight":
                        user_moves = moves.generate_knight_moves(last_selected_sq)
                    elif piece_type == "bishop":
                        user_moves = moves.generate_bishop_moves(last_selected_sq)
                    elif piece_type == "rook":
                        user_moves = moves.generate_rook_moves(last_selected_sq)
                    elif piece_type == "queen":
                        user_moves = moves.generate_queen_moves(last_selected_sq)
                    elif piece_type == "king":
                        user_moves = moves.generate_king_moves(last_selected_sq)
                    
                    # Check if the move is valid
                    move_to_check = (last_selected_sq, square)
                    
                    # Handle "King takes own Rook" as castling
                    if piece_type == "king":
                        tgt_c, tgt_p = board.get_piece(square)
                        if tgt_p == "rook" and tgt_c == color:
                            if color == "white":
                                if square == 7: move_to_check = (4, 6) # e1 -> g1
                                elif square == 0: move_to_check = (4, 2) # e1 -> c1
                            else:
                                if square == 63: move_to_check = (60, 62) # e8 -> g8
                                elif square == 56: move_to_check = (60, 58) # e8 -> c8

                    if move_to_check in user_moves:
                        # Move the piece
                        board.move_piece(move_to_check[0], move_to_check[1])
                        move_sound.play()
                        
                        # Switch turn
                        if board.turn == "white":
                            move_count += 1
                            board.turn = "black"
                            draw_all()
                            is_selected = False
                            best_move = find_best_move(board.bb, depth)
                            best_move_from = best_move[0]
                            best_move_to = best_move[1]
                            board.move_piece(best_move_from, best_move_to)
                            move_sound.play()
                        else:
                            board.turn = "white"
                        check_game_over()

                    else:
                        # Invalid move - check if clicking another piece to select it
                        new_color, new_piece = board.get_piece(square)
                        # If clicking the same square, deselect
                        if last_selected_sq == square:
                            is_selected = False
                        elif new_color == board.turn:
                            # Selecting a different piece of the same color
                            last_selected_sq = square
                        else:
                            # Invalid move to empty square or enemy piece (that isn't a capture)
                            is_selected = False

    # Draw Screen
    draw_all()

# Quit Pygame
pygame.quit()
sys.exit()
