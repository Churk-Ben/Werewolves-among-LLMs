import os
from datetime import datetime
from typing import List, Dict


class GameLogger:
    def __init__(self, base_log_dir="logs"):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = os.path.join(base_log_dir, self.timestamp)
        self.player_log_files: Dict[str, str] = {}
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _log(self, file_path, message):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            f.flush()  # 强制刷新缓冲区，确保内容立即写入磁盘

    def _get_player_log_file(self, player_name: str) -> str:
        if player_name not in self.player_log_files:
            self.player_log_files[player_name] = os.path.join(
                self.log_dir, f"{player_name}.txt"
            )
        return self.player_log_files[player_name]

    def log_event(self, message: str, visible_to: List[str]):
        """将消息记录到指定玩家的日志文件中。"""
        for player_name in visible_to:
            log_file = self._get_player_log_file(player_name)
            self._log(log_file, message)

    def log_public_event(self, message: str, all_players: List[str]):
        """将消息记录到所有玩家的日志文件中。"""
        self.log_event(message, all_players)
