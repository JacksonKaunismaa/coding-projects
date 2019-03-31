import numpy as np
from PIL import Image
import os
import time

cmap = {'red': (244, 4, 44),
        'sky-blue': (34, 214, 249),
        'indigo': (16, 12, 137),
        'green': (16, 137, 8),
        'lime': (49, 249, 34),
        'cyan': (34, 249, 224),
        'blue': (42, 35, 239),
        'purple': (140, 16, 211),
        'pink': (249, 53, 252),
        'orange': (244, 128, 4),
        'rose': (252, 53, 152),
        'brown': (104, 76, 40),
        'black': (0, 0, 0),
        'yellow': (241, 249, 77),
        'white': (255, 255, 255)}

class Plot(object):
    def __init__(self, res=1000, block=20, timename=None):
        self.res = res
        self.timename = str(time.time()).replace(".", "")
        if timename:
            self.timename = str(timename)
        self.bs = int(float(self.res)/block)
        self.minx, self.miny = -100, -100
        self.maxx, self.maxy = 100, 100
        self.grid = np.indices((self.bs, self.bs)).swapaxes(0,2).swapaxes(0,1).astype(np.float64) / (self.bs-1)
        self.img = np.ones((res, res, 3)).astype(np.uint8) * 255
        self.shaped = False

    def hollow_fill(self, loc, clr, sz):
        for i in range(-sz, sz+1):
            for j in range(-sz, sz+1):
                if i in [-sz, sz] or j in [-sz, sz]:
                    try:
                        self.img[loc[0]+i, loc[1]+j] = clr
                    except IndexError:
                        pass

    def solid_fill(self, loc, clr, sz):
        for i in range(-sz, sz+1):
            for j in range(-sz, sz+1):
                try:
                    self.img[loc[0]+i, loc[1]+j] = clr
                except IndexError:
                    pass

    def cross_fill(self, loc, clr, sz):
        for i in range(-sz, sz+1):
            for j in range(-sz, sz+1):
                if i in [-1, 0, 1] or j in [-1, 0, 1]:
                    try:
                        self.img[loc[0]+i, loc[1]+j] = clr
                    except IndexError:
                        pass

    def scale(self, loc):
        locx = int(self.res * (loc[0] - self.minx) / (self.maxx - self.minx))
        locy = int(self.res * (loc[1] - self.miny) / (self.maxy - self.miny))
        return [locx, locy]

    def plot_point(self, loc, clr):
        loc_scl = self.scale(loc)
        self.hollow_fill(loc_scl, cmap['black'], 8)
        self.solid_fill(loc_scl, list(cmap.values())[clr], 7)

    def sl(self, val):
        return val * (1 - 0.01 * np.sign(val)) - 0.1

    def sr(self, val):
        return val * (1 + 0.01 * np.sign(val)) + 0.1

    def plot_points(self, data, cats):
        for p, c in zip(data, cats):
            self.plot_point(p, c)

    def plot_means(self, means):
        for c, p in enumerate(means):
            self.cross_fill(self.scale(p), list(cmap.values())[c], 12)

    def set_frame(self, data):
        self.minx, self.miny = self.sl(np.min(data[:, 0])), self.sl(np.min(data[:, 1]))
        self.maxx, self.maxy = self.sr(np.max(data[:, 0])), self.sr(np.max(data[:, 1]))

    def shape_grid(self):
        if not self.shaped:
            self.grid[:, :, 0] *= self.maxx - self.minx
            self.grid[:, :, 1] *= self.maxy - self.miny
            self.grid[:, :, 0] += self.minx
            self.grid[:, :, 1] += self.miny
            self.shaped = True

    def closest(self, point, means):
        return np.argmin(((means - point)**2).sum(axis=1), axis=0)

    def colorize(self, means):
        self.shape_grid()
        for x in range(self.bs):
            for y in range(self.bs):
                p = self.grid[x,y]
                color = list(cmap.values())[self.closest(p, means)]
                self.hollow_fill(self.scale(p), color, 6)

    def clear(self):
        self.img = np.ones((self.res, self.res, 3)).astype(np.uint8) * 255

    def show(self):
        im = Image.fromarray(self.img, "RGB")
        im.show()

    def save(self, name):
        im = Image.fromarray(self.img, "RGB")
        if not os.path.exists(os.path.join("./kmviz", self.timename)):
            os.mkdir(os.path.join("./kmviz", self.timename))
        im.save(os.path.join("./kmviz", self.timename, name + '.png'))






