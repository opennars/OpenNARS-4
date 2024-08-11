from pynars.Narsese import Sentence
from pynars.NARS.DataStructures._py.Channel import Channel
from pynars.NARS.DataStructures._py.Channel import Buffer
from queue import Queue
from pynars.Narsese import Task
from pynars.Narsese import parser
from pynars.utils.Print import print_out, PrintType

class NarseseChannel(Channel):
    ''''''
    def put(self, text: str):
        try:
            task: Task = parser.parse(text)
        except Exception as e:
            task = None
            return False, None, None
        
        task_overflow = Buffer.put(self, task)
        return True, task, task_overflow
            