from pythroses import nest_squares
        
def gcd(a, b):
    if b > a:
        a, b = b, a
    if b == 0:
        return 0
    if b == 1:
        return 1
    q = int(a / b)
    r = a - b * q    
    while r != 0:
        a, b = b, r
        q = int(a / b)
        r = a - b * q
    return b
    
def generate_pairs(start, finish):
    if finish <= start:
        return []
    pairs = []
    n = start 
    while n < finish:
        m = n + 1
        while m <= finish:
            if gcd(m, n) == 1 and (m + n) % 2 == 1:
                a = m * m - n * n
                b = 2 * m * n
                if b < a:
                    a, b = b, a
                pairs.append([a, b])
            m += 1
        n += 1
    return pairs
            
def make_pyth_roses(leg_pairs, num, scale, color, prec):
    for pair in leg_pairs:
        nest_squares(pair[0], pair[1], num, scale, color, prec)
        
def make_roses(start, finish, num, scale, color):
    make_pyth_roses(generate_pairs(start, finish), num, scale, color, 4)
    
    
# example use    
make_roses(1, 5, 16, 5, "purple")
