import math
import cmath
import aux


def lifting_up((x, y), alpha, int_factor):
    return (x + int_factor*int(round(alpha*y.real)) +
            int_factor*int(round(alpha*y.imag)), y)


def lifting_down((x, y), alpha, int_factor):
    return (x, y + int_factor*int(round(alpha*x.real)) +
            int_factor*int(round(alpha*x.imag)))


def rotation(v, angle):
    v = lifting_up(v, -math.tan(angle/2.0), 1)
    v = lifting_down(v, math.sin(angle), 1)
    v = lifting_up(v, -math.tan(angle/2.0), 1)
    return v


def inverse_rotation(v, angle):
    v = lifting_up(v, -math.tan(angle/2.0), -1)
    v = lifting_down(v, math.sin(angle), -1)
    v = lifting_up(v, -math.tan(angle/2.0), -1)
    return v


def scaling(v, factor):
    v = lifting_down(v, 1, 1)
    v = lifting_up(v, factor-1, 1)
    v = lifting_down(v, -1.0/factor, 1)
    v = lifting_up(v, factor - factor*factor, 1)
    return v


def inverse_scaling(v, factor):
    v = lifting_up(v, factor - factor*factor, -1)
    v = lifting_down(v, -1.0/factor, -1)
    v = lifting_up(v, factor-1, -1)
    v = lifting_down(v, 1, -1)
    return v


def dct_butterfly(x, (N, j)):
    angle = math.pi*j/(2.0*N)
    return rotation((int(x.real), int(x.imag)), angle)


def inverse_dct_butterfly((x, y), (N, j)):
    angle = math.pi*j/(2.0*N)
    v = inverse_rotation((x, y), angle)
    return v[0] + 1j*v[1]


def butterfly((x, y), (N, j)):
    yr = rotation((y.real, y.imag), -2*math.pi*j/N)
    y = yr[0] + yr[1]*1j
    v = (x, y)
    v = scaling(v, 1.0/math.sqrt(2))
    v = lifting_up(v, -0.5, 1)
    v = lifting_down(v, 1, 1)
    return v


def inverse_butterfly((x, y), (N, j)):
    v = (x, y)
    v = lifting_down(v, 1, -1)
    v = lifting_up(v, -0.5, -1)
    v = inverse_scaling(v, 1.0/math.sqrt(2))
    (x, y) = v
    yr = inverse_rotation((y.real, y.imag), -2*math.pi*j/N)
    y = yr[0] + yr[1]*1j
    return (x, y)


def butterfly_a(v):
    v = scaling(v, 1.0/math.sqrt(2))
    v = lifting_up(v, -0.5, 1)
    v = lifting_down(v, 1, 1)
    return v


def butterfly_b((x, y)):
    return (x + 1j*y, x - 1j*y)


def inverse_butterfly_a(v):
    v = lifting_down(v, 1, -1)
    v = lifting_up(v, -0.5, -1)
    v = inverse_scaling(v, 1.0/math.sqrt(2))
    return v


def inverse_butterfly_b((x, y)):
    return (int(x.real), int(x.imag))


def fft_8(v):
    """
        Compute integer FFT on an array of 8 elements
    """
    # Binary invert indexes
    v = aux.convert_array_8(v)
    #
    # First step (N = 1 to N = 2)
    #
    result = [0]*8
    (result[0], result[1]) = butterfly_a((v[0], v[1]))
    (result[2], result[3]) = butterfly_a((v[2], v[3]))
    (result[4], result[5]) = butterfly_a((v[4], v[5]))
    (result[6], result[7]) = butterfly_a((v[6], v[7]))
    #
    # Second step (N = 2 to N = 4)
    #
    v = result
    result = [0]*8
    (result[0], result[2]) = butterfly_a((v[0], v[2]))
    (result[1], result[3]) = butterfly_b((v[1], v[3]))
    (result[4], result[6]) = butterfly_a((v[4], v[6]))
    (result[5], result[7]) = butterfly_b((v[5], v[7]))
    #
    # Third step (N = 4 to N = 8)
    #
    v = result
    result = [0]*8
    (result[0], result[4]) = butterfly_a((v[0], v[4]))
    (result[1], result[5]) = butterfly((v[1], v[5]), (8, 1))
    (result[2], result[6]) = butterfly_b((v[2], v[6]))
    result[3] = result[5].conjugate()
    result[7] = result[1].conjugate()
    return result


def inverse_fft_8(v):
    """
        Compute inverse integer FFT on an array of 8 elements
    """
    #
    # First step (N = 8 to N = 4)
    #
    result = [0]*8
    (result[0], result[4]) = inverse_butterfly_a((v[0], v[4]))
    (result[1], result[5]) = inverse_butterfly((v[1], v[5]), (8, 1))
    (result[2], result[6]) = inverse_butterfly_b((v[2], v[6]))
    result[3] = result[1].conjugate()
    result[7] = result[5].conjugate()
    #
    # Second step (N = 4 to N = 2)
    #
    v = result
    result = [0]*8
    (result[0], result[2]) = inverse_butterfly_a((v[0], v[2]))
    (result[1], result[3]) = inverse_butterfly_b((v[1], v[3]))
    (result[4], result[6]) = inverse_butterfly_a((v[4], v[6]))
    (result[5], result[7]) = inverse_butterfly_b((v[5], v[7]))
    #
    # Second step (N = 2 to N = 1)
    #
    v = result
    result = [0]*8
    (result[0], result[1]) = inverse_butterfly_a((v[0], v[1]))
    (result[2], result[3]) = inverse_butterfly_a((v[2], v[3]))
    (result[4], result[5]) = inverse_butterfly_a((v[4], v[5]))
    (result[6], result[7]) = inverse_butterfly_a((v[6], v[7]))
    # Binary invert array
    result = aux.convert_array_8(result)
    return result


def dct_8(v):
    efft = fft_8((v + list(reversed(v)))[::2])
    result = [0]*8
    result[0] = efft[0]
    result[4] = efft[4]
    for k in xrange(1, 4):
        (result[k], result[8-k]) = \
            dct_butterfly(efft[k], (8, k))
    return result


def inverse_dct_8(v):
    efft = [0]*8
    efft[0] = v[0]
    efft[4] = v[4]
    for k in xrange(1, 4):
        efft[k] = inverse_dct_butterfly((v[k], v[8-k]), (8, k))
        efft[8-k] = efft[k].conjugate()
    iefft = inverse_fft_8(efft)
    result = [x for t in zip(iefft[:4], list(reversed(iefft[4:]))) for x in t]
    return result
