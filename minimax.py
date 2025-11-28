import eval
import moves
import board

INF = 10**9

def minimax(bb, depth, turn, alpha, beta):
    """
    Minimax algorithm to determine the best move evaluation.
    
    Args:
        bb: The current board state (dictionary of bitboards).
        depth: The depth to search.
        turn: The current turn ("white" or "black").
        alpha: The best value that the maximizer currently can guarantee at that level or above.
        beta: The best value that the minimizer currently can guarantee at that level or above.
        
    Returns:
        The evaluation score of the board.
        Black wants to maximize this score (positive).
        White wants to minimize this score (negative).
    """

    if moves.is_game_over(bb) or depth == 0:
        return eval.eval_total(bb)

    if turn == "black": # Maximizing player
        max_eval = -INF
        for move in moves.generate_all_legal_moves_black(bb):
            copy = board.copy_current_board(bb)
            board.move_piece(move[0], move[1], copy)
            eval_val = minimax(copy, depth - 1, "white", alpha, beta)
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval
        
    else: # White (Minimizing player)
        min_eval = INF
        for move in moves.generate_all_legal_moves_white(bb):
            copy = board.copy_current_board(bb)
            board.move_piece(move[0], move[1], copy)
            eval_val = minimax(copy, depth - 1, "black", alpha, beta)
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(bb, depth):
    best_move = None
    best_score = -INF
    alpha = -INF
    beta = INF

    for move in moves.generate_all_legal_moves_black(bb):
        new_board = board.copy_current_board(bb)
        board.move_piece(move[0], move[1], new_board)

        # Now evaluate the result of this move
        # After Black moves, it is White's turn
        score = minimax(new_board, depth - 1, "white", alpha, beta)

        # If this is the best score so far, remember it
        if score > best_score:
            best_score = score
            best_move = move
        
        # Update alpha for pruning in sibling nodes
        alpha = max(alpha, best_score)
        
    board.turn = "white"
    return best_move

