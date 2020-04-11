import os
import pygame as pg
import random

pg.init()

white = (255, 255, 255)  # initialize RGB values of each colour
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 155, 0)
blue = (0, 0, 255)
bg_colour = (155, 155, 155)

display_width = 800
display_height = 600

gd = pg.display.set_mode((display_width, display_height))  # screen size, is a Surface
screen_rect = gd.get_rect()
pg.display.set_caption("Slither")  # set window title

# pygame.display.flip() # updates the ENTIRE screen every frame
# pygame.display.update()  # updates parts of screen that changed, if parameters input


img = pg.image.load(os.path.join('assets', 'snake_head.png'))
apl_img = pg.image.load(os.path.join('assets', 'apple.png'))
icon = pg.transform.scale(pg.image.load(os.path.join('assets', 'apple.png')), (32, 32))

pg.display.set_icon(icon)

vel_size = 20
clock = pg.time.Clock()  # object for fps
FPS = 10

small_font = pg.font.SysFont("comicsansms", 25)  # returns font object
med_font = pg.font.SysFont("comicsansms", 50)  # returns font object
big_font = pg.font.SysFont("comicsansms", 80)  # returns font object


def game_intro():
    intro = True
    while intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_c:
                    intro = False
                elif event.key == pg.K_q:
                    pg.quit()
                    quit()
        gd.fill(bg_colour)
        msg_to_screen("Welcome to Snake",
                      green,
                      y_displace=-100,
                      size="big")
        msg_to_screen("The objective is to eat red apples",
                      black,
                      y_displace=0,
                      size="small")
        msg_to_screen("The more apples you eat the longer you get",
                      black,
                      y_displace=40,
                      size="small")
        msg_to_screen("If you run into anything except for apples, you lose",
                      black,
                      y_displace=80,
                      size="small")
        msg_to_screen("Press c to play or q to quit",
                      black,
                      y_displace=200,
                      size="small")
        pg.display.update()
        clock.tick(FPS)


def score_display(score):
    text = small_font.render("Score: %s" % score, True, black)
    gd.blit(text, [0, 0])


def snake(snake_list, direction, head_rect, snake_colour):
    if direction == "right":
        head = pg.transform.rotate(img, 270)   # transformed img
    elif direction == "up":
        head = img
    elif direction == "down":
        head = pg.transform.rotate(img, 180)
    else:  # direction == "left":
        head = pg.transform.rotate(img, 90)

    for rect_obj in snake_list[:-1]:
        pg.draw.rect(gd, snake_colour, rect_obj)
    gd.blit(head, head_rect)


def text_objects(text, colour, size):
    if size == "small":
        text_surface = small_font.render(text, True, colour)  # creates a Surface and a rect object
    elif size == "med":
        text_surface = med_font.render(text, True, colour)  # creates a Surface and a rect object
    else:  # size == "big":
        text_surface = big_font.render(text, True, colour)  # creates a Surface and a rect object
    return text_surface, text_surface.get_rect()


def msg_to_screen(msg, colour, y_displace=0, size="small"):
    # sceen_text = font.render(msg, True, colour)  # puts text on the hidden screen, waiting for .update() so the text
    # gameDisplay.blit(sceen_text, [display_width // 2, display_height // 2])  # can be shown
    text_surface, text_rect = text_objects(msg, colour, size)
    text_rect.center = (display_width//2), ((display_height//2) + y_displace)  # how to center text properly
    gd.blit(text_surface, text_rect)


def transform_colours(r, g, b, dir):
    # if r >= 253 and g <= 3 and b <= 3:  # red full, green grow
    #     g += 2
    # elif r >= 3 and g >= 253 and b <= 253:  # green full, red die, blue grow
    #     r -= 2
    #     b += 2
    # elif r <= 3 and g >= 3 and b >= 253:  # blue full, green die
    #     g -= 2
    # elif r <= 253 and g <= 3 and 60 <= b <= 117:
    #     b += random.randint(-2, 2)
    # else:
    #     r -= 2
    #     g += 2
    #     b += 2
    # if 240 <= r <= 255:
    #     r -= 2
    # if 25 <= r <= 50:
    #     r += random.randint(-1, 5)
    # if 5 <= b <= 25:
    #     b += 6
    # if 216 <= b <= 236:
    #     b -= 2
    # if 2 <= g <= 15:
    #     g += 1
    # if 159 <= g <= 216:
    #     g += random.randint(-5, 2)
    if dir == 'left':
        r -= random.randint(-2, 3)
        g -= random.randint(-3, 2)
        b -= random.randint(-2, 5)
    elif dir == 'right':
        r += random.randint(-3, 1)
        g += random.randint(-1, 3)
        b += random.randint(-5, 3)
    elif dir == 'up':
        r -= random.randint(-6, 3)
        g += random.randint(-2, 5)
        b += random.randint(-1, 2)
    elif dir == 'down':
        r += random.randint(-1, 4)
        g -= random.randint(-4, 4)
        b -= random.randint(-1, 1)

    r %= 255
    g %= 255
    b %= 255
    return r, g, b


def play_snake():
    dead = False
    start_x = display_width // 2  # first block of snake
    start_y = display_height // 2
    head_rect = pg.Rect((start_x, start_y), (vel_size, vel_size))
    lead_x_v = 0
    lead_y_v = 0
    direction = 'right'

    s_r = 155
    s_g = 155
    s_b = 155

    snake_list = []   # initialize snake body
    snake_len = 1
    apple_img = pg.transform.scale(apl_img, (vel_size, vel_size))  # resize apple appropriately
    apple_rect = apple_img.get_rect()  # create a Rect() object for the apple
    apple_rect.x = random.randrange(0, (display_width - vel_size), vel_size)
    apple_rect.y = random.randrange(0, (display_height - vel_size), vel_size)
    while head_rect.colliderect(apple_rect):  # make sure the apple doesnt start exactly on the snake head
        apple_rect.x = random.randrange(0, (display_width - vel_size), vel_size)
        apple_rect.y = random.randrange(0, (display_height - vel_size), vel_size)

    while not dead:
        for event in pg.event.get():  # every frame event = what the user is doing
            if event.type == pg.QUIT:  # if user clicks exit button
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:  # make velocity 10 if press in some direction
                if event.key == pg.K_LEFT and lead_x_v == 0:
                    lead_x_v = -vel_size
                    lead_y_v = 0  # can only travel in one direction at once
                    direction = 'left'
                    break
                elif event.key == pg.K_RIGHT and lead_x_v == 0:
                    lead_x_v = vel_size
                    lead_y_v = 0
                    direction = 'right'
                    break
                elif event.key == pg.K_UP and lead_y_v == 0:
                    lead_y_v = -vel_size
                    lead_x_v = 0
                    direction = 'up'
                    break
                elif event.key == pg.K_DOWN and lead_y_v == 0:
                    lead_y_v = vel_size
                    lead_x_v = 0
                    direction = 'down'
                    break

        head_rect.x += lead_x_v  # move the snakey boi along
        head_rect.y += lead_y_v
        print(lead_x_v, lead_y_v)
        snake_list.append(pg.Rect.copy(head_rect))

        if not head_rect.colliderect(screen_rect):  # going out of bounds
            dead = True

        gd.fill(bg_colour)  # fill surface object to have white background (clear, wipe the screen clear)
        gd.blit(apple_img, apple_rect)

        if len(snake_list) > snake_len:  # remove the tail
            del snake_list[0]

        if head_rect.collidelist(snake_list[:-1]) != -1:
            dead = True

        s_r, s_g, s_b = transform_colours(s_r, s_g, s_b, direction)
        snake(snake_list, direction, head_rect, (s_r, s_g, s_b))
        score_display(len(snake_list) - 1)
        pg.display.update()  # update having been drawn things

        if head_rect.colliderect(apple_rect):
            apple_rect.x = random.randrange(0, (display_width - vel_size), vel_size)
            apple_rect.y = random.randrange(0, (display_height - vel_size), vel_size)
            while apple_rect.collidelist(snake_list) != -1:  # ensure the apple doesn't spawn inside the snake
                apple_rect.x = random.randrange(0, (display_width - vel_size), vel_size)
                apple_rect.y = random.randrange(0, (display_height - vel_size), vel_size)
            snake_len += 20

        clock.tick(FPS)  # set fps
    lose_screen(len(snake_list) - 1)


def lose_screen(final_score):
    # gameDisplay.fill(white)
    msg_to_screen("You suck!",
                  red,
                  y_displace=-50,
                  size="big")

    msg_to_screen("Press c to play again or q to quit. Final Score: %s" % final_score, black,
                  y_displace=20,
                  size="small")
    while True:
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    pg.quit()
                    quit()
                elif event.key == pg.K_c:
                    play_snake()

game_intro()
play_snake()
