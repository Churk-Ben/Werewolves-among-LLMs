from server.Server import GameServer


def main():
    server = GameServer()
    server.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
