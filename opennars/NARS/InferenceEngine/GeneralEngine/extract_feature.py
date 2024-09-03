from typing import Union
from collections import namedtuple

from opennars.Narsese._py.Connector import Connector
from opennars.NAL.Inference import *
from opennars.Narsese import Statement, Term, Compound

Feature = namedtuple(
    'Feature', 
    [
        'match_reverse', 
        'has_common_id', 
        'common_id_task', 
        'common_id_belief', 
        'has_at', 
        'p1_at_p2', 
        'p2_at_p1', 
        'has_compound_at', 
        'c1_at_c2', 
        'c2_at_c1',
        'has_compound_common_id', 
        'compound_common_id_task', 
        'compound_common_id_belief',
        'the_other1',
        'the_other2',
        # 'the_other_compound_has_common',
        # 'the_other_compound_p1_at_p2',
        # 'the_other_compound_p2_at_p1',
        # 'the_other_connector1',
        # 'the_other_connector2'
    ],
    defaults=[False, True, None, None, False, None, None, False, None, None, False, None, None, None, None]# False, False, False, None, None]
)

def _mirorr_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]):
    feature = extract_feature(premise2, premise1)
    return Feature(
        feature.match_reverse,
        feature.has_common_id,
        feature.common_id_belief,
        feature.common_id_task,
        feature.has_at,
        feature.p2_at_p1,
        feature.p1_at_p2,
        feature.has_compound_at,
        feature.c2_at_c1,
        feature.c2_at_c1,
        feature.has_compound_common_id,
        feature.compound_common_id_belief,
        feature.compound_common_id_task,
        feature.the_other2,
        feature.the_other1
    )


def extract_feature(premise1: Union[Term, Compound, Statement], premise2: Union[Term, Compound, Statement]) -> Feature:
    '''
    It should be ensured that premise1 and premise2 aren't identical.    
    '''
    if premise2 is None: return Feature()
    if premise1.is_statement:
        '''
        <S-->P>
        <S==>P>

        <<S-->T>-->P>
        <<S--><P-->Q>>
        <<S-->P>--><P-->Q>>

        <<S-->T>==>P>
        <<S==><P-->Q>>
        <<S-->P>==><P-->Q>>

        <(&,S,T)-->P>
        <S-->(|,P,Q)>
        <(&,S,T)-->(|,P,Q)>

        <(&,S,T)==>P>
        <S==>(|,P,Q)>
        <(&,S,T)==>(|,P,Q)>
        <(&&,<S-->T>, <M-->R>)==>(|,P,Q)>
        '''
        if premise2.is_statement:
            # <S-->M>, <M-->P>
            # <S==>M>, <M==>P>
            # <<S-->T>==>M>, <M-->P>
            if premise1.subject == premise2.predicate and premise1.predicate == premise2.subject:
                # <S-->P>, <P-->S>
                return Feature(
                    match_reverse=True
                )
            elif premise1.subject == premise2.subject:
                # <M-->S>, <M-->P>
                return Feature(
                    has_common_id=True,
                    common_id_task=0,
                    common_id_belief=0,
                    the_other1=premise1.predicate,
                    the_other2=premise2.predicate
                )
            elif premise1.subject == premise2.predicate:
                # <M-->P>, <S-->M>
                return Feature(
                    has_common_id=True,
                    common_id_task=0,
                    common_id_belief=1,
                    the_other1=premise1.predicate,
                    the_other2=premise2.subject
                )
            elif premise1.predicate == premise2.subject:
                # <S-->M>, <M-->P>
                return Feature(
                    has_common_id=True,
                    common_id_task=1,
                    common_id_belief=0,
                    the_other1=premise1.subject,
                    the_other2=premise2.predicate
                )
            elif premise1.predicate == premise2.predicate:
                # <S-->M>, <P-->M>
                return Feature(
                    has_common_id=True,
                    common_id_task=1,
                    common_id_belief=1,
                    the_other1=premise1.subject,
                    the_other2=premise2.subject
                )
            # <<S-->T>==>M>, <S-->T>; TaskLink is COMPOUND_CONDITION
            elif premise1.subject == premise2:
                # <<S-->T>==>M>, <S-->T>
                return Feature(
                    has_at=True,
                    p2_at_p1=True,
                    common_id_task=0
                ) 
            elif premise1.predicate == premise2:
                # <M==><S-->T>>, <S-->T>
                return Feature(
                    has_at=True,
                    p2_at_p1=True,
                    common_id_task=1
                )
            elif premise2.subject == premise1:
                # <S-->T>, <<S-->T>==>M>
                return Feature(
                    has_at=True,
                    p1_at_p2=True,
                    common_id_belief=0
                )
            elif premise2.predicate == premise1:
                # <S-->T>, <M==><S-->T>>
                return Feature(
                    has_at=True,
                    p1_at_p2=True,
                    common_id_task=1
                )
            # <(&&, <S-->M>, <P-->Q>)==>T>, <S-->M>
            elif premise1.subject.is_compound and premise2 in premise1.subject.terms:
                # <(&&, <S-->M>, <P-->Q>)==>T>, <S-->M>
                return Feature(
                    has_compound_at=True,
                    c2_at_c1=True,
                    compound_common_id_task=0,
                )
            elif premise1.predicate.is_compound and premise2 in premise1.predicate.terms:
                # <T==>(&&, <S-->M>, <P-->Q>)>, <S-->M>
                return Feature(
                    has_compound_at=True,
                    c2_at_c1=True,
                    compound_common_id_task=1,
                )
            elif premise2.subject.is_compound and premise1 in premise2.subject.terms:
                # <S-->M>, <(&&, <S-->M>, <P-->Q>)==>T>
                return Feature(
                    has_compound_at=True,
                    c1_at_c2=True,
                    compound_common_id_belief=0,
                )
            elif premise2.predicate.is_compound and premise1 in premise2.predicate.terms:
                # <S-->M>, <T==>(&&, <S-->M>, <P-->Q>)>
                return Feature(
                    has_compound_at=True,
                    c1_at_c2=True,
                    compound_common_id_belief=1,
                )
            # <(&&,S,P)==>T>, <S==>M>
            # <(&&,S,P,Q)==>T>, <(&&,S,P)==>M>
            elif premise1.subject.is_compound and premise2.subject in premise1.subject.terms:
                # <(&&,S,P)==>T>, <S==>M>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=0,
                    the_other1=premise1.predicate,
                    the_other2=premise2.predicate
                )
            elif premise1.predicate.is_compound and premise2.subject in premise1.predicate.terms:
                # <T==>(&&,S,P)>, <S==>M>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=0,
                    the_other1=premise1.subject,
                    the_other2=premise2.predicate
                )
            elif premise1.subject.is_compound and premise2.predicate in premise1.subject.terms:
                # <(&&,S,P)==>T>, <M==>S>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=1,
                    the_other1=premise1.predicate,
                    the_other2=premise2.subject
                )
            elif premise1.predicate.is_compound and premise2.predicate in premise1.predicate.terms:
                # <T==>(&&,S,P)>, <M==>S>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=1,
                    the_other1=premise1.subject,
                    the_other2=premise2.subject
                )
            
            elif premise2.subject.is_compound and premise1.subject in premise2.subject.terms:
                # <S==>M>, <(&&,S,P)==>T>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=0,
                    the_other1=premise1.predicate,
                    the_other2=premise2.predicate
                )
            elif premise2.predicate.is_compound and premise1.subject in premise2.predicate.terms:
                # <S==>M>, <T==>(&&,S,P)>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=1,
                    the_other1=premise1.predicate,
                    the_other2=premise2.subject
                )
            elif premise2.subject.is_compound and premise1.predicate in premise2.subject.terms:
                # <M==>S>, <(&&,S,P)==>T>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=0,
                    the_other1=premise1.subject,
                    the_other2=premise2.predicate
                )
            elif premise2.predicate.is_compound and premise1.predicate in premise2.predicate.terms:
                # <M==>S>, <T==>(&&,S,P)>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=1,
                    the_other1=premise1.subject,
                    the_other2=premise2.subject
                )

            # <(&&,S,P,Q)==>T>, <(&&,S,P)==>M>
            elif premise1.subject.is_compound and premise2.subject.is_compound and premise2.subject.has_common(premise1.subject):
                # <(&&,S,P,Q)==>T>, <(&&,S,P)==>M>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=0,
                    the_other1=premise1.predicate,
                    the_other2=premise2.predicate
                )
            elif premise1.predicate.is_compound and premise2.subject.is_compound and premise2.subject.has_common(premise1.predicate):
                # <T==>(&&,S,P,Q)>, <(&&,S,P)==>M>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=0,
                    the_other1=premise1.subject,
                    the_other2=premise2.predicate
                )
            elif premise1.subject.is_compound and premise2.predicate.is_compound and premise2.predicate.has_common(premise1.subject):
                # <(&&,S,P,Q)==>T>, <M==>(&&,S,P)>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=0,
                    compound_common_id_belief=1,
                    the_other1=premise1.predicate,
                    the_other2=premise2.subject
                )
            elif premise1.predicate.is_compound and premise2.predicate.is_compound and premise2.predicate.has_common(premise1.predicate):
                # <T==>(&&,S,P,Q)>, <M==>(&&,S,P)>
                return Feature(
                    has_compound_common_id=True,
                    compound_common_id_task=1,
                    compound_common_id_belief=1,
                    the_other1=premise1.subject,
                    the_other2=premise2.subject
                )
            
            else:
                return Feature(
                    has_common_id=False
                )
        elif premise2.is_compound:
            # <S-->P>, (|, P, T)
            # <S==>P>, (&&, S, T)
            # <S-->(|, P, Q)>, (|, P, Q, T)
            # <S-->P>, (&&, <S-->P>, T)
            if premise1.subject in premise2.terms: 
                # <S-->P>, (|, S, T)
                return Feature(
                    match_reverse=False,
                    has_compound_common_id=True,
                    compound_common_id_task=0
                )
            elif premise1.predicate in premise2.terms: 
                # <S-->P>, (|, P, T)
                return Feature(
                    match_reverse=False,
                    has_compound_common_id=True,
                    compound_common_id_task=1
                )
            elif premise1 in premise2.terms:
                # <S-->P>, (&&, <S-->P>, T)
                return Feature(
                    match_reverse=False,
                    p1_at_p2=True
                )
            # <(&,S,P)==>Q>, (&,S,M)
            # <(&,S,P,M)==>Q>, (&,S,M)
            # <(&,S,M)==>Q>, (&,S,P,M)
            elif premise1.subject.is_compound and premise1.subject.has_common(premise2):
                # <(&&,S,M)==>P>, (&&,M,Q,T)
                return Feature(
                    match_reverse=False,
                    has_compound_common_id=True,
                    compound_common_id_task=0
                )
            elif premise1.predicate.is_compound and premise1.predicate.has_common(premise2):
                # <S==>(||,M,P)>, (||,M,Q,T)
                return Feature(
                    match_reverse=False,
                    has_compound_common_id=True,
                    compound_common_id_task=1
                )
            else:
                return Feature(
                    match_reverse=False,
                    has_common_id=False
                )
        elif premise2.is_atom:
            # <S==>P>, S
            if premise2 == premise1.subject:
                # <S==>P>, S
                return Feature(
                    has_at=True,
                    p2_at_p1=True,
                    common_id_task=0
                )
            elif premise2 == premise1.predicate:
                # <S==>P>, P
                return Feature(
                    has_at=True,
                    p2_at_p1=True,
                    common_id_task=1
                )
            # <(&&,S,T)==>P>, S
            elif premise1.subject.is_compound and premise2 in premise1.subject.terms:
                # <(&&,S,T)==>P>, S
                return Feature(
                    has_compound_at=True,
                    p2_at_p1=True,
                    compound_common_id_task=0
                )
            elif premise1.predicate.is_compound and premise2 in premise1.predicate.terms:
                # <P==>(&&,S,T)>, S
                return Feature(
                    has_compound_at=True,
                    p2_at_p1=True,
                    compound_common_id_task=1
                )
            else:
                return Feature(
                    match_reverse=False,
                    has_common_id=False
                )

        else: raise "Invalide case"
    elif premise1.is_compound:
        '''
        (&, S, T)
        (&, <S-->P>, T)
        (&&, <S-->P>, <T-->Q>)
        (&, <S-->P>, T)
        '''
        if premise2.is_statement:
            return _mirorr_feature(premise1, premise2)
        elif premise2.is_compound:
            if premise1.has_common(premise2):
                # (&&, A, B, C), (&&, A, B)
                # (&&, A, B, C), (&&, A, B, D)
                return Feature(
                    has_compound_common_id=True,
                    p2_at_p1=True,
                    p1_at_p2=True,
                )
            else:
                return Feature(
                    has_common_id=False
                )
        elif premise2.is_atom:
            if premise2 in premise1.terms:
                # (&&, A, B, C), A.
                return Feature(
                    has_compound_common_id=True,
                    p2_at_p1=True,
                )
            else:
                return Feature(
                    match_reverse=False,
                    has_common_id=False
                )
        else: raise "Invalide case"
    elif premise1.is_atom:
        '''
        S.
        '''
        if premise2.is_statement:
            return _mirorr_feature(premise1, premise2)
        elif premise2.is_compound:
            return _mirorr_feature(premise1, premise2)
        elif premise2.is_atom:
            return Feature(
                match_reverse=False,
                has_common_id=False
            )
        else: raise "Invalide case"



