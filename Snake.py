import Grid, random


# Specific Object structure:
# [ Object ID , [ IndividualID , [ Next tail index (end of tail = -1) , Head or Not Head (if head then True) ] ] ]


class Create:
    def __init__(self, grid, gene=[], key=False, headpos=False, forward=0, objectid=2, low=1, high=10, mutate=False,
                 amount=2, magnitude=0.2, family={}):
        # snake setup data
        self.family = dict(family)
        self.maxv = None
        self.headpos = headpos  # head position
        self.length = 1
        self.forward = forward  # what direction it's looking (0,1,2,3) which way is up it is in the book
        self.key = key  # it's individual ID linked to the index in the snk array in main

        # other
        self.grid = grid
        self.low = low  # minimum vision
        self.high = high  # max vision
        self.objectid = objectid

        # setup of snake
        if not gene:  # if a gene was not provided #lab grown snake
            self.generate_gene()

        else:  # use given gene and mutate by magnitude of the parameters
            self.gene = gene
            if mutate:
                self.mutate(amount, magnitude)

        if not self.family:
            self.generate_surname()
        elif self.family['separation'] > 5:
            self.generate_surname()
        else:
            self.family['separation'] += 1

        # defalt meta data

        self.standard = {'seen': False, 'tail': -1, 'head': True, 'family': self.family}

        # create the snake on the grid

        self.grid.update(headpos,
                         [self.objectid, [self.key, self.standard]])

    def generate_surname(self):
        surname = [0, 0, 0]
        for i in range(len(self.gene)):
            surname[i % 3] += self.gene[i][0]*self.maxv + self.gene[i][1] * 100
        self.family['surname'] = '#'
        for i in surname:
            temp = hex(int(round(i, 0)) % 256)[2:]
            if len(temp) == 1:
                temp = '0' + temp
            self.family['surname'] += temp
        self.family['separation'] = 0

    def meta_data(self, altered):
        copy = dict(self.standard)
        for i in altered:
            copy[i] = altered[i]
        return copy

    # Creates a random gene if it doesn't already have one.
    def generate_gene(self):
        # gene: [ [ vision range low to high , interest -1 to 1 positive means attracted ] , ... ]
        # 0:Food 1:OwnTail 2:OtherTail 3:Heads
        self.gene = []
        for i in range(4):
            self.gene.append([random.randint(self.low, self.high), round(random.uniform(-1, 1), 2)])
        self.maxv = self.max_vision()

    def mutate(self, amount, magnitude):
        for i in range(amount):
            index = random.randint(0, len(self.gene) - 1)  # decide which one to change
            if random.randint(0, 1):  # 50 50 to change vision or interest
                temp = self.gene[index][1] + random.uniform(-magnitude, magnitude)
                # make sure it doesnt exceed the range
                if temp > 1:
                    temp = 1
                elif temp < -1:
                    temp = -1
                # assign it
                self.gene[index][1] = temp
            else:
                scale = magnitude * self.high
                temp = self.gene[index][1] + random.uniform(-scale, scale)
                if temp > self.high:
                    temp = self.high
                elif temp < self.low:
                    temp = self.low
                else:
                    temp = int(round(temp, 0))
                self.gene[index][0] = temp
        self.maxv = self.max_vision()

    # The "clever" part of the snake when it chooses where to go and tells it to main and main then carries out the
    # consequences (die, move etc)
    def choose_move(self, vision_type=1):
        choice = [0.1, 0.1, 0.1]  # i'll play around with all these at a later stage #don't want to be analysing a
        # bunch of print statements

        if vision_type == 0:  # this is the old one which is not in use currently
            for i in range(len(self.gene)):
                sector = self.grid.scan(self.headpos, self.gene[i][0])
                for j in range(len(sector)):
                    if i == self.identify(sector[j]):  # check if it is the object we are currently looking at
                        vector = self.vector(j, self.gene[i][0])  # get the vector relative to the head
                        for m in range(
                                self.forward):  # orient the vector correctly relative to the direction of the snake
                            vector = self.rotate(vector)
                        distance = vector[0] ** 2 + vector[1] ** 2
                        horizontal = self.gene[i][1] * vector[0] / distance
                        if horizontal > 0:
                            choice[2] += horizontal
                        else:
                            choice[0] -= horizontal
                        vertical = self.gene[i][1] * vector[1] / distance
                        if vertical < 0:
                            choice[1] -= vertical

        elif vision_type == 1:  # this one should theoretically work better
            seen = self.grid.queenslook(self.headpos, self.maxv)
            for i in seen:
                vector = i[0]
                what = self.identify(i[1])
                if vector[0] <= self.gene[what][0] and vector[1] <= self.gene[what][0]:  # so to call the queens look
                    #  function only once we do it for our max vision so it may give us some stuff that we don't want
                    #  and this is just filtering those out
                    for m in range(self.forward):  # orient the vector correctly relative to the direction of the snake
                        vector = self.rotate(vector)
                    distance = vector[0] ** 2 + vector[1] ** 2
                    horizontal = self.gene[what][1] * vector[0] / distance
                    if horizontal > 0:
                        choice[2] += horizontal
                    else:
                        choice[0] -= horizontal
                    vertical = self.gene[what][1] * vector[1] / distance
                    if vertical < 0:
                        choice[1] -= vertical
        ran = random.uniform(0, sum(choice))
        for i in range(len(choice)):
            ran -= choice[i]
            if ran < 0:
                decision = i
                break
        self.forward = (self.forward - 1 + decision) % len(self.gene)
        return self.grid.show_where(self.headpos, self.forward)

    # Rotation of a 2D vector by 90 degrees clockwise
    def rotate(self, vector):
        return [-vector[1], vector[0]]

    def max_vision(self):
        b = 0
        for i in self.gene:
            if i[0] > b:
                b = i[0]
        return b

    # takes and index from the vision sector (not grid index) and returns a vector relative to the head.
    def vector(self, index, vision):
        xy = self.itoc(index, vision * 2 + 1)
        return [xy[0] - vision, xy[1] - vision]

    # Conversion from index to coordinates.
    def itoc(self, index, width):
        return [index % width, index // width]

    # Translates from grid identification to Snake's
    def identify(self, item):
        if item == 0 or item == -1:  # is it empty
            return -1

        if item[0] == 1:  # is it food
            return 0

        elif item[0] == 2:  # is it a snake
            if item[1][1]['head']:  # is it a head
                if item[1][0] == self.key:  # is it its head
                    return -1
                return 3
            if item[1][0] == self.key:  # is it its tail
                return 1
            return 2

    # Moves the snake by one square, [where] says where to move.
    def move(self, where):
        if self.length == 1:
            self.grid.update(where, [self.objectid, [self.key, self.meta_data({'tail': -1, 'head': True})]])
            self.grid.update(self.headpos, 0)
        else:
            # Create head
            self.grid.update(where, [self.objectid, [self.key, self.meta_data({'tail': self.headpos, 'head': True})]])
            # Turn old head into body
            x = self.grid.show(self.headpos)
            x[1][1]['head'] = False
            self.grid.update(self.headpos, x)
            # Find end of tail and delete it
            pos = self.headpos
            while self.grid.show(pos)[1][1]['tail'] != -1:
                last = pos
                pos = self.grid.show(pos)[1][1]['tail']
            x = self.grid.show(last)
            x[1][1]['tail'] = -1
            self.grid.update(last, x)
            self.grid.update(pos, 0)

        self.headpos = where

    # Does the same as move but does not remove the tail causing a growth of 1.
    def grow(self, where):
        self.grid.update(where, [self.objectid, [self.key, self.meta_data({'tail': self.headpos, 'head': True})]])
        if self.length == 1:
            self.grid.update(self.headpos, [self.objectid, [self.key, self.meta_data({'tail': -1, 'head': False})]])
        else:
            x = self.grid.show(self.headpos)
            x[1][1]['head'] = False
            self.grid.update(self.headpos, x)
        self.length += 1
        self.headpos = where

    # Removes all components from head to tail.
    def die(self):
        pos = self.headpos
        while self.grid.show(pos)[1][1]['tail'] != -1:
            temp = pos
            pos = self.grid.show(pos)[1][1]['tail']
            self.grid.update(temp, 0)
        self.grid.update(pos, 0)

    # Removes components of the tail up to ([upto]) and reduces [length] accordingly
    def loose(self, upto):
        # Find the new tail end and update it to such
        pos = self.headpos
        while self.grid.show(pos)[1][1]['tail'] != upto:
            pos = self.grid.show(pos)[1][1]['tail']
        x = self.grid.show(pos)
        x[1][1]['tail'] = -1
        self.grid.update(pos, x)
        # Delete the rest
        pos = upto
        while self.grid.show(pos)[1][1]['tail'] != -1:
            temp = pos
            pos = self.grid.show(pos)[1][1]['tail']
            self.length -= 1
            self.grid.update(temp, 0)
        self.length -= 1
        self.grid.update(pos, 0)

    # Literally loose of size 1 and returns where it is lost and so shows where to put the new snake
    def split(self):
        pos = self.headpos
        while self.grid.show(pos)[1][1]['tail'] != -1:
            last = pos
            pos = self.grid.show(pos)[1][1]['tail']
        x = self.grid.show(last)
        x[1][1]['tail'] = -1
        self.grid.update(last, x)
        self.grid.update(pos, 0)
        self.length -= 1
        return pos
