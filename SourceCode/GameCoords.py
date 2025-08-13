def game_to_array_coords(x, y, size):
    return (size - 1 - x, y)

def array_to_game_coords(row, col, size):
    return (size - 1 - row, col)