import numpy as np
import pygame
import sys
import math
import random

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
GRAY = (128,128,128)

ROW_COUNT = 6
COLUMN_COUNT = 7

# AI difficulty levels
EASY = 1
MEDIUM = 2
HARD = 3

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    
    return False

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2
    
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4
    
    return score

def score_position(board, piece):
    score = 0
    
    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    
    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)
    
    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)
    
    # Score positive diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    
    # Score negative diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    
    return score

def minimax(board, depth, alpha, beta, maximizingPlayer, difficulty):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):  # AI wins
                return (None, 100000000000000)
            elif winning_move(board, 1):  # Human wins
                return (None, -100000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))
    
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, 2)
            new_score = minimax(board_copy, depth-1, alpha, beta, False, difficulty)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, 1)
            new_score = minimax(board_copy, depth-1, alpha, beta, True, difficulty)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def ai_move(board, difficulty):
    if difficulty == EASY:
        # Random move
        valid_locations = get_valid_locations(board)
        return random.choice(valid_locations)
    elif difficulty == MEDIUM:
        # Minimax with depth 2
        col, minimax_score = minimax(board, 2, -math.inf, math.inf, True, MEDIUM)
        return col
    else:  # HARD
        # Minimax with depth 4
        col, minimax_score = minimax(board, 4, -math.inf, math.inf, True, HARD)
        return col

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def draw_menu():
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.SysFont("monospace", 60)
    title = title_font.render("CONNECT 4", 1, BLUE)
    screen.blit(title, (width//2 - title.get_width()//2, 50))
    
    # Menu options
    menu_font = pygame.font.SysFont("monospace", 40)
    
    player_vs_player = menu_font.render("1. Player vs Player", 1, WHITE)
    player_vs_ai = menu_font.render("2. Player vs AI", 1, WHITE)
    quit_game = menu_font.render("3. Quit", 1, WHITE)
    
    screen.blit(player_vs_player, (width//2 - player_vs_player.get_width()//2, 180))
    screen.blit(player_vs_ai, (width//2 - player_vs_ai.get_width()//2, 240))
    screen.blit(quit_game, (width//2 - quit_game.get_width()//2, 300))
    
    # Instructions
    instr_font = pygame.font.SysFont("monospace", 25)
    instructions = instr_font.render("Press 1, 2, or 3 to select", 1, GRAY)
    screen.blit(instructions, (width//2 - instructions.get_width()//2, 380))
    
    pygame.display.update()

def draw_difficulty_menu():
    screen.fill(BLACK)
    
    # Title
    title_font = pygame.font.SysFont("monospace", 50)
    title = title_font.render("Select AI Difficulty", 1, BLUE)
    screen.blit(title, (width//2 - title.get_width()//2, 50))
    
    # Difficulty options
    menu_font = pygame.font.SysFont("monospace", 40)
    
    easy = menu_font.render("1. Easy", 1, GREEN)
    medium = menu_font.render("2. Medium", 1, YELLOW)
    hard = menu_font.render("3. Hard", 1, RED)
    back = menu_font.render("4. Back to Main Menu", 1, WHITE)
    
    screen.blit(easy, (width//2 - easy.get_width()//2, 150))
    screen.blit(medium, (width//2 - medium.get_width()//2, 210))
    screen.blit(hard, (width//2 - hard.get_width()//2, 270))
    screen.blit(back, (width//2 - back.get_width()//2, 330))
    
    # Difficulty descriptions
    desc_font = pygame.font.SysFont("monospace", 20)
    easy_desc = desc_font.render("AI makes random moves", 1, GRAY)
    medium_desc = desc_font.render("AI thinks 2 moves ahead", 1, GRAY)
    hard_desc = desc_font.render("AI thinks 4 moves ahead", 1, GRAY)
    
    screen.blit(easy_desc, (width//2 - easy_desc.get_width()//2, 185))
    screen.blit(medium_desc, (width//2 - medium_desc.get_width()//2, 245))
    screen.blit(hard_desc, (width//2 - hard_desc.get_width()//2, 305))
    
    pygame.display.update()

def main_menu():
    in_menu = True
    game_mode = None
    ai_difficulty = None
    
    while in_menu:
        draw_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Player vs Player
                    return "PVP", None
                elif event.key == pygame.K_2:
                    # Player vs AI - go to difficulty selection
                    ai_difficulty = difficulty_menu()
                    if ai_difficulty:
                        return "PVAI", ai_difficulty
                elif event.key == pygame.K_3:
                    # Quit
                    pygame.quit()
                    sys.exit()
    
    return None, None

def difficulty_menu():
    in_menu = True
    
    while in_menu:
        draw_difficulty_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return EASY
                elif event.key == pygame.K_2:
                    return MEDIUM
                elif event.key == pygame.K_3:
                    return HARD
                elif event.key == pygame.K_4:
                    return None
    
    return None

def game_loop(game_mode, ai_difficulty=None):
    board = create_board()
    print_board(board)
    game_over = False
    turn = 0  # 0 for Player 1 (human), 1 for Player 2 (human or AI)
    
    draw_board(board)
    pygame.display.update()
    
    myfont = pygame.font.SysFont("monospace", 75)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to main menu
            
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                # Show preview for current player
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                else:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                
                # Handle human player's turn
                if (game_mode == "PVP") or (game_mode == "PVAI" and turn == 0):
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
                    
                    if 0 <= col < COLUMN_COUNT and is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        piece = 1 if turn == 0 else 2
                        drop_piece(board, row, col, piece)
                        
                        if winning_move(board, piece):
                            if turn == 0:
                                label = myfont.render("Player 1 wins!!", 1, RED)
                            else:
                                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                            screen.blit(label, (40,10))
                            game_over = True
                        
                        print_board(board)
                        draw_board(board)
                        
                        # Switch turns
                        turn += 1
                        turn = turn % 2
        
        # Handle AI's turn (if playing against AI and it's AI's turn)
        if not game_over and game_mode == "PVAI" and turn == 1:
            pygame.time.wait(300)  # Small delay for AI "thinking"
            col = ai_move(board, ai_difficulty)
            
            if 0 <= col < COLUMN_COUNT and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)  # AI is always piece 2
                
                if winning_move(board, 2):
                    label = myfont.render("AI wins!!", 1, YELLOW)
                    screen.blit(label, (40,10))
                    game_over = True
                
                print_board(board)
                draw_board(board)
                
                # Switch turns back to human
                turn += 1
                turn = turn % 2
        
        # Check for draw (only check after a move has been made)
        if len(get_valid_locations(board)) == 0 and not game_over:
            label = myfont.render("It's a draw!", 1, WHITE)
            screen.blit(label, (80,10))
            game_over = True
        
        if game_over:
            # Show "Press ESC for menu" message
            esc_font = pygame.font.SysFont("monospace", 30)
            esc_msg = esc_font.render("Press ESC for main menu", 1, WHITE)
            screen.blit(esc_msg, (width//2 - esc_msg.get_width()//2, height - 40))
            pygame.display.update()
            
            # Wait for ESC to return to menu
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
    
    return  # Return to main menu

# Initialize Pygame
pygame.init()
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")

# Main game loop
while True:
    game_mode, ai_difficulty = main_menu()
    if game_mode:
        game_loop(game_mode, ai_difficulty)