from urls import api

if __name__ == "__main__":
    api.run(address="0.0.0.0", port=80, debug=True)
    # api.run(debug=True)