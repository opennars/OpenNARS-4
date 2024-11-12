from pynars.Narsese import Sentence
from .Buffer import Buffer
from queue import Queue
from pynars.Narsese import Task
from pynars.Narsese import parser
from pynars.utils.Print import print_out, PrintType

class Channel(Buffer):
    ''''''
    def put(self, task: Task):
        task_overflow = Buffer.put(self, task)
        return task_overflow
    
    def take(self) -> Sentence:
        return Buffer.take_max(self, remove=True)

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
            
            
    