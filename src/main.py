import time
import random
import pygame
import math
from enum import Enum
from collections import deque

"""
This file contains the class definitions and implementations for a Snake game
with GUI using pygame
"""



class Direction(Enum):
    
    """Enum representing a direction"""
    
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    
    def opposing(self):
        """Returns the opposing direction to the given one"""
        if self == Direction.UP: return Direction.DOWN
        elif self == Direction.DOWN: return Direction.UP
        elif self == Direction.LEFT: return Direction.RIGHT
        elif self == Direction.RIGHT: return Direction.LEFT
            

    
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

    SCREEN_SIZE_LIMIT = 720
    
    def __init__(self, seed = 0):
        random.seed(seed)
        pygame.init()
        self.size = Controller.initial_menu()
        if self.size == -1: raise Exception("Quitted")
        screen_width = 10 + 50*self.size
        if(screen_width > self.SCREEN_SIZE_LIMIT):
            self.reduction = self.SCREEN_SIZE_LIMIT / screen_width
            screen_width = self.SCREEN_SIZE_LIMIT
        else: self.reduction = 1
        self.screen = pygame.display.set_mode((screen_width, screen_width))
        self.clock = pygame.time.Clock()
        self.start(self.size)
            
    def initial_menu():
        """Shows an explanation of the controls and asks for size"""
        screen = pygame.display.set_mode((550,300))
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 32)
        clock = pygame.time.Clock()
        boxColor = (255,255,255)
        input_box = pygame.Rect(100, 220, 350, 32)
        controls_box = pygame.Rect(50, 30, 450, 96)
        prompt_box = pygame.Rect(50, 140, 450, 64)
        controlsText = ["CONTROLS: Move with arrow keys,", "pause with P, exit with ESC,", "go faster with F, slower with S."]
        promptText = ["Introduce the size of the board (5-100)", "and press ENTER to start playing."]
        sizeText = ''

        pygame.draw.rect(screen, boxColor, controls_box)
        pygame.draw.rect(screen, boxColor, prompt_box)

        offset = 0
        for text in controlsText:
            screen.blit(font.render(text, True, (0,0,0)), (controls_box.x+5, controls_box.y+5+offset))
            offset += 32

        offset = 0
        for text in promptText:
            screen.blit(font.render(text, True, (0,0,0)), (prompt_box.x+5, prompt_box.y+5+offset))
            offset += 32
            
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    size = -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        sizeText = sizeText[:-1]
                    elif event.key == pygame.K_RETURN:
                        size = int(sizeText)
                        if size >= 5 and size <= 100: done = True
                    elif event.key in range(pygame.K_0, pygame.K_9+1):
                        sizeText += event.unicode

                txt_surface = font.render(sizeText, True, (0,0,0))
                pygame.draw.rect(screen, boxColor, input_box)
                screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
                
                pygame.display.update()
                clock.tick(30)

        return size
        
    def start(self, size):
        """Sets the initial conditions of the game"""
        self.game = Game(size)
                
    def run(self):
        """Main loop of the game"""
        keep_running = True
        keep_current_game = True
        direction = Direction.UP
        timer = 0
        paused = False
        speed = 0
        
        while(keep_running):
            self.draw()
            newDirection = direction
            while keep_current_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        keep_current_game = False
                        keep_running = False
                    elif event.type == pygame.KEYDOWN:
                        
                        if event.key in list(map(lambda e: e.value, Direction)) and event.key != direction.opposing().value:
                            newDirection = Direction(event.key)

                        elif event.key == pygame.K_p:
                            paused = not paused

                        elif event.key == pygame.K_f:
                            if speed < 10*self.reduction - 1: speed += 1

                        elif event.key == pygame.K_s:
                            speed -= 1

                        elif event.key == pygame.K_ESCAPE:
                            keep_running = False
                            keep_current_game = False
                
                if not paused and timer >= 20*self.reduction - speed:
                    direction = newDirection
                    if self.game.advance(direction): keep_current_game = False
                    timer = 0
                    
                self.draw()
                pygame.display.update()
                self.clock.tick(120)
                timer += 1
                
            self.start(self.size)
            keep_current_game = True

            
    def draw(self):
        """Draws the GUI"""
        self.screen.fill((0, 0, 0))
        for i in range(self.size):
            for j in range(self.size):
                y = math.floor(self.reduction*(10 + 50*(i)))
                x = math.floor(self.reduction*(10 + 50*(j)))
                rectWidth = math.floor(self.reduction*40)
                rect = pygame.Rect(x, y, rectWidth, rectWidth)
                cell = self.game.board.at((i,j))
                if cell.content == CellType.EMPTY:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)

                if cell.content == CellType.SNAKE:
                    pygame.draw.rect(self.screen, (0, 97, 255), rect)
                
                if cell.content == CellType.FRUIT:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)

                
#Start the game

controller = Controller()
controller.run()
