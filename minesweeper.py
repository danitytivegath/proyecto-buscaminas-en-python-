"""
Minesweeper - Final Project (Introduction to Programming)

Console-based Minesweeper with user accounts, five difficulty levels
and a global leaderboard.
"""

import os
import random

os.system("")  #enables ANSI colors in the Windows console

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------

#console colors (ANSI escape codes)
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

#color of each number (the index is the number of adjacent mines)
NUMBER_COLORS = ["", BLUE, GREEN, RED, MAGENTA, YELLOW, CYAN, RED, GRAY]

#difficulty levels: the same index in each list refers to the same level
DIFFICULTY_NAMES = ["Beginner", "Easy", "Medium", "Hard", "Expert"]
BOARD_SIZES = [4, 6, 8, 10, 12]
MINE_COUNTS = [3, 6, 10, 18, 30]
SCORE_MULTIPLIERS = [1, 2, 3, 4, 5]

#scoring
POINTS_PER_CELL = 10
WIN_BONUS = 100

#values stored in the mine board
MINE = -1

#states of a cell in the visible board
HIDDEN = "?"
REVEALED = "R"
FLAGGED = "F"

#possible outcomes of a game
RESULT_WIN = "win"
RESULT_LOSS = "loss"
RESULT_QUIT = "quit"

#Helper functions

def read_number(prompt, minimum, maximum):
    """Ask for a number until the user enters a valid one in [minimum, maximum]."""
    while True:
        text = input(prompt)
        if text.isdigit():
            number = int(text)
            if minimum <= number <= maximum:
                return number
        print(f"{RED}Invalid input. Enter a number between {minimum} and {maximum}.{RESET}")


def create_matrix(rows, columns, value):
    """Return a rows x columns matrix (list of lists) filled with the given value."""
    matrix = []
    for i in range(0, rows):
        row = []
        for j in range(0, columns):
            row.append(value)
        matrix.append(row)
    return matrix


def print_title(text):
    """Print a centered title between two decorative lines."""
    print("\n" + CYAN + "=" * 40 + RESET)
    print(CYAN + BOLD + text.center(40) + RESET)
    print(CYAN + "=" * 40 + RESET)



#User management


def register_user(usernames, passwords, scores):
    """Create a new user account, rejecting empty or duplicated usernames."""
    print_title("NEW PLAYER REGISTRATION")
    new_username = input("Choose a username: ")

    if new_username.strip() == "":
        print(RED + "The username cannot be empty." + RESET)
        return

    for i in range(0, len(usernames)):
        if usernames[i] == new_username:
            print(RED + "That username already exists. Please choose another one." + RESET)
            return

    new_password = input("Choose a password: ")
    if new_password.strip() == "":
        print(RED + "The password cannot be empty." + RESET)
        return

    usernames.append(new_username)
    passwords.append(new_password)
    scores.append(0)
    print(GREEN + "Registration successful! You can now log in." + RESET)


def login(usernames, passwords, scores):
    """Validate the credentials and open the game menu if they are correct."""
    print_title("LOG IN")
    username = input("Username: ")
    password = input("Password: ")

    user_index = -1
    for i in range(0, len(usernames)):
        if usernames[i] == username and passwords[i] == password:
            user_index = i
            break

    if user_index != -1:
        print(GREEN + "\nWelcome to Minesweeper, " + username + "!" + RESET)
        game_menu(username, user_index, scores, usernames)
    else:
        print(RED + "Error: incorrect username or password." + RESET)


def show_leaderboard(usernames, scores):
    """Print all players sorted by high score (highest first)."""
    print_title("LEADERBOARD")

    #sort the user indexes (bubble sort) without modifying the original lists
    order = []
    for i in range(0, len(usernames)):
        order.append(i)

    for i in range(0, len(order)):
        for j in range(0, len(order) - 1 - i):
            if scores[order[j]] < scores[order[j + 1]]:
                temp = order[j]
                order[j] = order[j + 1]
                order[j + 1] = temp

    for rank in range(0, len(order)):
        index = order[rank]
        print(f" {rank + 1}. {usernames[index]:<15} {YELLOW}{scores[index]:>6} pts{RESET}")
    print(CYAN + "=" * 40 + RESET)


#Game logic

def place_mines(mine_board, rows, columns, mine_count, safe_row, safe_column):
    """Randomly place the mines and compute the adjacent-mine count of every cell.

    The cell (safe_row, safe_column) never receives a mine, so the first
    move of the player is always safe.
    """
    placed = 0
    while placed < mine_count:
        row = random.randint(0, rows - 1)
        column = random.randint(0, columns - 1)
        is_safe_cell = (row == safe_row and column == safe_column)
        if mine_board[row][column] != MINE and not is_safe_cell:
            mine_board[row][column] = MINE
            placed = placed + 1

    #count the mines around every cell that is not a mine
    for row in range(0, rows):
        for column in range(0, columns):
            if mine_board[row][column] != MINE:
                adjacent_mines = 0
                for d_row in range(-1, 2):
                    for d_column in range(-1, 2):
                        neighbor_row = row + d_row
                        neighbor_column = column + d_column
                        if 0 <= neighbor_row < rows and 0 <= neighbor_column < columns:
                            if mine_board[neighbor_row][neighbor_column] == MINE:
                                adjacent_mines = adjacent_mines + 1
                mine_board[row][column] = adjacent_mines


def reveal_cells(row, column, mine_board, visible_board, rows, columns):
    """Reveal a cell. If it has no adjacent mines, also reveal its neighbors.

    Returns the number of cells that were revealed.
    """
    revealed_count = 0
    pending = [[row, column]]  #cells waiting to be processed

    while len(pending) > 0:
        current = pending.pop()
        current_row = current[0]
        current_column = current[1]

        if visible_board[current_row][current_column] != HIDDEN:
            continue  #already revealed or flagged

        visible_board[current_row][current_column] = REVEALED
        revealed_count = revealed_count + 1

        if mine_board[current_row][current_column] == 0:
            for d_row in range(-1, 2):
                for d_column in range(-1, 2):
                    neighbor_row = current_row + d_row
                    neighbor_column = current_column + d_column
                    if 0 <= neighbor_row < rows and 0 <= neighbor_column < columns:
                        pending.append([neighbor_row, neighbor_column])

    return revealed_count


def get_cell_symbol(visible_board, mine_board, row, column, reveal_all):
    """Return the colored text used to draw a single cell."""
    state = visible_board[row][column]
    value = mine_board[row][column]

    if reveal_all and value == MINE:
        if state == FLAGGED:
            return GREEN + "F" + RESET  #correctly flagged mine
        return RED + "*" + RESET        #mine
    if state == FLAGGED:
        return YELLOW + "F" + RESET
    if state == HIDDEN:
        return GRAY + "■" + RESET
    if value == 0:
        return " "
    return NUMBER_COLORS[value] + str(value) + RESET


def print_board(visible_board, mine_board, rows, columns, reveal_all):
    """Print the board with row and column coordinates."""
    print()
    header = "    "
    for j in range(0, columns):
        header = header + f"{j:^3}"
    print(BOLD + header + RESET)
    print("    " + "---" * columns)

    for i in range(0, rows):
        line = f"{i:>2} |"
        for j in range(0, columns):
            line = line + " " + get_cell_symbol(visible_board, mine_board, i, j, reveal_all) + " "
        print(line)
    print()


def choose_difficulty():
    """Show the difficulty menu and return the index of the chosen level."""
    print("\n" + BOLD + "--- SELECT DIFFICULTY ---" + RESET)
    for i in range(0, len(DIFFICULTY_NAMES)):
        print(f"{i + 1}. {DIFFICULTY_NAMES[i]:<9} ({BOARD_SIZES[i]}x{BOARD_SIZES[i]} board, "
              f"{MINE_COUNTS[i]} mines, x{SCORE_MULTIPLIERS[i]} points)")
    return read_number("Choose an option: ", 1, len(DIFFICULTY_NAMES)) - 1


def play_minesweeper(user_index, scores):
    """Play one game and update the player's high score if it is beaten."""
    level = choose_difficulty()
    rows = BOARD_SIZES[level]
    columns = BOARD_SIZES[level]
    mine_count = MINE_COUNTS[level]
    multiplier = SCORE_MULTIPLIERS[level]

    mine_board = create_matrix(rows, columns, 0)          #adjacent-mine counts and mines
    visible_board = create_matrix(rows, columns, HIDDEN)  #what the player can see

    mines_placed = False
    game_active = True
    result = ""
    game_score = 0
    safe_cells_left = (rows * columns) - mine_count
    flags_placed = 0

    print_title("LEVEL: " + DIFFICULTY_NAMES[level].upper())
    print("Actions: " + BOLD + "r" + RESET + " = reveal | " + BOLD + "f" + RESET +
          " = flag/unflag | " + BOLD + "q" + RESET + " = quit with your points")

    while game_active:
        print_board(visible_board, mine_board, rows, columns, False)
        print(f"Mines left: {RED}{mine_count - flags_placed}{RESET}   "
              f"Score: {YELLOW}{game_score}{RESET}")

        action = input("Action (r / f / q): ").lower()

        if action == "q":
            result = RESULT_QUIT
            game_active = False

        elif action == "r" or action == "f":
            row = read_number(f"Choose row (0 to {rows - 1}): ", 0, rows - 1)
            column = read_number(f"Choose column (0 to {columns - 1}): ", 0, columns - 1)

            if action == "f":
                if visible_board[row][column] == HIDDEN:
                    visible_board[row][column] = FLAGGED
                    flags_placed = flags_placed + 1
                elif visible_board[row][column] == FLAGGED:
                    visible_board[row][column] = HIDDEN
                    flags_placed = flags_placed - 1
                else:
                    print(RED + "You cannot flag a revealed cell." + RESET)

            else:  #action == "r"
                if visible_board[row][column] == FLAGGED:
                    print(RED + "That cell is flagged. Remove the flag first with 'f'." + RESET)
                elif visible_board[row][column] == REVEALED:
                    print(RED + "That cell is already revealed. Try another one." + RESET)
                else:
                    #mines are placed on the first move so it is always safe
                    if not mines_placed:
                        place_mines(mine_board, rows, columns, mine_count, row, column)
                        mines_placed = True

                    if mine_board[row][column] == MINE:
                        result = RESULT_LOSS
                        game_active = False
                    else:
                        revealed = reveal_cells(row, column, mine_board, visible_board, rows, columns)
                        game_score = game_score + revealed * POINTS_PER_CELL * multiplier
                        safe_cells_left = safe_cells_left - revealed

                        if safe_cells_left == 0:
                            result = RESULT_WIN
                            game_active = False
        else:
            print(RED + "Invalid action. Use r, f or q." + RESET)

    #game over
    if result == RESULT_LOSS:
        print_board(visible_board, mine_board, rows, columns, True)
        print(RED + BOLD + "BOOM! You stepped on a mine. You lost the game." + RESET)
        print("You score no points when you lose. Quit in time next game!")
        game_score = 0
    elif result == RESULT_WIN:
        print_board(visible_board, mine_board, rows, columns, True)
        bonus = WIN_BONUS * multiplier
        game_score = game_score + bonus
        print(GREEN + BOLD + "CONGRATULATIONS! You cleared the whole board." + RESET)
        print(f"Victory bonus: +{bonus} points")
    else:
        print(YELLOW + "You quit in time and kept your points." + RESET)

    print(f"\nScore for this game: {YELLOW}{game_score}{RESET}")
    if game_score > scores[user_index]:
        scores[user_index] = game_score
        print(GREEN + "New personal record saved to the leaderboard!" + RESET)

#menus


def game_menu(username, user_index, scores, usernames):
    """Menu shown after a successful login."""
    option = ""
    while option != "3":
        print_title("MINESWEEPER MENU")
        print(f"Player: {BOLD}{username}{RESET}   "
              f"High score: {YELLOW}{scores[user_index]}{RESET} pts\n")
        print("1. Play a game")
        print("2. View global leaderboard")
        print("3. Log out")
        option = input("Choose an option: ")

        if option == "1":
            play_minesweeper(user_index, scores)
        elif option == "2":
            show_leaderboard(usernames, scores)
        elif option == "3":
            print("Logging out...")
        else:
            print(RED + "Invalid option." + RESET)


def main():
    """Program entry point: main menu loop."""
    usernames = ["pro_gamer"]
    passwords = ["1234"]
    scores = [150]

    option = ""
    while option != "4":
        print_title("FINAL PROJECT - MINESWEEPER")
        print("1. Register")
        print("2. Log in")
        print("3. View leaderboard")
        print("4. Exit")
        option = input("Choose an option: ")

        if option == "1":
            register_user(usernames, passwords, scores)
        elif option == "2":
            login(usernames, passwords, scores)
        elif option == "3":
            show_leaderboard(usernames, scores)
        elif option == "4":
            print("Goodbye! Thanks for playing.")
        else:
            print(RED + "Invalid option." + RESET)


main()
