
from pynars.Narsese import Truth
from .UncertaintyMappingFunctions import w_to_c
from pynars.Config import Config

def project(truth: Truth, t_source: int, t_current: int, t_target: int):
    '''
    Reference:
        p.172 Non-Axiomatic Logic
            — A Model of Intelligent Reasoning
            (Second Edition)
    '''
    v = abs(t_source - t_target)

    t_current_is_in_interval = False
    if t_source < t_target:
        if t_current >= t_source and t_current <= t_target: t_current_is_in_interval = True
    else:
        if t_current <= t_source and t_current >= t_target: t_current_is_in_interval = True

    if t_current_is_in_interval: s = 0.5
    else: s = min(abs(t_source - t_current),abs(t_target-t_current))

    confidence_discount = 1 - v/(2*s + v)
    c_new = truth.c * confidence_discount
    return Truth(truth.f, c_new, truth.k)


def eternalize(truth: Truth):
    '''
    Reference:
    [1] OpenNARS 3.1.0 TruthFunctions.java line 485~490:
        ```
            public static final EternalizedTruthValue eternalize(final TruthValue v1, Parameters narParameters) {
                final float f1 = v1.getFrequency();
                final double c1 = v1.getConfidence();
                final double c = w2c(c1, narParameters);
                return new EternalizedTruthValue(f1, c, narParameters);
            }
        ```
    [2] Hammer, Patrick, Tony Lofthouse, and Pei Wang. "The OpenNARS implementation of the non-axiomatic reasoning system." International conference on artificial general intelligence. Springer, Cham, 2016.
        
        Section 5. Projection and Eternalization

            $$c_{eternal} = \frac{1}{k + c_{temporal}}$$
    TODO: The two dealing with eternalizaiton are different. Which is right? Using the first one for the moment, because it seems more reasonable.
    '''
    return Truth(truth.f, w_to_c(truth.c, truth.k), truth.k)