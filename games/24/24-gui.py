#!/usr/bin/env python3

import pygame as pg
import colors
import random
import time
import cards
import subprocess
import elo
import threading as th
import os

pg.init()
pg.font.init()
WIDTH, HEIGHT = 1200, 1000     # 1200, 1000  #400, 300
CARDS_NUM = 5
TARGET = 60
MAX_SCORE = 8500
MIN_SCORE = 150
PENALTY = 6000
font_size = 50           # 50   # 20
frac_font = 40
card_size = (133, 194)     # 133, 194    #70, 85
button_size = (75, 75)   # 75, 75     # 40, 40
gui_size = (75, 75)      # 75, 60    #45, 30
wide_gui_size = (100, 25)       #100,25     #
big_wide_gui_size = (320, 50)     # 160, 25     #
SCRIPT_LOC = os.path.dirname(os.path.realpath(__file__))
gd = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(f'{TARGET}!')
clock = pg.time.Clock()
elo_table = elo.EloTable(f"{SCRIPT_LOC}/gui-24.elo")
lock = th.Lock()
th_event = th.Event()
key_to_slot_num = {pg.K_1: 0,      # mappings between keyboard keys and the selected card
                   pg.K_2: 1,
                   pg.K_3: 2,
                   pg.K_4: 3,
                   pg.K_5: 4,
                   pg.K_6: 5,
                   pg.K_7: 6,
                   pg.K_8: 7,
                   pg.K_9: 8,
                   pg.K_0: 9}
op_keys = {pg.K_q:1, pg.K_w:2, pg.K_e:3, pg.K_r:4}   # mappings between keyboard keys and the selected op

def load_imgs():
    img_arr = []
    val_map = {1: "ace", 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11: "jack", 12: "queen", 13: "king"}
    suits = ["hearts", "clubs", "diamonds", "spades"]
    for v in range(1, 14):
        for s in suits:
            new_c = cards.Card(v, f"{SCRIPT_LOC}/../assets/cards/light/{val_map[v]}_of_{s}.png", sz=card_size)
            new_c.hide()
            img_arr.append(new_c)
    return img_arr


def rand_slot(deck):
    random.shuffle(deck)
    slotted = []
    cs = random.sample(deck, CARDS_NUM)
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


def continue_screen(gs, txt_msg):
    t_msg = cards.TextBox(txt_msg, pg.Rect(WIDTH//2-(len(txt_msg)*font_size//4), HEIGHT//2, len(txt_msg)*font_size//2, font_size*1.25), fsize=font_size)
    cont_msg = cards.TextBox("Click to continue", pg.Rect(WIDTH//2-(17*font_size//4), HEIGHT//2-font_size*2.0, 17*font_size//2, font_size*1.25), fsize=font_size)
    while True:
        for evt in pg.event.get():
            if evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.KEYDOWN:
                return 0
            elif evt.type == pg.QUIT:
                gs.keep_looping = False
                return 0
        gd.fill(colors.WHITE)
        t_msg.draw(gd)
        cont_msg.draw(gd)
        pg.display.update()
        clock.tick(15)


def async_check(gs):
    while gs.keep_looping:
        flags = ["krypto", str(TARGET)] + [str(x.value) for x in gs.hand_copy] + ["-f"]
        with lock:
            res = subprocess.run(flags, stdout=subprocess.PIPE)
            gs.solution = res
        th_event.wait()
        th_event.clear()

def verify_no_solution(gs):
    with lock:
        if gs.solution.stdout[0] == 78:
            return 1
        else:
            return gs.solution.stdout.decode('utf-8')


def load_gui():
    names = ["undo.jpeg", "plus_sign.jpeg", "minus_sign.jpeg", "multiply_sign.jpeg", "divide_sign.jpeg", "redo.jpeg"]
    buttons = []
    for idx, name in enumerate(names):
        new_b = cards.Card(idx, f"{SCRIPT_LOC}/../assets/math_symbols/{name}", sz=button_size, dark_flag=True)
        new_b.slot_below(WIDTH, HEIGHT, len(names), idx)
        buttons.append(new_b)
    buttons[0].darken()
    buttons[-1].darken()
    return buttons


def do_operation(result, gs):
    if gs.card1 == result:
        return
    if type(gs.card1.value) is cards.MathFraction:
        c1_val = gs.card1.value
    else:
        c1_val = cards.MathFraction(gs.card1.value, 1)
    if type(result.value) is cards.MathFraction:
        res_val = result.value
    else:
        res_val = cards.MathFraction(result.value, 1)
    new_val = do_op(gs.op_selected.value, c1_val, res_val)
    new_card = cards.Fraction(new_val, gs.card1.rect, fontsize=frac_font)
    sp_cpy = gs.sp+3  # if overwriting stack, delete everything above overwrite point
    try:
        while True:
            del gs.stack[sp_cpy]
            sp_cpy += 1
    except KeyError:  # absolutely beautiful code right here, waiting to throw an error to exit a loop
        pass
    gs.stack[gs.sp] = result
    gs.stack[gs.sp+1] = gs.card1
    gs.stack[gs.sp+2] = new_card
    gs.sp += 3
    gs.card1.deselect()
    result.deselect()
    gs.card1.hide()
    result.hide()
    new_card.slot(WIDTH, HEIGHT, CARDS_NUM, result.slot_num)
    gs.extra_cards.append(new_card)
    gs.op_selected.deselect()
    gs.op_selected = None
    gs.card1 = new_card
    gs.card1.select_it()


def handle_undo(gs):
    if gs.op_selected:
        gs.op_selected.deselect()
        gs.op_selected = None
        gs.buttons[0].deselect()
    else:
        gs.stack[gs.sp-1].hide()  # delete newest card
        gs.stack[gs.sp-2].reslot(WIDTH, HEIGHT, CARDS_NUM)
        gs.stack[gs.sp-3].reslot(WIDTH, HEIGHT, CARDS_NUM)
        gs.stack[gs.sp-2].unhide()
        gs.stack[gs.sp-3].unhide()
        gs.stack[gs.sp-2].select_it()
        gs.card1.deselect()
        gs.card1 = gs.stack[gs.sp-2]
        gs.sp -= 3


def handle_redo(gs):
    gs.stack[gs.sp].hide()
    gs.stack[gs.sp+1].hide()
    gs.stack[gs.sp+2].unhide()
    gs.stack[gs.sp+2].reslot(WIDTH, HEIGHT, CARDS_NUM)
    gs.stack[gs.sp+2].select_it()
    gs.card1.deselect()
    gs.card1 = gs.stack[gs.sp+2]
    gs.sp += 3


def get_cards_in_play(gs):
    return [c for c in gs.deck+gs.extra_cards if c.visible]


def add_all(gs):
    while True:
        c_remaining = get_cards_in_play(gs)
        if len(c_remaining) == 1:
            break
        gs.op_selected = gs.buttons[1]
        gs.card1 = c_remaining[0]
        result = c_remaining[1]
        do_operation(result, gs)


def mul_all(gs):
    while True:
        c_remaining = get_cards_in_play(gs)
        if len(c_remaining) == 1:
            break
        gs.op_selected = gs.buttons[3]
        gs.card1 = c_remaining[0]
        result = c_remaining[1]
        do_operation(result, gs)


def select_card_by_index(gs, idx):
    cards_in_play = get_cards_in_play(gs)
    correct_card = [c for c in cards_in_play if c.slot_num == idx]
    if correct_card:
        if not gs.card1:
            gs.card1 = correct_card[0]
            correct_card[0].select_it()
        elif gs.op_selected:
            do_operation(correct_card[0], gs)
        elif gs.card1 != correct_card[0]:
            gs.card1.deselect()
            gs.card1 = correct_card[0]
            correct_card[0].select_it()

def handle_events(evt, gs):
    if evt.type == pg.QUIT:
        gs.keep_looping = False
    elif evt.type == pg.KEYDOWN:
        if evt.key == pg.K_a:
            add_all(gs)
        elif evt.key == pg.K_s:
            mul_all(gs)
        elif evt.key == pg.K_ESCAPE:
            if gs.buttons[0].enabled:
                handle_undo(gs)
        elif evt.key in key_to_slot_num.keys():     # slightly better way of selecting cards by pressing keyboard keys using predefined dict (i could also use key - 48, but that's sketchier)
            select_card_by_index(gs, key_to_slot_num[evt.key])
        elif evt.key in op_keys.keys():
            if gs.card1:
                if gs.op_selected:
                    gs.op_selected.deselect()
                gs.op_selected = gs.buttons[op_keys[evt.key]]
                gs.buttons[op_keys[evt.key]].select_it()
        elif evt.key == pg.K_p:
            gs.correct_flag = verify_no_solution(gs)
    elif evt.type == pg.MOUSEBUTTONDOWN:  # if any button maybe clicked
        if gs.pass_btn.try_select(evt):      # claim no solution
            gs.correct_flag = verify_no_solution(gs)
        result = attempt_select(evt, gs.deck+gs.extra_cards)  # selecting other cars
        if result:
            if not gs.card1:   # if any card1 not already chosen  (card1 = currently selected card)
                gs.card1 = result
            elif gs.op_selected:    # if op already chosen + card1 already chosen
                do_operation(result, gs)
            elif gs.card1 != result:   # if no op selected and another card clicked, change which card is selected
                gs.card1.deselect()
                gs.card1 = result
        else:              # card was not clicked so check if an op button was clicked
            if gs.card1:
                op_result = attempt_select(evt, gs.buttons)
                if op_result == gs.buttons[0]:  # undo
                    handle_undo(gs)
                if op_result == gs.buttons[-1]:  # redo
                    handle_redo(gs)
                if op_result and op_result not in [gs.buttons[0], gs.buttons[-1]]:
                    if gs.op_selected:                 # changing op chosen
                        gs.op_selected.deselect()
                    gs.op_selected = op_result         # selecting brand new op
                    gs.op_selected.select_it()


def buttons_enable_disable(gs):
    if gs.sp == 0:
        gs.buttons[0].disable()
        gs.buttons[0].darken()
    if gs.sp != 0 and len(gs.stack) != 0:
        gs.buttons[0].enable()
        gs.buttons[0].lighten()
    if len(gs.stack) != gs.sp:
        gs.buttons[-1].enable()
        gs.buttons[-1].lighten()
    else:
        gs.buttons[-1].disable()
        gs.buttons[-1].darken()
    if gs.op_selected:
        gs.buttons[0].enable()
        gs.buttons[0].lighten()
    if len(gs.stack) == 0 and gs.op_selected is None:
        gs.buttons[0].disable()
        gs.buttons[0].darken()


def get_puzzle_name(gs):
    puzzle_values = sorted([x.value for x in gs.hand_copy])
    puzzle_name = "|".join([str(x) for x in puzzle_values])
    return puzzle_name

def handle_correct(gs):
    gs.stack = {}
    gs.sp = 0
    gs.extra_cards = []
    deselect_all(gs.deck)
    deselect_all(gs.buttons)
    hide_all(gs.deck)
    gs.hand_copy = rand_slot(gs.deck)
    gs.card1 = None   # card currently selected
    gs.op_selected = None          # op chosen

    points_earned = MAX_SCORE/(time.time()-gs.start)+MIN_SCORE
    score_earned = max(1 - 0.05*((time.time() - gs.start)), 0.6)

    puzzle_name = get_puzzle_name(gs)
    gs.correct += 1
    elo_table.update_player(puzzle_name, score_earned)
    gs.score += points_earned
    gs.score_box.update_text("%.1f"%gs.score, WIDTH, HEIGHT)
    gs.start = time.time()
    gs.correct_flag = 0
    gs.pf_box.update_text("%.1f"%elo_table.performance, WIDTH, HEIGHT)
    gs.solved_box.update_text(gs.correct, WIDTH, HEIGHT)
    th_event.set()

def handle_wrong(gs):
    gs.stack = {}
    gs.sp = 0
    gs.extra_cards = []
    deselect_all(gs.deck)
    deselect_all(gs.buttons)
    hide_all(gs.deck)
    gs.hand_copy = rand_slot(gs.deck)
    gs.card1 = None   # card currently selected
    gs.op_selected = None          # op chosen
    puzzle_name = get_puzzle_name(gs)
    elo_table.update_player(puzzle_name, 0)
    gs.score -= PENALTY
    gs.score_box.update_text("%.1f"%gs.score, WIDTH, HEIGHT)
    gs.start = time.time()
    gs.wrong += 1
    continue_screen(gs, f"A solution was {gs.correct_flag[:-1]}")
    gs.pass_btn.deselect()
    gs.correct_flag = 0
    gs.pf_box.update_text("%.1f"%elo_table.performance, WIDTH, HEIGHT)
    gs.wrong_box.update_text(gs.wrong, WIDTH, HEIGHT)
    th_event.set()

def game():
    gs = cards.GameState()     # not really a class, basically a struct with named variables
    gs.deck = load_imgs()
    gs.hand_copy = rand_slot(gs.deck)
    gs.buttons = load_gui()
    gs.extra_cards = []
    gs.card1 = None   # card currently selected
    gs.op_selected = None          # op chosen
    gs.score = 0
    gs.start = time.time()
    game_start = time.time()
    gs.correct = 0
    gs.wrong = 0
    gs.keep_looping = True

    th_event.clear()
    solver_thread = th.Thread(target=async_check, args=(gs,))
    solver_thread.start()

    right_height = 0
    left_height = 0
    gs.score_disp = cards.TextBox("Score", pg.Rect(WIDTH, right_height, *wide_gui_size), bsize=2, fsize=font_size, align="right")   # just need the top left corner
    gs.score_disp.resize(WIDTH, HEIGHT)
    right_height = gs.score_disp.border.bottom
    gs.score_box = cards.TextBox("0", pg.Rect(WIDTH, right_height, *wide_gui_size), bsize=2, fsize=font_size, align="right")
    gs.score_box.resize(WIDTH, HEIGHT)
    right_height = gs.score_box.border.bottom

    gs.pf_disp = cards.TextBox("Performance", pg.Rect(WIDTH, right_height, *wide_gui_size), bsize=2, fsize=font_size, align="right")
    gs.pf_disp.resize(WIDTH, HEIGHT)
    right_height = gs.pf_disp.border.bottom
    gs.pf_box = cards.TextBox("------", pg.Rect(WIDTH, right_height, *wide_gui_size), bsize=2, fsize=font_size, align="right")
    gs.pf_box.resize(WIDTH, HEIGHT)
    right_height = gs.pf_box.border.bottom

    gs.time_disp = cards.TextBox("Time", pg.Rect(0, left_height, *gui_size), bsize=2, fsize=font_size, align="left")
    gs.time_disp.resize(WIDTH, HEIGHT)
    left_height = gs.time_disp.border.bottom
    gs.time_box = cards.TextBox("0", pg.Rect(0, left_height, *gui_size), bsize=2, fsize=font_size, align="left")
    gs.time_box.resize(WIDTH, HEIGHT)
    left_height = gs.time_box.border.bottom

    gs.solved_disp = cards.TextBox("Solved", pg.Rect(0, left_height, *gui_size), bsize=2, fsize=font_size, align="left")
    gs.solved_disp.resize(WIDTH, HEIGHT)
    left_height = gs.solved_disp.border.bottom
    gs.solved_box = cards.TextBox("0", pg.Rect(0, left_height, *gui_size), bsize=2, fsize=font_size, align="left")
    gs.solved_box.resize(WIDTH, HEIGHT)
    left_height = gs.solved_box.border.bottom

    gs.wrong_disp = cards.TextBox("Wrong", pg.Rect(0, 0, *gui_size), bsize=2, fsize=font_size, align="center")
    gs.wrong_disp.resize(WIDTH, HEIGHT)
    gs.wrong_box = cards.TextBox("0", pg.Rect(0, gs.wrong_disp.border.bottom, *gui_size), bsize=2, fsize=font_size, align="center")
    gs.wrong_box.resize(WIDTH, HEIGHT)

    gs.pass_btn = cards.TextBox("Claim no solution!", pg.Rect(0, HEIGHT-button_size[1]*4, *big_wide_gui_size), bsize=2, fsize=font_size, align="center")
    gs.pass_btn.resize(WIDTH, HEIGHT)

    gs.correct_flag = 0
    gs.stack = {}
    gs.sp = 0
    while gs.keep_looping:
        for evt in pg.event.get():
            handle_events(evt, gs)

        buttons_enable_disable(gs)
        gd.fill(colors.WHITE)
        for card in gs.deck+gs.extra_cards:
            card.draw(gd)
        for buto in gs.buttons:
            buto.draw(gd)
        gs.score_disp.draw(gd)
        gs.score_box.draw(gd)
        gs.pass_btn.draw(gd)
        gs.pf_disp.draw(gd)
        gs.pf_box.draw(gd)
        gs.time_disp.draw(gd)
        gs.time_box.draw(gd)
        gs.solved_disp.draw(gd)
        gs.solved_box.draw(gd)
        gs.wrong_box.draw(gd)
        gs.wrong_disp.draw(gd)

        gs.buttons[0].deselect()
        gs.buttons[-1].deselect()
        gs.pass_btn.deselect()

        gs.time_box.update_text(int(time.time()-game_start), WIDTH, HEIGHT)

        last_card = one_left(gs.deck+gs.extra_cards)
        if (last_card and last_card.value == TARGET) or gs.correct_flag == 1:
            handle_correct(gs)
        if gs.correct_flag not in [0, 1]:
            handle_wrong(gs)
        pg.display.update()
        clock.tick(15)
    th_event.set()
    try:
        lock.release()
    except RuntimeError as e:
        print(e)
        pass
    elo_table.save()
    elo_table.record_save()
    solver_thread.join()
    pg.quit()
    return 0

if __name__ == "__main__":
    game()
