from pynars.NARS.DataStructures.MC.EventBuffer import EventBuffer
from pynars.NARS.DataStructures.MC.Utils import PriorityQueue
from pynars.Narsese import parser


class SensorimotorChannel:

    def __init__(self, ID, num_slot, num_events, num_anticipations, num_operations, num_predictive_implications,
                 num_reactions, N=1):
        self.ID = ID
        """
        The name "input buffer" might be a bit misleading, since there are no corresponding "output buffer" in a
        channel, but this is the name in the conceptual design.
        """
        self.input_buffer = EventBuffer(num_slot, num_events, num_anticipations, num_operations,
                                        num_predictive_implications, N)
        self.reactions = PriorityQueue(num_reactions)
        self.num_reactions = num_reactions
        self.operations = {}
        """
        Vocabularies are the terms used by operations in this channel. 
        Keeping a record of them for unregistering operations.
        And also to check whether some commands sent by the reasoner are consistent with this channel.
        """
        self.vocabulary = {}
        self.function_vocabulary = {}

    def register_operation(self, name, function, vocabulary):
        # name := str
        self.operations[name] = function
        self.function_vocabulary[name] = vocabulary
        for each in vocabulary:
            self.vocabulary[each] = self.vocabulary.get(each, 0) + 1

    def unregister_operation(self, name):
        self.operations.pop(name)
        for each in self.function_vocabulary[name]:
            if each in self.vocabulary:
                self.vocabulary[each] -= 1
                if self.vocabulary[each] <= 0:
                    del self.vocabulary[each]

    def information_gathering(self):
        """
        Define how this channel gathers information outside NARS, and how such information is turned into Narsese
        sentences.
        """
        return []

    def identify(self, terms):
        """
        Check whether terms can be produced from this channel. Return True if yes, False if no.
        """
        for each in terms:
            if each.word not in self.vocabulary:
                return False
        return True

    @staticmethod
    def reaction_evaluation(reaction, memory):
        """
        Reactions are created by some goals. If the goal is still needed, the reaction is needed, and vice versa.
        """

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # this means there are reactions with no corresponding goals
        # ==============================================================================================================
        if reaction.goal is None:
            return 0.7
        # ==============================================================================================================

        concept = memory.take_by_key(reaction.goal.term, False)
        if concept is not None:
            return concept.budget.priority
        return 0

    def add_reaction(self, reaction):
        self.reactions.push(reaction, reaction.goal.budget.priority)

    def babbling(self):
        return []

    def channel_cycle(self, memory):
        """
        Get input information (Narsese or the other form) from the outside environment (mostly via RPC)

        1. Get the inputs from the environment and check them against the reactions, apply the one with the highest
            priority. If there are no applicable reactions, babbling if wanted.
            Babbling is not a reaction.

            It looks like reactions only consider atomic inputs, but this can be further extended by letting some
            specific compositions be generated in advance.

        2. Everything is then sent to the input buffer for the next level.
        """

        reactions = PriorityQueue(self.num_reactions)
        # re-evaluate all reactions at the beginning of each cycle
        while len(self.reactions) != 0:
            reaction, _ = self.reactions.pop()
            reactions.push(reaction, self.reaction_evaluation(reaction, memory))
        self.reactions = reactions

        # get the input
        inputs = self.information_gathering()

        # if there are some operations
        has_operation = False
        if len(self.reactions) != 0:
            reaction_to_use, _ = self.reactions.pop()
            if inputs is not None:
                for each_input in inputs:
                    tmp = reaction_to_use.fire(each_input)
                    if tmp is not None:
                        self.operations[tmp]()
                        has_operation = True
                        inputs.append(tmp)
                    break

        # babbling
        if not has_operation:
            operation_from_babbling = self.babbling()
            if operation_from_babbling is not None:
                self.operations[operation_from_babbling]()
                inputs.append(parser.parse(operation_from_babbling + "."))

        print("input_from_environment", inputs)

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        reactions, ret = self.input_buffer.buffer_cycle(inputs, memory)
        for each in reactions:
            self.reactions.push(each, self.reaction_evaluation(each, memory))
        return ret
        # ==============================================================================================================
        # original
        # return self.input_buffer.buffer_cycle(inputs, memory)
        # ==============================================================================================================
