import sys

import pygame
import socket
import random
from threading import Thread

# initialize pygame
pygame.init()

# game canvas
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

# game variables
ball_speed_x = random.choice([1, -1]) * random.randint(2, 4)
ball_speed_y = -random.randint(2, 4)
paddle_speed = 0
paddle_width = 100
paddle_height = 20
ball_radius = 10

# game score
survive_time = 0

# game state
ball_pos = [screen_width // 2, screen_height // 2]
paddle_pos = [screen_width // 2 - paddle_width // 2, screen_height - paddle_height]

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
game_address = ("localhost", 12345)
control_address = ("localhost", 54321)

font = pygame.font.Font(None, 36)


def reset_game():
    global ball_pos, ball_speed_x, ball_speed_y, paddle_pos, paddle_speed
    ball_pos = [screen_width // 2, screen_height // 2]
    ball_speed_x = random.choice([1, -1]) * random.randint(2, 4)
    ball_speed_y = -random.randint(2, 4)
    paddle_pos = [screen_width // 2 - paddle_width // 2, screen_height - paddle_height]
    paddle_speed = 0


def send_status(message=None):

    if message is None:

        if ball_pos[0] < paddle_pos[0]:
            message = "<{left} --> [on]>."
        elif ball_pos[0] > paddle_pos[0] + paddle_width:
            message = "<{right} --> [on]>."
        else:
            message = "<{center} --> [on]>."

    sock.sendto(message.encode(), control_address)


def game_loop():
    global ball_pos, ball_speed_x, ball_speed_y, paddle_pos, paddle_speed, survive_time, survive_time_curve

    running = True
    clock = pygame.time.Clock()

    while running:

        survive_time += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        # update ball pos
        ball_pos[0] += ball_speed_x
        ball_pos[1] += ball_speed_y

        # boundary collision check
        if ball_pos[0] <= ball_radius or ball_pos[0] >= screen_width - ball_radius:
            ball_speed_x = -ball_speed_x
        if ball_pos[1] <= ball_radius:
            ball_speed_y = -ball_speed_y

        # paddle collision check
        if ball_pos[1] + ball_radius >= paddle_pos[1] and paddle_pos[0] < ball_pos[0] < paddle_pos[0] + paddle_width:
            ball_speed_y = -ball_speed_y  # toggle y-axis speed

            # optional
            # # increase difficulty, ball speed change on collusion
            # offset = (ball_pos[0] - (paddle_pos[0] + paddle_width / 2)) / (paddle_width / 2)
            # ball_speed_x += offset * 2  # 2 is a hyperparameter

        # game failed
        if ball_pos[1] >= screen_height:
            send_status("GAME FAILED")
            survive_time = 0
            reset_game()  # restart

        paddle_pos[0] += paddle_speed

        if paddle_pos[0] < 0:
            paddle_pos[0] = 0
        if paddle_pos[0] > screen_width - paddle_width:
            paddle_pos[0] = screen_width - paddle_width

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255),
                         pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))
        pygame.draw.circle(screen, (255, 255, 255), ball_pos, ball_radius)
        # show the survived time
        score_text = font.render(f"Score: {survive_time}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))  # in the top left corner
        pygame.display.flip()

        send_status()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def receive_commands():
    global paddle_speed
    sock.bind(game_address)

    while True:
        data, _ = sock.recvfrom(1024)
        command = data.decode()
        print(f"command received: {command}")

        if command == "^left":
            paddle_speed = -5
        elif command == "^right":
            paddle_speed = 5
        elif command == "^stop":
            paddle_speed = 0


t = Thread(target=receive_commands)
t.daemon = True
t.start()

game_loop()
