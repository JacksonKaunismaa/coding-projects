import pygame as pg
import colors
import random
import time
import cards
import subprocess

pg.init()
pg.font.init()
WIDTH, HEIGHT = 1000, 800
CARDS_NUM = 4
TARGET = 24
MAX_SCORE = 8500
MIN_SCORE = 150
PENALTY = 6000
gd = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(f'{TARGET}!')
clock = pg.time.Clock()

def load_imgs():
    img_arr = []
    val_map = {1: "ace", 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11: "jack", 12: "queen", 13: "king"}
    suits = ["hearts", "clubs", "diamonds", "spades"]
    for v in range(1, 14):
        for s in suits:
            new_c = cards.Card(v, f"cards/light/{val_map[v]}_of_{s}.png")
            new_c.hide()
            img_arr.append(new_c)
    return img_arr


def rand_slot(deck):
    random.shuffle(deck)
    slotted = []
    cs = random.sample(deck, 4)
    for card in deck:
        card.hide()
    for s, c in enumerate(cs):
        c.slot(WIDTH, HEIGHT, CARDS_NUM, s)
        slotted.append(c)
    return slotted

def do_op(op_chosen, val1, val2):
    if op_chosen == 1:
        return val1 + val2
    elif op_chosen == 2:
        return val1 - val2
    elif op_chosen == 3:
        return val1*val2
    elif op_chosen == 4:
        return val1/val2
    else:
        raise ValueError(f"Illegal operation '{op_chosen}', must be in [0,3]")


def attempt_select(mpos, deck):
    for card in deck:
        if card.try_select(mpos):
            return card
    return False

def hide_all(deck):
    for card in deck:
        card.hide()


def deselect_all(deck):
    for card in deck:
        card.deselect()

def one_left(deck):
    one = False
    for card in deck:
        if card.visible:
            if one:
                return False
            else:
                one = card
    return card


def continue_screen(txt_msg):
    t_msg = cards.TextBox(txt_msg, pg.Rect((WIDTH//2-(len(txt_msg)*20), HEIGHT//2), (len(txt_msg)*40, 100)))
    cont_msg = cards.TextBox("Click to continue", pg.Rect((WIDTH//2-(17*20), HEIGHT//2-200), (17*40, 100)))
    while True:
        for evt in pg.event.get():
            if evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.KEYDOWN:
                return 0
            elif evt.type == pg.QUIT:
                pg.quit()
                quit()
        gd.fill(colors.WHITE)
        t_msg.draw(gd)
        cont_msg.draw(gd)
        pg.display.update()
        clock.tick(15)



def verify_no_solution(hand):
    res = subprocess.run(["krypto", str(TARGET), str(hand[0].value), str(hand[1].value), str(hand[2].value), str(hand[3].value), "-f"], stdout=subprocess.PIPE)
    if res.stdout[0] == 78:
        return 1
    return res.stdout.decode('utf-8')

def load_gui():
    names = ["undo.jpeg", "plus_sign.jpeg", "minus_sign.jpeg", "multiply_sign.jpeg", "divide_sign.jpeg", "redo.jpeg"]
    buttons = []
    for idx, name in enumerate(names):
        new_b = cards.Card(idx, f"math_symbols/{name}", dark_flag=True)
        new_b.slot_below(WIDTH, HEIGHT, len(names), idx)
        buttons.append(new_b)
    buttons[0].darken()
    buttons[-1].darken()
    return buttons

def game():
    deck = load_imgs()
    hand_copy = rand_slot(deck)
    buttons = load_gui()
    moves_played = []
    extra_cards = []
    card1 = None   # card currently selected
    op_selected = None          # op chosen
    score = 0
    start = time.time()
    score_disp = cards.TextBox("Score", pg.Rect((WIDTH//2-100, 10), (200, 70)))
    score_box = cards.TextBox("0", pg.Rect((WIDTH//2-125, 80), (250, 60)))
    pass_btn = cards.TextBox("Claim no solution!", pg.Rect((WIDTH//2-250, HEIGHT-90), (500, 80)))
    correct_flag = 0
    stack = {}
    sp = 0
    while True:
        for evt in pg.event.get():
            pass_btn.deselect() # this button keeps selecting for some reason, this makes it not do that
            if evt.type == pg.QUIT:
                pg.quit()
                return 0
            elif evt.type == pg.MOUSEBUTTONDOWN:
                if pass_btn.try_select(evt):
                    correct_flag = verify_no_solution(hand_copy)
                result = attempt_select(evt, deck+extra_cards)
                if result:
                    if not card1:
                        card1 = result
                    elif op_selected:
                        if card1 == result:
                            break
                        if type(card1.value) is cards.MathFraction:
                            c1_val = card1.value
                        else:
                            c1_val = cards.MathFraction(card1.value, 1)
                        if type(result.value) is cards.MathFraction:
                            res_val = result.value
                        else:
                            res_val = cards.MathFraction(result.value, 1)
                        new_val = do_op(op_selected.value, c1_val, res_val)
                        new_card = cards.Fraction(new_val, card1.rect)
                        sp_cpy = sp+3  # if overwriting stack, delete everything above overwrite point
                        try:
                            while True:
                                del stack[sp_cpy]
                                sp_cpy += 1
                        except KeyError:  # absolutely beautiful code right here, waiting to throw an error to exit a loop
                            pass
                        stack[sp] = result
                        stack[sp+1] = card1
                        stack[sp+2] = new_card
                        sp += 3
                        card1.deselect()
                        result.deselect()
                        card1.hide()
                        result.hide()
                        new_card.slot(WIDTH, HEIGHT, CARDS_NUM, result.slot_num)
                        extra_cards.append(new_card)
                        op_selected.deselect()
                        op_selected = None
                        card1 = new_card
                        card1.select_it()
                    elif card1 != result:
                        card1.deselect()
                        card1 = result
                else:
                    if card1:
                        op_result = attempt_select(evt, buttons)
                        if op_result == buttons[0]:  # back arrow
                            if op_selected:
                                op_selected.deselect()
                                op_selected = None
                                op_result.deselect()
                            else:
                                 stack[sp-1].hide()  # delete newest card
                                 stack[sp-2].reslot(WIDTH, HEIGHT, CARDS_NUM)
                                 stack[sp-3].reslot(WIDTH, HEIGHT, CARDS_NUM)
                                 stack[sp-2].unhide()
                                 stack[sp-3].unhide()
                                 stack[sp-2].select_it()
                                 card1.deselect()
                                 card1 = stack[sp-2]
                                 sp -= 3
                        if op_result == buttons[-1]:
                            stack[sp].hide()
                            stack[sp+1].hide()
                            stack[sp+2].unhide()
                            stack[sp+2].reslot(WIDTH, HEIGHT, CARDS_NUM)
                            stack[sp+2].select_it()
                            card1.deselect()
                            card1 = stack[sp+2]
                            sp += 3
                        if op_result and op_result not in [buttons[0], buttons[-1]]:
                            if op_selected:
                                op_selected.deselect()
                            op_selected = op_result
                            op_selected.select_it()
        gd.fill(colors.WHITE)
        for card in deck+extra_cards:
            card.draw(gd)
        for buto in buttons:
            buto.draw(gd)
        #print("stack is", stack, "with sp being", sp)
        #print("sp", sp, "len(stack)", len(stack))
        #print("in play", [c for c in deck+extra_cards if c.visible], "card1", card1)
        if sp == 0:
            buttons[0].disable()
            buttons[0].darken()
        if sp != 0 and len(stack) != 0:
            buttons[0].enable()
            buttons[0].lighten()
        if len(stack) != sp:
            buttons[-1].enable()
            buttons[-1].lighten()
        else:
            buttons[-1].disable()
            buttons[-1].darken()

        if op_selected:
            buttons[0].enable()
            buttons[0].lighten()
        if len(stack) == 0 and op_selected is None:
            buttons[0].disable()
            buttons[0].darken()
        buttons[0].deselect()
        buttons[-1].deselect()
        score_disp.draw(gd)
        score_box.draw(gd)
        pass_btn.draw(gd)
        last_card = one_left(deck+extra_cards)
        if (last_card and last_card.value == TARGET) or correct_flag == 1:
            stack = {}
            sp = 0
            extra_cards = []
            deselect_all(deck)
            deselect_all(buttons)
            hide_all(deck)
            hand_copy = rand_slot(deck)
            moves_played = []
            card1 = None   # card currently selected
            op_selected = None          # op chosen
            score += MAX_SCORE/(time.time()-start)+MIN_SCORE
            score_box.update_text(score)
            start = time.time()
            correct_flag = 0
        if correct_flag not in [0, 1]:
            stack = {}
            sp = 0
            extra_cards = []
            deselect_all(deck)
            deselect_all(buttons)
            hide_all(deck)
            hand_copy = rand_slot(deck)
            moves_played = []
            card1 = None   # card currently selected
            op_selected = None          # op chosen
            score -= PENALTY
            score_box.update_text(score)
            start = time.time()
            continue_screen(f"A solution was {correct_flag[:-1]}")
            pass_btn.deselect()
            correct_flag = 0
        pg.display.update()
        clock.tick(15)







if __name__ == "__main__":
    game()
