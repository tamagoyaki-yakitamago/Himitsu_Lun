import os
import re
import secrets

from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir

PATH = "storage/"

# ファイル名がアップロードディレクトリ先で重複しているかをチェックする
def check_if_filename_duplicated(filename):
    return os.path.exists(PATH + filename)


# アップロードディレクトリ先で、ファイル名が存在しているかをチェックする
def check_if_filename_exist(filename):
    return os.path.exists(PATH + filename)


# アップロードされたファイルからシェアを作成して返す
def create_shares(filename, content):
    key = get_random_bytes(16)
    shares = Shamir.split(2, 3, key)
    share_dict = {}

    for idx, share in shares:
        share_dict["%d" % idx] = hexlify(share)

    cipher = AES.new(key, AES.MODE_EAX)
    ct, tag = cipher.encrypt(content), cipher.digest()

    try_count = 0
    while try_count < 10:
        tmp_filename = secrets.token_hex(16)
        if not check_if_filename_duplicated(tmp_filename):
            break
        try_count += 1

    if try_count >= 10:
        return {}, "error"

    file_content = cipher.nonce + tag + ct
    with open(PATH + tmp_filename, "xb") as fo:
        fo.write(cipher.nonce + tag + ct)

    return share_dict, tmp_filename


# 復元用のシェアを作成する
def create_shares_for_decrypt(id_list, share_list):
    shares = []
    for i in range(2):
        shares.append((int(id_list[i]), unhexlify(share_list[i])))

    return shares


# codeからファイルを復元する
def decrypt_file(code, shares):
    key = Shamir.combine(shares)

    with open(PATH + code, "rb") as fi:
        nonce, tag = [fi.read(16) for i in range(2)]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        try:
            result = cipher.decrypt(fi.read())
            cipher.verify(tag)

            return True
        except ValueError:

            return False

