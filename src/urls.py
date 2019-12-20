import responder

from process import create_shares

api = responder.API()


@api.route("/")
class Index:
    def on_get(self, req, res):
        res.content = api.template("index.html")

    async def on_post(self, req, res):
        data = await req.media(format="files")
        file = data["file"]
        filename = file["filename"]
        content = file["content"]
        content_type = file["content-type"]
        if len(content) > 10000000:
            message = """
            ひみつるんにアップロードする際に、問題が発生しました。<br>
            お手数ですが、時間をおいて再度アップロードしてください。<br>
            """
        else:
            share_dict, tmp_filename = create_shares(filename, content)

            if tmp_filename == "error":
                message = """
                ひみつるんにアップロードする際に、問題が発生しました。<br>
                お手数ですが、時間をおいて再度アップロードしてください。<br>
                """
            else:
                message = """
                ひみつるんにアップロードが完了しました。<br>
                データの復元をするには、次のURLにアクセスしてください。<br>
                （データの復元には、3つのひみつるんきーのうち2つが必要です）<br>
                <p class="url">http://localhost/%s</p>
                <ul>
                <li>ひみつるんきー：</li>
                <li>#%s：%s</li>
                <li>#%s：%s</li>
                <li>#%s：%s</li>
                </ul>
                """ % (
                    tmp_filename,
                    "1",
                    share_dict["1"].decode("utf-8"),
                    "2",
                    share_dict["2"].decode("utf-8"),
                    "3",
                    share_dict["3"].decode("utf-8"),
                )

        res.content = api.template("index.html", message=message)

