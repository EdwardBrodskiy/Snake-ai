# How stuff exists in the grid I suggest learning it as it comes up a lot
# Empty space : 0
# Error : -1
# More complex 'living' objects : [ Object ID , [ IndividualID , [ All other object specific info ] ] ]
# Current Object IDs : Food = 1 , Snake = 2


class Grid:
    def __init__(self, width=50, height=50):
        self.log = []  # holds all the stuff that has been updated in it Note: log is wiped when called in main
        # empty grid generation
        self.width = width
        self.height = height
        self.grid = []
        for i in range(self.width * self.height):
            self.grid.append(0)

    def show(self, index): # returns the thing at that index
        return self.grid[index]

    def show_where(self, index, direction):  # used in choose move as it only knows if it wants to move left, forward
        #  or right so it needs to be converted into an index
        xy = self.itoc(index)
        if direction == 0:
            xy[1] -= 1
        elif direction == 1:
            xy[0] += 1
        elif direction == 2:
            xy[1] += 1
        else:
            xy[0] -= 1
        return self.ctoi(xy[0] % self.width, xy[1] % self.height)

    def update(self, index, value):  # updates that point and logs it
        self.grid[index] = value
        self.log.append(index)

    def scan(self, index, vision):  # scans a square sector around a point vision being a sort of 'radius'
        #  currently not in use
        # finding the top left corner
        x = (index % self.width - vision) % self.width
        y = (index // self.width - vision) % self.height
        sector = []
        dimensions = int(vision * 2 + 1)
        for j in range(dimensions):
            for i in range(dimensions):
                sector.append(self.grid[self.ctoi((x + i) % self.width, (y + j) % self.height)])
        return sector

    def queenslook(self, index, vision):  # like a chess queen in looks in 8 directions and returns anything in vision
        # Note: coordinates are returned are in the form [ [ vector relative to index ] , index position on the grid ]
        vis = []
        cr = self.itoc(index)
        direction = [-1, 0, 1]
        for i in direction:
            for j in direction:
                if i != 0 or j != 0:
                    for v in range(1, vision + 1):
                        pos = self.grid[self.ctoi((cr[0] + i * v) % self.width, (cr[1] + j * v) % self.height)]
                        if pos != 0:
                            vis.append([[i * v, j * v], pos])
                            break
        return vis

    def ctoi(self, x, y):  # coordinates to index
        return x + self.width * y

    def itoc(self, index):  # index to coordinates
        return [index % self.width, index // self.width]

    def all(self):  # send the whole damn thing
        return self.grid

    def givelog(self):  # returns the log and wipes it
        x = list(self.log)
        self.log = []
        return x
