#
cdef class Term:
    cdef bool hashed
    cdef long hash_value
    atoms = []
