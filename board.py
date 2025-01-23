import random
import enum

class Animations(enum.Enum):
    NewTile = enum.auto()
    MoveTile = enum.auto()
    MergeTile = enum.auto()

class Board:
    def __init__(self):
        self.tiles = [[0 for _ in range(4)] for _ in range(4)]
        self.static_tiles = []
        self.animations = []
        self.queue = []

    def get_tile(self, row, column):
        return self.tiles[row][column]

    def new_tile(self):
        empty_locations = []
        for i in range(4):
            for j in range(4):
                if self.get_tile(i, j) == 0:
                    empty_locations.append((i, j))
        chosen_location = random.choice(empty_locations)
        chosen_number = random.choices([2, 4], cum_weights=[9, 10])[0]
        return chosen_location, chosen_number

    def queue_new_tile(self):
        self.queue.append((Animations.NewTile, self.new_tile()))

    def queue_move_tile(self, before, after):
        self.queue.append((Animations.MoveTile, (before, after)))

    def play_move(self, move):
        # TODO: merge all 4 branches
        if move == 0:
            # Down, row increases
            for col in range(4):
                line = [self.tiles[row][col] for row in range(4)]
                can_merge = [True for _ in range(4)]
                for row in [2, 1, 0]:
                    if line[row] == 0 or line[row + 1] != line[row] and line[row + 1] != 0:
                        # no tile or cannot move
                        continue
                    dest_row = row
                    while True:
                        if dest_row != 3 and line[dest_row + 1] == line[row] and can_merge[dest_row + 1]:
                            dest_row += 1
                            self.queue_move_tile((row, col), (dest_row, col))
                            line[dest_row] = line[row] * 2
                            line[row] = 0
                            can_merge[dest_row] = False
                            break
                        elif dest_row == 3 or line[dest_row + 1] != 0:
                            self.queue_move_tile((row, col), (dest_row, col))
                            line[dest_row] = line[row]
                            line[row] = 0
                            break
                        dest_row += 1
        elif move == 1:
            # Up, row decreases
            for col in range(4):
                line = [self.tiles[row][col] for row in range(4)]
                can_merge = [True for _ in range(4)]
                for row in [1, 2, 3]:
                    if line[row] == 0 or line[row - 1] != line[row] and line[row - 1] != 0:
                        # no tile or cannot move
                        continue
                    dest_row = row
                    while True:
                        if dest_row != 0 and line[dest_row - 1] == line[row] and can_merge[dest_row - 1]:
                            dest_row -= 1
                            self.queue_move_tile((row, col), (dest_row, col))
                            line[dest_row] = line[row] * 2
                            line[row] = 0
                            can_merge[dest_row] = False
                            break
                        elif dest_row == 0 or line[dest_row - 1] != 0:
                            self.queue_move_tile((row, col), (dest_row, col))
                            line[dest_row] = line[row]
                            line[row] = 0
                            break
                        dest_row -= 1
        elif move == 2:
            # Right, col increases
            for row in range(4):
                line = self.tiles[row].copy()
                can_merge = [True for _ in range(4)]
                for col in [2, 1, 0]:
                    if line[col] == 0 or line[col + 1] != line[col] and line[col + 1] != 0:
                        # no tile or cannot move
                        continue
                    dest_col = col
                    while True:
                        if dest_col != 3 and line[dest_col + 1] == line[col] and can_merge[dest_col + 1]:
                            dest_col += 1
                            self.queue_move_tile((row, col), (row, dest_col))
                            line[dest_col] = line[col] * 2
                            line[col] = 0
                            can_merge[dest_col] = False
                            break
                        elif dest_col == 3 or line[dest_col + 1] != 0:
                            self.queue_move_tile((row, col), (row, dest_col))
                            line[dest_col] = line[col]
                            line[col] = 0
                            break
                        dest_col += 1
        elif move == 3:
            # Left, col decreases
            for row in range(4):
                line = self.tiles[row].copy()
                can_merge = [True for _ in range(4)]
                for col in [1, 2, 3]:
                    if line[col] == 0 or line[col - 1] != line[col] and line[col - 1] != 0:
                        # no tile or cannot move
                        continue
                    dest_col = col
                    while True:
                        if dest_col != 0 and line[dest_col - 1] == line[col] and can_merge[dest_col - 1]:
                            dest_col -= 1
                            self.queue_move_tile((row, col), (row, dest_col))
                            line[dest_col] = line[col] * 2
                            line[col] = 0
                            can_merge[dest_col] = False
                            break
                        elif dest_col == 0 or line[dest_col - 1] != 0:
                            self.queue_move_tile((row, col), (row, dest_col))
                            line[dest_col] = line[col]
                            line[col] = 0
                            break
                        dest_col -= 1
        self.resolve_animations()
        return len(self.animations) > 0

    def resolve_animations(self):
        moved = False
        while self.animations:
            animation = self.animations.pop(0)
            if animation[0] == Animations.MoveTile:
                moved = True
                before, after = animation[1]
                if self.tiles[after[0]][after[1]] != 0:
                    self.queue.append((Animations.MergeTile, animation[1]))
                self.tiles[after[0]][after[1]] = self.tiles[before[0]][before[1]]
                self.tiles[before[0]][before[1]] = 0
            elif animation[0] == Animations.NewTile:
                location, number = animation[1]
                self.tiles[location[0]][location[1]] = number
            elif animation[0] == Animations.MergeTile:
                before, after = animation[1]
                self.tiles[after[0]][after[1]] *= 2

        if moved:
            self.queue_new_tile()
        self.animations = self.queue
        self.queue = []

    def is_animating(self):
        return len(self.animations) > 0

    def get_animations(self):
        return self.animations

    def get_static_tiles(self):
        tiles = [(i, j) for i in range(4) for j in range(4) if self.tiles[i][j] != 0]
        for animation in self.animations:
            if animation[0] == Animations.MoveTile and animation[1][0] in tiles:
                tiles.remove(animation[1][0])
        return tiles
