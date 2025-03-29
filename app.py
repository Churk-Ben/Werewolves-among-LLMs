from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
from game_logic import Game, GamePhase, Role
from ai_player import AIPlayer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 游戏实例
game = Game()
ai_players = {}

# AI玩家名称
AI_NAMES = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']

def broadcast_game_state():
    state = {
        'phase': game.phase.value,
        'players': [{'name': p.name, 'is_alive': p.is_alive} for p in game.players]
    }
    emit('game_state', state, broadcast=True)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    if not game.players:  # 如果游戏还没开始，初始化游戏
        # 创建AI玩家
        for name in AI_NAMES:
            ai_players[name] = AIPlayer(name, game)
        
        # 初始化游戏
        game.initialize_game(AI_NAMES)
        
        # 分配角色给AI玩家
        for player in game.players:
            ai_players[player.name].role = player.role
        
        broadcast_game_state()
        
        # 开始游戏循环
        socketio.start_background_task(game_loop)

@socketio.on('message')
def handle_message(data):
    # 将玩家身份改为法官
    player_name = '法官' if data['player'] == '玩家一' else data['player']
    message = {
        'player': player_name,
        'content': data['content'],
        'type': data['type']  # 'thought' or 'speech'
    }
    emit('message', message, broadcast=True)
    
    # 处理游戏指令
    content = data['content'].strip()
    if content == '天黑请闭眼':
        if game.phase == GamePhase.DAY:
            game.phase = GamePhase.VOTING
            broadcast_game_state()
            emit('message', {
                'player': 'System',
                'content': '天黑请闭眼，进入投票阶段',
                'type': 'speech'
            }, broadcast=True)
            # 触发AI玩家投票
            for name, ai_player in ai_players.items():
                if game.get_player_by_name(name).is_alive:
                    thought = ai_player.think(GamePhase.VOTING)
                    emit('message', {
                        'player': name,
                        'content': thought,
                        'type': 'thought'
                    }, broadcast=True)
                    
                    vote_target = ai_player.make_decision(GamePhase.VOTING)
                    if vote_target:
                        game.votes[name] = vote_target
                        emit('message', {
                            'player': name,
                            'content': f'我投票给{vote_target}。',
                            'type': 'speech'
                        }, broadcast=True)
            
            # 处理投票结果并进入夜晚阶段
            eliminated_player = game.process_vote()
            if eliminated_player:
                emit('message', {
                    'player': 'System',
                    'content': f'{eliminated_player}被投票出局。',
                    'type': 'speech'
                }, broadcast=True)
            
            game.votes = {}
            if not game.check_game_end():
                game.phase = GamePhase.NIGHT
                game.day_count += 1
                broadcast_game_state()
                emit('message', {
                    'player': 'System',
                    'content': f'第{game.day_count}天夜晚开始',
                    'type': 'speech'
                }, broadcast=True)

def game_loop():
    # 游戏开始提示
    emit('message', {
        'player': 'System',
        'content': '游戏开始！我是法官，我会主持这场狼人杀游戏。',
        'type': 'speech'
    }, broadcast=True)
    
    while not game.check_game_end():
        # 夜晚阶段
        if game.phase == GamePhase.NIGHT:
            for name, ai_player in ai_players.items():
                if game.get_player_by_name(name).is_alive:
                    # 发送AI思考过程
                    thought = ai_player.think(GamePhase.NIGHT)
                    emit('message', {
                        'player': name,
                        'content': thought,
                        'type': 'thought'
                    }, broadcast=True)
                    
                    # 发送AI决策
                    decision = ai_player.make_decision(GamePhase.NIGHT)
                    if decision:
                        emit('message', {
                            'player': name,
                            'content': f'我决定对{decision}采取行动。',
                            'type': 'speech'
                        }, broadcast=True)
            
            game.next_phase()
            broadcast_game_state()
            socketio.sleep(2)  # 给玩家时间阅读消息
        
        # 白天阶段
        elif game.phase == GamePhase.DAY:
            for name, ai_player in ai_players.items():
                if game.get_player_by_name(name).is_alive:
                    thought = ai_player.think(GamePhase.DAY)
                    emit('message', {
                        'player': name,
                        'content': thought,
                        'type': 'thought'
                    }, broadcast=True)
            
            game.next_phase()
            broadcast_game_state()
            socketio.sleep(2)
        
        # 投票阶段
        elif game.phase == GamePhase.VOTING:
            for name, ai_player in ai_players.items():
                if game.get_player_by_name(name).is_alive:
                    thought = ai_player.think(GamePhase.VOTING)
                    emit('message', {
                        'player': name,
                        'content': thought,
                        'type': 'thought'
                    }, broadcast=True)
                    
                    vote_target = ai_player.make_decision(GamePhase.VOTING)
                    if vote_target:
                        game.votes[name] = vote_target
                        emit('message', {
                            'player': name,
                            'content': f'我投票给{vote_target}。',
                            'type': 'speech'
                        }, broadcast=True)
            
            eliminated_player = game.next_phase()
            if eliminated_player:
                emit('message', {
                    'player': 'System',
                    'content': f'{eliminated_player}被投票出局。',
                    'type': 'speech'
                }, broadcast=True)
            
            broadcast_game_state()
            socketio.sleep(2)
    
    # 游戏结束
    emit('message', {
        'player': 'System',
        'content': f'游戏结束！{game.winner}获胜！',
        'type': 'speech'
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)