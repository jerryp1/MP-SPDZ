import itertools
from Compiler import types, library, instructions
from Compiler import comparison, util

def dest_comp(B):
    Bt = B.transpose()
    St_flat = Bt.get_vector().prefix_sum()
    Tt_flat = Bt.get_vector() * St_flat.get_vector()
    Tt = types.Matrix(*Bt.sizes, B.value_type)
    Tt.assign_vector(Tt_flat)
    return sum(Tt) - 1

def reveal_sort(k, D, reverse=False):
    r""" Sort in place according to "perfect" key. The name hints at the fact
    that a random order of the keys is revealed.

    :param k: vector or Array of sint containing exactly :math:`0,\dots,n-1`
      in any order
    :param D: Array or MultiArray to sort
    :param reverse: wether :py:obj:`key` is a permutation in forward or
      backward order

    """
    comparison.require_ring_size(util.log2(len(k)) + 1, 'sorting')
    assert len(k) == len(D)
    library.break_point()
    shuffle = types.sint.get_secure_shuffle(len(k))
    k_prime = k.get_vector().secure_permute(shuffle).reveal()
    idx = types.Array.create_from(k_prime)
    if reverse:
        D.assign_vector(D.get_slice_vector(idx))
        library.break_point()
        D.secure_permute(shuffle, reverse=True)
    else:
        D.secure_permute(shuffle)
        library.break_point()
        v = D.get_vector()
        D.assign_slice_vector(idx, v)
    library.break_point()
    instructions.delshuffle(shuffle)

def radix_sort(k, D, n_bits=None, signed=True):
    """ Sort in place according to key.

    :param k: keys (vector or Array of sint or sfix)
    :param D: Array or MultiArray to sort
    :param n_bits: number of bits in keys (int)
    :param signed: whether keys are signed (bool)

    """
    assert len(k) == len(D)
    # 这里会输出一个sbitint的矩阵，都是64bits
    bs = types.Matrix.create_from(k.get_vector().bit_decompose(n_bits))
    if signed and len(bs) > 1:
        bs[-1][:] = bs[-1][:].bit_not()
    # 根据bs生成permutation，再apply到D中。
    radix_sort_from_matrix(bs, D)

def radix_sort_perm(k, D, n_bits=None, signed=True):
    """ Sort in place according to key.

    :param k: keys (vector or Array of sint or sfix)
    :param D: Array or MultiArray to sort
    :param n_bits: number of bits in keys (int)
    :param signed: whether keys are signed (bool)

    """
    assert len(k) == len(D)
    # 这里会输出一个sbitint的矩阵，都是64bits
    bs = types.Matrix.create_from(k.get_vector().bit_decompose(n_bits))
    if signed and len(bs) > 1:
        bs[-1][:] = bs[-1][:].bit_not()
    # 根据bs生成permutation，再apply到D中。
    return radix_sort_from_matrix_perm(bs, D)

def radix_sort_from_matrix(bs, D):
    n = len(D)
    for b in bs:
        assert(len(b) == n)
    B = types.sint.Matrix(n, 2)
    h = types.Array.create_from(types.sint(types.regint.inc(n)))
    @library.for_range(len(bs))
    def _(i):
        b = bs[i]
        # B是CCS'22中的两个f
        B.set_column(0, 1 - b.get_vector())
        B.set_column(1, b.get_vector())
        # c 是当前的permutation
        c = types.Array.create_from(dest_comp(B))
        # 用c来更新permutation h(compose)
        reveal_sort(c, h, reverse=False)
        # 前面n-i个，只apply permutation到单个bit （CCS’22中的算法）
        @library.if_e(i < len(bs) - 1)
        def _():
            # 用更新后的permutation h来置换bs[i+1]
            reveal_sort(h, bs[i + 1], reverse=True)
        # 最后，把permutation h apply到整个value D 中
        @library.else_
        def _():
            reveal_sort(h, D, reverse=True)

def radix_sort_from_matrix_perm(bs, D):
    n = len(D)
    for b in bs:
        assert(len(b) == n)
    B = types.sint.Matrix(n, 2)
    h = types.Array.create_from(types.sint(types.regint.inc(n)))
    result = h.same_shape()
    @library.for_range(len(bs))
    def _(i):
        b = bs[i]
        # B是CCS'22中的两个f
        B.set_column(0, 1 - b.get_vector())
        B.set_column(1, b.get_vector())
        # c 是当前的permutation
        c = types.Array.create_from(dest_comp(B))
        # 用c来更新permutation h(compose)
        reveal_sort(c, h, reverse=False)
        # 前面n-i个，只apply permutation到单个bit （CCS’22中的算法）
        @library.if_e(i < len(bs) - 1)
        def _():
            # 用更新后的permutation h来置换bs[i+1]
            reveal_sort(h, bs[i + 1], reverse=True)
        # 最后，把permutation h apply到整个value D 中
        @library.else_
        def _():
            pass
    return h

