import os
import re
import secrets
import json

from base64 import b64encode, b64decode
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from models import Himitsu_lun
from settings import session
from datetime import datetime, date, timedelta

PATH = "storage/"

# 指定したレスポンスヘッダを付与する
def add_response_headers(res):
    res.headers["X-Frame-Options"] = "SAMEORIGIN"
    res.headers["X-XSS-Protection"] = "1; mode=block"
    res.headers["X-Content-Type-Options"] = "nosniff"

    return res


# 削除するファイル一覧を取得する
def delete_file():
    now = datetime.now()
    shares = session.query(Himitsu_lun).filter(Himitsu_lun.delete_at < now).all()
    delete_file_list = []
    for share in shares:
        delete_file_list.append(f"{share.enc_filename}")

    for enc_filename in delete_file_list:
        count = 0
        while count < 2:
            print(count)
            if os.path.exists(PATH + enc_filename):
                os.remove(PATH + enc_filename)
                break
            else:
                count += 1

        session.query(Himitsu_lun).filter(
            Himitsu_lun.enc_filename == enc_filename
        ).delete()

    session.commit()


# DB登録用のシェア情報を暗号化する（CTRモード）
def enc_db_share(share):
    key = os.environ.get("KEY").encode("utf-8")

    share = share.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(share)
    nonce = b64encode(cipher.nonce).decode("utf-8")
    ct = b64encode(ct_bytes).decode("utf-8")
    enc_result = json.dumps({"nonce": nonce, "cipher_text": ct})

    return enc_result


# DB登録用のシェア情報を復号する（CRTモード）
def dec_db_share(nonce, cipher_text):
    key = os.environ.get("KEY").encode("utf-8")

    try:
        b64 = json.loads(json.dumps({"nonce": nonce, "cipher_text": cipher_text}))
        dec_nonce = b64decode(b64["nonce"])
        dec_ct = b64decode(b64["cipher_text"])
        cipher = AES.new(key, AES.MODE_CTR, nonce=dec_nonce)
        plain_text = cipher.decrypt(dec_ct)
        return plain_text.decode("utf-8")
    except (ValueError, KeyError):
        return "Incorrect decryption"


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

            insert_db(filename, tmp_filename, share_dict)
            break
        try_count += 1

    if try_count >= 10:
        return {}, "error"

    return share_dict, tmp_filename


# データベースに登録する
def insert_db(filename, tmp_filename, share_dict):
    himitsu_lun = Himitsu_lun()
    enc_json = enc_db_share(share_dict["3"].decode("utf-8"))
    enc_json = json.loads(enc_json)
    now = datetime.now()

    himitsu_lun.filename = filename
    himitsu_lun.enc_filename = tmp_filename
    himitsu_lun.share_id = "3"
    himitsu_lun.share = enc_json["cipher_text"]
    himitsu_lun.nonce = enc_json["nonce"]
    himitsu_lun.created_at = now
    himitsu_lun.delete_at = now + timedelta(days=3)

    session.add(himitsu_lun)
    session.commit()


# 復元用のシェアを作成する
def create_shares_for_decrypt(code, share):
    db_share = (
        session.query(Himitsu_lun).filter(Himitsu_lun.enc_filename == code).first()
    )
    db_dec_share = dec_db_share(f"{db_share.nonce}", f"{db_share.share}")
    if db_dec_share == "Incorrect decryption":
        return "error"

    shares = [(1, unhexlify(share)), (3, unhexlify(db_dec_share))]

    return shares


# codeからファイルを復元する
def decrypt_file(code, shares):
    key = Shamir.combine(shares)
    db_share = (
        session.query(Himitsu_lun).filter(Himitsu_lun.enc_filename == code).first()
    )
    filename = f"{db_share.filename}"

    with open(PATH + code, "rb") as fi:
        nonce, tag = [fi.read(16) for i in range(2)]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        try:
            result = cipher.decrypt(fi.read())
            cipher.verify(tag)

            return result, filename
        except ValueError:

            return "error", ""

