import argparse
import random


# random.seed(123)

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
VERIFY_FNAME = 'verify.txt'

def generate_keys():
    """-k handler"""
    data = load_file(ELGAMAL_FNAME)
    data = get_strlist_as_intlist(data)
    assert 2 == len(data), 'bad elgamal.txt file'

    prime_n, generator = data
    private_key = random.randint(10, 1000000)  # b
    public_key = pow(generator, private_key, prime_n)

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
    gk = pow(gen, rand_k, prime_n)
    mbk = (msg * pow(pbkey, rand_k, prime_n)) % prime_n

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
    factor = pow(c1, pkey, prime_n)
    factor_1 = modinv(factor, prime_n)  # (c1^a)^-1
    message = (c2 * factor_1) % prime_n  # (c2*(c1^a)^-1) % p
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


    while True:
        k = random.randint(1, 1000000)
        gcd_ = gcd(k, prime_n - 1)
        if gcd_ == 1:
            break

    # r = (g^k) % p
    r = pow(gen, k, prime_n)
    # x = (m−b*r)*k^(−1) % (p−1)
    k_1 = modinv(k, prime_n - 1)
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


    # sprawdzając równość (mod p) dwu wielkości: g^m oraz r^x * β^r.
    # β^r * r^s = α^m mod p
    # gm = (gen ** msg) % prime_n
    gm = pow(gen, msg, prime_n)
    rx = pow(r, x, prime_n)
    br = pow(pbkey, r, prime_n)
    rxbr = (rx * br) % prime_n
    result = 'T' if (gm == rxbr) else 'N'
    data = [gm, rxbr]
    data = '\n'.join(get_intlist_as_strlist(data)) + '\n' + result
    print(result)
    save_data(VERIFY_FNAME, data)


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


def gcd(a, b):
    if a == 0:
        return b
    return gcd(b % a, a)


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


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
