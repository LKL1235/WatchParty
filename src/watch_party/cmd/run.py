import waitress
from watch_party.main import app, main


def run():
    port = main()
    if port is None:
        port = 5070
    waitress.serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()
