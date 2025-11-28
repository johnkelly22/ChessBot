def squares_in(bb):
    squares = []
    while bb:
        sq = (bb & -bb).bit_length() - 1
        bb &= bb - 1
        squares.append(sq)
    return squares

def sq_to_bb(square):
    return 0xFFFFFFFFFFFFFFFF & (1 << square)

def to_xy(square):
    x = square % 8
    y = 7 - (square // 8)
    return (x * 100, y * 100)

def set_bit(bb, square):
    return bb | (1 << square)

def clear_bit(bb, square):
    return bb & ~(1 << square)

def is_set(bb, square):
    return (bb >> square) & 1
