'''
# Data to Narsese

Define a format for converting Python data structures to Narsese
Core function: <Python data structure>→<Narsese **text**>

# Example

## A Simple Translation

```
Please input your Python object: {"a":1}
Please enter a name for this object (leave blank for automatic generation): a       
Please enter your modality for the object (./?/!) (Leave blank default.): 
Input object: {'a': 1}
Narsese:
<a --> dict>.
<str_a__a --> str>.
<int_1 --> int>.
<(*, a, str_a, int_1) --> obj_property_value>.
```

## Some complex example uses nearly full JSON

```
Please input your Python object: {"description": "This is an object", "list": [1,2,3.0], "tuple": (True, False), "set": {None,}} 
Please enter a name for this object (leave blank for automatic generation): my_object 
Please enter your modality for the object (./?/!) (Leave blank default.): .
verify_term_name: failed to verify term name "str_This is an object", skipped...
verify_term_name: failed to verify term name "This is an object", skipped...
verify_term_name: failed to verify term name "list_[1, 2, 3.0]", skipped...
verify_term_name: failed to verify term name "float_3.0", skipped...
verify_term_name: failed to verify term name "set_{None}", skipped...
Input object: {'description': 'This is an object', 'list': [1, 2, 3.0], 'tuple': (True, False), 'set': {None}}
Narsese:
<my_object --> dict>.
<str_description__description --> str>.
<str_1995411977392 --> str>.
<(*, my_object, str_description, str_1995411977392) --> obj_property_value>.
<str_list__list --> str>.
<{list_1995399980096} --> list>.
<int_1 --> int>.
<int_0 --> int>.
<(*, {list_1995399980096}, int_0, int_1) --> obj_property_value>.
<int_2 --> int>.
<int_1 --> int>.
<(*, {list_1995399980096}, int_1, int_2) --> obj_property_value>.
<float_1995376564784 --> float>.
<int_2 --> int>.
<(*, {list_1995399980096}, int_2, float_1995376564784) --> obj_property_value>.
<(*, my_object, str_list, {list_1995399980096}) --> obj_property_value>.
<str_tuple__tuple --> str>.
<{tuple_(True, False)} --> tuple>.
<bool_True --> bool>.
<int_0 --> int>.
<(*, {tuple_(True, False)}, int_0, bool_True) --> obj_property_value>.
<bool_False --> bool>.
<int_1 --> int>.
<(*, {tuple_(True, False)}, int_1, bool_False) --> obj_property_value>.
<(*, my_object, str_tuple, {tuple_(True, False)}) --> obj_property_value>.
<str_set__set --> str>.
<{set_1995373733568} --> set>.
<(*, NoneType_None, {set_1995373733568}) --> belong>.
<(*, my_object, str_set, {set_1995373733568}) --> obj_property_value>.
```

'''  # compatible type annotation
from typing import List, Dict, Tuple, Union


from opennars.Narsese import Punctuation
from opennars.Narsese import parser
# opennars

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


def is_basic_type(obj: any) -> bool:
    '''Determining whether a type is an "immutable type"
    Note: Strings are counted'''
    t = type(obj)
    return obj == None or t == bool or t == int or t == float or t == str


def verify_term_name(name: str) -> Union[str, None]:
    try:
        return (
            name
            if parser.parse(text=f'<{name} --> {name}>.')
            else None)
    except:
        print(
            f'verify_term_name: failed to verify term name "{name}", skipped...')
        return None

# term construction


def term_relation(*atoms: Tuple[str]) -> str:
    '''
    Construct the term "Relationship between A and B" by uses "Product" in Narsese
    Narsese representation: (*, atoms...)

    Example:
    - ("A", "B", "C") => "(*, A, B, C)"
    "'''
    return f'(*, {", ".join(atoms)})'


def term_name(A: any) -> str:
    '''
    Get the valid Narsese term name of an object
    '''
    t: type = type(A)
    # test whether the object can be directly accepted as a lexical item, if it is attached, if not, no
    instance_wrapper: str = '%s' if is_basic_type(A) else '{%s}'
    # first format encapsulation: Fill "class name _ value /id"
    init_name: str = verify_term_name(f'{t.__name__}_{str(A)}')
    # check: Whether the filled term is valid (cause: the array "first pass, second fail" problem)
    init_name = verify_term_name(
        init_name if init_name else f'{t.__name__}_{id(A)}')
    # second format encapsulation: Specifies whether an instance term is required
    final_name: str = instance_wrapper % init_name
    # return
    return final_name

# sentence construction


def sentence_inheritance(A: str, B: str, punct: Union[Punctuation, str] = Punctuation.Judgement) -> str:
    '''
    Building relationships "A is B"
    Narsese representation: <A --> B>
    '''
    return f'<{A} --> {B}>{punct.value if isinstance(punct,Punctuation) else punct}'  # <A --> B> default with "."


def sentence_relation(r: str, *terms: Tuple[str], punct: Punctuation = Punctuation.Judgement) -> str:
    '''
    Construct relation "(r A B ...)" i.e. "The relation between A, B (and so on)" is r"
    Narsese representation: <(*, A, B, ...) --> r>
    '''
    return sentence_inheritance(
        term_relation(*terms),
        f'{r}',
        punct=punct)  # <(*,A,B) --> r>. The "relationship" between A and B is r


def sentence_type_sign(name: str, type: type, punct: Punctuation = Punctuation.Judgement) -> str:
    '''Name the name based on the type of the object'''
    return sentence_inheritance(name, SIGN_TYPE_NAMES(type), punct=punct)  # name --> type


def sentence_tri_rel(obj: str, key: str, value: str, relation: str = SIGN_RELATION_OBJ_PROPERTY_VALUE,
                     punct: Punctuation = Punctuation.Judgement) -> str:
    '''
    Building a ternary relationship "Object [key] = value"
    Example: <(*,{object},(*,{attribute},{value})) --> object_attribute_value>
    '''
    return sentence_relation(
        relation, obj, key, value,
        punct=punct)  # (*,{obj},(*,{key},{value})) --> relation

# Main conversion module #

# basic


# Use kwargs to automatically pass "punctuation" information
def none2narsese(n: None, special_name: str, **kwargs) -> List[str]:
    '''None to Narsese'''
    return [sentence_type_sign(special_name, type(n), **kwargs)]


def bool2narsese(b: str, special_name: str, **kwargs) -> List[str]:
    '''boolean to Narsese'''
    result: List[str] = [sentence_type_sign(
        special_name, bool, **kwargs)]  # preset type identification
    return result


def int2narsese(i: int, special_name: str, **kwargs) -> List[str]:
    '''Integer to Narsese
        TODO: Build an integer system'''
    result: List[str] = [sentence_type_sign(
        special_name, int, **kwargs)]  # preset type identification
    return result


def float2narsese(f: float, special_name: str, **kwargs) -> List[str]:
    '''Floating-point number becomes Narsese
    TODO: Build a floating point number system and combine it with an integer system'''
    result: List[str] = [sentence_type_sign(
        special_name, float, **kwargs)]  # preset type identification
    return result


def str2narsese(s: str, special_name: str, **kwargs) -> List[str]:
    '''Set to Narsese
    TODO: How does distinguish between "name" and "value" of a string?'''
    # tests whether a string can be directly accepted as a term, appended if it is, unappended if it is not
    # try to use the string itself as a name for easy identification
    # ? [2023-09-26 13:02:03] may I can translate the str into a list of characters? Such as "ab c" => ["char_a", "char_b", "char_u0020", "char_c"]...
    final_name = verify_term_name(s)
    final_name: str = special_name + \
        (f'__{s}' if final_name else '')  # Include itself if you can, do not add information otherwise
    # preset type identification
    result: List[str] = [
        sentence_type_sign(final_name, str, **kwargs)]
    return result

# containers


def set2narsese(s: set, special_name: str, **kwargs) -> List[str]:
    '''Set to Narsese
    Use the relative item "belong"
    Import a collection name as the concept name, and then convert all elements within it to Narsese
    Return: A list of multiple Narsese statements (easy to split)'''
    result: List[str] = [sentence_type_sign(
        special_name, set, **kwargs)]  # preset type identification
    for item in s:  # TODO: Implementing recursive logic @auto2narsese(item)
        result.append(
            sentence_relation(
                SIGN_RELATION_BELONG,
                term_name(item), special_name,
                **kwargs))
    return result


def list_tuple2narsese(array: Union[list, tuple], special_name: str, **kwargs) -> List[str]:
    '''List/tuple to Narsese: Lists whose keys are integers'''
    result: List[str] = [sentence_type_sign(
        special_name, type(array), **kwargs)]  # preset type identification
    for i in range(len(array)):
        # get element
        item: any = array[i]
        iName: str = term_name(i)
        item_name: str = term_name(item)
        # pre-add definitions for keys and values
        result.extend(auto2narsese(item, item_name, **kwargs))
        result.extend(auto2narsese(i, iName, **kwargs))
        # bind objects, keys, and values
        result.append(sentence_tri_rel(
            special_name,
            iName,
            item_name,
            **kwargs))  # List[integer_index] = value
    return result


def dict2narsese(d: dict, special_name: str, **kwargs) -> List[str]:
    '''dict to Narsese
    #! In fact, JSON is a dictionary, to achieve the dictionary↔Narsese conversion, which is equivalent to NARS can read JSON
    TODO models dictionaries using an index system'''
    result: List[str] = [sentence_type_sign(
        special_name, dict, **kwargs)]  # preset type identification
    for key, value in d.items():
        key_name: str = term_name(key)
        value_name: str = term_name(value)
        # pre-add definitions for keys and values
        result.extend(auto2narsese(key, key_name, **kwargs))
        result.extend(auto2narsese(value, value_name, **kwargs))
        # bind objects, keys, and values
        result.append(sentence_tri_rel(
            special_name,
            key_name,
            value_name,
            **kwargs))  # dictionary[immutable_data_index] = value
    return result


def type2narsese(t: type, special_name: str, **kwargs) -> List[str]:
    '''Type to Narsese
    The "type" itself also needs to become Narsese'''
    return [sentence_type_sign(special_name, type, **kwargs)]  # only type notations

# default values


def default2narsese(obj: any, special_name: str, **kwargs) -> List[str]:
    '''Other objects become Narsese
    Temporarily occupy the one place, will later be separated from many types'''
    print(f'WARNING: unsupported object {obj} with type {type(obj)}')
    # only type notations
    return [sentence_type_sign(special_name, type, **kwargs)]

# Main function: Integrate all parts #


CONVERT_FUNCTIONS: Dict[type, any] = {
    type(None): none2narsese,
    int: int2narsese,
    float: float2narsese,
    bool: bool2narsese,
    str: str2narsese,
    list: list_tuple2narsese,
    tuple: list_tuple2narsese,
    set: set2narsese,
    dict: dict2narsese,
    type: type2narsese,
    None: default2narsese,


}


def auto2narsese(obj: any, name: str = None, punct: Punctuation = Punctuation.Judgement) -> List[str]:
    '''Function integration: Python object →Narsese statement sequence
    Automatically identify the object type and call the corresponding conversion function'''
    # get name
    # If no, automatically generate
    name = name if name else term_name(obj)
    # get type
    t = type(obj)
    # select & Generate, with default values (all parameters must accept a "Narsese parsed name")
    nars_sentences: List[str] = CONVERT_FUNCTIONS.get(
        t, CONVERT_FUNCTIONS[None])(obj, name, punct=punct)
    # verify
    for sentence in nars_sentences:
        parser.parse(sentence)
    # return
    return nars_sentences
