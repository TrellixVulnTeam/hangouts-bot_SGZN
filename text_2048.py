import random

games = dict()
current_game = None


def newline(text, number=1):
    return text.strip() + ("\n" * number)


class Cell():
    offset = 10

    def __init__(self, value=0):
        self.length = 1
        self.value = value
        self.has_merged = False


class Board():

    def __init__(self, mode):
        self.size = mode.size
        self.number_of_cells = self.size ** 2
        # creates empty board and adds 2 random blocks
        self.cells = [Cell() for i in range(self.number_of_cells)]

    def move_blocks(self, x, positive, game):
        """Moves all blocks in the board"""
        # generates indexes of cell for each row/column
        for i in range(self.size):
            if x:
                indexes = list(range(i * self.size, (i + 1) * self.size))
            else:
                indexes = list(range(i, self.number_of_cells, self.size))
            if positive:
                indexes.reverse()

            for j in indexes:
                current_cell = self.cells[j]
                current_cell.has_merged = False
                neighbor = self.cells[indexes[indexes.index(j) - 1]]

                if current_cell.value > 0:
                    while current_cell is not self.cells[indexes[0]]:
                        # moves if neighbor is empty
                        if neighbor.value == 0:
                            neighbor.value = current_cell.value
                            neighbor.has_merged = current_cell.has_merged
                            current_cell.value = 0
                            j = indexes[indexes.index(j) - 1]
                            current_cell = self.cells[j]
                            neighbor = self.cells[indexes[indexes.index(j) - 1]]
                        # merges blocks
                        elif (
                                current_cell.value == neighbor.value and not
                                current_cell.has_merged and not neighbor.has_merged
                                ):
                            current_cell.value = game.mode.increase(current_cell.value)
                            game.score += game.mode.increase_score(current_cell.value)
                            neighbor.value = 0
                            current_cell.has_merged = True
                        else:
                            break

    def check_can_move(self):
        """Checks if the player can move"""
        if not self.check_full():
            return True

        # checks if adjacent cells are the same
        for i in range(self.size):
            row_indexes = list(range(i * self.size, i * self.size + self.size))
            column_indexes = list(range(i, self.number_of_cells, self.size))
            for indexes in (row_indexes, column_indexes):
                for j in indexes:
                    if j is indexes[0]:
                        continue
                    if self.cells[j].value == self.cells[indexes[indexes.index(j) - 1]].value:
                        return True
        return False

    def check_full(self):
        """Checks if the board is full"""
        for cell in self.cells:
            if cell.value == 0:
                return False
        return True

    def make_new_block(self, mode):
        """Makes random new block"""
        empty_blocks = [cell for cell in self.cells if cell.value == 0]
        empty_cell = random.choice(empty_blocks)
        if random.randint(0, 10) == 10:
            value = mode.values[1]
        else:
            value = mode.values[0]
        empty_cell.value = value

    def draw_board(self, game):
        """Draws the board"""
        max_length = 0
        for cell in self.cells:
            cell.length = len(str(cell.value))
            max_length = cell.length if cell.length > max_length else max_length
        max_length += 1
        for row in range(game.mode.size):
            for column in range(game.mode.size):
                cell = game.board.cells[row * 4 + column]
                game.text += str(cell.value).ljust(max_length)
            game.text += "\n"


class GameMode():
    shuffled = [i for i in range(100)]
    random.shuffle(shuffled)

    def __init__(
        self, start_value=2, increase_type="normal",
        size=4, win_value=None, description="", shuffled=False
            ):
        self.size = size
        self.number_of_cells = size ** 2
        self.increase_type = increase_type
        self.high_score = 0
        if shuffled:
            self.values = GameMode.shuffled
        else:
            self.values = [start_value]
            for i in range(12):
                self.values.append(self.increase(self.values[-1]))
        self.win_value = win_value if win_value else self.values[10]
        self.description = description

    def increase(self, value):
        """Increases cell value based on game mode"""
        if self.increase_type == "normal":
            next_value = value * 2
        elif self.increase_type == "plus one":
            next_value = value + 1
        elif self.increase_type == "random":
            next_value = self.values[self.values.index(value) + 1]

        return next_value

    def increase_score(self, value):
        if self.increase_type == "normal":
            points = value
        elif self.increase_type == "plus one":
            points = 2 ** value
        elif self.increase_type == "random":
            points = 2 ** (self.values.index(value) + 1)

        return points


class Game():
    modes = {
        "normal": GameMode(description="normal 2048"),
        "65536": GameMode(size=5, win_value=65536, description="5x5 board and higher win condition"),
        str(2 ** 20): GameMode(size=6, win_value=2 ** 20, description="6x6 board and higher win condition"),
        "eleven": GameMode(1, "plus one", description="blocks increase by 1 when merging"),
        "twenty": GameMode(1, "plus one", win_value=20, description="eleven with a higher win condition"),
        "confusion": GameMode(1, "random", shuffled=True, description="randomly generated block sequence")
    }
    commands = {
        "restart": "restarts the game in the current gamemode",
        "gamemodes": "lists the gamemodes",
        "help": "prints this help text",
        "scores": "prints the highscore for each mode"
    }
    help_text = (
        "this is a 2048 clone by chendi",
        "how to play:",
        "move the tiles",
        "when 2 with the same value touch, they merge",
        "try to get the highest value posible without filling up the board",
        "commands:",
        "prefix all commands with 2048",
        "playing 2048 will not interfere with other bot commands",
        "all commands must be spelled correctly but are NOT case-sensitive",
        "note that the current game and highscores are reset when the bot resets",
        "move <direction> - move the tiles in the given direction (eg. move up) can be abbreviated (eg. m u)"
    )

    def __init__(self):
        self.score = 0
        self.text = ""
        self.mode = self.modes["normal"]
        self.state = "help"
        self.board = Board(self.mode)
        for i in range(2):
            self.board.make_new_block(self.mode)

    def update(self):
        """Draws based on current state"""

        if self.state == "help":
            self.text += newline("\n".join(self.help_text))
            for command, description in self.commands.items():
                self.text += f"{command} - {description}\n"

        if self.state == "won":
            self.draw_game()
            self.text += "you won, use move to continue playing"
        elif self.state == "lost":
            self.text += "you lost, use restart to restart, or gamemodes to get a list of gamemodes"
        elif self.state == "restart":
            self.restart()
        elif self.state == "gamemodes":
            self.text += "pick a gamemode or continue playing\n"
            for mode_name, mode in self.modes.items():
                self.text += f"{mode_name} - {mode.description}\n"
            self.state = None
        elif self.state == "scores":
            for mode_name, mode in self.modes.items():
                self.text += f"{mode_name}: {mode.high_score}\n"
            self.state = None

        self.text = newline(self.text, 2)
        self.draw_game()

    def draw_game(self):
        """Draws board and scores"""
        self.text += "score: " + str(self.score) + "\nhigh score: " + str(self.mode.high_score) + "\n"
        self.board.draw_board(self)

    def restart(self, mode=None):
        """Resets the game"""
        self.mode = mode if mode else self.mode
        self.score = 0
        if self.mode == Game.modes["confusion"]:
            self.setup_confusion()
        self.board = Board(self.mode)
        for i in range(2):
            self.board.make_new_block(self.mode)
        self.state = None

    def move(self, x, positive):
        """Moves all blocks"""
        if None in (x, positive):
            return
        if self.board.check_can_move():
            old_board_values = [cell.value for cell in self.board.cells]
            self.board.move_blocks(x, positive, self)

            # does not create new block if board is full or the board did not change
            if not self.board.check_full() and old_board_values != [cell.value for cell in self.board.cells]:
                self.board.make_new_block(self.mode)

        if self.score > self.mode.high_score:
            self.mode.high_score = self.score
        if not self.board.check_can_move():
            self.state = "lost"
        if self.state != "won":
            self.check_win()

    def check_win(self):
        for block in self.board.cells:
            if block.value == self.mode.win_value:
                self.state = "won"

    def setup_confusion(self):
        random.shuffle(GameMode.shuffled)
        Game.modes["confusion"].win_value = Game.modes["confusion"].values[10]


def play_game(command_list, game):

    game.text = ""
    try:
        command = command_list[0]
    except IndexError:
        command = None
    # check player movement
    if command in ("move", "m"):
        try:
            command = command_list[1]
        except IndexError:
            command = None
        x = None
        positive = None
        if command in ("up", "u"):
            x = False
            positive = False
        elif command in ("left", "l"):
            x = True
            positive = False
        elif command in ("down", "d"):
            x = False
            positive = True
        elif command in ("right", "r"):
            x = True
            positive = True
        else:
            game.text += "invalid move\n"
        game.move(x, positive)

    elif command in game.modes.keys():
        game.restart(Game.modes[command])
    elif command in game.commands.keys():
        game.state = command
    else:
        game.text += "invalid command, use help to see commands\n"

    game.update()
    return newline(game.text)


def create_game(game_name):
    current_game = games[game_name] = Game()
    return Game()


def run_game(commands):
    """"""
    # cleaning input
    if type(commands) == str:
        command_list = commands.lower().split()
    elif type(commands) == list:
        command_list = commands
    else:
        print("invalid input joseph wat r u doing")
    command = command_list[0]
    if command == "2048":
        command_list = command_list[1:]
        command = command_list[0]
    # get game_name
    if game_name in games:
        return play_game(command_list, games[game_name])
    else:
        create_game(game_name)


# testing via console
if __name__ == "__main__":
    game = Game()
    game_text = play_game([""], game)
    print(game_text)
    while True:
        text = input("enter a command: ").lower().split()
        if text and text[0] == "break":
            break
        game_text = play_game(text, game)
        print(game_text)
