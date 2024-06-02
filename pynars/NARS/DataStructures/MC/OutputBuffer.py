from pynars.Narsese import Compound


class Reaction:

    def __init__(self, condition, operation, goal):
        self.condition = condition
        self.operation = operation
        self.goal = goal

    def fire(self, task):
        if task.term == self.condition:
            return self.operation


class OutputBuffer:
    """
    Output buffer is the bridge from NARS reasoner to all outside parts.
    You may think the output buffer is the translator for the reasoner.
    There are many "input buffers", but there is only one output buffer.
    """

    def __init__(self, Narsese_channel):
        # usually, a Narsese channel is necessary for the system (for user inputs and display outputs of reasoning)
        self.Narsese_channel = Narsese_channel

    def buffer_cycle(self, tasks, sensorimotor_channels):
        """
        Get the derived tasks and send them to the corresponding channels as outputs.
        It can be sent to the Narsese Chanel for display in the console, or it can be sent to the corresponding
        sensorimotor channels for operation execution.
        """

        # put all derived things to the Narsese channel to display
        self.Narsese_channel.display(tasks)
        # convert sub-goals and send to the corresponding channels (if any)
        for each_task in tasks:
            if each_task.is_goal:

                if each_task.term.is_compound and each_task.term.components[-1].word[0] == "^":
                    for each_channel in sensorimotor_channels:
                        if sensorimotor_channels[each_channel].identify(each_task.term.components):

                            condition = None
                            operation = None

                            if each_task.term.connector == "Connector.ParallelEvents":
                                condition = Compound.ParallelEvents(*each_task.term.components[:-1])
                                operation = each_task.term.components[-1]
                            elif each_task.term.connector == "Connector.ParallelEvents":
                                condition = Compound.SequentialEvents(*each_task.term.components[:-1])
                                operation = each_task.term.components[-1]

                            if condition is not None and operation is not None:
                                sensorimotor_channels[each_channel].add_reaction(Reaction(condition, operation,
                                                                                          each_task))
