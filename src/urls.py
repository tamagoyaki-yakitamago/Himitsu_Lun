import responder

api = responder.API()


@api.route("/")
class Index:
    def on_get(self, req, res):
        res.content = api.template("index.html")

