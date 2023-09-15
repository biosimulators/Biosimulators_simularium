def interleave_bits(*args):
    """Interleave bits of multiple integer arguments."""
    result = 0
    num_values = len(args)
    for i in range(32):  # Using 32 bits for each coordinate (this is adjustable)
        for j, arg in enumerate(args):
            result |= ((arg >> i) & 1) << (i * num_values + j)
    return result


def deinterleave_bits(value, num_values):
    """Deinterleave bits into multiple integer values."""
    results = [0] * num_values
    for i in range(32):
        for j in range(num_values):
            results[j] |= ((value >> (i * num_values + j)) & 1) << i
    return results


def coordinates_to_id(x, y, z):
    return interleave_bits(x, y, z)


def id_to_coordinates(value):
    return deinterleave_bits(value, 3)


x, y, z = 12, 34, 56
id_value = coordinates_to_id(x, y, z)
print(id_value)
print(id_to_coordinates(id_value))  # Expected (12, 34, 56)