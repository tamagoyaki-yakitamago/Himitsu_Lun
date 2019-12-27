import os
import re
import secrets

from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from models import Himitsu_lun
from settings import session
from datetime import datetime, date, timedelta

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
            file_content = cipher.nonce + tag + ct
            with open(PATH + tmp_filename, "wb") as fo:
                fo.write(cipher.nonce + tag + ct)

            insert_db(filename, share_dict)
            break
        try_count += 1

    if try_count >= 10:
        return {}, "error"

    return share_dict, tmp_filename


# データベースに登録する
def insert_db(filename, share_dict):
    himitsu_lun = Himitsu_lun()
    now = datetime.now()

    himitsu_lun.filename = filename
    himitsu_lun.share_id = "3"
    himitsu_lun.share = share_dict["3"].decode("utf-8")
    himitsu_lun.created_at = now
    himitsu_lun.delete_at = now + timedelta(days=3)

    session.add(himitsu_lun)
    session.commit()

    shares = session.query(Himitsu_lun).all()
    for share in shares:
        print(f"{share.filename} {share.share} {share.delete_at}")


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

