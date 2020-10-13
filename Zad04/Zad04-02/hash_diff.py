import argparse
from collections import OrderedDict


parser = argparse.ArgumentParser(description='Calculating hash diffs')
parser.add_argument('--fpath', type=str, required=True, dest='FPATH')


def get_bits_diff(byte_arr1, byte_arr2):
    # eg.: byte_arr1 = [170, 240, 160]
    bits1_str = get_bits_str(byte_arr1)  # d7c122779405766a14f895153c7ab633 as bits str
    bits2_str = get_bits_str(byte_arr2)

    diff = 0

    for bit1, bit2 in zip(bits1_str, bits2_str):
        if bit1 != bit2:
            diff += 1

    return diff


def get_bits_str(byte_arr):
    bits_str = ''
    for byte in byte_arr:
        bin_str = bin(byte)  # '0b11001100'
        bin_str = bin_str[2:]  # '11001100'
        zeros_to_fill = 8 - len(bin_str)
        if zeros_to_fill > 0:
            bin_str = '0' * zeros_to_fill + bin_str
        bits_str += bin_str

    return bits_str


if __name__ == '__main__':
    args = parser.parse_args()

    hash_func_name_to_hex_size_map = OrderedDict({
        'md5sum': int(128 / 4),
        'sha1sum': int(160 / 4),
        'sha224sum': int(224 / 4),
        'sha256sum': int(256 / 4),
        'sha384sum': int(384 / 4),
        'sha512sum': int(512 / 4)
    })

    lines = []
    with open(args.FPATH, 'r') as f:
        lines = f.read().splitlines()

    assert lines, 'lack of lines!'
    assert len(lines) == 12, 'not enough lines!'

    beg_idx = 0
    step = 2
    proc_cmd = 'cat hash.pdf personal.txt |'
    proc2_cmd = 'cat hash.pdf personal_.txt |'
    msg = 'Liczba rozniacych sie bitow: '
    diffs_list = []

    for key, val in hash_func_name_to_hex_size_map.items():
        line1, line2 = lines[beg_idx:beg_idx+step]
        hash1_key_as_str = line1[:val]  # eg.: d7c122779405766a14f895153c7ab633
        hash2_key_as_str = line2[:val]
        byte_arr1 = bytearray.fromhex(hash1_key_as_str)
        byte_arr2 = bytearray.fromhex(hash2_key_as_str)

        bits_diff = get_bits_diff(byte_arr1, byte_arr2)
        bits_diff_perc = (bits_diff / (val * 4)) * 100

        """cat hash.pdf personal.txt | md5sum
        cat hash.pdf personal_.txt | md5sum
        f6df877b14aa1ee2c024bef98d1fb0c0
        f82923c0fda16eeb90ed012245cbee4a
        Liczba rozniacych sie bitow: 65 z 128, procentowo: 51%."""

        diff_str = ''
        diff_str += f'{proc_cmd} {key}\n'
        diff_str += f'{proc2_cmd} {key}\n'
        diff_str += f'{hash1_key_as_str}\n'
        diff_str += f'{hash2_key_as_str}\n'
        diff_str += f'{msg} {bits_diff} z {val * 4}, procentowo: {round(bits_diff_perc)}%.\n\n'
        diffs_list.append(diff_str)

        beg_idx += step

    with open('diff.txt', 'w') as f:
        for diff in diffs_list:
            f.write(diff)
