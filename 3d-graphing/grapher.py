import pygame as pg
import colors


WIDTH = 800
HEIGHT = 800
pg.init()
gd = pg.display.set_mode((WIDTH, HEIGHT))
gd.fill(colors.WHITE)
clock = pg.time.Clock()


class Vector(object):
    OFFSET_X = WIDTH//2
    OFFSET_Y = HEIGHT//2
    scale = 20    # pixels/unit (ie. if scale=20, and vector is [1,0] it will be 20 pixels large)
    def __init__(self, x, y, width=3, offset_x=0, offset_y=0):
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.strt_x, self.strt_y = Vector.OFFSET_X + self.offset_x*Vector.scale, Vector.OFFSET_Y - self.offset_y*Vector.scale
        self.draw_x, self.draw_y = self.x*Vector.scale + self.strt_x, -self.y*Vector.scale + self.strt_y


    def __mul__(self, other):
        pass
    def __add__(self, other):
        pass
    def __div__(self, other):
        pass
    def __sub__(self, other):
        pass

    def draw(self, display, color):
        pg.draw.line(display,
                     color,
                     (self.strt_x, self.strt_y),
                     (self.draw_x, self.draw_y),
                     self.width)

    def drawline(self, display, color):
        pg.draw.line(display,
                     color,
                     (100*self.draw_x, 100*self.draw_y),
                     (-100*self.draw_x, -100*self.draw_y),
                     self.width)


class Grid(object):
    axes_clr = colors.BLUE
    major_clr = colors.SKY_BLUE
    minor_clr = colors.GRAY
    units = 20     # units is the number of major grid lines to fit in the main window to determine spacing
    lines = 80     # determines total width of grid (num of lines)
    def __init__(self):
        self.axes = [Vector(-5000, 0), Vector(5000, 0), Vector(0, 5000), Vector(0, -5000)]
        self.major = []
        self.minor = []

    def draw(self):
        pass
c = Vector(5, -1, offset_x=0, offset_y=0)
d = Vector(5, 1, offset_x=0, offset_y=0)
e = Vector(2, 3, offset_x=0, offset_y=1)
f = Vector(1, 4, offset_x=0, offset_y=1)
#c.draw(gd, colors.HOT_PINK)
d.draw(gd, colors.RED)
c.drawline(gd, colors.BLUE)
e.draw(gd, colors.AQUA)
f.drawline(gd, colors.ICE)
while True:
    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            pg.quit()
            quit()
    pg.display.update()
    clock.tick()
