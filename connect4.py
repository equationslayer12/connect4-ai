import pygame
from numpy import array
import numpy

# Pygame setup
pygame.init()
pygame.display.set_caption('Connect 4')
screen = pygame.display.set_mode((700, 700))
clock = pygame.time.Clock()

run = True
screen.fill((210, 140, 70))

# CONSTANTS
WHITE = 1
BLACK = 0
DRAW = 5

WHITE_TURN = True
BLACK_TURN = False

HOR_DOTS = [[5, 3], [4, 3], [3, 3], [2, 3], [1, 3], [0, 3]]
VER_DOTS = [[2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6]]

TOPRIGHT = 1
TOPLEFT = 2
BOTTOMRIGHT = 3
BOTTOMLEFT = 4

DIRECTIONS = [TOPRIGHT, TOPLEFT, BOTTOMRIGHT, BOTTOMLEFT]

DEPTH = 5
AI_FIRST = False
MACHINE_GAME = False
MANUAL = False


def order_moves(moves):
    evals = {}
    for x in moves:
        evaluation = 0
        # CLOSE TO THE CENTER
        evaluation += 10 * 7 - abs(3 - x)
        # if last_dot is None:
        #     state = 0
        # else:
        #     demo_board = numpy.copy(board)
        #     demo_board[last_dot[0], last_dot[1]] = WHITE if turn else BLACK
        #     state = game_state(demo_board, last_dot)
        # # Win in the next move
        # if state == 1:
        #     evaluation += 200
        # # Lose in the next move
        # elif state == -1:
        #     evaluation -= 200
        evals[x] = evaluation
    sorted_values = sorted(evals, key=evals.get)
    sorted_values.reverse()
    return sorted_values


def best_move(depth, board, turn, last_dot, alpha, beta):
    global positions
    state = game_state(board, last_dot)
    possible_moves_ = order_moves(possible_moves(board))

    # STOP CONDITIONS
    if depth == 0 or state == 1 or state == 0 or len(possible_moves_) == 0:
        if (state == 0 and turn == WHITE_TURN) or (state == 1 and turn == BLACK_TURN):
            return last_dot[1], -1
        elif (state == 1 and turn == WHITE_TURN) or (state == 0 and turn == BLACK_TURN):
            return last_dot[1], 1
        else:
            return last_dot[1], 0

    scores = []
    for x in possible_moves_:
        demo_board = numpy.copy(board)
        for y in range(6):
            if demo_board[5 - y, x] is None:
                demo_board[5 - y, x] = WHITE if turn else BLACK
                last_move = (5 - y, x)
                break
        move, evaluation = best_move(depth - 1, demo_board, not turn, last_move, -beta, -alpha)
        evaluation = -evaluation
        positions += 1
        # print(f"TURN: {turn}")
        # print(f"alpha: {alpha}, beta: {beta}, eval: {evaluation}, DEPTH: {depth}")

        if evaluation >= beta and depth != DEPTH:
            # move is too good
            # print("SNIP!!!!!!!")
            return x, evaluation

        alpha = max(evaluation, alpha)

        scores.append(evaluation)

    if depth == DEPTH:
        print(scores)

    maximum = max(scores)
    return [possible_moves_[scores.index(maximum)], maximum]


def random_move(board):
    import random
    return random.choice(possible_moves(board))


def get_index(y, x, direction):
    if direction == TOPRIGHT:
        x += 1
        y -= 1
    elif direction == TOPLEFT:
        x -= 1
        y -= 1
    elif direction == BOTTOMRIGHT:
        x += 1
        y += 1
    elif direction == BOTTOMLEFT:
        x -= 1
        y += 1
    if x < 0 or x > 6 or y < 0 or y > 5:
        return None
    return y, x


def zigzags(board, last_dot):
    # zigzags
    y, x = last_dot
    color = board[last_dot[0], last_dot[1]]

    # \
    while 1:
        topleft = get_index(y, x, TOPLEFT)
        if topleft:
            y, x = topleft
        else:
            break
    in_a_row = 0
    while 1:
        if board[y, x] == color:
            in_a_row += 1
        else:
            in_a_row = 0
        if in_a_row >= 4:
            return color
        move = get_index(y, x, BOTTOMRIGHT)

        if not move:
            break
        else:
            y, x = move

    # /
    y, x = last_dot
    while 1:
        topright = get_index(y, x, TOPRIGHT)
        if topright:
            y, x = topright
        else:
            break
    in_a_row = 0

    while 1:
        if board[y, x] == color:
            in_a_row += 1
        else:
            in_a_row = 0
        if in_a_row >= 4:
            return color
        move = get_index(y, x, BOTTOMLEFT)

        if not move:
            break
        else:
            y, x = move

    return None


def game_state(board, last_dot):
    """RETURNS 0, 1, or 5"""
    if not last_dot:
        return
    color = board[last_dot[0], last_dot[1]]
    # horizontal
    for dot in HOR_DOTS:
        y, x = dot
        if y != last_dot[0]:
            continue

        if board[y, x] != color:
            break
        if board[y, x + 1] != color and board[y, x - 1] != color:
            break
        in_a_row = 0

        for x in range(7):
            if board[y, x] == color:
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row >= 4:
                return color

    # vertical
    for dot in VER_DOTS:
        y, x = dot
        if x != last_dot[1]:
            continue

        if board[y, x] != color:
            break
        if board[y + 1, x] != color and board[y - 1, x] != color:
            break
        in_a_row = 0
        for y in range(6):
            y = 5 - y
            if board[y, x] == color:
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row >= 4:
                return color
    # zigzags
    zigzag = zigzags(board, last_dot)
    if zigzag or zigzag == 0:
        return zigzag
    for y in board:
        for x in y:
            if x is None:
                return None

    return DRAW


def possible_moves(board):
    return list(filter(lambda y: y is not None, [x if board[0, x] is None else None for x in range(7)]))


class Board:
    def __init__(self, screen):
        self.screen = screen
        self.turn = True
        self.last_move = None
        self.game_running = True
        self.image = pygame.image.load('board.png')
        self.board = array([[None, None, None, None, None, None, None] for _ in range(6)])
        # self.board = array([[0, 0, 0, 0, 0, 0, 0],
        #                     [0, 0, 0, 0, 0, 0, 0],
        #                     [0, 0, 0, 0, 0, 0, 1],
        #                     [0, 0, 0, 0, 0, 0, -1],
        #                     [0, 0, 0, 0, 1, -1, -1],
        #                     [0, 0, 0, 1, -1, -1, -1]])

    def update_board(self, x):
        if self.board[0, x] is not None:
            return False
        for y in range(6):
            if self.board[5 - y, x] is None:
                self.board[5 - y, x] = WHITE if self.turn else BLACK
                self.last_move = (5 - y, x)
                self.change_turn()
                return True

    def draw_board(self):
        self.screen.blit(self.image, (0, 0))
        for y in range(6):
            for x in range(7):
                piece = self.board[y, x]
                if piece is not None:
                    if piece == WHITE:
                        pygame.draw.circle(self.screen, (255, 255, 255), (x * 100 + 50, y * 100 + 150), 50)
                    else:
                        pygame.draw.circle(self.screen, (0, 0, 0), (x * 100 + 50, y * 100 + 150), 50)

        pygame.display.update()

    def change_turn(self):
        self.turn = not self.turn
        # if self.turn == WHITE:
        #     self.turn = BLACK
        # else:
        #     self.turn = WHITE

    def stop_game(self):
        self.game_running = False

    def reset(self):
        print("""====================
      RESET!!!
====================""")
        self.__init__(self.screen)


def get_pos_from_loc(pos):
    return pos[0] // 100


board = Board(screen)
# if AI_FIRST == 1:
#     board.change_turn()
#     AI_FIRST = -1

from datetime import datetime

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if event.type == pygame.MOUSEBUTTONUP and board.game_running:
            x = get_pos_from_loc(pygame.mouse.get_pos())
            turn_changed = board.update_board(x)
            if turn_changed:
                state = game_state(board.board, board.last_move)
                if state or state == 0 or state == DRAW:
                    board.stop_game()
                    print("state:", state)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                board.reset()
            elif event.key == pygame.K_f:
                print(possible_moves(board.board))
                print(game_state(board.board, board.last_move))
            elif event.key == pygame.K_s:
                before = datetime.now()
                positions = 0
                move, evaluation = best_move(DEPTH, board.board, board.turn, board.last_move, -10, 10)
                print(f"MOVE: {move} EVAL: {evaluation}")
                print(f"DEPTH: {DEPTH}")
                print(f"{positions} positions")
                after = datetime.now()
                print(f"{(after - before).total_seconds()} seconds\n")
                DEPTH += 1
    if board.game_running and (MACHINE_GAME or board.turn == AI_FIRST) and not MANUAL:
        before = datetime.now()
        positions = 0
        move, evaluation = best_move(DEPTH, board.board, board.turn, board.last_move, -10, 10)
        print(f"MOVE: {move} EVAL: {evaluation}")
        print(f"DEPTH: {DEPTH}")
        print(f"{positions} positions")
        after = datetime.now()
        print(f"{(after - before).total_seconds()} seconds\n")

        board.update_board(move)
        state = game_state(board.board, board.last_move)
        if state == 1 or state == 0 or state == DRAW:
            board.stop_game()
            print("state:", state)

    board.draw_board()
    clock.tick(60)
pygame.quit()
