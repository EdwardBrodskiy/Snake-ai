from tkinter import *
from time import sleep
import Grid, Food, Snake, random, Output


def updateinfo():
    global info
    try:
        if info['world age'] == world_counter:
            print('ye boi')
    except:
        pass
    info = {'world age': world_counter, 'snakes': snk, 'foods': fod, 'grid': grd}



root = Tk()

info = None
# in the future there will be set up choices like load or new etc hence this
choice = 1
if choice == 1:
    # how many squares
    w = 32
    h = 32
    size = w * h
    grd = Grid.Grid(width=w, height=h)  # create a grid object
    # snk index related to the actual snake index so we don't want shifts when some are deleted hence its a dictionary
    snk = {}
    snakec = 0  # snake count
    while snakec < 4:  # create 4 snakes
        ran = random.randint(0, size - 1)
        if grd.show(ran) == 0:  # if there is something there it will not generate it helps with over crowding
            snk[snakec] = Snake.Create(grd, headpos=ran, key=snakec)
            snakec += 1

    # all object are treated equally and so they to get a dictionary
    fod = {}
    foodc = 0  # food count
    while foodc < 10:  # create 10 apples
        ran = random.randint(0, size - 1)
        if grd.show(ran) == 0:
            fod[foodc] = Food.Create(grd, index=ran, key=foodc)
            foodc += 1

world_counter = 0  # basically a global counter used for refreshing at different rates and other stuff

# by map it means the world map
map = Output.Table(root, grd, w, h, siz=800 // h)

updateinfo()  # in this case sets it up
ui = Output.Ui(root, grd, map, info, )  # all the other shit in the window

while True:  # main world loop
    # input()
    # these need to exist as we are looping through the snk so we can't actively change it
    born_log = []
    death_log = []
    for i in snk:
        # check if it is alive
        live = True
        for j in death_log:
            if i == j:
                live = False
        if live:  # and proceed if so
            where = snk[i].choose_move()  # let the snake decide where to move
            what = grd.show(where)  # look it up
            # and then identify what it is and process the out come accordingly Note: I don't like having separate
            # identification procedures every where but I currently can't think of a way to do it in a single
            # function, in a way it is just a python [CASE]
            # also there is an option of -1 which is just for the output module to identify an error
            if what == 0:  # it's empty
                snk[i].move(where)

            elif what[0] == 1:  # it's food
                fod[what[1][0]].die()  # in case it becomes a more complicated object at some point
                del fod[what[1][0]]
                snk[i].grow(where)
                # this is the current birth mechanism
                if snk[i].length > 3:
                    if random.randint(0, 1) == 0:  # the chance of it to actually happen allows them to grow beyond '3'
                        # the birth procedure
                        nspos = snk[i].split()
                        born_log.append(Snake.Create(grd, headpos=nspos, key=snakec, gene=snk[i].gene, mutate=True,
                                                     family=snk[i].family))
                        snakec += 1

            elif what[0] == 2:  # it's a snake
                if what[1][1]['head']:  # head collision #R.I.P #.die
                    snk[i].die()
                    try:  # non new born snake
                        snk[what[1][0]].die()
                        death_log.append(what[1][0])
                    except:  # new born snake #late abortion
                        for j in range(len(born_log)):
                            if born_log[j].key == what[1][0]:
                                born_log[j].die()
                                del born_log[j]
                                break
                    death_log.append(i)

                elif what[1][1]['tail']:  # it's a tail
                    if i == what[1][0]:  # it's own tail
                        snk[i].die()
                        death_log.append(i)
                    else:  # some one else's tail count as food maybe a gene mutation in the future
                        snk[what[1][0]].loose(where)
                        snk[i].grow(where)
    for i in born_log:  # new born get added to snk
        snk[i.key] = i
    born_log = []

    for i in death_log:  # we must berry the dead
        del snk[i]
    death_log = []

    for i in range(4):  # add some fresh food
        ran = random.randint(0, size - 1)
        if grd.show(ran) == 0:
            fod[foodc] = Food.Create(grd, index=ran, key=foodc, dob=world_counter)
            foodc += 1
    for i in range(1):  # add some fresh snakes
        ran = random.randint(0, size - 1)
        # only places it over space and food what was it about treating them equally
        if grd.show(ran) == 0:
            snk[snakec] = Snake.Create(grd, headpos=ran, key=snakec)
            snakec += 1
        elif grd.show(ran)[0] == 1:
            temp = grd.show(ran)[1][0]
            fod[temp].die()
            del fod[temp]
            snk[snakec] = Snake.Create(grd, headpos=ran, key=snakec)
            snakec += 1

    if not world_counter % 20:
        for i in fod:
            age = fod[i].age(world_counter)
            if age > 100:
                fod[i].die()
                death_log.append(i)
        for i in death_log:
            del fod[i]
        death_log = []
    # where we update all the outputs
    if not world_counter % 1:  # how often we do it output is the main thing that slows it down

        map.update(grd.givelog())
        updateinfo()
        ui.update(info)

    world_counter += 1
    root.update_idletasks()
    root.update()
