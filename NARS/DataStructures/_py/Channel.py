from Narsese import Sentence
from .Buffer import Buffer
from queue import Queue
from Narsese import Task
from Narsese import parser
from utils.Print import out_print, PrintType

class Channel(Buffer):
    ''''''

class NarseseChannel(Channel):
    ''''''
    def put(self, text: str):
        try:
            task: Task = parser.parse(text)
        except:
            task = None
            return False, None, None
        
        task_overflow = Buffer.put(self, task)
        return True, task, task_overflow
    
    def take(self) -> Sentence:
        return Buffer.take_max(self, remove=True)
            
            
    