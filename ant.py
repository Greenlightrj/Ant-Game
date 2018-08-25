# python 3

import pygame
from pygame.locals import RESIZABLE
import random

# todo: make ants turn back from edge
"""
ideas:
    scouts wander outward in a pattern and come back to home along same path they took, leaving trail
    each square has a pheromone for the direction previous ants were going when they crossed it
    randomly wandering ants don't leave trails
    ants that have found food leave strong trails
    gatherer ants follow trails of ants that have found food (in opposite direction) and when they have food they follow in forward direction
    paths fade over time
    give player a tool to erase paths
    paths must smooth over time somehow
"""


class Main():

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.view = View(self)
        self.model = Model(self)
        self.controller = Controller()

    def mainLoop(self):
        self.done = False
        while not self.done:
            self.controller.checkInput(self)  # check for keystrokes
            self.model.update(self.view)
            self.view.redraw(self)
            self.clock.tick(30)  # limits FPS by ticking forward a bit at a time
        pygame.quit()


class Model(object):
    """holds the lists and updates"""

    def __init__(self, window):
        self.hill = AntHill()
        self.antlist = AntList()
        self.foodlist = FoodList()
        self.board = Board(window)

    def update(self, window):
        self.hill.update(window)
        for ant in self.antlist:  # draw the gatherer ants
            ant.update(self.board.surface)


class View():

    def __init__(self, window, width=500, height=500):
        self.width = width                              # sets width of screen (as a variable so we can use it later)
        self.height = height
        size = (self.width, self.height)                         # sets height
        self.screen = pygame.display.set_mode(size, RESIZABLE)    # makes screen thing so we can make it green later
        self.green = (0, 170, 0)

    def redraw(self, window):
        self.screen.fill(self.green)        # makes green background first
        window.model.board.draw(self.screen)  # draws the trails level
        window.model.hill.draw(self.screen)
        for food in window.model.foodlist:
            food.draw(self.screen)
        for ant in window.model.antlist:  # draw the gatherer ants
            ant.draw(self.screen)

        pygame.display.flip()                       # actually draws all that stuff.


class Controller():

    def __init__(self):
        pass

    def checkInput(self, window):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:               # If user clicked close
                window.done = True
            elif event.type == pygame.KEYDOWN:          # If user pressed a key
                if event.key == pygame.K_ESCAPE:        # escape key is an escape   
                    window.done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:  # when mouse button is clicked
                if pygame.mouse.get_pressed()[0]:     # left mouse button click
                    GatherAnt(window.model.hill, window)   # make a gather ant
                elif pygame.mouse.get_pressed()[2]:       # right mouse button click
                    window.model.board.surface.set_at((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]), (250, 0, 0))   # make a dinosaur
            elif event.type == pygame.locals.VIDEORESIZE:
                window.view.screen = pygame.display.set_mode((event.w, event.h), RESIZABLE)
                window.view.width = event.w
                window.view.height = event.h


class AntHill(pygame.sprite.Sprite):
    """
    The anthill in the center of the screen
    """

    def __init__(self):
        """
        always in middle of screen
        """
        self.x = 10
        self.y = 10
        self.color = (100, 50, 0)

    def update(self, window):
        self.x = window.width / 2
        self.y = window.height / 2

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, 15, 20])


class AntList(pygame.sprite.Group):
        """
    List of dinosaurs
    inherited methods:
    .add adds a sprite to group
    .remove removes a sprite from group
    .update runs update method of every sprite in group
    .draw blits the image of every sprite in group
    """


class GatherAnt(pygame.sprite.Sprite):
    """
    ants that gather food
    """

    def __init__(self, hill, window):
        pygame.sprite.Sprite.__init__(self, window.model.antlist)  #puts ant in list of ants
        self.x = hill.x + 5
        self.y = hill.y + 20
        self.color = (0, 0, 0)
        self.carryingfood = False
        self.step = (0, 0)
        self.memory = []  # array that tracks its motion since it last left home

    def walk(self):
        self.x += self.step[0]  # move according to decided direction
        self.y += self.step[1]

    def leavetrail(self):
        pass

    def update(self, boardsurf):
        food = boardsurf.get_at((int(self.x), int(self.y)))[0] # get the food value from clurrent location
        (x, side, vert, a) = pygame.transform.average_color(boardsurf, pygame.Rect(self.x - 2, self.y - 2, 5, 5))  # get the trail values from the surrounding area

        if self.carryingfood:
            # follow own memory trail in reverse while laying trail
            # todo: implement reversing of direction
            self.step = ((random.random() - 0.5, (random.random() - 0.5)))
            boardsurf.set_at((int(self.x), int(self.y)), (food, side + self.step[0], vert + self.step[1]))

        else:  # if not carrying food
            if food > 50:  # if there is any food remaining on the tile the ant is on
                boardsurf.set_at((int(self.x), int(self.y)), (food - 50, side, vert))  # update the tile
                self.carryingfood =True  # mark self as carrying food
                self.color = (50, 0, 0)

            elif side != 125 or vert != 125: # if there is a trail on the current tile
                self.step = ((side - 125) / 250, (vert - 125) / 250)  # move in direction of trail

            else:
                self.step = ((5*(random.random() - 0.5), 5 * (random.random() - 0.5)))
            self.memory.append(self.step)

        self.walk()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, 5, 5])


class Board():
    """
    the layer containing the ant trails
    red value is the food amount in an area
    green value is the left-right directionality of a trail (0 is all left, 125 is none, 250 is all right)
    blue value is the up-down directionality of a trail (0 is all down, 125 is none, 250 is all up)
    """

    def __init__(self, window):
        self.surface = pygame.Surface((window.view.width, window.view.height)) #creates a surface (image) for the ground
        self.surface.fill((0, 125, 125))  # fills the surface with a color to start
        #self.array = pygame.PixelArray(self.surface)  # makes an array of the pixel colors

    def update(self, position, color):
        """
        adds RGB color difference (r, g , b) to pixel at position (x, y)
        """
        pass

    def draw(self, screen):
        #self.surface = self.array.make_surface() # makes a new image from the current array
        #self.array.close()  # unlocks surface 
        screen.blit(self.surface, (0, 0))

class Food(pygame.sprite.Sprite):
    """
    food items
    """

    def __init__(self, x, y, window):
        pygame.sprite.Sprite.__init__(self, window.model.foodlist)  #puts food in list of food
        self.x = x
        self.y = y
        self.color = (50, 0, 0) 

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, [self.x, self.y, 5, 5])

class FoodList(pygame.sprite.Group):
        """
    List of dinosaurs
    inherited methods:
    .add adds a sprite to group
    .remove removes a sprite from group
    .update runs update method of every sprite in group
    .draw blits the image of every sprite in group
    """

if __name__ == "__main__":
    MainWindow = Main()
    MainWindow.mainLoop()
