from Compiler.library import *
from Compiler import mpc_math
from Compiler.types import MultiArray


def copy_array_2d(a):
    b = a.same_shape()
    @for_range(len(a))
    def f(i):
        b[i] = Array.create_from(a[i])
    return b


def secure_perm_inv(sp, v):
    assert len(sp) == len(v)

    sp_copy = Array.create_from(sp)
    v_copy = Array.create_from(v)

    shuffle = sint.get_secure_shuffle(len(sp))
    sp_copy.secure_permute(shuffle)
    v_copy.secure_permute(shuffle)
    plain_sp = sp_copy.reveal()
    v_copy.permute(plain_sp, reverse=True)
    return v_copy

def secure_perm(sp, v):
    assert len(sp) == len(v)

    sp_copy = Array.create_from(sp)
    v_copy = Array.create_from(v)

    shuffle = sint.get_secure_shuffle(len(sp))
    sp_copy.secure_permute(shuffle)
    plain_sp = sp_copy.reveal()
    v_copy.permute(plain_sp)
    v_copy.secure_permute(shuffle, reverse=True)
    return v_copy

def print_array_3d(x, len1, len2,len3):
    @for_range(len1)
    def f(i):
        @for_range(len2)
        def g(j):
            values = [x[i][j][k].reveal() for k in range(len3)]
            print_ln('x[%s][%s][:] = %s', i, j, values)

def print_array_2d(x, len1, len2):
    @for_range(len1)
    def f(i):
        values = [x[i][k].reveal() for k in range(len2)]
        print_ln('x[%s][:] = %s', i, values)

def print_array(x, len1):
    values = [x[k].reveal() for k in range(len1)]
    print_ln('x[:] = %s',  values)

def sfix_to_sint(a):
    return a.v
def sint_to_sfix(a):
    return a / (1 << sint(sfix.f))

# 按照小端序串接，后面的是高位
def bit_concat(a, b, bit_length_a, bit_length_b):
    # return sint(0)
    a_bits = a.bit_decompose(bit_length_a)
    b_bits = b.bit_decompose(bit_length_b)
    c_bits = a_bits + b_bits
    return sint.bit_compose(c_bits)

def bit_split(x, bit_length_a, bit_length_b):
    # return sint(0), sint(0)
    length = bit_length_a + bit_length_b
    x_bits = x.bit_decompose(length)
    bits_a = [x_bits[i] for i in range(bit_length_a)]

    bits_b = [x_bits[i] for i in range(bit_length_a, bit_length_a + bit_length_b)]
    return sint.bit_compose(bits_a),sint.bit_compose(bits_b)

# 定义计算距离的函数
def dist(v1, v2, length):
    # 初始化差值
    sum_of_squares = sfix(0)
    # 计算向量差的平方和
    for i in range(length):
        diff = v1[i] - v2[i]
        sum_of_squares += diff * diff
    # 计算平方根
    # distance = mpc_math.sqrt(sum_of_squares)
    # return distance
    return sum_of_squares


def swap(a,i1,i2):
    temp = a[i1]
    a[i1] = a[i2]
    a[i2] = temp


