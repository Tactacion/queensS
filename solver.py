from z3 import Solver, Bool, Sum, If, Not, Implies, sat
import tempfile
import webbrowser
import os
import time

def html_print_board(board_size, colored_regions, solution):
    """Print the board as an HTML table with colored regions and Queens"""
    html = '<html><meta charset="UTF-8"><table>'
    for r in range(board_size):
        html += "<tr>"
        for c in range(board_size):
            color = "white"
            for region, cells in colored_regions.items():
                if (r, c) in cells:
                    color = region
                    break
            html += f'<td style="background-color: {color}; font-size: 60px; text-align: center">'
            html += "♛" if solution[r][c] else " "
            html += "</td>"
        html += "</tr>"
    html += "</table></html>"
    return html

def convert_to_colored_regions(board: str, color_to_name_mapping: dict) -> tuple:
    """Convert the board string to a dictionary of colored regions"""
    colored_regions = {}
    rows = board.strip().split("\n")
    for r, row in enumerate(rows):
        for c, color_key in enumerate(row):
            color_name = color_to_name_mapping[color_key]
            if color_name not in colored_regions:
                colored_regions[color_name] = []
            colored_regions[color_name].append((r, c))
    board_size = len(rows)
    return colored_regions, board_size

def solve_queens_game(board_size, colored_regions):
    """Solve the Queens game using Z3"""
    # Create a Z3 solver instance
    solver = Solver()

    # Create a 2D array of boolean variables representing the board
    board = [
        [Bool(f"cell_{r}_{c}") for c in range(board_size)] for r in range(board_size)
    ]
    # Constraint: Each row must contain exactly one queen
    for r in range(board_size):
        solver.add(Sum([If(board[r][c], 1, 0) for c in range(board_size)]) == 1)
    # Constraint: Each column must contain exactly one queen
    for c in range(board_size):
        solver.add(Sum([If(board[r][c], 1, 0) for r in range(board_size)]) == 1)
    # Constraint: Each colored region must contain exactly one queen
    for region in colored_regions.values():
        solver.add(Sum([If(board[r][c], 1, 0) for r, c in region]) == 1)
    # Constraint: No two queens can be adjacent, including diagonally
    for r in range(board_size):
        for c in range(board_size):
            if r > 0:
                solver.add(Implies(board[r][c], Not(board[r - 1][c])))
            if r < board_size - 1:
                solver.add(Implies(board[r][c], Not(board[r + 1][c])))
            if c > 0:
                solver.add(Implies(board[r][c], Not(board[r][c - 1])))
            if c < board_size - 1:
                solver.add(Implies(board[r][c], Not(board[r][c + 1])))
            if r > 0 and c > 0:
                solver.add(Implies(board[r][c], Not(board[r - 1][c - 1])))
            if r > 0 and c < board_size - 1:
                solver.add(Implies(board[r][c], Not(board[r - 1][c + 1])))
            if r < board_size - 1 and c > 0:
                solver.add(Implies(board[r][c], Not(board[r + 1][c - 1])))
            if r < board_size - 1 and c < board_size - 1:
                solver.add(Implies(board[r][c], Not(board[r + 1][c + 1])))
    start_time = time.time()  # Start the timer
    if solver.check() == sat:
        solve_time = time.time() - start_time  # Calculate the elapsed time
        model = solver.model()
        solution = [
            [model.evaluate(board[r][c]) for c in range(board_size)]
            for r in range(board_size)
        ]
        return solution, solve_time
    else:
        return None, None

def open_html_in_browser(html_content):
    """Open the given HTML content in the default web browser"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        temp_file.write(html_content.encode("utf-8"))
        temp_file_path = temp_file.name
    webbrowser.open(f"file://{os.path.abspath(temp_file_path)}")

# Your board and color mapping
board = """
CCCCCCOOO
TVVVWCCCO
TTTVWCGGO
BVVVWYGYO
BVPPPYGYO
BVVVPYYYO
BBBBPOOYO
BBBBBOOYO
BBBOOOOOO
"""

color_to_name_mapping = {
    "V": "purple",
    "O": "orange",
    "G": "green",
    "B": "blue",
    "W": "gray",
    "C": "cyan",
    "P": "pink",
    "T":"red",
    "Y":"yellow"

}

# Convert to colored regions and solve
colored_regions, board_size = convert_to_colored_regions(board, color_to_name_mapping)
solution, solve_time = solve_queens_game(board_size, colored_regions)

if solution:
    html_content = html_print_board(board_size, colored_regions, solution)
    open_html_in_browser(html_content)
    print(f"Solution found in {solve_time:.4f} seconds")
else:
    print("No solution found!")
