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
        # lines: the 4 rows/columns
        # direction: 0 if y, 1 if x
        if move == 0 or move == 1:
            lines = [[self.tiles[i][j] for i in range(4)] for j in range(4)]
            direction = 0
        else:
            lines = [self.tiles[i].copy() for i in range(4)]
            direction = 1

        # next: direction to increment/decrement
        # starts: tiles to check for movement
        # end: end of the line where no more movement can occur
        if move == 0 or move == 2:
            next = 1
            starts = [2, 1, 0]
            end = 3
        else:
            next = -1
            starts = [1, 2, 3]
            end = 0

        for linenum in range(4):
            line = lines[linenum]
            can_merge = [True for _ in range(4)]
            moves = []
            for start in starts:
                if line[start] == 0 or line[start + next] != line[start] and line[start + next] != 0:
                    # no tile or cannot move
                    continue
                dest = start
                while True:
                    next_dest = dest + next
                    if dest != end and line[next_dest] == line[start] and can_merge[next_dest]:
                        # next tile is same as start, and hasn't been merged before
                        moves.append((start, next_dest))
                        line[next_dest] = line[start]
                        line[start] = 0
                        can_merge[next_dest] = False
                        break
                    if dest == end or line[next_dest] != 0:
                        # reached the end or a different tile
                        moves.append((start, dest))
                        line[dest] = line[start]
                        line[start] = 0
                        break
                    dest = next_dest
            for start, dest in moves:
                if direction == 0:
                    # moving in y direction, column doesn't change
                    before = (start, linenum)
                    after = (dest, linenum)
                else:
                    # moving in x direction, row doesn't change
                    before = (linenum, start)
                    after = (linenum, dest)
                self.queue_move_tile(before, after)

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
