'''
Configure some hyper-parameters and some other settings via the file `config.json`.
'''
from pathlib import Path

try:
    import jstyleson as json # json with C/C++ style comments
except:
    # import json
    raise "please install the module by `pip install jstyleson`"

class Enable:
    temporal_reasoning = False
    variable = True
    anticipation = False
    operation = False
    debug = False

class Config:
    r_top_level_attention_adjust = 0.5

    priority: float=0.8
    durability: float=0.8
    quality: float=0.5
    num_buckets: int = 100
    max_duration: int = 10000
    f: float=1.0
    c: float=0.9
    c_judgement: float=0.9
    c_goal: float=0.9
    k: int=1
    p_judgement: float=0.8
    d_judgement: float=0.5
    p_question: float=0.9
    d_question: float=0.9
    p_quest: float=0.9
    d_quest: float=0.9
    p_goal: float=0.9
    d_goal: float=0.9
    
    p_feedback: float = 0.9
    d_feedback: float = 0.5

    budget_thresh: float=0.01

    nlevels_task_link: int=10
    capacity_task_link: int=100
    nlevels_term_link: int=10
    capacity_term_link: int=100
    capacity_table: int=100


    quality_min: float=0.3
    cycles_per_duration: int=5
    n_forget_durations: int=2
    cycles_forget = cycles_per_duration*n_forget_durations

    revision_max_occurence_distance: int=10

    truth_epsilon = 0.01
    budget_epsilon = 0.0001

    r_term_complexity_unit = 0.5
    t_sentence_directness_unit = 1.0


    variable_repr_normalized = False

    rate_discount_c = 0.5

    rate_discount_p_internal_exp = 0.1
    rate_discount_d_internal_exp = 0.1

    # parameters for updating the Budget of Concept.
    # Lower values means it is harder to change the budget, higher values means it is easier to change the budget
    concept_update_durability_weight = 0.1
    concept_update_quality_weight = 0.1

    # temporal parameters
    temporal_duration = 5
    n_sequence_attempts = 10
    n_op_condition_attempts = 10

    projection_decay = 0.99
    Td_decision_threshold = 0.51

    # what this value represents was originally equal to the termlink record length (10), but we may want to adjust it or make it scaled according to duration since it has more to do with time than # of records.  it can probably be increased several times larger since each item should remain in the recording queue for longer than 1 cycle
    novelty_horizon = 100000
    term_link_record_length = 10

    maximum_evidental_base_length = 20000

    @classmethod
    def check(cls):
        '''Check if each parameter is valid'''
        pass

    @classmethod
    def apply(cls):
        '''Apply setting values of hyper-parameters'''
        # from pynars.NARS import DataStructures
        # # Budget
        # DataStructures.Budget.priority = cls.priority
        # DataStructures.Budget.durability = cls.durability
        # DataStructures.Budget.quality = cls.quality


def load(file_path: str):

    file_path: Path = Path(file_path)

    valid = True
    if not file_path.exists():
        if Enable.debug:
            print(f"The file `{file_path}` does not exist.")
        valid = False
    if file_path.suffix != '.json':
        if Enable.debug:
            print(f"The file `{file_path}` should be `*.json`.")
        valid = False
    if not valid:
        file_path = Path(__file__).parent/'config.json'
        if Enable.debug:
            print(f'Loaded config file: {file_path}')
    try:
        with open(file_path, 'r') as f:
            content = json.load(f)
    except:
        raise f"Error when openning the file `{file_path}`."
    # set driver mode (py/pyx/cypy/cpp)
    try:
        pass # TODO
    except:
        pass # TODO
    
    # set hyper-parameters
    try:
        defaults: dict = content['HYPER-PARAMS']['DEFAULT']
        budget = defaults.get('BUDGET', None)
        if budget is not None:
            budget: dict
            Config.p_judgement = budget.get('PRIORITY_JUDGEMENT', Config.p_judgement)
            Config.d_judgement = budget.get('DURABILITY_JUDGEMENT', Config.d_judgement)
            Config.p_question = budget.get('PRIORITY_QUESTION', Config.p_question)
            Config.d_question = budget.get('DURABILITY_QUESTION', Config.d_question)
            Config.p_quest = budget.get('PRIORITY_QUEST', Config.p_quest)
            Config.d_quest = budget.get('DURABILITY_QUEST', Config.d_quest)
            Config.p_goal = budget.get('PRIORITY_GOAL', Config.p_goal)
            Config.d_goal = budget.get('DURABILITY_GOAL', Config.d_goal)
            Config.p_feedback = budget.get('PRIORITY_FEEDBACK', Config.p_feedback)
            Config.d_feedback = budget.get('DURABILITY_FEEDBACK', Config.d_feedback)
            Config.budget_thresh = budget.get('THRESHOLD', Config.budget_thresh)

        num_buckets = defaults.get('NUM_BUCKETS', None)
        if num_buckets is not None:
            Config.num_buckets = 100
        truth = defaults.get('TRUTH', None)
        if truth is not None:
            Config.f = truth['FREQUENCY']
            Config.c = truth['CONFIDENCE']
            Config.c_judgement = truth['CONFIDENCE_JUDGEMENT']
            Config.c_goal = truth['CONFIDENCE_GOAL']
            Config.k = truth['K']
        
        max_duration = defaults.get('MAX_DURATION', None)
        if max_duration is not None:
            Config.max_duration = max_duration
        
        concept: dict = defaults.get('CONCEPT', None)
        if concept is not None:
            Config.nlevels_task_link = concept.get('NUM_LEVELS_TASKLINK_BAG', Config.nlevels_task_link)
            Config.capacity_task_link = concept.get('CAPACITY_TASKLINK_BAG', Config.capacity_task_link)
            Config.nlevels_term_link = concept.get('NUM_LEVELS_TERMLINK_BAG', Config.nlevels_term_link)
            Config.capacity_term_link = concept.get('CAPACITY_TERMLINK_BAG', Config.capacity_term_link)
            Config.capacity_table = concept.get('CAPACITY_TABLE', Config.capacity_table)
        Config.r_term_complexity_unit = defaults.get('COMPLEXITY_UNIT', Config.r_term_complexity_unit)
        Config.quality_min = defaults.get('QUALITY_MIN', Config.quality_min)
        Config.cycles_per_duration = defaults.get('CYCLES_PER_DURATION', Config.cycles_per_duration)
        Config.n_forget_durations = defaults.get('NUM_FORGET_DURATIONS', Config.n_forget_durations)
        Config.cycles_forget = Config.cycles_per_duration * Config.n_forget_durations
        Config.revision_max_occurence_distance = defaults.get('REVISION_MAX_OCCURRENCE_DISTANCE', Config.revision_max_occurence_distance)

        Config.rate_discount_c = defaults.get('RATE_DISCOUNT_CONFIDENCE', Config.rate_discount_c)

        Config.rate_discount_p_internal_exp = defaults.get('RATE_DISCOUNT_PRIORITY_INTERNAL_EXPERIENCE', Config.rate_discount_p_internal_exp)
        Config.rate_discount_d_internal_exp = defaults.get('RATE_DISCOUNT_DURABILITY_INTERNAL_EXPERIENCE', Config.rate_discount_d_internal_exp)
        
        hyperparams: dict = content['HYPER-PARAMS']
        Config.truth_epsilon = hyperparams.get('TRUTH_EPSILON', Config.truth_epsilon)
        Config.budget_epsilon = hyperparams.get('BUDGET_EPSILON', Config.budget_epsilon)
        Config.r_term_complexity_unit = hyperparams.get('COMPLEXITY_UNIT', Config.r_term_complexity_unit)
        Config.temporal_duration = hyperparams.get('TEMPORAL_DURATION', Config.temporal_duration)
        Config.n_sequence_attempts = hyperparams.get('TEMPORAL_DURATION', Config.n_sequence_attempts)
        Config.n_op_condition_attempts = hyperparams.get('NUM_OP_CONDITION_ATTEMPTS', Config.n_op_condition_attempts)

        pass # TODO
    except:
        pass # TODO

    Config.check()
    Config.apply()