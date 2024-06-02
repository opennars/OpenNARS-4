import random
import socket
import sys
from threading import Thread

import pygame

# initialize pygame
pygame.init()

# game canvas
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

"""
For NARS, the game is run independently. It is very likely that in the game, the ball runs one frame, but NARS has read 
this frame dozens of times. Adjust the overall movement speed to solve this problem.
"""
ball_speed_augment = 1

# default variables
ball_speed_x = random.choice([1, -1]) * random.randint(2 * ball_speed_augment, 4 * ball_speed_augment)
ball_speed_y = -random.randint(2 * ball_speed_augment, 4 * ball_speed_augment)
paddle_speed = 0  # paddle initial speed, 0 := not moving
paddle_width = 100
paddle_height = 20
ball_radius = 10
ball_pos = [screen_width // 2, screen_height // 2]
paddle_pos = [screen_width // 2 - paddle_width // 2, screen_height - paddle_height]
font = pygame.font.Font(None, 36)

# game score, for display
survive_time = 0

"""
The socket is used to establish communication between NARS and the game, and as expected, NARS will also use the exact 
same method to print content to the UI.
"""
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
game_address = ("localhost", 12345)
control_address = ("localhost", 54321)


def reset_game():
    global ball_pos, ball_speed_x, ball_speed_y, paddle_pos, paddle_speed
    ball_pos = [screen_width // 2, screen_height // 2]
    ball_speed_x = random.choice([1, -1]) * random.randint(2 * ball_speed_augment, 4 * ball_speed_augment)
    ball_speed_y = -random.randint(2 * ball_speed_augment, 4 * ball_speed_augment)
    paddle_pos = [screen_width // 2 - paddle_width // 2, screen_height - paddle_height]
    paddle_speed = 0


def send_status(message=None):
    """
    In this game, information is sent to NARS every frame, describing: 1) the position of the ball relative to the
    paddle, and 2) whether the current situation is satisfactory.

    Each message is just a string.
    Messages are separated by "|".
    """
    if message is None:

        if ball_pos[0] < paddle_pos[0]:
            msg_1 = "<{left} --> [on]>. %1;0.9%"
            # sock.sendto(msg.encode(), control_address)
            msg_2 = "<{SELF} --> [good]>. %" + str(
                1 - (paddle_pos[0] - ball_pos[0]) / (screen_width - paddle_width)) + ";0.9%"
            sock.sendto((msg_1 + "|" + msg_2).encode(), control_address)
        elif ball_pos[0] > paddle_pos[0] + paddle_width:
            msg_1 = "<{right} --> [on]>. %1;0.9%"
            # sock.sendto(msg.encode(), control_address)
            msg_2 = "<{SELF} --> [good]>. %" + str(
                1 - (ball_pos[0] - (paddle_pos[0] + paddle_width)) / (screen_width - paddle_width)) + ";0.9%"
            sock.sendto((msg_1 + "|" + msg_2).encode(), control_address)
        else:
            msg = "<{SELF} --> [good]>. %1;0.9%"
            sock.sendto(msg.encode(), control_address)


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
            ball_speed_y = -ball_speed_y

        # game failed
        if ball_pos[1] >= screen_height:
            send_status("GAME FAILED")
            survive_time = 0
            reset_game()  # restart

        # update paddle
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
            paddle_speed = -5 * ball_speed_augment
        elif command == "^right":
            paddle_speed = 5 * ball_speed_augment
        elif command == "^stop":
            paddle_speed = 0


if __name__ == "__main__":
    t = Thread(target=receive_commands)
    t.daemon = True
    t.start()

    game_loop()
