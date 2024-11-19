from copy import copy
from opennars.Config import Enable
from opennars.Narsese._py.Interval import Interval
from opennars.utils.IndexVar import IndexVar
from .Term import Term, TermType, place_holder
from .Terms import Terms
from .Connector import Connector
from typing import Iterable, List, Type, Union
from ordered_set import OrderedSet
from typing import Set
from opennars.utils.tools import list_contains
from opennars.Global import States
from collections import Counter
from .Tense import TemporalOrder

class Compound(Term):
    type = TermType.COMPOUND

    components: set[Term]|list[Term]
    connector: Connector
    temporal_order = TemporalOrder.NONE

    def __init__(self, connector: Connector, *terms: Term) -> None:
        ''''''
        self._is_commutative = connector.is_commutative
        if self.is_commutative:
            self.components = OrderedSet(sorted(terms, key=hash))
        else:
            self.components = list(terms)
        self.connector = connector

        word = self._terms_to_word(self.components)
        Term.__init__(self, word)

        self._complexity += sum(term.complexity for term in terms)

        self._is_single_only = self.connector.is_single_only
        self._is_double_only = self.connector.is_double_only
        self._is_multiple_only = self.connector.is_multiple_only

        self.has_ivar = any(term.has_ivar for term in self.components)
        self.has_dvar = any(term.has_dvar for term in self.components)
        self.has_qvar = any(term.has_qvar for term in self.components)
        self.has_var = self.has_ivar or self.has_dvar or self.has_qvar

        if self.has_var:
            self.normalized = False

        match self.connector:
            case Connector.SequentialEvents:
                self.temporal_order = TemporalOrder.FORWARD
            case Connector.ParallelEvents:
                self.temporal_order = TemporalOrder.CONCURRENT

    @property
    def recursive_terms(self) -> Iterable[Term]:
        return (term for component in self.components for term in component.recursive_terms)
    
    @property
    def is_commutative(self):
        return self._is_commutative

    @property
    def is_single_only(self):
        return self._is_single_only

    @property
    def is_double_only(self):
        return self._is_double_only

    @property
    def is_multiple_only(self):
        return self._is_multiple_only
    
    @property
    def contained_temporal_relations(self) -> int:
        if self._contained_temporal_relations == -1:
            self._contained_temporal_relations = 0
            for t in self.components:
                self._contained_temporal_relations += t._contained_temporal_relations
        return self._contained_temporal_relations
    
    def contains_component(self, t: Term) -> bool:
        '''
        Check whether the compound contains a certain component

        Args:
            t: The component to be checked
        Returns:
            Whether the component is in the compound
        '''
        return t in self.components
    
    def contains_term(self, target: Term, count_self: bool=False) -> bool:
        '''
        Recursively check if a compound contains a term
        Args:
            target: The term to be searched
            count_self: Whether to count the compound itself
        Returns:
            Whether the target is in the current term
        '''
        if count_self:
            if Term.contains_term(self, target):
                return True
        for term in self.components:
            if term.contains_term(target):
                return True
        return False
    
    def count_term_recursively(self, count_self: bool=False) -> dict[Term, int]:
        '''
        Recursively count how often the terms are contained

        Args:
            count_self: Whether to count the compound itself
        Returns:
            The counts of the terms
        '''
        map: dict[Term, int] = dict(Counter(self.recursive_terms))
        if count_self:
            map[self] = 1
        return map

    def contains_all_components(self, t: Term) -> bool:
        '''
        Check whether the compound contains all components of another term, or that term as a whole
        Args:
            t: The other term
        Returns:
            Whether the components are all in the compound
        
        '''
        if t.is_compound and (t.connector is self.connector):
            components1 = t.components if t.is_commutative else set(t.components)
            components2 = self.components if self._is_commutative else set(self.components)
            return components1 <= components2
        else:
            return t in self.components
    
    @staticmethod
    def set_component(compound: 'Compound', index: int, t: Term) -> Term:
        '''
        Try to replace a component in a compound at a given index by another one

        Args:
            compound: The compound   
            index: The location of replacement
            t: The new component
            memory Reference to the memory
        Returns:
            The new compound
        '''
        if t is not None:
            l = list(compound.components)
            if t.is_compound and compound.connector is t.connector:
                l = [*l[:index], *t.components, *l[index+1:]]
            else:
                l[index] = t
            
        return Compound(compound.connector, *l)

    def _merge_compounds(self, connector_parent: Connector, connector: Connector, compounds: List[Type['Compound']],
                         is_input: bool):
        '''
        The `compounds` should have got the same `connector`.
        (&, {A, B}, {B, C}) ====> {B}
        (|, {A, B}, {B, C}) ====> {A, B, C}
        (&, [A, B], [B, C]) ====> [A, B, C]
        (|, [A, B], [B, C]) ====> [B]
        (-, {A, B}, {B, C}) ====> {A}
        (~, [A, B], [B, C]) ====> [A]

        It is ensured that the concerned components have no further nested compound which should be unfolded, because if there were, it would be unfolded when building its parent compound.
        '''
        if connector_parent is Connector.ExtensionalIntersection:
            if connector is Connector.ExtensionalSet:
                return Terms.intersection(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                          is_input=is_input)
                # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).intersection(*(Terms(compound, compound.is_commutative, is_input) for compound in compounds[1:]))
            elif connector is Connector.IntensionalSet:
                # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).union(*(Terms(compound.terms, compound.is_commutative, is_input) for compound in compounds[1:]))
                return Terms.union(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                   is_input=is_input)
            else:
                return None
        elif connector_parent is Connector.IntensionalIntersection:
            if connector is Connector.ExtensionalSet:
                # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).union(*(Terms(compound.terms, compound.is_commutative, is_input) for compound in compounds[1:]))
                return Terms.union(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                   is_input=is_input)
            elif connector is Connector.IntensionalSet:
                # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).intersection(*(Terms(compound.terms, compound.is_commutative, is_input) for compound in compounds[1:]))
                return Terms.intersection(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                          is_input=is_input)
            else:
                return None

        elif connector_parent is Connector.ExtensionalDifference and connector is Connector.ExtensionalSet:
            # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).intersection(*(Terms(compound.terms, compound.is_commutative, is_input) for compound in compounds[1:]))
            return Terms.difference(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                      is_input=is_input)
        elif connector_parent is Connector.IntensionalDifference and connector is Connector.IntensionalSet:
            # return Terms(compounds[0].terms, compounds[0].is_commutative, is_input).intersection(*(Terms(compound.terms, compound.is_commutative, is_input) for compound in compounds[1:]))
            return Terms.difference(compounds[0].terms, *(compound.terms for compound in compounds[1:]),
                                      is_input=is_input)

        elif connector_parent is connector:
            return Terms((t for ts in compounds for t in ts), connector.is_commutative)
        else:
            return None

    def prepocess_terms(self, connector_parent: Connector, terms: Iterable[Union[Type['Compound'], Term]],
                        is_input=False):
        '''
        pre-process the terms, return the connecor of this compound and the set/list of components.
        For `{{A, B}, {B, C}}`, return `{, A, B, C`;
            proof: {{A, B}, {B, C}}={(|, {A}, {B}), (|, {B}, {C})}=(|, (|, {A}, {B}), (|, {B}, {C}))=(|, {A}, {B}, {C})={A, B, C}
        For `[[A, B], [B, C]]`, return `[, A, B, C`;
        For `(con, (con, A, B), (con, B, C))`, return `con, A, B, C` if con is commutative, else return `con, A, B, B, C`
        For `(|, {A, B}, {B, C})`, return `{, A, B, C`;
        For `(&, [A, B], [B, C])`, return `[, A, B, C`;
        For `(con, A, B, C)`, return `con, A, B, C`;
        For `{{A, B}, {B, C}, D}`, return `{, {A, B, C}, D`;

        Returns:
            connector, terms
        '''
        if connector_parent in {Connector.Product, Connector.ExtensionalImage, Connector.IntensionalImage, Connector.ExtensionalDifference, Connector.IntensionalDifference}:
            '''
            For example, in the test-case `nal6.22.nal`, there is a statement
                `<(*,(*,(*,0))) --> num>`
            '''
            return connector_parent, terms

        if self.is_commutative:
            # if there are terms with the same commutative connector, they should be combined togethor
            
            terms2 = terms
            terms = []
            for term in terms2:
                if term.is_compound and term.connector == connector_parent:
                    for _term in term.terms:
                        terms.append(_term)
                else:
                    terms.append(term)

            categories = {}
            for term in terms:
                # `None` means the connector of the term is not cared about, because it just needs to be added into the parent compound-term as a whole.
                connector = term.connector if term.is_compound and term.is_commutative else None
                category = categories.get(connector, None)
                if category is None:
                    categories[connector] = category = []
                category.append(term)

            terms_norm: List[Compound] = []
            for connector, compounds in categories.items():
                if connector is None:
                    terms_norm.extend([(connector, compound)
                                      for compound in compounds])
                    continue
                # Now, `connector` is not `None`.

                terms_merged = self._merge_compounds(
                    connector_parent, connector, compounds)
                if terms_merged is None:  # they don't need to be merged to be a whole
                    # terms_norm.append((connector, compounds))
                    terms_norm.extend([(connector, compound)
                                      for compound in compounds])
                    continue

                # Now, `terms_merged` is not `None`.
                # However, the compounds (in `terms_merged`), as components, shouldn't further be constructed as a compound term immediately, as there are some cases where there is only one compound and the parent connector should be set as the current single compound connector, for example, (|, {A, B}, {C, D}) is handled and `terms_merged` is `A, B, C, D`. In this case, if this function returned a compound `{A, B, C, D}`, the parent compound would be (&, {A, B, C, D}), which is obviously incorrect.
                # Hence, the final construction of the compound is out of this function.

                terms_norm.append((connector, terms_merged))
            
            if len(terms_norm) > 1:
                terms = []
                connector: Connector
                for connector, term in terms_norm:
                    if connector is None:
                        terms.append(term)
                    elif connector is connector_parent:
                        terms.extend(term)
                    else:
                        if connector.check_valid(len(term)):
                            term = Compound(connector, *term)
                            terms.append(term)
                if len(terms) > 1:
                    return connector_parent, Terms(terms, is_commutative=True)
                else:  # len(terms) == 1
                    term = terms[0]
                    terms_norm = [[term.connector, term.terms]
                                  if term.is_compound else [None, term]]

            # Now, there is only one term in `terms_norm`

            # the connector returned depends on the types of `connector` and `connector_parent`. For example,
            # if `connector_parent` is `&` and `connector` is `{`, the return `connector`;
            # if `connector_parent` is `|` and `connector` is `{`, the return `connector`;
            # if `connector_parent` is `&` and `connector` is `&`, it makes no difference returning either `connector` or `connector_parent`;

            connector, terms = terms_norm[0]
            if connector is None:
                terms = (terms,)

            if (connector in (Connector.ExtensionalSet, Connector.IntensionalSet)) and (
                    connector_parent in (Connector.IntensionalIntersection, Connector.ExtensionalIntersection)):
                return connector, Terms(terms, is_commutative=True)

            # otherwise, return `connector_parent` as the connector.
            return connector_parent, Terms(terms, is_commutative=True)
        else:
            # if len(terms == 1):
            #     term: Compound = terms[0]
            #     if term.is_compound and term.connector == Connector.Negation and connector_parent == Connector.Negation:
            #         return connector_parent, terms

            # e.g. (&/, (&/, A, B), (&|, C, D), E) will be converted to (&/, A, B, (&|, C, D), E)
            terms = (term2 for term1 in (
                ((term0 for term0 in term.terms) if term.is_compound and (
                    term.connector is connector_parent) else (term,))
                for term in terms) for term2 in term1)

            return connector_parent, Terms(terms, is_commutative=False)


    def __iter__(self):
        return iter(self.components)  # OrderedSet.__iter__(self)

    def __getitem__(self, index: int|tuple[int]) -> Term:
        if isinstance(index, int):
            return self.components[index]
        if len(index) == 0:
            return self

        idx = index[0]
        if idx >= len(self.components):
            raise "Out of bounds."

        index = index[1:]
        term: Term = self.components[idx]  # OrderedSet.__getitem__(self, idx)
        if term.is_atom:
            if len(index) > 0:
                return None
            return term
        return term.__getitem__(index)

    # def __sub__(self, s: Type['Compound']) -> Union[Type['Compound'], Term]:
    #     # if self.is_double_only or self.is_single_only: raise 'Invalid case.'
    #     # if OrderedSet.__contains__(self, s): s = (s,)

    #     if self.is_commutative:
    #         if s.is_compound and s.connector:
    #             s = s.terms  # s should be a type of `Term`
    #         else:
    #             s = Terms((s,), False)
    #         terms = self.terms - s
    #     else:
    #         if s.is_compound and s.connector:
    #             s = s.terms  # s should be a type of `Term`
    #             terms = [term for term in self.terms if term not in s]
    #         else:
    #             terms = [term for term in self.terms if term != s]

    #     if self.is_multiple_only and len(terms) == 1:
    #         result = terms[0]
    #     else:
    #         result = Compound(self.connector, *terms)
    #     return result

    # def __rsub__(self, s: Term) -> Union[Type['Compound'], Term]:
    #     return self - s

    # def has_common(self, compound: Type['Compound'], same_connector: bool = True) -> bool:
    #     if not compound.is_compound:
    #         return False

    #     return ((self.connector is compound.connector) if same_connector else True) and (
    #         (not self.terms.isdisjoint(compound.terms)) if self.is_commutative else list_contains(self.terms,
    #                                                                                               list(compound.terms)))

    # @classmethod
    # def copy(cls, compound: Type['Compound']):
    #     '''
    #     create a new list, but each element in the list is identical to that in the input(old) one correspondingly.
    #     returns a shallow copy of the input compound.
    #     '''
    #     return cls(compound.connector, *compound)

    # def replace(self, term_old: Term, term_new: Term, connector: Connector = None, idx: int = None) -> Type['Compound']:
    #     # if term_old.is_atom: term_old = (term_old,)
    #     # elif term_old.is_compo
    #     terms: Union[OrderedSet, list] = self.terms
    #     idx = terms.index(term_old) if idx is None else idx
    #     return Compound(self.connector if connector is None else connector,
    #                     *(term if i != idx else term_new for i, term in enumerate(self)))

    # def equal(self, o: Type['Compound']) -> bool:
    #     '''
    #     Return:
    #         is_equal (bool), is_replacable(bool)
    #     '''
    #     if o.is_compound:
    #         if not self.connector is o.connector:
    #             return False
    #         if self.is_commutative:
    #             set1: Iterable[Term] = self.terms - o.terms
    #             set2: Iterable[Term] = o.terms - self.terms
    #             if len(set1) == len(set2) == 0:
    #                 return True
    #             # ChatGPT: directly returns the result of the logical AND condition, 
    #             # checking if all column sums and all row sums are greater than zero. 
    #             # This uses the built-in all() function to ensure every sum in each direction (column and row) 
    #             # is greater than zero. The zip(*eq_array) unpacks each row of eq_array into columns.
    #             eq_array = [[term1.equal(term2)
    #                          for term2 in set2] for term1 in set1]
    #             if all(sum(col) > 0 for col in zip(*eq_array)) and all(sum(row) > 0 for row in eq_array):
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             if len(self) != len(o):
    #                 return False
    #             term1: Term
    #             term2: Term
    #             for term1, term2 in zip(self.terms, o.terms):
    #                 if not term1.equal(term2):
    #                     return False
    #             return True
    #     elif o.is_atom and o.is_var:
    #         return True
    #     else:
    #         return False

    def __repr__(self, *args) -> str:
        return f'<Compound: {self.repr()}>'

    def __len__(self):
        return len(self.components)
    
    def __eq___(self, o: Term):
        if not o.is_compound: return False
        if self.connector is not o.connector: return False
        return Term.__eq__(self, o)

    def _terms_to_word(self, terms: Iterable[Term]):
        connector = self.connector
        if connector == Connector.ExtensionalSet:
            word = f"{{{', '.join([str(term) for term in terms])}}}"
        elif connector == Connector.IntensionalSet:
            word = f"[{', '.join([str(term) for term in terms])}]"
        else:
            word = f"({connector.value}, {', '.join([str(term) for term in terms])})"
        return word

    # def repr(self):
    #     compound: Set[Term] = self
    #     word_terms = (str(component) for component in compound)

    #     return self._terms_to_word(word_terms)

    def deep_clone(self, variables_only=False) -> 'Compound|None':
        '''
        Deep copy the compound. Recursively copy the components.
        Returns:
            Compound if the deep copy of the components succeeded.
            None if the deep copy of the components failed.
        '''
        l = list[Term]()
        for component in self.components:
            if not variables_only:
                component = component.deep_clone()
            else:
                if component.has_var:
                    component = component.deep_clone()
                else:
                    component = component.clone()
            if component is None:
                return None
            l.append(component)
        c = Compound(self.connector, *l)
        if self.normalized:
            c.normalized = True
        return c


    def clone(self):
        '''
        Shallow copy the compound.
        '''
        clone = copy(self)
        return clone

    """ -------------- Constructors -------------- """

    @classmethod
    def ExtensionalSet(cls, *terms: Term) -> Type['Compound']:
        return cls._convert(Compound(Connector.ExtensionalSet, *terms))

    @classmethod
    def IntensionalSet(cls, *terms: Term) -> Type['Compound']:
        return cls._convert(Compound(Connector.IntensionalSet, *terms))

    @classmethod
    def Instance(cls, term: Term) -> Type['Compound']:
        return cls._convert(Compound.ExtensionalSet(term))

    @classmethod
    def Property(cls, term: Term) -> Type['Compound']:
        return cls._convert(Compound.IntensionalSet(term))

    @classmethod
    def ExtensionalImage(cls, term_relation: Term, *terms: Term, idx: int = None, compound_product: Type['Compound'] = None) -> Type['Compound']:
        if compound_product is not None:
            # if idx is None:
            terms = compound_product.terms
            idx = terms.index(term_relation) if idx is None else idx
            compound = Compound.ExtensionalImage(
                term_relation, *(tm if i != idx else place_holder for i, tm in enumerate(compound_product)))
        elif terms is not None:
            if idx is not None:
                terms: list = [*terms[:idx], place_holder, *terms[idx:]]
            compound = Compound(Connector.ExtensionalImage,
                                term_relation, *terms)
        return cls._convert(compound)

    @classmethod
    def IntensionalImage(cls, term_relation: Term, *terms: Term, idx: int = None, compound_product: Type['Compound'] = None, compound_image: Type['Compound'] = None) -> Type['Compound']:
        if compound_product is not None:
            # if idx is None:
            idx = compound_product.terms.index(
                term_relation) if idx is None else idx
            compound = Compound.IntensionalImage(
                term_relation, *(tm if i != idx else place_holder for i, tm in enumerate(compound_product)))
        elif terms is not None:
            if idx is not None:
                terms: list = [*terms[:idx], place_holder, *terms[idx:]]
            compound = Compound(Connector.IntensionalImage,
                                term_relation, *terms)
        return cls._convert(compound)

    @classmethod
    def Image(cls, replaced_term: Term, compound_image: Type['Compound'], idx_replaced: int = None) -> Type['Compound']:
        '''Convert Image to Image'''
        idx_replaced = compound_image.terms.index(
            replaced_term) if idx_replaced is None else idx_replaced

        compound = Compound(compound_image.connector, *((place_holder if i == idx_replaced else tm if tm !=
                            place_holder else replaced_term) for i, tm in enumerate(compound_image)))

        return cls._convert(compound)

    @classmethod
    def Product(cls, term: Term, *terms: Term, idx: int = None, compound_image: Type['Compound'] = None):
        if compound_image is not None:
            idx = compound_image.terms.index(
                place_holder)-1 if idx is None else idx
            compound = Compound.Product(
                *((tm if i != idx else term) for i, tm in enumerate(compound_image.terms[1:])))
        else:
            compound = Compound(Connector.Product, term,
                                *terms)
        return cls._convert(compound)

    @classmethod
    def Negation(cls, term: Type['Compound']) -> Union[Type['Compound'], Term]:
        if term.is_compound and term.connector == Connector.Negation:
            compound = term[0]
        else:
            compound = Compound(Connector.Negation, term)
        return cls._convert(compound)

    @classmethod
    def Conjunction(cls, *terms: Union[Term, Type['Compound']], temporal_order: TemporalOrder=None) -> Type['Compound']:
        if temporal_order is None or temporal_order is TemporalOrder.NONE:
            connector = Connector.Conjunction
        elif temporal_order is TemporalOrder.FORWARD:
            connector = Connector.SequentialEvents
        elif temporal_order is TemporalOrder.CONCURRENT:
            connector = Connector.ParallelEvents
        else:
            raise RuntimeError("Invalid case!")
        
        terms = (term for compound in terms for term in (
            compound if compound.is_compound and compound.connector == connector else (compound,)))
        
        return cls._convert(Compound(connector, *terms))

    @classmethod
    def Disjunction(cls, *terms: Union[Term, Type['Compound']]) -> Type['Compound']:
        terms = (term for compound in terms for term in (
            compound if compound.is_compound and compound.connector == Connector.Disjunction else (compound,)))
        return cls._convert(Compound(Connector.Disjunction, *terms))

    @classmethod
    def IntensionalIntersection(cls, *terms: Union[Term, Type['Compound']]) -> Type['Compound']:
        terms = (term for compound in terms for term in (
            compound if compound.is_compound and compound.connector == Connector.IntensionalIntersection else (compound,)))
        return cls._convert(Compound(Connector.IntensionalIntersection, *terms))

    @classmethod
    def ExtensionalIntersection(cls, *terms: Union[Term, Type['Compound']]) -> Type['Compound']:
        terms = (term for compound in terms for term in (
            compound if compound.is_compound and compound.connector == Connector.ExtensionalIntersection else (compound,)))
        return cls._convert(Compound(Connector.ExtensionalIntersection, *terms))

    @classmethod
    def ExtensionalDifference(cls, term1: Term, term2: Term) -> Type['Compound']:
        return cls._convert(Compound(Connector.ExtensionalDifference, term1, term2))

    @classmethod
    def IntensionalDifference(cls, term1: Term, term2: Term) -> Type['Compound']:
        return cls._convert(Compound(Connector.IntensionalDifference, term1, term2))

    @classmethod
    def SequentialEvents(cls, *terms: Union[Term, Interval]) -> Type['Compound']:
        return cls._convert(Compound(Connector.SequentialEvents, *terms))

    @classmethod
    def ParallelEvents(cls, *terms: Term) -> Type['Compound']:
        return cls._convert(Compound(Connector.ParallelEvents, *terms))

    @staticmethod
    def _convert(compound: Type['Compound']):
        '''
        convert the form of the compound.
        for example, if the compound is multiple-only and the length of its terms is 1, then return the first term, instead of the compound, of the terms.
        '''
        if compound.is_compound:
            # it cannot be 0.
            if compound.is_multiple_only and len(compound.terms) == 1:
                return compound[0]
            elif compound.is_single_only and len(compound.terms) > 1:
                raise "Invalid case!"
            elif compound.is_double_only and len(compound.terms) != 2:
                raise "Invalid case!"
        return compound