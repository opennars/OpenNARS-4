from pynars.NARS import Reasoner
from pynars.NARS.DataStructures.MC.Buffer import Buffer
from pynars.Narsese import parser
from pynars.utils.Print import print_out, PrintType


class NarseseChannel:

    def __init__(self, size, N=1, D=0.9):
        self.input_buffer = Buffer(size, N, D)

    def channel_cycle(self, line, memory):
        """
        Print out: 1) what is input (to the channel, not to the memory or the reasoner);
        2) what the system wants to print.
        """
        if not line.isdigit():
            try:
                task = parser.parse(line)
                print_out(PrintType.IN, task.sentence.repr(), *task.budget)
                self.input_buffer.add([task], memory)
            except:
                print_out(PrintType.ERROR, f"Invalid input! Failed to parse: {line}")
        else:
            print_out(PrintType.INFO, f'Run {int(line)} cycles.')

        return self.input_buffer.select()

    @staticmethod
    def display(tasks):
        for each in tasks:
            print_out(PrintType.OUT, f"{each.sentence.repr()} {str(each.stamp)}", *each.budget)


if __name__ == "__main__":
    r = Reasoner(100, 100)
    m = r.memory
    c = NarseseChannel(10)
    c.display([parser.parse("<A --> X>.")])
    print(c.channel_cycle("<A --> B>", m))
    print(c.channel_cycle("<A --> B>.", m))
