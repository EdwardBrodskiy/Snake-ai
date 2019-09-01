from tkinter import *
import Grid, Snake, Food, Instance, math


class Table:
    def __init__(self, root, grid, width, height, siz=8, buffer=5):

        self.current = None
        self.b = buffer
        self.grid = grid
        self.width = width  # note: the squares not the pixels
        self.height = height
        self.siz = siz  # size of each individual square

        self.canvas = Canvas(root, width=self.width * self.siz + self.b * 2, height=self.height * self.siz + self.b * 2,
                             bg='#ACACAC')
        self.canvas.grid(row=0, column=0, rowspan=10)

        self.items = list(grid.all())  # crude way of creating a list of the correct size
        self.best = []
        # and it will store all visuals in each square
        for index in range(len(self.items)):
            self.items[index] = []  # now puts the right data structure in it
        self.update(range(len(self.grid.all())))  # fills items

    def update(self, log):  # log is all the stuff that got updated in the grid since last frame
        for i in log:
            self.current = self.grid.show(i)
            self.draw(self.current, i)

    def itopos(self, index):  # index to coordinates conversion
        return [self.b + (index % self.width) * self.siz, self.b + (index // self.width) * self.siz]

    def scale_age_to_col(self, value):
        value *= 3
        if value > 255:
            value = 255
        col = '#'
        temp = hex(value)[2:]
        if len(temp) == 1:
            temp = '0' + temp
        col += temp
        temp = hex(255 - value)[2:]
        if len(temp) == 1:
            temp = '0' + temp
        col += temp
        return col + '00'

    def antipode(self, col):
        '''
        hx = '0123456789abcdef'
        anticol = '#'
        for i in col:
            if i != '#':
                for j in range(16):
                    if hx[j] == i:
                        anticol += hx[(j - 8) % 16]
        return anticol
        '''
        col = col[1:]
        big = 0
        for i in range(3):
            if col[2 * i] > '7':
                big += 1
        if big > 1:
            return '#000000'
        else:
            return '#FFFFFF'

    def draw(self, i, where):  # identifies what is in that square
        if i == 0:
            self.draw_space(where)
        elif i == -1:
            self.draw_warning(where)
        elif i[0] == 1:
            self.draw_food(where)
        elif i[0] == 2:
            if i[1][1]['head']:  # [1][1]['head'] is boolean for head or not head look in book
                self.draw_snkhead(where)
            else:
                self.draw_snkbody(where)

    # All draw_... work in the same way so only this one is commented
    def draw_space(self, index):
        for i in self.items[index]:  # delete the items previously being displayed at that index
            self.canvas.delete(i)
        xy = self.itopos(index)  # change index to coordinates
        # then create all the stuff needed for displaying it
        self.items[index] = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz,
                                                          fill='#ACACAC',
                                                          outline='#FFFFFF')]

    def draw_warning(self, index):
        for i in self.items[index]:
            self.canvas.delete(i)
        xy = self.itopos(index)
        self.items[index] = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz,
                                                          fill='#FF0000',
                                                          outline='#FF0000')]

    def draw_food(self, index):
        for i in self.items[index]:
            self.canvas.delete(i)
        xy = self.itopos(index)
        self.items[index] = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz,
                                                          fill=self.scale_age_to_col(self.current[1][1]['age']),
                                                          outline='#FFFFFF')]

    def draw_snkhead(self, index):
        for i in self.items[index]:
            self.canvas.delete(i)
        xy = self.itopos(index)
        self.items[index] = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz,
                                                          fill=self.current[1][1]['family']['surname'],
                                                          outline='#000000'),
                             self.canvas.create_text(xy[0] + self.siz // 2, xy[1] + self.siz // 2,
                                                     text=self.grid.show(index)[1][0],
                                                     fill=self.antipode(self.current[1][1]['family']['surname']))]

    def draw_snkbody(self, index):
        for i in self.items[index]:
            self.canvas.delete(i)
        xy = self.itopos(index)
        self.items[index] = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz,
                                                          fill=self.current[1][1]['family']['surname'],
                                                          outline='#FFFFFF')]

    def draw_highlight(self, index, views, interest):
        for i in self.best:
            self.canvas.delete(i)
        xy = self.itopos(index)

        self.best = [self.canvas.create_rectangle(xy[0], xy[1], xy[0] + self.siz, xy[1] + self.siz, outline='#FFAA77', dash=(2, 2))]
        for i in range(len(views)):
            views[i] = [views[i][0] * self.siz + xy[0], views[i][1] * self.siz + xy[1]]
            self.best.append(self.canvas.create_rectangle(views[i][0], views[i][1], views[i][0] + self.siz, views[i][1] + self.siz,
                                                          outline=self.scale_age_to_col(int(interest[i] * 128 // 1) + 128)))
            self.best.append(self.canvas.create_line(xy[0] + 0.5 * self.siz, xy[1] + 0.5 * self.siz,
                                                     views[i][0] + 0.5 * self.siz, views[i][1] + 0.5 * self.siz,
                                                     fill=self.scale_age_to_col(int(interest[i] * 128 // 1) + 128)))


class Ui:
    def __init__(self, root, grid, table, data, test=None):
        if test:
            self.test = test
            self.tc = 0.0

        self.table = table
        self.root = root
        self.grid = grid
        self.data = data
        # Top menu thingy
        self.menu = Menu(root)  # creates an empty menu
        self.root.config(menu=self.menu)
        self.submenu = Menu(self.menu)
        # creating a dropdown menu aka cascade
        self.menu.add_cascade(label="File", menu=self.submenu)
        # adding stuff to drop down menu
        self.submenu.add_command(label="New")  # command=self.create_info)

        # info column
        #           {Name : [ Frame object , Groups of outputs with type, input and widget set }
        self.info = {'General': {},
                     'Snakes': {},
                     # 'Waves': {}
                     # 'Food': {}
                     }
        # wave
        self.angle = 0
        # Has all the functions to assemble the info
        self.setup_info()
        self.assemble_info()
        # what row the frame will go in
        row = 0
        for i in self.info:
            # places the frame
            self.info[i]['frame']['tk'].grid(row=row, column=1)
            # places header
            self.info[i]['Header']['tk'].grid(row=0, column=0, columnspan=2)

            r = 1  # in frame row
            # creates the Simple outputs (eg: population 25)
            for j in self.info[i]:
                if self.info[i][j]['type'] == 'simple':
                    self.info[i][j]['tk'] = [Label(self.info[i]['frame']['tk'], text=j),  # data name label
                                             Label(self.info[i]['frame']['tk'],
                                                   text=self.info[i][j]['data'])]  # the data it self
                    # place them in
                    c = 0
                    for k in self.info[i][j]['tk']:
                        k.grid(row=r, column=c)
                        c += 1
                    r += 1
                elif self.info[i][j]['type'] == 'plot':
                    self.info[i][j]['init'][0].grid(row=r, column=0, columnspan=2)
                    self.info[i][j]['tk'] = Plot(*self.info[i][j]['init'], *self.info[i][j]['data'])

                    r += 1
            row += 1

            # plot simple output test
            '''
            t = Frame(self.root)
            t.grid(row=row, column=1)
            m = Plot(t, 0, 10)
            '''

            # places all the stuff into the info thing so they can then be systematically outputted

    def setup_info(self):
        for i in self.info:

            self.info[i]['frame'] = {'tk': Frame(self.root), 'type': None}
            # creates a Header
            self.info[i]['Header'] = {'type': 'header'}

            if i == 'General':
                # All the info from main
                self.info[i]['world age'] = {'type': 'simple'}

                self.info[i]['snake count'] = {'type': 'simple'}

                self.info[i]['food count'] = {'type': 'simple'}

            elif i == 'Snakes':
                self.info[i]['average length'] = {'type': 'simple'}

                self.info[i]['average l'] = {'type': 'plot', 'init': [Frame(self.info[i]['frame']['tk']), 1, 11]}

                # self.info[i]['test'] = {'type': 'simple'}

            elif i == 'Food':
                self.info[i]['population'] = {'type': 'simple'}

                self.info[i]['average age'] = {'type': 'simple'}

            elif i == 'Waves':
                self.info[i]['sin'] = {'type': 'plot', 'init': [Frame(self.info[i]['frame']['tk']), -2, 0]}

    def assemble_info(self):
        for i in self.info:
            # creates a Header
            self.info[i]['Header']['tk'] = Label(self.info[i]['frame']['tk'], text=i)

            if i == 'General':
                # All the info from main
                self.info[i]['world age']['data'] = self.data['world age']

                self.info[i]['snake count']['data'] = len(self.data['snakes'])

                self.info[i]['food count']['data'] = len(self.data['foods'])

            elif i == 'Snakes':
                # The average length is calculated here
                total = 0
                lower = 1000000
                lowerc = '#000000'
                upper = 0
                upperc = '#000000'
                for j in self.data['snakes']:

                    if self.data['snakes'][j].length > upper:
                        upper = self.data['snakes'][j].length
                        upperc = self.data['snakes'][j].family['surname']
                        pos = self.data['snakes'][j].headpos
                        best_snk = j

                    if self.data['snakes'][j].length < lower:
                        lower = self.data['snakes'][j].length
                        lowerc = self.data['snakes'][j].family['surname']

                    total += self.data['snakes'][j].length

                self.info[i]['average length']['data'] = round(total / len(self.data['snakes']), 2)
                # add on table
                self.info[i]['average l']['data'] = [['Best', 'Mean', 'Worst'], [upperc, '#0000FF', lowerc],
                                                     [upper, round(total / len(self.data['snakes']), 2), lower]]
                # table command
                views = self.grid.queenslook(self.data['snakes'][best_snk].headpos, self.data['snakes'][best_snk].maxv)
                seen = []
                interest = []
                for j in views:
                    vector = j[0]
                    what = self.data['snakes'][best_snk].identify(j[1])
                    if vector[0] <= self.data['snakes'][best_snk].gene[what][0] \
                            and vector[1] <= self.data['snakes'][best_snk].gene[what][0]:
                        #  so to call the queens look
                        #  function only once we do it for our max vision so it may give us some stuff that we don't want
                        #  and this is just filtering those out
                        seen.append(j[0])
                        interest.append(self.data['snakes'][best_snk].gene[what][1])

                self.table.draw_highlight(pos, seen, interest)
                # self.info[i]['test']['data'] = self.test.show(pos, )

            elif i == 'Food':
                pass

            elif i == 'Waves':
                self.info[i]['sin']['data'] = [['sin', 'cos'], ['#0000FF', '#FF0000'], [math.sin(self.angle), math.cos(self.angle)]]
                self.angle += 0.3
    def update(self, data):
        self.data = data
        self.update_info()

    def update_info(self):
        if self.test:
            self.test.set_test(int(120 * math.sin(self.tc) // 1 + 1))
            self.tc += 0.1
        self.assemble_info()
        for i in self.info:
            for j in self.info[i]:
                if self.info[i][j]['type'] == 'simple':
                    self.info[i][j]['tk'][1].configure(text=self.info[i][j]['data'])

                elif self.info[i][j]['type'] == 'plot':
                    self.info[i][j]['tk'].update(*self.info[i][j]['data'])


class Plot:
    def __init__(self, root, lower, upper, names, colours, start, points=20, solid_b=False, scales=6, mode='run',
                 height=100,
                 width=200):
        self.root = root

        # data related variables
        self.min = lower
        self.max = upper
        self.span = self.max - self.min
        self.scales = scales
        self.solid_b = solid_b
        self.points = points

        self.plots = [[i] for i in start]
        self.tkplots = [list() for i in range(len(self.plots))]
        self.mode = mode
        self.colour_set = {'scales': '#AAAAAA', 'lines': colours}

        # canvas dimensions
        self.b = 10
        self.height = height
        self.width = width
        self.canvas = Canvas(root, width=self.width + self.b * 2, height=self.height + self.b * 2)

        self.row = 0
        self.column = 0
        self.canvas.grid(row=self.row, column=self.column, columnspan=2)
        self.row += 1

        self.draw_scale()

        # key
        self.key = []
        for i in range(len(names)):
            self.key.append([Label(root, text=names[i], fg=self.colour_set['lines'][i]),
                             Label(root, text=start[i], fg=self.colour_set['lines'][i])])
            for j in range(len(self.key[i])):
                self.key[i][j].grid(row=self.row, column=self.column + j)
            self.row += 1

    def draw_scale(self):
        for i in range(self.scales):
            y = self.height * (1 - i / (self.scales - 1)) + self.b
            x = self.b * 2
            self.canvas.create_line(x, y, x + self.width, y, fill=self.colour_set['scales'])
            self.canvas.create_text(x - self.b, y, text=self.span * i / (self.scales - 1),
                                    fill=self.colour_set['scales'])

    def update(self, names, colours, values):
        self.colour_set['lines'] = list(colours)

        for i in range(len(self.plots)):
            self.key[i][0].configure(text=names[i], fg=self.colour_set['lines'][i])
            self.key[i][1].configure(text=values[i], fg=self.colour_set['lines'][i])

            for j in self.tkplots[i]:
                self.canvas.delete(j)
            self.tkplots[i] = list()
            self.plots[i].append(values[i])
            try:
                for j in range(self.points):
                    y = self.height * (1 - self.plots[i][-(1 + j)] / self.span) + self.b
                    x = self.width * (1 - j / self.points) + self.b
                    y2 = self.height * (1 - self.plots[i][-(2 + j)] / self.span) + self.b
                    x2 = self.width * (1 - (j + 1) / self.points) + self.b
                    self.tkplots[i].append(self.canvas.create_line(x, y, x2, y2, fill=self.colour_set['lines'][i]))
            except IndexError:
                pass
