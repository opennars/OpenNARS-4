from opennars.Narsese import Truth

fc_to_w_plus    = lambda f, c, k: k*f*c/(1-c)
fc_to_w         = lambda f, c, k: k*c/(1-c)
fc_to_w_minus   = lambda f, c, k: k*(1-f)*c/(1-c)

w_to_f          = lambda w_plus, w: w_plus/w
w_to_c          = lambda w, k     : w/(w+k)

# lu_to_w_plus    = lambda 

def truth_from_w(w_plus, w, k):
    f, c = (w_to_f(w_plus, w), w_to_c(w, k)) if w != 0 else (0.5, 0.0)
    return Truth(f, c, k)

def w_from_truth(truth: Truth):
    f, c, k = truth.f, truth.c, truth.k
    return fc_to_w_plus(f, c, k), fc_to_w_minus(f, c, k)