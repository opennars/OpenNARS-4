import re
from copy import deepcopy
from typing import List, Tuple

import nltk
from nltk.corpus import wordnet as wn

from pynars import Narsese
from pynars.NARS import Reasoner as Reasoner
from pynars.Narsese import Task
from pynars.utils.Print import print_out, PrintType

nltk.download('wordnet')


def convert_util(sentence: str):
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
                ret.append("<" + convert_util(word) + " <-> " + convert_util(each_synonym) + ">.")
                for each_synonym_synset in wn.synsets(each_synonym):
                    synsets.append(each_synonym_synset)  # add to stage 2 processing
                    synset_t = convert_util(each_synonym_synset.name())  # synset term
                    ret.append("<" + synset_t + " --> " + convert_util(each_synonym) + ">.")

    # build links between word and its synsets
    for each_synset in wn.synsets(word):
        synsets.append(each_synset)  # add to stage 2 processing
        synset_t = convert_util(each_synset.name())  # synset term
        ret.append("<" + synset_t + " --> " + convert_util(word) + ">.")

    # stage 2
    # ==================================================================================================================

    for synset in synsets:

        synset_t = convert_util(synset.name())  # synset term

        for each in synset.hypernyms():  # hypernyms
            ret.append("<" + synset_t + " --> " + convert_util(each.name()) + ">.")
        for each in synset.hyponyms():  # hyponyms
            ret.append("<" + convert_util(each.name()) + " --> " + synset_t + ">.")
        for each in synset.instance_hypernyms():  # instance hypernyms
            ret.append("<{" + synset_t + "} --> " + convert_util(each.name()) + ">.")
        for each in synset.instance_hyponyms():  # instance hyponyms
            ret.append("<{" + convert_util(each.name()) + "} --> " + synset_t + ">.")
        for each in synset.member_holonyms():  # member holonyms
            ret.append("<(*," + convert_util(each.name()) + "," + synset_t + ") --> MemberOf>.")
        for each in synset.substance_holonyms():  # substance holonyms
            ret.append("<(*," + convert_util(each.name()) + "," + synset_t + ") --> SubstanceOf>.")
        for each in synset.part_holonyms():  # part holonyms
            ret.append("<(*," + convert_util(each.name()) + "," + synset_t + ") --> PartOf>.")
        for each in synset.member_meronyms():  # member meronyms
            ret.append("<(*," + synset_t + "," + convert_util(each.name()) + ") --> MemberOf>.")
        for each in synset.substance_meronyms():  # substance meronyms
            ret.append("<(*," + synset_t + "," + convert_util(each.name()) + ") --> SubstanceOf>.")
        for each in synset.part_meronyms():  # part meronyms
            ret.append("<(*," + synset_t + "," + convert_util(each.name()) + ") --> PartOf>.")
        for each in synset.attributes():  # attributes
            ret.append("<(&," + convert_util(each.name()) + "," + synset_t + ") --> " + synset_t + ">.")
        for each in synset.entailments():  # entailments
            ret.append("<" + convert_util(each.name()) + " =/> " + synset_t + ">.")
        for each in synset.causes():  # causes
            ret.append("<" + synset_t + " =/> " + convert_util(each.name()) + ">.")
        for each in synset.also_sees():  # also sees
            ret.append("<" + synset_t + " <|> " + convert_util(each.name()) + ">.")
        for each in synset.verb_groups():  # verb groups
            ret.append("<" + synset_t + " <-> " + convert_util(each.name()) + ">.")
        for each in synset.similar_tos():  # similar-to's
            ret.append("<" + synset_t + " <-> " + convert_util(each.name()) + ">.")

        lemmas = synset.lemmas()
        for lemma in lemmas:  # lemmas
            lemma_t = convert_util(lemma.name())
            ret.append("<" + lemma_t + " --> " + synset_t + ">.")
            for antonym in lemma.antonyms():  # antonyms, higher priority
                ret.append("$0.9; 0.9; 0.5$ <" + convert_util(antonym.name()) + " <-> " + lemma_t + ">. %0.0; 0.9%")

    return "\n".join(ret)


def words2narsese(words: list[str]):
    ret = []

    for word in words:
        ret.append(word2narsese(word))

    return "\n".join(ret)


def run_line(nars: Reasoner, line: str):  # PyNARS call
    line = line.strip(' \n')
    if line.startswith("//"):
        return None
    elif line.startswith("''"):
        if line.startswith("''outputMustContain('"):
            line = line[len("''outputMustContain('"):].rstrip("')\n")
            if len(line) == 0: return
            try:
                content_check = Narsese.parser.parse(line)
                # out_print(PrintType.INFO, f'OutputContains({content_check.sentence.repr()})')
            except:
                print_out(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')
        return
    elif line.startswith("'"):
        return None
    elif line.isdigit():
        n_cycle = int(line)
        print_out(PrintType.INFO, f'Run {n_cycle} cycles.')
        tasks_all_cycles = []
        for _ in range(n_cycle):
            tasks_all = nars.cycle()
            tasks_all_cycles.append(deepcopy(tasks_all))
        return tasks_all_cycles
    else:
        line = line.rstrip(' \n')
        if len(line) == 0:
            return None
        try:
            success, task, _ = nars.input_narsese(line, go_cycle=True)
            if success:
                print_out(PrintType.IN, task.sentence.repr(), *task.budget)
            else:
                print_out(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')

            tasks_all = nars.cycle()
            return [deepcopy(tasks_all)]
        except:
            print_out(PrintType.ERROR, f'Unknown error: {line}')


def handle_lines(nars: Reasoner, lines: str):  # PyNARS call
    tasks_lines = []
    for line in lines.split('\n'):
        if len(line) == 0: continue

        tasks_line = run_line(nars, line)
        if tasks_line is not None:
            tasks_lines.extend(tasks_line)

    check_list = set()
    ret = []

    tasks_lines: List[Tuple[List[Task], Task, Task, List[Task], Task, Tuple[Task, Task]]]
    for tasks_line in tasks_lines:
        tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = tasks_line

        for task in tasks_derived:
            if task.term.word not in check_list:
                check_list.add(task.term.word)
                ret.append(task)

        if judgement_revised is not None:
            if judgement_revised.term.word not in check_list:
                check_list.add(judgement_revised.term.word)
                ret.append(judgement_revised)

        if goal_revised is not None:
            if goal_revised.term.word not in check_list:
                check_list.add(goal_revised.term.word)
                ret.append(goal_revised)

        if answers_question is not None:
            for answer in answers_question:
                if answer.term.word not in check_list:
                    check_list.add(answer.term.word)
                    ret.append(answer)

        if answers_quest is not None:
            for answer in answers_quest:
                if answer.term.word not in check_list:
                    check_list.add(answer.term.word)
                    ret.append(answer)

    return ret


def result_filtering(reasoning_results):
    # find positive/negative judgments
    pos = []
    neg = []

    for each in reasoning_results:
        if each.truth.f > 0.9:
            pos.append(each)
        elif each.truth.f < 0.1:
            neg.append(each)

    return pos, neg


def next_rank(base, reasoning_results, lower_ranks):
    """
    If we have a sentence <A --> B>., and if we call A (or B) the rank_i term, then B (or A) is the rank_i+1 term.
    "RANK" represents how many sentences are needed.
    If two same terms are of different ranks, the smaller rank will be chosen.
    :param base: dic
    :param reasoning_results: list[Task]
    :param lower_ranks: list[dic]
    :return: dic
    """
    rkn = {}
    for each_result in reasoning_results:
        words = [each.word.replace("\"", "") for each in each_result.term.terms]  # get sub-terms
        for i, word in enumerate(words):
            # if a sub-term is in the base, then all remaining sub-terms will be rank_next terms
            if word in base:
                for j in range(len(words)):
                    if j == i:
                        continue
                    elif words[j] in rkn:
                        rkn[words[j]] = [rkn[words[j]][0] + 1, (rkn[words[j]][1] + each_result.truth.e) / 2]
                    else:
                        rkn.update({words[j]: [1, each_result.truth.e]})
    tmp = deepcopy(rkn)
    for each in rkn:
        if rkn[each][0] < 3:
            tmp.pop(each)
            continue
        for lower_rank in lower_ranks:
            if each in lower_rank:
                tmp.pop(each)
                break
    return tmp


def term2nl_util(term, ret):
    if term[0] != "(":
        if "." not in term:
            return ret.union({term})
        else:
            return ret.union({wn.synset(term).definition()})
    else:
        sub_terms = term[4:-1].split(", ")
        for sub_term in sub_terms:
            ret = ret.union(term2nl_util(sub_term, ret))

    return ret


def term2nl(term, connector=None):
    if connector is not None:
        components = term2nl_util(term, set())
        return connector.join(components)
    else:
        return list(term2nl_util(term, set()))[0]


def terms2nl(terms):
    ret = []
    for term in terms:
        try:
            if term[1] == "&":
                ret.append(term2nl(term, " and "))
            elif term[1] == "|":
                ret.append(term2nl(term, " or "))
            else:
                ret.append(term2nl(term))
        except:
            continue
    return ret


if __name__ == "__main__":
    # some compound words cannot be found in wordnet directly, but can also be represented by NARS
    # e.g., "car accident", (&, car, accident)

    narsese = words2narsese(["abuse",
                             "burglary",
                             "robbery",
                             "stealing",
                             "shooting",
                             "shoplifting",
                             "assault",
                             "fighting",
                             "arson",
                             "explosion",
                             "arrest",
                             "car",
                             "accident",
                             "vandalism",
                             "normal",
                             "event"])

    original_labels = {"abuse": [1, 0.9],
                       "burglary": [1, 0.9],
                       "robbery": [1, 0.9],
                       "stealing": [1, 0.9],
                       "shooting": [1, 0.9],
                       "shoplifting": [1, 0.9],
                       "assault": [1, 0.9],
                       "fighting": [1, 0.9],
                       "arson": [1, 0.9],
                       "explosion": [1, 0.9],
                       "arrest": [1, 0.9],
                       "(&, car, accident)": [1, 0.9],
                       "(&, accident, car)": [1, 0.9],
                       "vandalism": [1, 0.9],
                       "(&, normal, event)": [1, 0.9],
                       "(&, event, normal)": [1, 0.9]}

    nars = Reasoner(100000, 100000)

    reasoning_results = handle_lines(nars, narsese + "\n1000")

    pos, neg = result_filtering(reasoning_results)

    rk1 = next_rank(original_labels, pos, [original_labels])
    A = sorted([[each, rk1[each][0], rk1[each][1]] for each in rk1], key=lambda x: x[2], reverse=True)
    rk2 = next_rank(rk1, pos, [original_labels, rk1])
    rk3 = next_rank(rk2, pos, [original_labels, rk1, rk2])

    print(1)

    # pos_terms = rk1.union(*[rk2, rk3])
    # pos_scores = sorted(terms_score(pos_terms, pos), key=lambda x: x[1], reverse=True)[:400]
    # pos_terms = set([each[0] for each in pos_scores])
    #
    # neg_terms = next_rank(original_labels.union(pos_terms), neg, original_labels.union(pos_terms))
    #
    # pos_labels = terms2nl(pos_terms)
    # neg_labels = terms2nl(neg_terms)
    #
    # print("pos labels: ", pos_labels)
    # print("========")
    # print("neg labels: ", neg_labels)
    #
    # with open("expanded labels ExAll pos.txt", "w") as file:
    #     for each in pos_labels:
    #         file.write(each + "\n")
    #
    # with open("expanded labels ExAll neg.txt", "w") as file:
    #     for each in neg_labels:
    #         file.write(each + "\n")
