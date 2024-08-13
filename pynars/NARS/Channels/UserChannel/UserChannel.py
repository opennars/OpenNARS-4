from pynars.Narsese import Sentence
from pynars.NARS.DataStructures._py.Channel import Channel, NarseseChannel
from pynars.NARS.DataStructures._py.Buffer import Buffer
from queue import Queue
from pynars.Narsese import Task
from pynars.Narsese import parser
from pynars.utils.Print import print_out, PrintType
from typing import List, Tuple
from copy import deepcopy
from pynars import Narsese
from pynars.Narsese import Task
from pathlib import Path
from pynars.NARS.Channels.ConsoleChannel import ConsoleChannel

import sys
from PySide6 import QtWidgets
import qdarkstyle
from .GUI.MainWindow import NARSWindow
from .GUI.Backend import run_nars
from multiprocessing import Process
from qasync import QEventLoop
import asyncio
from time import sleep, time
from as_rpc import AioRpcServer, AioRpcClient, rpc
import threading


class UserChannel(NarseseChannel):
    rpc_servers = {}

    def __init__(self, reasoner, capacity: int, priority_decay: float = 0.4, n_buckets: int = None, take_in_order: bool = False, max_duration: int = None) -> None:
        from pynars.NARS import Reasoner
        self.nars: Reasoner = reasoner
        super().__init__(capacity, n_buckets, take_in_order, max_duration)

        self.priority_decay: float = max(0.0, min(priority_decay, 1.0))

        # def pause(paused: bool = True):
        #     self.nars.paused = paused
        from functools import partial

        if self.nars not in UserChannel.rpc_servers:
            server = AioRpcServer(buff=6553500)
            # print("server root: ", server.root)
            UserChannel.rpc_servers[self.nars] = server
            rpc(server, f"handle_lines")(UserChannel.handle_lines)


            def _on_handshake( client_id, mark):
                channel: UserChannel = server.objs[mark]
                channel.client_id = client_id
            

            server.on_handshake = _on_handshake
            
        server: AioRpcServer = UserChannel.rpc_servers[self.nars]
        server.add_obj(self, id(self))
        # rpc(server, "pause")(pause)


        # self.client_id = client.id



        thread_server = threading.Thread(target=server.run)
        thread_server.setDaemon(True)
        thread_server.start()
        self.client_id = None
        p_gui = Process(target=self.run_gui, args=(id(self),))
        p_gui.start()


    def on_cycle_finished(self):
        tasks = self.nars.get_derived_tasks()
        tasks_strs = self._tasks_to_strs(tasks) if tasks is not None else []
        global_evals = self.nars.get_global_evaluations()
        server: AioRpcServer = UserChannel.rpc_servers[self.nars]
        # def callback(*args):
        #     pass
        server.call_func(self.client_id, "print_out", None, ('\n'.join(
            tasks_strs), [[val] for val in global_evals]))

    def put(self, text: str):
        """
        Parse the text and decay the priority, then put the task into the buffer.
        """
        try:
            task: Task = parser.parse(text)
            task.channel_id = self.channel_id
            task.budget.priority *= self.priority_decay
        except Exception as e:
            task = None
            return False, None, None
        
        task_overflow = Buffer.put(self, task)
        return True, task, task_overflow

    def run_line(self, line: str):
        ''''''
        nars = self.nars

        line = line.strip(' \n')
        if line.startswith("'"):
            return None
        elif line.isdigit():
            n_cycle = int(line)
            for _ in range(n_cycle):
                nars.cycle()
        else:
            line = line.rstrip(' \n')
            if len(line) == 0:
                return
            server: AioRpcServer = UserChannel.rpc_servers[self.nars]
            try:
                success, task, task_overflow = self.put(line)
                if success:
                    server.call_func(self.client_id, "print_out", None, (repr(task), [[] for _ in range(4)]))
                    nars.cycle()
                else:
                    server.call_func(self.client_id, "print_out", None, (f"ERROR : Invalid input! Failed to parse: {line}", [[] for _ in range(4)]))
                    pass

            except Exception as e:
                server.call_func(self.client_id, "print_out", None, (f"ERROR : Unknown error: {line}. \n{e}", [[] for _ in range(4)]))
                pass
    
    def handle_lines(self, lines: str):
        for line in lines.split('\n'):
            if len(line) == 0:
                continue
            self.run_line(line)

    @staticmethod
    def _tasks_to_strs(tasks: Tuple[
            List[Task],
            Task,
            Task,
            List[Task],
            List[Task],
            Tuple[Task, Task]]) -> List[str]:
        ret = []

        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = tasks

        for task in tasks_derived:
            ret.append(repr(task))

        if judgement_revised is not None:
            ret.append(repr(judgement_revised))
        if goal_revised is not None:
            ret.append(repr(goal_revised))
        if answers_question is not None:
            for answer in answers_question:
                ret.append(repr(answer))
        if answers_quest is not None:
            for answer in answers_quest:
                ret.append(repr(answer))
        if task_executed is not None:
            ret.append(
                f'{task_executed.term.repr()} = {str(task_operation_return) if task_operation_return is not None else None}')

        return ret

    @staticmethod
    def run_gui(instance_id: int):
        app = QtWidgets.QApplication(sys.argv)
        loop = QEventLoop(app)

        asyncio.set_event_loop(loop)
        # setup the stylesheet
        app.setStyleSheet(qdarkstyle.load_stylesheet())

        client = AioRpcClient(buff=6553500, mark=instance_id)
        # print("client root: ", client.root/(client.name+'.json'))
        timeout = 10
        t_begin = time()
        while True:
            try:
                client.init()
                break
            except (ConnectionRefusedError, FileNotFoundError) as e:
                t_now = time()
                if t_now - t_begin <= timeout:
                    sleep(1)
                else:
                    raise TimeoutError(
                        "Cannot initialize NARS reasoner properly.")
                
        window = NARSWindow()
        window.set_client(client)
        window.instance_id = instance_id

        @rpc(client, "print_out")
        def print_out(content):
            window.print_out(content)

        # run
        window.show()
        with loop:
            loop.run_forever()
