import argparse
import random


random.seed(123)

parser = argparse.ArgumentParser(description='crypto solution 5')
parser.add_argument('-k', action='store_true', dest='generate_keys')
parser.add_argument('-e', action='store_true', dest='encrypt_msg')
parser.add_argument('-d', action='store_true', dest='decrypt_msg')
parser.add_argument('-s', action='store_true', dest='sign_msg')
parser.add_argument('-v', action='store_true', dest='verify_sign')

ELGAMAL_FNAME = 'elgamal.txt'
PUBLIC_KEY_FNAME = 'public.txt'
PRIVATE_KEY_FNAME = 'private.txt'
MSG_FNAME = 'plain.txt'
ENCRYPTED_FNAME = 'crypto.txt'
DECRYPTED_FNAME = 'decrypt.txt'
MSG2_FNAME = 'message.txt'
SIGN_FNAME = 'signature.txt'


def generate_keys():
    """-k handler"""
    data = load_file(ELGAMAL_FNAME)
    data = get_strlist_as_intlist(data)
    assert 2 == len(data), 'bad elgamal.txt file'

    prime_n, generator = data
    private_key = random.randint(10, 1000000)  # b
    public_key = (generator ** private_key) % prime_n  # pb = g^b % p

    public_key_f = data + [public_key]
    public_key_f = '\n'.join(get_intlist_as_strlist(public_key_f))
    save_data(PUBLIC_KEY_FNAME, public_key_f)

    private_key_f = data + [private_key]
    private_key_f = '\n'.join(get_intlist_as_strlist(private_key_f))
    save_data(PRIVATE_KEY_FNAME, private_key_f)


def encrypt_msg():
    """-e handler"""
    data = load_file(PUBLIC_KEY_FNAME)
    data = get_strlist_as_intlist(data)
    assert 3 == len(data), 'bad public key'
    prime_n, gen, pbkey = data

    msg = load_file(MSG_FNAME)
    msg = get_strlist_as_intlist(msg)
    assert 1 == len(msg), 'bad message'
    msg = msg[0]
    assert msg < prime_n, 'bad message'

    rand_k = random.randint(100, 1000)
    gk = (gen ** rand_k) % prime_n
    mbk = (msg * (pbkey ** rand_k)) % prime_n

    crypto = [gk, mbk]
    crypto = '\n'.join(get_intlist_as_strlist(crypto))
    save_data(ENCRYPTED_FNAME, crypto)


def decrypt_msg():
    """-d handler"""
    data = load_file(PRIVATE_KEY_FNAME)
    data = get_strlist_as_intlist(data)
    assert 3 == len(data), 'bad private key'
    prime_n, gen, pkey = data

    crypto = load_file(ENCRYPTED_FNAME)
    crypto = get_strlist_as_intlist(crypto)
    assert 2 == len(crypto), 'bad cryptogram'

    c1, c2 = crypto
    factor = inversed_modulo(c1 ** pkey, prime_n)  # (c1^a)^-1
    message = (c2 * factor) % prime_n  # (c2*(c1^a)^-1) % p
    message = [message]
    message = '\n'.join(get_intlist_as_strlist(message))
    save_data(DECRYPTED_FNAME, message)


def sign_msg():
    """-s handler"""
    data = load_file(PRIVATE_KEY_FNAME)
    data = get_strlist_as_intlist(data)
    assert 3 == len(data), 'bad private key'
    prime_n, gen, pkey = data

    msg = load_file(MSG2_FNAME)
    msg = get_strlist_as_intlist(msg)
    assert 1 == len(msg), 'bad message'
    msg = msg[0]
    assert msg < prime_n, 'bad message'

    k = None
    while True:
        k = random.randint(10, 1000000)
        p_1 = prime_n - 1
        gcd_ = gcd(k, p_1)
        if gcd_ == 1:
            break

    # r = (g^k) % p
    r = (gen ** k) % prime_n
    # x = (m−b*r)*k^(−1) % (p−1)
    k_1 = inversed_modulo(k, prime_n - 1)
    mbr = (msg - (pkey * r)) % (prime_n - 1)
    # x = ((msg - (pkey * r)) * k_1) % (prime_n - 1)
    x = (mbr * k_1) % (prime_n - 1)
    sign = [r, x]
    sign = '\n'.join(get_intlist_as_strlist(sign))
    save_data(SIGN_FNAME, sign)


def verify_sign():
    """-v handler"""
    # (g^m) % p, ((r^x) * (β^r)) % p
    data = load_file(PUBLIC_KEY_FNAME)
    data = get_strlist_as_intlist(data)
    assert 3 == len(data), 'bad public key'
    prime_n, gen, pbkey = data

    msg = load_file(MSG2_FNAME)
    msg = get_strlist_as_intlist(msg)
    assert 1 == len(msg), 'bad message'
    msg = msg[0]

    sign = load_file(SIGN_FNAME)
    sign = get_strlist_as_intlist(sign)
    assert 2 == len(sign), 'bad signature'
    r, x = sign

    # gm = (gen ** msg) % prime_n
    gm = fme(gen, msg, prime_n)
    rx = fme(r, x, prime_n)
    br = fme(pbkey, r, prime_n)
    rxbr = (rx * br) % prime_n
    print(gm == rxbr)


def load_file(f_name):
    lines = []
    with open(f_name, 'r') as f:
        lines = f.readlines()
    return lines


def save_data(f_name, data):
    with open(f_name, 'w') as f:
        f.write(data)


def get_strlist_as_intlist(list_):
    return [int(elem) for elem in list_]


def get_intlist_as_strlist(list_):
    return [str(elem) for elem in list_]


def inversed_modulo(a, m):
    g = gcd(a, m)
    if g != 1:
        return -1
    else:
        return power(a, m - 2, m)


def power(x, y, m):
    if y == 0:
        return 1

    p = power(x, y // 2, m) % m
    p = (p * p) % m

    if y % 2 == 0:
        return p
    else:
        return (x * p) % m


def gcd(a, b):
    if a == 0:
        return b
    return gcd(b % a, a)


def fme(a, k, n):
    b = bin(k)[2:]
    m = len(b)
    r = 1
    x = a % n

    for i in range(m - 1, -1, -1):
        if b[i] == '1':
            r = r * x % n

    x **= 2
    x %= n

    return r


if __name__ == '__main__':
    args = parser.parse_args()

    if args.generate_keys:
        generate_keys()

    if args.encrypt_msg:
        encrypt_msg()

    if args.decrypt_msg:
        decrypt_msg()

    if args.sign_msg:
        sign_msg()

    if args.verify_sign:
        verify_sign()
