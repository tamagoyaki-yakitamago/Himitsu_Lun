import responder

from process import (
    add_response_headers,
    delete_file,
    check_if_filename_match,
    check_if_filename_duplicated,
    check_if_filename_exist,
    create_shares,
    create_shares_for_decrypt,
    decrypt_file,
)

api = responder.API()
one_mbyte = 1024 ** 2
# Content-Type
CONTENT_TYPE = {"zip": "application/zip"}
URL = "http://localhost/"


@api.route("/")
class Index:
    def on_get(self, req, res):
        res = add_response_headers(res)
        # delete_file()
        res.headers["Content-Type"] = "text/html; charset=utf-8"

        res.content = api.template("index.html")

    async def on_post(self, req, res):
        res = add_response_headers(res)
        data = await req.media(format="files")
        file = data.get("file")
        filename = file.get("filename")
        content = file.get("content")
        content_type = file.get("content-type")

        # 1. content_typeが"application/zip"か確認
        if not content_type == "application/zip":
            message = """1
            ひみつるんにアップロードする際に、問題が発生しました。<br>
            お手数ですが、時間をおいて再度アップロードしてください。<br>
            """
            res.headers["Content-Type"] = "text/html; charset=utf-8"

            res.content = api.template("index.html", error_message=message)

        # 2. ファイル拡張子が".zip"かどうか確認
        elif not filename[-4:] == ".zip":
            message = """2
            ひみつるんにアップロードする際に、問題が発生しました。<br>
            お手数ですが、時間をおいて再度アップロードしてください。<br>
            """
            res.headers["Content-Type"] = "text/html; charset=utf-8"

            res.content = api.template("index.html", error_message=message)

        # 3. contentの容量が10MB以下かどうか確認
        elif len(content) > 10 * one_mbyte:
            message = """3
            ひみつるんにアップロードする際に、問題が発生しました。<br>
            お手数ですが、時間をおいて再度アップロードしてください。<br>
            """
            res.headers["Content-Type"] = "text/html; charset=utf-8"

            res.content = api.template("index.html", error_message=message)

        else:
            share_dict, tmp_filename = create_shares(filename, content)

            if tmp_filename == "error":
                message = """4
                ひみつるんにアップロードする際に、問題が発生しました。<br>
                お手数ですが、時間をおいて再度アップロードしてください。<br>
                """
                res.headers["Content-Type"] = "text/html; charset=utf-8"

                res.content = api.template("index.html", error_message=message)

            else:
                message = """
                ひみつるんにアップロードが完了しました。<br>
                データの復元をするには、次のURLにアクセスしてください。<br>
                <p class="url">%s%s</p>
                <ul>
                <li>ひみつるんきー：</li>
                <li>#%s：%s</li>
                </ul>
                """ % (
                    URL,
                    tmp_filename,
                    "1",
                    share_dict["1"].decode("utf-8"),
                )
                res.headers["Content-Type"] = "text/html; charset=utf-8"

                res.content = api.template("index.html", message=message)


@api.route("/{code}")
class Decrypt:
    def on_get(self, req, res, code):
        res = add_response_headers(res)
        res.headers["Content-Type"] = "text/html; charset=utf-8"
        # delete_file()

        # コードの形式チェック
        if not check_if_filename_match(code):
            res.status_code = api.status_codes.HTTP_400

        # コードが正しいかチェック（ファイル存在チェック）
        if not res.status_code == 400:
            if not check_if_filename_exist(code):
                res.status_code = api.status_codes.HTTP_400

        if not res.status_code == 400:
            res.content = api.template("decrypt.html", code=code)
        else:
            res.content = api.template("error.html")

    async def on_post(self, req, res, code):
        res = add_response_headers(res)
        data = await req.media()
        req_code = data.get("code")

        # コードの形式チェック（code）
        if not check_if_filename_match(code):
            res.status_code = api.status_codes.HTTP_400

        # コードの形式チェック（req_code）
        if not res.status_code == 400:
            if not check_if_filename_match(req_code):
                res.status_code = api.status_codes.HTTP_400

        # コードが正しいかチェック（ファイル存在チェック）
        if not res.status_code == 400:
            if not (check_if_filename_exist(code) and code == req_code):
                res.status_code = api.status_codes.HTTP_400

        if not res.status_code == 400:
            share = data.get("share")

            # Noneが含まれていないか判定
            if not res.status_code == 400:
                if share is None:
                    res.status_code = api.status_codes.HTTP_400

            # 復元用のシェア配列を作成する
            if not res.status_code == 400:
                shares = create_shares_for_decrypt(code, share)

            if not res.status_code == 400:
                if shares == "error":
                    res.status_code = api.status_codes.HTTP_400

            # codeからファイルを復元する
            if not res.status_code == 400:
                content, filename = decrypt_file(code, shares)
                if content == "error":
                    res.status_code = api.status_codes.HTTP_400

        if not res.status_code == 400:
            res.headers["Content-Type"] = CONTENT_TYPE.get("zip")
            res.headers["Content-Disposition"] = "attachment; filename=" + filename
            res.content = content
        else:
            res.headers["Content-Type"] = "text/html; charset=utf-8"
            res.content = api.template("error.html")
