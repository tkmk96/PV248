from sys import argv
from aiohttp import web


class Manager:
    def __init__(self):
        self.games = dict()
        self.id = 0

    def __get_game(self, game_id):
        return self.games.get(game_id)

    def new_game(self, name):
        if name is None:
            name = ''
        game = Game(name if name is not None else '', self.id)
        self.games[game.id] = game
        self.id += 1
        return game.id

    def game_status(self, game_id):
        game = self.__get_game(game_id)
        if game is not None:
            return game.status()
        return None

    def game_play(self, game_id, player, x, y):
        game = self.__get_game(game_id)
        if game is None:
            return None
        if game.winner is not None:
            return {'status': 'bad', 'message': 'Game has already ended!'}
        if game.validate_turn(player):
            return {'status': 'bad', 'message': 'Player is not on the turn!'}
        if game.validate_field(x, y):
            return {'status': 'bad', 'message': 'Position is not empty!'}
        game.make_move(player, x, y)
        return {'status': 'ok'}

    def game_exists(self, game_id):
        return self.__get_game(game_id) is not None


class Game:
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.board = [[0, 0, 0],[0, 0, 0],[0, 0, 0]]
        self.next = 1
        self.moves = 0
        self.winner = None

    def status(self):
        if self.winner is None:
            return {'board': self.board, 'next': self.next}
        return {'board': self.board, 'winner': self.winner}

    def make_move(self, player, x, y):
        self.board[x][y] = player
        self.next = abs(self.next - 3)
        self.moves += 1
        self.check_game_over_condition(player, x, y)

    def check_game_over_condition(self, player, x, y):
        r = [0, 1, 2]

        for i in r:
            if self.board[i][y] != player:
                break
        else:
            self.winner = player
            return

        for i in r:
            if self.board[x][i] != player:
                break
        else:
            self.winner = player
            return

        if x == y and self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            self.winner = player
            return

        if (y == 0 and x == 2) or (y == 2 and x == 2):
            if self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
                self.winner = player
                return

        if self.moves == 9:
            self.winner = 0

    def validate_turn(self, player):
        return self.next != player

    def validate_field(self, x, y):
        return self.board[x][y] != 0


routes = web.RouteTableDef()
manager = Manager()
app = web.Application()
port = int(argv[1])


@routes.get('/start')
async def start(request):
    # if 'name' not in request.query:
    #     return web.json_response({'id': manager.new_game(None)})
    return web.json_response({'id': manager.new_game(request.query.get('name'))})


@routes.get('/status')
async def status(request):
    if 'game' not in request.query:
        return web.json_response({'message': "'game' param is missing!"}, status=400)
    try:
        game_id = int(request.query['game'])
    except:
        return web.json_response({'message': "'game' param must be a valid number!"}, status=400)

    game_status = manager.game_status(game_id)
    if game_status is None:
        return web.json_response({'message': 'Game does not exist!'}, status=404)
    return web.json_response(game_status)


def validate_position(x, y):
    if x < 0 or x > 2 or y < 0 or y > 2:
        return True
    return False


def validate_player(player):
    if player != 1 and player != 2:
        return True
    return False


@routes.get('/play')
async def play(request):
    if 'game' not in request.query:
        return web.json_response({'message': "'game' param is missing!"}, status=400)

    if 'player' not in request.query or 'x' not in request.query or 'y' not in request.query:
        return web.json_response({'status': 'bad', 'message': "Params 'player', 'x','y' are required!"})

    try:
        game_id = int(request.query['game'])
        player = int(request.query['player'])
        x = int(request.query['x'])
        y = int(request.query['y'])
    except:
        return web.json_response({'message': "Params 'game', 'player', 'x','y' must be valid integers"}, status=400)

    if not manager.game_exists(game_id):
        return web.json_response({'message': 'Game does not exist!'}, status=404)
    if validate_player(player):
        return web.json_response({'status': 'bad', 'message': "Param 'player' must be 1 or 2!"})
    if validate_position(x, y):
        return web.json_response({'status': 'bad', 'message': "Params 'x' and 'y' must be in range [0,1,2]!"})
    return web.json_response(manager.game_play(game_id, player, x, y))

app.add_routes(routes)
web.run_app(app, port=port)