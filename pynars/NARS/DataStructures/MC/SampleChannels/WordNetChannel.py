"""
Compatible with BufferMC.

ChannelMC (the old one) class is kept there for further changes.
"""
import re

from nltk.corpus import wordnet as wn

from pynars.Narsese import parser


def convert_util(sentence: str):
    if len(re.findall("[a-zA-Z0-9]+", sentence)) == 1:
        return sentence
    else:
        return "\"" + sentence + "\""


def word2narsese(word: str):
    """
    Two stages:
    1) pre-synset processing: build links between i) word and its own synsets, ii) word and its synonyms, iii) word's
    synonyms and their synsets
    2) synset processing: build links between i) synset and its related synsets, ii) synset and its lemmas, iii)
    lemmas with their antonyms (with a higher priority)
    :return: list[str]
    """

    ret = []

    # stage 1
    # ==================================================================================================================

    synsets = []  # for stage 2 processing

    synonyms = wn.synonyms(word)  # get synonyms first, they are word-level (not give in synsets)
    # build links between word and its synonyms
    for synonym in synonyms:
        if len(synonym) != 0:
            for each_synonym in synonym:
                # synonym
                ret.append(parser.parse("<" + convert_util(word) + " <-> " + convert_util(each_synonym) + ">."))
                for each_synonym_synset in wn.synsets(each_synonym):
                    synsets.append(each_synonym_synset)  # add to stage 2 processing
                    synset_t = convert_util(each_synonym_synset.name())  # synset term
                    ret.append(parser.parse("<" + synset_t + " --> " + convert_util(each_synonym) + ">."))

    # build links between word and its synsets
    for each_synset in wn.synsets(word):
        synsets.append(each_synset)  # add to stage 2 processing
        synset_t = convert_util(each_synset.name())  # synset term
        ret.append(parser.parse("<" + synset_t + " --> " + convert_util(word) + ">."))

    # stage 2
    # ==================================================================================================================

    for synset in synsets:

        synset_t = convert_util(synset.name())  # synset term

        for each in synset.hypernyms():  # hypernyms
            ret.append(parser.parse("<" + synset_t + " --> " + convert_util(each.name()) + ">."))
        for each in synset.hyponyms():  # hyponyms
            ret.append(parser.parse("<" + convert_util(each.name()) + " --> " + synset_t + ">."))
        for each in synset.instance_hypernyms():  # instance hypernyms
            ret.append(parser.parse("<{" + synset_t + "} --> " + convert_util(each.name()) + ">."))
        for each in synset.instance_hyponyms():  # instance hyponyms
            ret.append(parser.parse("<{" + convert_util(each.name()) + "} --> " + synset_t + ">."))
        for each in synset.member_holonyms():  # member holonyms
            ret.append(parser.parse("<(*," + convert_util(each.name()) + "," + synset_t + ") --> MemberOf>."))
        for each in synset.substance_holonyms():  # substance holonyms
            ret.append(parser.parse("<(*," + convert_util(each.name()) + "," + synset_t + ") --> SubstanceOf>."))
        for each in synset.part_holonyms():  # part holonyms
            ret.append(parser.parse("<(*," + convert_util(each.name()) + "," + synset_t + ") --> PartOf>."))
        for each in synset.member_meronyms():  # member meronyms
            ret.append(parser.parse("<(*," + synset_t + "," + convert_util(each.name()) + ") --> MemberOf>."))
        for each in synset.substance_meronyms():  # substance meronyms
            ret.append(parser.parse("<(*," + synset_t + "," + convert_util(each.name()) + ") --> SubstanceOf>."))
        for each in synset.part_meronyms():  # part meronyms
            ret.append(parser.parse("<(*," + synset_t + "," + convert_util(each.name()) + ") --> PartOf>."))
        for each in synset.attributes():  # attributes
            ret.append(parser.parse("<(&," + convert_util(each.name()) + "," + synset_t + ") --> " + synset_t + ">."))
        for each in synset.entailments():  # entailments
            ret.append(parser.parse("<(*," + convert_util(each.name()) + "," + synset_t + ") --> After>."))
        for each in synset.causes():  # causes
            ret.append(parser.parse("<(*," + synset_t + "," + convert_util(each.name()) + ") --> After>."))
        for each in synset.also_sees():  # also sees
            ret.append(parser.parse("<(*," + synset_t + "," + convert_util(each.name()) + ") --> SameTime>."))
        for each in synset.verb_groups():  # verb groups
            ret.append(parser.parse("<" + synset_t + " <-> " + convert_util(each.name()) + ">."))
        for each in synset.similar_tos():  # similar-to's
            ret.append(parser.parse("<" + synset_t + " <-> " + convert_util(each.name()) + ">."))

        lemmas = synset.lemmas()
        for lemma in lemmas:  # lemmas
            lemma_t = convert_util(lemma.name())
            ret.append(parser.parse("<" + lemma_t + " --> " + synset_t + ">."))
            for antonym in lemma.antonyms():  # antonyms, higher priority
                ret.append(parser.parse(
                    "$0.9; 0.9; 0.5$ <" + convert_util(antonym.name()) + " <-> " + lemma_t + ">. %0.0; 0.9%"))

    return ret


class WordNetChannel:

    def __init__(self, ID, buffer):
        self.ID = ID
        self.buffer = buffer

    def WordNetQuery(self, task=None):
        """
        Query WordNet with a single natural language word. Can be an empty query, if so, then it will pop previous
        remaining queries.
        """
        tasks = []
        if task is not None and task.is_goal:

            try:
                """
                Something is wrong with the variable related functionalities.
                Here is a relatively fixed format extracting the query word.
                """
                query_word = \
                    [x.word for x in task.term.subject.sub_terms if
                     x.word != "WordNet" and x.word != task.term.subject.word][0]
                tasks = word2narsese(query_word)
            except:
                tasks = []

        return self.buffer.buffer_cycle(tasks)
