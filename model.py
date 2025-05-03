class Message:
    def __init__(self, head, player, content, type, room="ALL"):
        self.head = head
        self.player = player
        self.content = content
        self.type = type
        self.room = room

    # 序列化json
    def json(self):
        return {
            "head": self.head,
            "player": self.player,
            "content": self.content,
            "type": self.type,
            "room": self.room,
        }


class State:
    def __init__(self, players, messages, current_player, current_room):
        self.players = players
        self.messages = messages
        self.current_player = current_player
        self.current_room = current_room

    # 序列化json
    def json(self):
        return {
            "players": [p.json() for p in self.players],
            "messages": [m.json() for m in self.messages],
            "current_player": self.current_player,
            "current_room": self.current_room,
        }
