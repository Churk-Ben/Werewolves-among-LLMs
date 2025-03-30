class Game:
    @staticmethod
    def parse_order(order):
        match True:
            case _ if "开始" in order:
                return Game.game_start
            case _ if "结束" in order:
                return Game.game_end
            case _:
                return Game.default

    @staticmethod
    def game_start():
        print("Game started")

    @staticmethod
    def game_end():
        print("Game ended")

    @staticmethod
    def default():
        print("Invalid order")
