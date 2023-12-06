
from pynars.Narsese import Truth
from .UncertaintyMappingFunctions import w_to_c
from pynars.Config import Config

def project(truth: Truth, t_source: int, t_current: int, t_target: int):
    '''
    Reference:
    [1] OpenNARS 3.1.0 TruthFunctions.java line 492~495:
        ```
            public static final float temporalProjection(final long sourceTime, final long targetTime, final long currentTime, Parameters param) {
                final double a = 100000.0 * param.PROJECTION_DECAY; //projection less strict as we changed in v2.0.0  10000.0 slower decay than 100000.0
                return 1.0f - abs(sourceTime - targetTime) / (float) (abs(sourceTime - currentTime) + abs(targetTime - currentTime) + a);
            }
        ```
    [2] Hammer, Patrick, Tony Lofthouse, and Pei Wang. "The OpenNARS implementation of the non-axiomatic reasoning system." International conference on artificial general intelligence. Springer, Cham, 2016.

        Section 5. Projection and Eternalization

            $$k_c = \frac{|tB - tT|}{|tB - tC| + |tT - tC|}$$

            $$c_{new} = (1 - k_c) * c_{old}$$
    '''
    c_new = truth.c * (Config.projection_decay ** (t_current - t_source))
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