import pygame
from random import randint
import datetime as dt
import webbrowser

pygame.init()

width, height = 800, 600
fps = 60

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption("Flappy Bird")

small_font = pygame.font.Font("fonts/hardpixel.otf", 42)
large_font = pygame.font.Font("fonts/1987.ttf", 76)

img_title = pygame.image.load("images/title.png")
img_start = pygame.image.load("images/start.png")
img_leaderboard = pygame.image.load("images/leaderboard.png")
img_tap = pygame.image.load("images/tap.png")
img_get_ready = pygame.image.load("images/get_ready.png")
img_game_over = pygame.image.load("images/game_over.png")
img_menu = pygame.image.load("images/menu.png")

pygame.mixer.music.load("sounds/original_mix.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

snd_point = pygame.mixer.Sound("sounds/sfx_point.ogg")
snd_point.set_volume(0.3)
snd_fall = pygame.mixer.Sound("sounds/sfx_hit.ogg")
snd_fall.set_volume(0.6)
snd_die = pygame.mixer.Sound("sounds/sfx_die.ogg")

state = "menu"
play = False
timer = 10
lives = 3
scores = 0
pos, speed, accel = height // 2, 0, 0
player = pygame.Rect(width // 3, pos, 34, 24)
frame = 0

pipe_speed = 3
pipe_size = 200
pipe_pos = height // 2

pipes = []
bgs = [pygame.Rect(0, 0, 288, 600)]
pipes_scores = []


def add_result(score):
    update_board = []
    for line in open("leaderboard.txt").readlines():
        update_board.append(int(line.strip().split()[1]))

    if score not in update_board and score > 0:
        update_board.append(score)
    update_board = [str(line) for line in sorted(update_board, reverse=True)]

    for n in range(1, len(update_board) + 1):
        update_board[n - 1] = str(n) + ". " + update_board[n - 1]

    with open("leaderboard.txt", "w") as new:
        new.write("\n".join(update_board))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            add_result(scores)
            running = False

    if dt.datetime.now().hour in range(6, 17):
        pygame.display.set_icon(pygame.image.load("images/day/icon.png"))
        img_bg = pygame.image.load("images/day/background.png")
        img_bird = pygame.image.load("images/day/bird.png")
        img_tpipe = pygame.image.load("images/day/top_pipe.png")
        img_bpipe = pygame.image.load("images/day/bottom_pipe.png")
    else:
        pygame.display.set_icon(pygame.image.load("images/night/icon.png"))
        img_bg = pygame.image.load("images/night/background.png")
        img_bird = pygame.image.load("images/night/bird.png")
        img_tpipe = pygame.image.load("images/night/top_pipe.png")
        img_bpipe = pygame.image.load("images/night/bottom_pipe.png")

    press = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()
    click = press[0]
    space = keys[pygame.K_SPACE]
    esc = keys[pygame.K_ESCAPE]

    if timer > 0:
        timer -= 1

    frame = (frame + 0.2) % 4

    for i in range(len(bgs) - 1, -1, -1):
        bg = bgs[i]
        bg.x -= pipe_speed // 2

        if bg.right < 0:
            bgs.remove(bg)

        if bgs[-1].right <= width:
            bgs.append(pygame.Rect(bgs[-1].right, 0, 288, 600))

    for i in range(len(pipes) - 1, -1, -1):
        pipe = pipes[i]
        pipe.x -= pipe_speed

        if pipe.right < 0:
            pipes.remove(pipe)
            if pipe in pipes_scores:
                pipes_scores.remove(pipe)

    if state == "menu":
        if timer == 0 and play and click:
            state = "start"
            timer = 10

    elif state == "start":
        if timer == 0 and play and (click or space) and not pipes:
            state = "play"

        pos += (height // 2 - pos) * 0.1
        player.y = pos

    elif state == "play":
        if space or click:
            accel = -2
        else:
            accel = 0

        pos += speed
        speed = (speed + accel + 1) * 0.98
        player.y = pos

        if len(pipes) == 0 or pipes[-1].x < width - 200:
            pipes.append(pygame.Rect(width, 0, 52, pipe_pos - pipe_size // 2))
            pipes.append(pygame.Rect(width, pipe_pos + pipe_size // 2,
                                     52, height - pipe_pos - pipe_size // 2))

            pipe_pos += randint(-100, 100)
            if pipe_pos < pipe_size:
                pipe_pos = pipe_size
            elif pipe_pos > height - pipe_size:
                pipe_pos = height - pipe_size

        if player.top < 0 or player.bottom > height:
            state = "fall"

        for pipe in pipes:
            if player.colliderect(pipe):
                state = "fall"

            if pipe.right < player.left and pipe not in pipes_scores:
                snd_point.play()
                pipes_scores.append(pipe)
                scores += 5
                pipe_speed = 3 + scores // 100

    elif state == "fall":
        speed, accel = 0, 0
        pipe_pos = height // 2
        lives -= 1
        if lives > 0:
            snd_fall.play()
            state = "start"
            timer = 60
        else:
            snd_die.play()
            state = "game over"
            timer = 180

    elif state == "game over":
        pos += speed
        speed = (speed + accel + 1) * 0.98
        player.y = pos
        add_result(scores)

        if timer == 0 and play and click:
            state = "start"
            timer = 10
            lives = 3
            scores = 0
            pos, speed, accel = height // 2, 0, 0
            player = pygame.Rect(width // 3, pos, 34, 24)
            frame = 0

            pipe_speed = 3
            pipe_size = 200
            pipe_pos = height // 2

    for bg in bgs:
        screen.blit(img_bg, bg)

    for pipe in pipes:
        if pipe.y == 0:
            rect = img_tpipe.get_rect(bottomleft=pipe.bottomleft)
            screen.blit(img_tpipe, rect)
        else:
            rect = img_bpipe.get_rect(topleft=pipe.topleft)
            screen.blit(img_bpipe, rect)

    image = img_bird.subsurface(34 * int(frame), 0, 34, 24)
    image = pygame.transform.rotate(image, -speed * 2)
    screen.blit(image, player)

    if state == "menu":
        rect = img_title.get_rect(topleft=(width // 2 - 178 // 2, 20))
        screen.blit(img_title, rect)

        rect = img_start.get_rect(topleft=(width // 2 - 104 - 30, 4 * height // 5))
        screen.blit(img_start, rect)
        if timer == 0:
            play = rect.collidepoint(pygame.mouse.get_pos())

        rect = img_leaderboard.get_rect(topleft=(width // 2 + 30, 4 * height // 5))
        screen.blit(img_leaderboard, rect)
        if rect.collidepoint(pygame.mouse.get_pos()) and click and timer == 0:
            webbrowser.open("leaderboard.txt")

    if state == "start":
        rect = img_get_ready.get_rect(topleft=(width // 2 - 184 // 2, height // 3))
        screen.blit(img_get_ready, rect)

        if not pipes:
            rect = img_tap.get_rect(topleft=(width // 2 - 114 // 2, height // 2))
            screen.blit(img_tap, rect)

    if state != "menu" and state != "game over":
        text = small_font.render("Очки: " + str(scores), True, pygame.Color("black"))
        screen.blit(text, (20, 5))

        text = small_font.render("Жизни: " + str(lives), True, pygame.Color("black"))
        screen.blit(text, (20, height - 60))

    if state == "game over":
        rect = img_game_over.get_rect(topleft=(width // 2 - 192 // 2, height // 3))
        screen.blit(img_game_over, rect)

        if timer == 0 or not pipes:
            rect = img_start.get_rect(topleft=(width // 2 - 104 // 2, 4 * height // 5))
            screen.blit(img_start, rect)
            play = rect.collidepoint(pygame.mouse.get_pos())

            rect = img_menu.get_rect(topleft=(width // 2 - 80 // 2, 20))
            screen.blit(img_menu, rect)
            if rect.collidepoint(pygame.mouse.get_pos()) and click or esc:
                state = "menu"
                play = False
                timer = 10
                lives = 3
                scores = 0
                pos, speed, accel = height // 2, 0, 0
                player = pygame.Rect(width // 3, pos, 34, 24)
                frame = 0

                pipe_speed = 3
                pipe_size = 200
                pipe_pos = height // 2

        text = large_font.render(str(scores), True, pygame.Color("black"))
        screen.blit(text, (20, 15))

    pygame.display.update()
    clock.tick(fps)

pygame.quit()