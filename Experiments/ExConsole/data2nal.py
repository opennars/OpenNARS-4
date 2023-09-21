'''Data to NAL
Define a format for converting Python data structures to Narsese
Core function: <Python data structure>→<NAL **text**>
'''
from pynars.Narsese import Punctuation
from pynars.Narsese import parser
# pynars

# Constants #


def SIGN_TYPE_NAMES(type): return type.__name__


# {1,2,3}
SIGN_RELATION_BELONG: str = 'belong'
# [1,2,3]
SIGN_RELATION_OBJ_ITEM_VALUE: str = 'obj_item_value'
# {a: 1, b: 2}
SIGN_RELATION_OBJ_PROPERTY_VALUE: str = 'obj_property_value'

# Utils #

# Preset identification


def isBasicType(obj: any) -> bool:
    '''Determining whether a type is an "immutable type"
    Note: Strings are counted'''
    t = type(obj)
    return obj == None or t == bool or t == int or t == float or t == str


def verifyTermName(name: str) -> str | None:
    try:
        return (
            name
            if parser.parse(text=f'< {name} --> {name} >.')
            else None)
    except:
        return None

# term construction


def termRel(A: str, B: str) -> str:
    '''Construct the term "Relationship between A and B"'''
    return f'(*,{A},{B})'


def termName(A: any) -> str:
    '''Build term "object name"'''
    t: type = type(A)
    # test whether the object can be directly accepted as a lexical item, if it is attached, if not, no
    instanceWrapper: str = '%s' if isBasicType(A) else '{%s}'
    # first format encapsulation: Fill "class name _ value /id"
    initName: str = verifyTermName(f'{t.__name__}_{str(A)}')
    # check: Whether the filled term is valid (cause: the array "first pass, second fail" problem)
    initName = verifyTermName(
        initName if initName else f'{t.__name__}_{id(A)}')
    # second format encapsulation: Specifies whether an instance term is required
    finalName: str = instanceWrapper % initName
    # return
    return finalName

# sentence construction


def sentenceInh(A: str, B: str, punct: Punctuation | str = Punctuation.Judgement) -> str:
    '''Building relationships "A is B"'''
    return f'<{A} --> {B}>{punct.value if isinstance(punct,Punctuation) else punct}'  # <A --> B> default with "."


def sentenceRel(A: str, r: str, B: str, punct: Punctuation = Punctuation.Judgement) -> str:
    '''Construct relation "ArB" i.e. "The relation between A and B" is r"'''
    return sentenceInh(termRel(A, B), f'{r}', punct=punct)  # <(*,A,B) --> r>. The "relationship" between A and B is r


def sentenceTypeSign(name: str, type: type, punct: Punctuation = Punctuation.Judgement) -> str:
    '''Name the name based on the type of the object'''
    return sentenceInh(name, SIGN_TYPE_NAMES(type), punct=punct)  # name --> type


def sentenceTriRel(obj: str, key: str, value: str, relation: str = SIGN_RELATION_OBJ_PROPERTY_VALUE,
                   punct: Punctuation = Punctuation.Judgement) -> str:
    '''Building a ternary relationship "Object [key] = value"
    Example: (*,{object},(*,{attribute},{value})) --> objectAttributeValue
    '''
    return sentenceRel(obj, relation, termRel(key, value), punct=punct)  # (*,{obj},(*,{key},{value})) --> relation

# Main conversion module #

# basic


# Use kwargs to automatically pass "punctuation" information
def none2NAL(n: None, specialName: str, **kwargs) -> list[str]:
    '''None to NAL'''
    return [sentenceTypeSign(specialName, type(n), **kwargs)]


def bool2NAL(b: str, specialName: str, **kwargs) -> list[str]:
    '''boolean to NAL'''
    result: list[str] = [sentenceTypeSign(
        specialName, bool, **kwargs)]  # preset type identification
    return result


def int2NAL(i: int, specialName: str, **kwargs) -> list[str]:
    '''Integer to NAL
        TODO: Build an integer system'''
    result: list[str] = [sentenceTypeSign(
        specialName, int, **kwargs)]  # preset type identification
    return result


def float2NAL(f: float, specialName: str, **kwargs) -> list[str]:
    '''Floating-point number becomes NAL
    TODO: Build a floating point number system and combine it with an integer system'''
    result: list[str] = [sentenceTypeSign(
        specialName, float, **kwargs)]  # preset type identification
    return result


def str2NAL(s: str, specialName: str, **kwargs) -> list[str]:
    '''Set to NAL
    TODO: How does distinguish between "name" and "value" of a string?'''
    # tests whether a string can be directly accepted as a term, appended if it is, unappended if it is not
    # Try to use the string itself as a name for easy identification
    finalName = verifyTermName(s)
    finalName: str = specialName + \
        (f'「{s}」' if finalName else '')  # Include itself if you can, do not add information otherwise
    # preset type identification
    result: list[str] = [sentenceTypeSign(finalName, str, **kwargs)]
    return result

# containers


def set2NAL(s: set, specialName: str, **kwargs) -> list[str]:
    '''Set to NAL
    Use the relative item "belong"
    Import a collection name as the concept name, and then convert all elements within it to NAL
    Return: A list of multiple NAL statements (easy to split)'''
    result: list[str] = [sentenceTypeSign(
        specialName, set, **kwargs)]  # preset type identification
    for item in s:  # TODO: Implementing recursive logic @auto2NAL(item)
        result.append(sentenceRel(termName(item),
                      SIGN_RELATION_BELONG, specialName, **kwargs))
    return result


def lisTuple2NAL(array: list | tuple, specialName: str, **kwargs) -> list[str]:
    '''List/tuple to NAL: Lists whose keys are integers'''
    result: list[str] = [sentenceTypeSign(
        specialName, type(array), **kwargs)]  # preset type identification
    for i in range(len(array)):
        # get element
        item: any = array[i]
        iName: str = termName(i)
        itemName: str = termName(item)
        # pre-add definitions for keys and values
        result.extend(auto2NAL(item, itemName, **kwargs))
        result.extend(auto2NAL(i, iName, **kwargs))
        # bind objects, keys, and values
        result.append(sentenceTriRel(
            specialName,
            iName,
            itemName,
            **kwargs))  # list[integerIndex] = value
    return result


def dict2NAL(d: dict, specialName: str, **kwargs) -> list[str]:
    '''dict to NAL
    #! In fact, JSON is a dictionary, to achieve the dictionary↔NAL conversion, which is equivalent to NARS can read JSON
    TODO models dictionaries using an index system'''
    result: list[str] = [sentenceTypeSign(
        specialName, dict, **kwargs)]  # preset type identification
    for key, value in d.items():
        keyName: str = termName(key)
        valueName: str = termName(value)
        # pre-add definitions for keys and values
        result.extend(auto2NAL(key, keyName, **kwargs))
        result.extend(auto2NAL(value, valueName, **kwargs))
        # bind objects, keys, and values
        result.append(sentenceTriRel(
            specialName,
            keyName,
            valueName,
            **kwargs))  # dictionary[immutableDataIndex] = value
    return result


def type2NAL(t: type, specialName: str, **kwargs) -> list[str]:
    '''Type to NAL
    The "type" itself also needs to become NAL'''
    return [sentenceTypeSign(specialName, type, **kwargs)]  # only type notations

# default values


def default2NAL(obj: any, specialName: str, **kwargs) -> list[str]:
    '''Other objects become NAL
    Temporarily occupy the one place, will later be separated from many types'''
    print(f'WARNING: unsupported object {obj} with type {type(obj)}')
    # only type notations
    return [sentenceTypeSign(specialName, type, **kwargs)]

# Main function: Integrate all parts #


CONVERT_FUNCTIONS: dict[type:any] = {
    type(None): none2NAL,
    int: int2NAL,
    float: float2NAL,
    bool: bool2NAL,
    str: str2NAL,
    list: lisTuple2NAL,
    tuple: lisTuple2NAL,
    set: set2NAL,
    dict: dict2NAL,
    type: type2NAL,
    None: default2NAL,
}


def auto2NAL(obj: any, name: str = None, punct: Punctuation = Punctuation.Judgement) -> list[str]:
    '''Function integration: Python object →NAL statement sequence
    Automatically identify the object type and call the corresponding conversion function'''
    # get name
    # If no, automatically generate
    name = name if name else termName(obj)
    # get type
    t = type(obj)
    # select & Generate, with default values (all parameters must accept a "Narsese parsed name")
    narsSentences: list[str] = CONVERT_FUNCTIONS.get(
        t, CONVERT_FUNCTIONS[None])(obj, name, punct=punct)
    # verify
    for sentence in narsSentences:
        parser.parse(sentence)
    # return
    return narsSentences
