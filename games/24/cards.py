import pygame as pg
import colors
#import random


class GameState(object):
    def __init__(self):
        self.keep_looping = None
        self.deck = None
        self.hand_copy = None
        self.buttons = None
        self.extra_cards = None
        self.card1 = None
        self.op_selected = None
        self.score = None
        self.start = None
        self.score_disp = None
        self.score_box = None
        self.pass_btn = None
        self.pf_disp = None
        self.pf_box = None
        self.time_disp = None
        self.time_box = None
        self.solved_disp = None
        self.solved_box = None
        self.correct_flag = None
        self.stack = None
        self.sp = None
        self.correct = None
        self.wrong = None
        self.wrong_disp = None
        self.wrong_box = None
        self.solution = None


class BorderedSprite(pg.sprite.Sprite):
    def __init__(self, sz, bsize=None):
        pg.sprite.Sprite.__init__(self)
        if bsize is None:
            self.b_width = 5
        else:
            self.b_width = bsize
        self.rect = sz.copy()

        self.back = pg.Surface((self.rect.width, self.rect.height))
        self.back.fill(colors.WHITE)

        self.border = pg.Rect(self.rect.left-self.b_width, self.rect.top-self.b_width, self.rect.width+2*self.b_width, self.rect.height+2*self.b_width)
        self.border_color = colors.BLACK

        self.selected = False
        self.visible = False
        self.enabled = True
        self.slot_num = -1

    def draw(self, surf, gd):
        if self.visible:
            pg.draw.rect(gd, self.border_color, self.border)
            gd.blit(self.back, self.rect)
            gd.blit(surf, self.rect)

    def center_draw(self, surf, gd):
        if self.visible:
            pg.draw.rect(gd, self.border_color, self.border)
            gd.blit(self.back, self.rect)
            gd.blit(surf, surf.get_rect(center=self.rect.center))

    def unhide(self):
        self.visible = True
        self.selected = False

    def move(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.border.x = pos[0] - self.b_width
        self.border.y = pos[1] - self.b_width

    def hide(self):
        self.move((-1000, -1000))
        self.visible = False
        self.selected = False

    def reslot(self, WIDTH, HEIGHT, CARDS_NUM):
        self.slot(WIDTH, HEIGHT, CARDS_NUM, self.slot_num)

    def slot(self, WIDTH, HEIGHT, CARDS_NUM, s):
        self.visible = True
        self.selected = False
        if s in range(CARDS_NUM):
            self.move((self.rect.width//1.2+((WIDTH-2*self.rect.width)//(CARDS_NUM-1))*s, HEIGHT//2-self.rect.height//3))
            self.slot_num = s
        else:
            raise ValueError(f"Slot value must be in the range [0,{CARDS_NUM-1}]")

    def slot_below(self, WIDTH, HEIGHT, buttons_num, s):
        self.visible = True
        self.selected = False
        if s in range(buttons_num):
            self.move((self.rect.width*1.5+((WIDTH-3.5*self.rect.width)//(buttons_num-1))*s, int(HEIGHT-self.rect.height*2)))
            self.slot_num = s
        else:
            raise ValueError(f"Slot below value must be in the range [0,{buttons_num-1}]")

    def try_select(self, mouse_evt):
        if self.enabled and self.rect.collidepoint(mouse_evt.pos):
            self.select_it()
            return self.selected

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def select_it(self):
        self.selected = True
        self.border_color = colors.ORANGE

    def deselect(self):
        self.selected = False
        self.border_color = colors.BLACK

    def copy(self):
        cpy = BorderedSprite(self.sz)
        cpy.selected = self.selected
        cpy.visible = self.visible
        cpy.slot_num = self.slot_num
        cpy.enabled = self.enabled
        cpy.border_color = self.border_color
        return cpy


class Card(BorderedSprite):
    def __init__(self, value, im_name, sz=None, dark_flag=False):
        im_load = pg.image.load(im_name).convert_alpha()
        if sz is not None:
            im_load = pg.transform.scale(im_load, sz)
        super().__init__(im_load.get_rect())

        self.value = value
        self.name = im_name
        self.image = im_load
        self.darkened = False
        self.dark_flag = dark_flag
        if dark_flag:
            self.dark = self.image.copy().convert_alpha()
            filt = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA, 32)
            filt.fill((0, 0, 0, 180), self.rect)
            self.dark.blit(filt, self.rect)
        else:
            self.dark = False

    def draw(self, gd):
        if self.darkened:
            super().draw(self.dark, gd)
        else:
            super().draw(self.image, gd)

    def darken(self):
        self.darkened = True
        self.disable()
        if not self.dark:
            raise ValueError(f"Tried to darken a card for which dark_flag was not set! Card was {self}")

    def lighten(self):
        self.enable()
        self.darkened = False

    def __repr__(self):
        #return f"Card(name={self.name}, value={self.value}, loc={self.rect}, visible={self.visible}), hbox={self.border}"
        return f"C(s={self.selected},v={self.value},n={self.slot_num})"

    def copy(self):
        cpy = Card(self.value, self.name, dark_flag=self.dark_flag)
        cpy.darkened = self.darkened
        cpy.selected = self.selected
        cpy.visible = self.visible
        cpy.slot_num = self.slot_num
        cpy.enabled = self.enabled
        cpy.border_color = self.border_color
        return cpy


class MathFraction(object):
    def __init__(self, top, low):
        if not low:
            raise ZeroDivisionError(f"Can't create a fraction with denominator 0 (numerator was {top})")
        self.top = top
        self.low = low
        self.reduce()

    def reduce(self):
        a = abs(self.top)
        b = abs(self.low)
        while b:
            a, b = b, a%b
        self.top //= a
        self.low //= a
        if self.low < 0:
            self.top *= -1
            self.low *= -1

    def __sub__(self, other):
        res = MathFraction(1,1)
        if type(other) is self.__class__:
            res.top = other.low*self.top - other.top*self.low
            res.low = other.low*self.low
        elif type(other) is int:
            res.top = self.top - other*self.low
        else:
            raise ValueError(f"Can't add type 'Fraction' and '{type(other)}'")
        res.reduce()
        return res

    def __add__(self, other):
        res = MathFraction(1,1)
        if type(other) is self.__class__:
            res.top = other.low*self.top + other.top*self.low
            res.low = other.low*self.low
        elif type(other) is int:
            res.top = self.top + other*self.low
        else:
            raise ValueError(f"Can't sub type 'Fraction' and '{type(other)}'")
        res.reduce()
        return res

    def __mul__(self, other):
        res = MathFraction(1,1)
        if type(other) is self.__class__:
            res.top = self.top * other.top
            res.low = self.low * other.low
        elif type(other) is int:
            res.top = self.top*other
        else:
            raise ValueError(f"Can't mul type 'Fraction' and '{type(other)}'")
        res.reduce()
        return res

    def __truediv__(self, other):
        res = MathFraction(1,1)
        if type(other) is self.__class__:
            if other.top  == 0:
                raise ZeroDivisionError(f"You can't do that! (Tried to divide a fraction <{self}> by fraction <{other}>)")
            res.top = self.top * other.low
            res.low = self.low * other.top
        elif type(other) is int:
            if other == 0:
                raise ZeroDivisionError(f"You can't do that! (Tried to divide a fraction <{self}> by int 0)")
            res.low = self.low * other
        else:
            raise ValueError(f"Can't div type 'Fraction' and '{type(other)}'")
        res.reduce()
        return res

    def __floordiv__(self, other):
        res = self.__truediv__(other)
        return res

    def __eq__(self, other):
        if type(other) is self.__class__:
            return other.top == self.top and other.low == self.low
        elif type(other) is int:
            return self.top == other and self.low == 1
        else:
            raise ValueError(f"Can't compare type '{self.__class__}' with type '{type(other)}'!")

    def __repr__(self):
        if self.low == 1 or self.top == 0:
            text = f"{self.top}"
        else:
            text = f"{self.top}/{self.low}"
        return text




class Fraction(BorderedSprite):
    def __init__(self, value, sz, fontsize=80):
        super().__init__(sz)
        self.sz = sz.copy()
        self.value = value
        self.font = pg.font.SysFont("Comic Sans MS", fontsize)

    def draw(self, gd):
        text = repr(self)
        text_surf = self.font.render(text, True, colors.BLACK)
        super().center_draw(text_surf, gd)

    def __repr__(self):
        return str(self.value)
        #return f"F(s={self.selected},v={self.value},n={self.slot_num})"

    def copy(self):
        cpy = Card(self.value, self.sz)
        cpy.darkened = self.darkened
        cpy.selected = self.selected
        cpy.visible = self.visible
        cpy.slot_num = self.slot_num
        cpy.enabled = self.enabled
        cpy.border_color = self.border_color
        return cpy


class TextBox(BorderedSprite):
    def __init__(self, txt, sz, fsize=None, bsize=None, align="left"):
        super().__init__(sz, bsize=bsize)
        self.txt = txt
        if fsize is not None:
            self.font = pg.font.SysFont("Comic Sans MS", fsize)
        else:
            self.font = pg.font.SysFont("Comic Sans MS", 80)
        self.align = align
        if self.align == "right":
            self.rect.topright = self.rect.topleft
        elif self.align == "center":
            self.rect.centerx = self.rect.left
        self.unhide()


    def get_size(self):
        return self.font.size(str(self.txt))


    def draw(self, gd):
        text = repr(self)
        text_surf = self.font.render(text, True, colors.BLACK)
        #super().center_draw(text_surf, gd)
        super().draw(text_surf, gd)

    def __repr__(self):
        if type(self.txt) is float:
            return "%.2f" % self.txt
        else:
            return str(self.txt)

    def update_text(self, new_text, WIDTH, HEIGHT):
        self.txt = new_text
        self.resize(WIDTH, HEIGHT)

    def resize(self, WIDTH, HEIGHT):
        old_wide = self.rect.width
        wideness, highness = self.get_size()

        self.back = pg.Surface((wideness, highness))
        self.back.fill(colors.WHITE)
        self.rect.width = wideness
        self.rect.height =  highness
        self.border.width = wideness + self.b_width*2
        self.border.height = highness + self.b_width*2
        self.border.top = self.rect.top - self.b_width

        if self.align == "right":
            self.border.right = self.rect.right + self.b_width - (wideness-old_wide)  # since it would grow in that direction
            self.rect.right = self.rect.right - (wideness-old_wide)
        elif self.align == "left":
            self.border.left = self.rect.left - self.b_width
        elif self.align == "center":
            self.border.left = (WIDTH - wideness - 2*self.b_width) // 2
            self.rect.left = (WIDTH- wideness) // 2
