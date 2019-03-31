import pygame as pg
import colors
import random

pg.init()
pg.font.init()
WIDTH, HEIGHT = 1000, 800
CARDS_NUM = 4
gd = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('24!')
clock = pg.time.Clock()


class BorderedSprite(pg.sprite.Sprite):
    def __init__(self, sz):
        pg.sprite.Sprite.__init__(self)
        self.b_width = 3
        self.rect = sz.copy()

        self.back = pg.Surface((self.rect.width, self.rect.height))
        self.back.fill(colors.WHITE)

        self.border = pg.Rect(self.rect.left-self.b_width, self.rect.top-self.b_width, self.rect.width+2*self.b_width, self.rect.height+2*self.b_width)
        self.border_color = colors.BLACK

        self.selected = False
        self.visible = False

    def draw(self, surf):
        if self.visible:
            pg.draw.rect(gd, self.border_color, self.border)
            gd.blit(self.back, self.rect)
            gd.blit(surf, self.rect)

    def center_draw(self, surf):
        if self.visible:
            pg.draw.rect(gd, self.border_color, self.border)
            gd.blit(self.back, self.rect)
            gd.blit(surf, surf.get_rect(center=self.rect.center))


    def move(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.border.x = pos[0] - self.b_width
        self.border.y = pos[1] - self.b_width

    def hide(self):
        self.move((-1000, -1000))
        self.visible = False
        self.selected = False

    def slot(self, s):
        self.visible = True
        self.selected = False
        for i in range(CARDS_NUM):
            if s == i:
                self.move((self.rect.width+((WIDTH-3*self.rect.width)//(CARDS_NUM-1))*i, HEIGHT//2-self.rect.height//2))
                print(self)
                return
        else:
            raise ValueError(f"Slot value must be in the range [0,{CARDS_NUM-1}]")

    def try_select(self, mouse_evt):
        if self.rect.collidepoint(mouse_evt.pos):
            self.selected = True
            self.border_color = colors.ORANGE
        return self.selected

    def deselect(self):
        self.selected = False
        self.border_color = colors.BLACK


class Card(BorderedSprite):
    def __init__(self, value, im_name):
        im_load = pg.image.load(f"./assets/{im_name}").convert_alpha()
        super().__init__(im_load.get_rect())

        self.value = value
        self.name = im_name
        self.image = im_load

    def draw(self):
        super().draw(self.image)

    def __repr__(self):
        return f"Card(name={self.name}, value={self.value}, loc={self.rect}, visible={self.visible}), hbox={self.border}"


class Fraction(BorderedSprite):
    def __init__(self, top, low, sz):
        if not low:
            raise ZeroDivisionError(f"Can't create a fraction with denominator 0 (numerator was {top})")
        super().__init__(sz)
        self.top = top
        self.low = low
        self.sz = sz.copy()

        self.font = pg.font.SysFont("Comic Sans MS", 80)
        self.reduce()

    def draw(self):
        text = repr(self)
        text_surf = self.font.render(text, True, colors.BLACK)
        super().center_draw(text_surf)

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
        if type(other) is Fraction:
            self.top = other.low*self.top - other.top*self.low
            self.low = other.low*self.low
        elif type(other) is int:
            self.top = self.top - other*self.low
        else:
            raise ValueError(f"Can't add type 'Fraction' and '{type(other)}'")
        self.reduce()
        return self

    def __add__(self, other):
        if type(other) is Fraction:
            self.top = other.low*self.top + other.top*self.low
            self.low = other.low*self.low
        elif type(other) is int:
            self.top += other*self.low
        else:
            raise ValueError(f"Can't sub type 'Fraction' and '{type(other)}'")
        self.reduce()
        return self

    def __mul__(self, other):
        if type(other) is Fraction:
            self.top *= other.top
            self.low *= other.low
        elif type(other) is int:
            self.top *= other
        else:
            raise ValueError(f"Can't mul type 'Fraction' and '{type(other)}'")
        self.reduce()
        return self

    def __truediv__(self, other):
        if type(other) is Fraction:
            if other.top  == 0:
                raise ZeroDivisionError(f"You can't do that! (Tried to divide a fraction <{self}> by fraction <{other}>)")
            self.top *= other.low
            self.low *= other.top
        elif type(other) is int:
            if other == 0:
                raise ZeroDivisionError(f"You can't do that! (Tried to divide a fraction <{self}> by int 0)")
            self.low *= other
        else:
            raise ValueError(f"Can't div type 'Fraction' and '{type(other)}'")
        self.reduce()
        return self

    def __floordiv__(self, other):
        self.__truediv__(other)
        return self

    def __repr__(self):
        if self.low == 1 or self.top == 0:
            text = f"{self.top}"
        else:
            text = f"{self.top}/{self.low}"
        return text

def load_imgs():
    img_arr = []
    val_map = {1: "ace", 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11: "jack", 12: "queen", 13: "king"}
    suits = ["hearts", "clubs", "diamonds", "spades"]
    for v in range(1, 14):
        for s in suits:
            new_c = Card(v, f"cards/light/{val_map[v]}_of_{s}.png")
            new_c.hide()
            img_arr.append(new_c)
    return img_arr


def rand_slot(cards):
    random.shuffle(cards)
    cs = random.sample(cards, 4)
    for card in cards:
        card.hide()
    for s, c in enumerate(cs):
        c.slot(s)

def do_op(op_chosen, val1, val2):
    if op_chosen == 0:
        return val1 + val2
    elif op_chosen == 1:
        return val1 - val2
    elif op_chosen == 2:
        return val1*val2
    elif op_chosen == 3:
        return val1/val2
    else:
        raise ValueError(f"Illegal operation '{op_chosen}', must be in [0,3]")


def game():
    cards = load_imgs()
    rand_slot(cards)
    num = Fraction(2, 3, cards[5].rect)
    num.slot(1)
    while True:
        for evt in pg.event.get():
            if evt.type == pg.QUIT:
                pg.quit()
                return 0
            elif evt.type == pg.MOUSEBUTTONDOWN:
                pass
            elif evt.type == pg.MOUSEBUTTONUP:
                pass

        gd.fill(colors.WHITE)
        for card in cards:
            card.draw()
        num.draw()
        pg.display.update()
        clock.tick(15)







if __name__ == "__main__":
    game()
