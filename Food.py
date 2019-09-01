import Grid



class Create():
    def __init__(self, grid, index=None, key=None, objectid=1, dob=0):
        self.dob = dob  # date of birth
        self.key = key
        self.objectid = objectid
        self.grid = grid
        self.index = index
        self.grid.update(self.index, [self.objectid, [self.key, {'seen':False, 'age':0}]])

    def age(self, date):
        temp = date - self.dob
        self.grid.update(self.index, [self.objectid, [self.key, {'age':temp}]])
        return temp

    def die(self):
        self.grid.update(self.index, 0)
