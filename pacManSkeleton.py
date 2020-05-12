"""
Justin Stitt
LAST UPDATE: 2/20/2020
-buffer inputs
-level design (brush)

To-Do:
-level save/load
   - see last line of 'pacManSkeleton.py'

Logged Minutes: 240
"""

import pygame # rendering, input, collision
import sys
import random
import time
pygame.init()

#Constants
fps = 60 # frames per second to call the update pipeline...
move_buffer = fps//2;#how many frames to store (buffer) a movement input for pm
"""
_size is our (width,height) of the game window
CELL_SIZE should be a multiple of both width and height
Pac_Man.speed variable should be a multiple of CELL_SIZE
"""
_size = (900,900)
CELL_SIZE = 45 # This cell size is essentially the scale of our game. Pac_man's size is based of this as well.
fill_color = pygame.Color(15,15,23)# background fill color
window = pygame.display.set_mode(_size)
pygame.display.set_caption("Escape Room: A Pac-Man Adventure!")
clock = pygame.time.Clock()
#end Constants


#dynamic lists
grid = []# stores cells
"""
 grid is a collection of Cell objects, which inherently have a type (see Cell implementation)
 grid is massively important and is how we will create, save, and load levels
"""

#level creation
brush = 0 # 0 = terrain, 1 = edible dot, 2 = unedible dot, 3 = erase
#end level creation

#used in converting from 2d matrix to 1d
r = _size[0]//CELL_SIZE # how many rows
c = _size[1]//CELL_SIZE # how many columns

class Pac_Man(): # essentially our 'player' object
    """
    for all intents and purposes, this is our player object
    we check for movement, collision, and any other update-pipeline based inquiries
    """
    def __init__(self):
        self.index = [0,0]# x,y indexes on our grid
        self.size = CELL_SIZE
        self.pos = [self.index[0] * self.size,self.index[1] * self.size]# used for pixel rendering (real position)
        self.color = pygame.Color(252,207,4)
        self.speed = 5
        self.dir = -1 # 0 = north, 1 = east, 2 = south, 3 = west, -1 = not moving (up agaisnt a wall)
        self.rect = (self.pos[0],self.pos[1],self.size,self.size)
        self.buffer = [-1,move_buffer]#dir to be issued, frame count to allow for buffering
        self.new_index = 0
    def update(self):
        """
        Called once per frame from the global update-pipeline
        """
        self.buffer[1]-=1
        if(self.can_move()):
            self.move()#usually want to move before rendering
        else:
            self.dir = -1
        self.change_direction()#then we want to check if we can change direction
        self.check_for_dot()
        self.render()

    def render(self):
        """
        Called from local update (self.update)
        """
        pygame.draw.ellipse(window,self.color,self.rect)
    def move(self):
        """
        checks our direction, checks validity (legality) of our requested move
        if it is legal, we issue the move and update our index
        """
        if(self.dir == 0):
            self.pos[1]-=self.speed
        elif(self.dir == 1):
            self.pos[0] += self.speed
        elif(self.dir == 2):
            self.pos[1]+=self.speed
        elif(self.dir == 3):
            self.pos[0]-=self.speed
        self.rect = (self.pos[0] ,self.pos[1] ,self.size,self.size)#update rect object

        if(self.pos[0] % CELL_SIZE == 0 and self.pos[1] % CELL_SIZE == 0):#
            if(self.dir == 0):
                self.index[1]-=1
            elif(self.dir == 1):
                self.index[0]+=1
            elif(self.dir == 2):
                self.index[1]+=1
            elif(self.dir == 3):
                self.index[0]-=1
        self.new_index = c * self.index[0] + self.index[1]#map 2d matrix to 1d
        print(self.new_index)
    def change_direction(self):
        """
        handles all the buffering of movements
        """
        #c = _size[0]//CELL_SIZE
        #r = _size[1]//CELL_SIZE

        if(self.buffer[0] == 0 and grid[self.new_index - 1].type == 0):
            return
        elif(self.buffer[0] == 1 and grid[self.new_index + c].type == 0):
            return
        elif(self.buffer[0] == 2 and  grid[self.new_index + 1].type == 0):
            return
        elif(self.buffer[0] == 3 and grid[self.new_index - c].type == 0):
            return

        if(self.pos[0] % CELL_SIZE == 0 and self.pos[1] % CELL_SIZE == 0):#
            if(self.buffer[0] != -1 and self.buffer[1] > 0):
                self.dir = self.buffer[0]
                self.buffer[0] = -1
                self.buffer[1] = move_buffer
        if(self.buffer[1] == 0):
            self.buffer[0] = -1
            self.buffer[1] = move_buffer
    def eat_dot(self):
        """
        whenever check_for_dot() thinks we have collided with a dot, we call this
        """
        print('we ate a dot!')
    def check_for_dot(self):
        """
        is there an edible dot colliding with pacman? if so call eat_dot (see above)
        """
        cell = grid[self.new_index]
        if(cell.type == 2):#edible dot?
            cell.type = 1
            self.eat_dot()


    def can_move(self):
        """
        can pacmove issue a move command? basically this is our collision detection
        to see if we can start updating our position. See local update (self.update) for usage
        """
        #print('new_index: {}'.format(new_index))
        if( (self.index[0] >= r - 1 and self.dir == 1 ) or (self.index[1] >= c - 1 and self.dir == 2) or
            (self.index[0] <= 0 and self.dir == 3) or (self.index[1] <= 0 and self.dir == 0)            ):
            return False

        if(self.dir == 0 and grid[self.new_index - 1 ].type == 0):#going up a row
            return False
        elif(self.dir == 1 and grid[self.new_index + c].type == 0):#going right a column
            return False
        elif(self.dir == 2 and grid[self.new_index + 1].type == 0):#going down a row
            return False
        elif(self.dir == 3 and grid[self.new_index - c].type == 0):#going left a colunm
            return False
        return True


class Cell(): # cell object. we are going to instantiate a list to store multiple cells. this will be aptly named 'grid'
    """
    The core of level development. We are operating on a grid, which is a collection
    of Cell objects. Any given Cell object has a 'type' which lets us design levels
    """
    def __init__(self,x,y):
        self.size = CELL_SIZE
        self.index = [x,y]# x , y indexes (not used for rendering directly)
        self.pos = [self.index[0] * self.size,self.index[1]*self.size] # position used for pixel rendering
        self.type = 1 # 0 = terrain, 1 = moveable, 2 = edible dot (and is therefore moveable), 3 = inedible dot
        #The goal of the cell object is to store data about spots on 'grid' (is there a Dot, is it pathable terrain? etc.)
        self.color = fill_color
    def __repr__(self):# when print(cell_obj) is called it prints this return. Debug purposes mainly.
        return 'I am Cell [{},{}] of type {}'.format(self.index[0],self.index[1],self.type)
    def update(self):
        self.render()
    def render(self):
        if(self.type == 0):
            pygame.draw.rect(window,(30,27,224),(self.pos[0],self.pos[1],self.size,self.size))
        elif(self.type == 1):
            pygame.draw.rect(window,self.color,(self.pos[0],self.pos[1],self.size,self.size))
        elif(self.type == 2 or self.type == 3):
            pygame.draw.ellipse(window,(255,255,230),(self.pos[0] + self.size//4,self.pos[1] + self.size//4,CELL_SIZE//2,CELL_SIZE//2)) # dot render test

def grid_setup():
    """
    creates a bunch of cell objects based on GLOBAL variables (r and c)
    these all have a default type of 1 (moveable)
    grid_setup should almost always be followed either by creating a level, or by loading a level.
    No one wants to play pacman on a blank screen!
    """
    for x in range(r):
        for y in range(c):
            grid.append(Cell(x,y))


# auxiliary functions
def window_meshing(): # we want to ensure that we have precisely enough cells to cover the screen and that there isnt a gap of 'uncellable' area
    """
    checks to make sure we have proper integer numbers so that we dont get floating point pixel stuff.
    """
    if (_size[0] % CELL_SIZE != 0 or _size[1] % CELL_SIZE != 0):
        print("WINDOW MESHING MISALIGNMENT... Consider making CELL_SIZE a multiple of the window size")
    if(CELL_SIZE % pm.speed != 0 ):
        print("WARNING: consider making pacman's speed a factor of cell_size to ensure smooth movement")

def exit_game():
    """
    self-explanatory
    """
    pygame.quit()
    sys.exit()
#end auxiliary functions


def update():# main update loop
    """
    Welcome to the update-pipeline!!!
    If you're and object (or event) and you need to update every frame
    then you've come to the right place!
    we handle KEYBOARD, MOUSE, OBJECT UPDATE CALLS, and many more things here!
    """
    global brush
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        elif event.type ==  pygame.KEYDOWN:#remap this to your cardinal direction joystick
            if event.key == pygame.K_UP :#cardinal north
                #pm.dir = 0;
                pm.buffer[0] = 0
                pm.buffer[1] = move_buffer
            elif event.key == pygame.K_RIGHT :#cardinal east
                pm.buffer[0] = 1
                pm.buffer[1] = move_buffer
            elif event.key == pygame.K_DOWN :#cardinal south
                pm.buffer[0] = 2
                pm.buffer[1] = move_buffer
            elif event.key == pygame.K_LEFT :#cardinal west
                pm.buffer[0] = 3
                pm.buffer[1] = move_buffer
            #changing brush
            elif event.key == pygame.K_h:#terrain
                brush = 0
            elif event.key == pygame.K_j:#edible dot
                brush = 1
            elif event.key == pygame.K_k:#unedible Dot
                brush = 2
            elif event.key == pygame.K_l:#erase
                brush = 3

        #elif event.type == pygame.MOUSEBUTTONDOWN: # handles  mouse button down. (x,y) returned with event.pos
        if(pygame.mouse.get_pressed() == (1,0,0)):
            index = [event.pos[0]//CELL_SIZE,event.pos[1]//CELL_SIZE]
            new_index = index[0] * (_size[1]//CELL_SIZE) + (index[1] )
            if(brush == 0):#terrain
                grid[new_index].type = 0
                print('placed at index {}'.format(new_index))
            elif(brush == 1):#edible dot
                grid[new_index].type = 2
            elif(brush == 2):#unedible dot
                grid[new_index].type = 3
            elif(brush == 3):#erase
                grid[new_index].type = 1
    # obj updates

    for cell in grid:
        cell.update()
    pm.update()
    #end obj updates

def render():# auxiliary render pipeline (unused mostly)
    """
    This is the main render-pipeline
    mostly used for menu design or other things that we need to render that
    are not instantiated objects
    """
    pass


pm = Pac_Man()#create our main 'player' object here of type Pac_Man
#should be noted we should only ever have one instance of a Pac_Man object

#aux calls
window_meshing()# ensure proper cell allignment
grid_setup()
#end aux calls

grid[5].type = 0;

#ENGINE
while True:
    window.fill(fill_color)#clean slate
    update();#main update-pipeline
    render();#main render-pipeline
    pygame.display.flip()#paint all new additions after our update and render pipeline calls
    clock.tick(fps)#fps



"""
TO-DO:
Schema for saving levels:
store each cell type as an integer in a JSON? or notepad file
e.g for a 10 cell 'level';
{0,0,1,2,1,1,2,2,3,3}
this would store if any given cell is a type (terrain,moveable,e-dot,uedot)
some save_level(this_setup) def could be written to loop, write, and store each cell type (hard-disk save not cache)
some load_level(my_level) def could be written which loops and maps each cell type
"""
