import random
from threading import Thread

from pynars import Narsese
from pynars.NARS import Reasoner
from pynars.NARS.DataStructures import EventBuffer
import socket

from pynars.Narsese import Task

# reasoner
nars = Reasoner(1000, 1000)

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
control_address = ("localhost", 54321)
game_address = ("localhost", 12345)

# EB
capacity = 5
event_buffer: EventBuffer = EventBuffer(capacity=capacity)

# clock
stamp = 0


def create_task_util(s):
    global stamp
    task: Task = Narsese.parser.parse(s)
    task.stamp.t_occurrence = stamp
    stamp += 1
    return task


def receive_status():
    global event_buffer
    sock.bind(control_address)
    while True:
        data, _ = sock.recvfrom(1024)
        status = data.decode()
        print(f"game state received: {status}")
        if status != "GAME FAILED":
            event_buffer.put(create_task_util(status))


def send_commands(command: str):
    sock.sendto(command.encode(), game_address)


if __name__ == "__main__":
    t = Thread(target=receive_status)
    t.start()

    # NARS cycle
    limit = 1000000
    count = -1

    while True:

        count += 1

        if count > limit:
            break

        task_from_EB = event_buffer.generate_temporal_sentences()
        if len(task_from_EB) != 0:
            nars.input_narsese(str(task_from_EB[0]))

        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = nars.cycle()

        for each in tasks_derived:
            if each.is_goal and each.term in ["^left", "^right", "^stop"]:
                send_commands(each.term)

        # motor babbling
        if random.random() > 0.8 and count < 2000:  # 20% chance
            opt = random.choice(["^left", "^right", "^stop"])
            event_buffer.put(create_task_util(opt + "."))
            send_commands(opt)
            print("!")
