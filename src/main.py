import time
import random
import pygame
from enum import Enum
from collections import deque

"""
This file contains the class definitions and implementations for a Snake game
with GUI using pygame
"""

class Direction(Enum):
    
    """Enum representing a direction"""
    
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    
class CellType(Enum):
    
    """Enum representing a type of Cell: empty, snake body and fruit"""
    
    EMPTY = " "
    SNAKE = "#"
    FRUIT = "@"

    
class Cell(object):
    
    """A cell of the board"""
    
    def __init__(self, cont = CellType.EMPTY):
        self.content = cont

    def print_cell(self):
        return self.content.value


    

class Board(object):
    
    """The board of the game"""
    
    def __init__(self, size = 10):
        self.size = size
        self.board = [[Cell() for j in range(size)] for i in range(size)]
        self.print_board()

    def at(self, pos):
        """Accesses the Cell at position pos"""
        if self.is_valid(pos):
            return self.board[pos[0]][pos[1]]
        else: return None

    def is_valid(self, pos):
        """Checks if the given position is valid in this board"""
        return 0 <= pos[0] and pos[0] < self.size \
            and 0 <= pos[1] and pos[1] < self.size

    def is_empty(self, pos):
        """Checks if the Cell at position pos is empty"""
        if self.is_valid(pos):
            return self.at(pos).content == CellType.EMPTY
        else: return None
        
    def go_dir(self, pos, direction):
        """Returns the result of moving in the given direction one cell from
        the given position"""
        _pos_modif = {Direction.UP : (-1,0), Direction.RIGHT : (0,1), Direction.DOWN : (1,0), Direction.LEFT : (0,-1)}
        return (pos[0] + _pos_modif[direction][0], pos[1] + _pos_modif[direction][1])
        
    def print_board(self):
        """Returns a string representation of the board"""
        vDel = "-" + ''.join(['--' for i in range(self.size)]) + "\n"
        str_board = vDel
        for i in range(self.size):
            str_board += "|"
            for j in range(self.size):
                str_board += self.board[i][j].print_cell() + "|"

            str_board += "\n";
            str_board += vDel;

        return str_board



    

class Snake(object):

    """The snake"""
    
    def __init__(self, board, pos = (0,0)):
        self.body = deque()
        self.body.append(pos)
        board.at(pos).content = CellType.SNAKE

    def advance(self, board, newPos, ate = False):
        """Sets newPos as the new head of the snake and removes the last
        cell of the body, unless the snake ate a fruit"""
        self.body.append(newPos)
        board.at(newPos).content = CellType.SNAKE
        if not ate:
            tail = self.body.popleft()
            board.at(tail).content = CellType.EMPTY



        
class Game(object):

    """Represents the game: contains a Board, a Snake, and a fruit"""
    
    def __init__(self, size = 10):
        self.board = Board(size)
        self.snake = Snake(self.board, self.get_random_empty_pos())
        self.add_fruit()


    def advance(self, direction = Direction.UP):
        """Advances the snake in the given direction, updating the
        relevant board cells"""
        newPos = self.board.go_dir(self.snake.body[-1], direction)
        if not self.board.is_valid(newPos): collide = True
        else:
            if self.board.at(newPos).content == CellType.SNAKE:
                collide = True
                
            elif self.board.at(newPos).content == CellType.FRUIT:
                self.snake.advance(self.board, newPos, True)
                self.add_fruit()
                collide = False

            else:
                self.snake.advance(self.board, newPos, False)
                collide = False

            
        return collide

        
    def add_fruit(self):
        """Adds a fruit in an empty random position"""
        self.fruit = self.get_random_empty_pos()
        self.board.at(self.fruit).content = CellType.FRUIT

    def get_random_empty_pos(self):
        """Returns an empty random position in the board"""
        startPos = (random.randrange(self.board.size), random.randrange(self.board.size))
        pos = startPos
        board_full = False
        while not self.board.is_empty(pos) and not board_full:
            if pos[1] == self.board.size-1:
                if pos[0] == self.board.size-1: pos = (0,0)
                else: pos = (pos[0]+1, 0)

            else: pos = (pos[0], pos[1]+1)
            if pos == startPos: board_full = True

        return pos

    def print_game(self):
        return self.board.print_board()




class Controller(object):
    
    """Creates the Game and manages IO and GUI"""
    
    def __init__(self, size = 10, seed = 0):
        """You can specify size of the board and seed for the PRNG"""
        random.seed(seed)
        self.game = Game(size)
        self.size = size
        pygame.init()
        screen_width = 10 + 50*self.size
        self.screen = pygame.display.set_mode((screen_width, screen_width))
        self.clock = pygame.time.Clock()

    def run(self):
        """Main loop of the game"""
        keep_running = True
        direction = Direction.UP
        timer = 0
        
        self.draw()
        while keep_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: keep_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN and not direction == Direction.UP:
                        direction = Direction.DOWN
                        
                    if event.key == pygame.K_UP and not direction == Direction.DOWN:
                        direction = Direction.UP

                    if event.key == pygame.K_LEFT and not direction == Direction.RIGHT:
                        direction = Direction.LEFT

                    if event.key == pygame.K_RIGHT and not direction == Direction.LEFT:
                        direction = Direction.RIGHT


            if timer == 15:
                if self.game.advance(direction): keep_running = False
                timer = 0
            
            self.draw()
            pygame.display.update()
            self.clock.tick(60)
            timer += 1
               
    def draw(self):
        """Draws the GUI"""
        self.screen.fill((0, 0, 0))
        for i in range(self.size):
            for j in range(self.size):
                y = 10 + 50*(i)
                x = 10 + 50*(j)
                rect = pygame.Rect(x, y, 40, 40)
                cell = self.game.board.at((i,j))
                if cell.content == CellType.EMPTY:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)

                if cell.content == CellType.SNAKE:
                    pygame.draw.rect(self.screen, (0, 97, 255), rect)
                
                if cell.content == CellType.FRUIT:
                    pygame.draw.rect(self.screen, (0, 255, 33), rect)

                
#Start the game
controller = Controller(10, 0)
controller.run()

