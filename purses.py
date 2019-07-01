from panda3d.core import TextNode, TextPropertiesManager, TextProperties
from panda3d.core import TextFont, SamplerState


# These are mostly for testing, make your own damn properties!
colors = {
    "black"  : (0,0,0,1),
    "white"  : (1,1,1,1),
    "red"    : (1,0,0,1),
    "orange" : (1,0.5,0,1),
    "yellow" : (1,1,0,1),
    "green"  : (0,1,0,1),
    "blue"   : (0,0,1,1),
    "cyan"   : (0,1,1,1),
    "magenta": (1,0,1,1),
}

manager = TextPropertiesManager.getGlobalPtr()
for color in colors:
    tp = TextProperties()
    tp.setTextColor(colors[color])
    manager.setProperties(color, tp)

EMPTY_CHAR = None
EMPTY_ATTR = [None, None]

# A window, which has a grid (list of lists) of characters.
# A character is either None or looks like this:
# ("c", ["fg_properties", "bg_properties"])
# Properties can be None to get a white fg and a transparent bg.
class Window:
    def __init__(self, x, y, width, height):
        self.cursor = [0,0]
        self.isscrolling = False
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.fill() # Creates self.grid

    # Move cursor to position
    def move(self, x, y):
        self.cursor = [x. y]

    # Increment the cursor
    def increment(self, n=1):
        for i in range(n):
            self.cursor[0] += 1
            if self.cursor[0] >= self.width:
                self.cursor[1] += 1
                self.cursor[0] = 0
                if self.cursor[1] > self.height:
                    self.scroll()

    # Scroll the grid 
    def scrolldown(self):
        self.grid.pop(0)
        self.grid.append([])
        for i in range(self.width):
            self.grid[self.height-1].append(EMPTY_CHAR)

    def scrollup(self):
        self.grid.pop()
        r = []
        for i in range(self.width):
            r.append(EMPTY_CHAR)
        self.grid.insert(0, r)

    # Set up grid for garbage collecting
    def destroy(self):
        self.grid = []

    # Copy the contents of a window to this window
    def copyfrom(self, window):
        for y, row in enumerate(window.grid):
            for x, ch in enumerate(row):
                if ch:
                    self.grid[y+window.y][x+window.x] = ch

    # Fill the grid with a character (or empty)
    def fill(self, ch=EMPTY_CHAR):
        self.grid = []
        for y in range(self.height):
            self.grid.append([])
            for x in range(self.width):
                self.grid[y].append(ch)

    # Remove a single character
    def delete(x, y):
        self.grid[y][x] = EMPTY_CHAR

    # Add a single character
    def addch(self, x, y, char, attr=EMPTY_ATTR):
        self.cursor = [x, y]
        try:
            self.grid[self.cursor[1]][self.cursor[0]] = (char, attr)
        except IndexError:
            raise IndexError("Trying to write outside of the window!")
        self.increment()

    #  Add a string
    def addstr(self, x, y, string, attr=EMPTY_ATTR):
        self.cursor = [x, y]
        for s, char in enumerate(string):
            self.addch(self.cursor[0], self.cursor[1], char, attr)

    # Draw a horizontal line to the right
    def linehori(self, x, y, length, char, attr=EMPTY_ATTR):
        for i in range(length):
            self.addch(x+i, y, char, attr)

    # Draw a vertical line down
    def linevert(self, x, y, length, char, attr=EMPTY_ATTR):
        for i in range(length):
            self.addch(x, y+i, char, attr)

    # Make a border around the window
    def border(self, ls, rs, ts, bs, tl, tr, bl, br):
        w = self.width-1
        h = self.height-1
        # Top, down, left right bars
        self.line_hori(0, 0, self.width, ts)
        self.line_hori(0, h, self.width, bs)
        self.line_vert(0, 0, self.height, ls)
        self.line_vert(w, 0, self.height, rs)
        # Corners
        self.addch(0, 0, tl[0], tl[1]) 
        self.addch(w, 0, tr[0], tr[1]) 
        self.addch(0, h, bl[0], bl[1]) 
        self.addch(w, h, br[0], br[1]) 

    # Make a simpler border around the window
    def box(vertch, horch):
        v, h = vertch, horch
        self.border(h, h, v, v, v, v, v, v) 


# Is also a window but spans the entire screen.
class Purses(Window):
    def __init__(self, width, height, font="hack.ttf"):
        self.width = width
        self.height = height

        Window.__init__(self, 0, 0, self.width, self.height)
        self.textnodes = (TextNode("PursesFG"), TextNode("PursesBG"))
        self.font = loader.loadFont(font)

        # Set to nearest filter so background color doesn't have lines.
        self.font.setMagfilter(SamplerState.FT_nearest)
        self.font.setMinfilter(SamplerState.FT_nearest)

        self.w = self.font.getSpaceAdvance()/2
        self.h = self.font.getLineHeight()/2
        self.cw = (self.w*self.width)
        self.ch = (self.h*self.height)

        # Background color is a seperate textnode that 
        # only prints a unicode full block with properties. 
        # Not ideal but it works and is faster then tons of cards.
        # Caveat: doesn't work with fonts without block character.
        for n, node in enumerate(self.textnodes):
            node.setFont(self.font)
            np = render2d.attachNewNode(node)
            np.setScale(1/self.cw, 1, 1/self.ch)
            np.setPos(-1 ,n+100,1-(self.h/15))

        self.mousewatcher = base.mouseWatcherNode
        self.getmouse()

    # Set grid to a single string and throw it to the screen. (messy)
    def refresh(self):
        strings = [str(), str()]
        properties = [None, None]
        for y in range(self.height):
            for x in range(self.width):
                char = self.grid[y][x]
                if char:
                    for i, attr in enumerate(char[1]):
                        if not properties[i] == attr:
                            properties[i] = attr
                            if properties[i]:
                                strings[i] += "\1"+properties[i]+"\1"
                            else:
                                strings[i] += "\2"
                    strings[0] += char[0]
                else:
                    if not properties == [None, None]:
                        properties = [None, None]
                        strings[0] += "\2"
                    strings[0] += " "
                if properties[1]:
                    strings[1] += "█" # Full block unicode character 
                else:
                    strings[1] += " "
            strings[0] += "\n"
            strings[1] += "\n"
        for n, node in enumerate(self.textnodes):
            node.setText(strings[n])

    def getmouse(self, window=None):
        if self.mousewatcher.hasMouse():
            x = (self.mousewatcher.getMouseX()+1)/2
            y = (-self.mousewatcher.getMouseY()+1)/2
            x = int(x*self.width)
            y = int(y*self.height)
            if window:
                x -= window.x
                y -= window.y
            return x, y
        return None

# Some random display of capability.
if __name__ == "__main__":
    import sys
    from random import choice
    from direct.showbase.ShowBase import ShowBase


    cc = []
    for c in colors: cc.append(c)

    class Game(ShowBase):
        def __init__(self):
            ShowBase.__init__(self)
            self.setFrameRateMeter(True)
            self.win.setClearColor((0,0,0,1))
            self.accept("escape", sys.exit)

            self.disableMouse()
            self.purses = Purses(81, 41) # Init purses
            self.t_wind = Window(0, 0, 81, 41) # Make a window
            self.l_wind = Window(81-8, 0, 8, 41) # Make another window
            self.s_wind = Window(30, 0, 25, 3) # One more

            # Some lazy timers
            self.i = 0
            self.n = 0
            self.s = 0

            # Render a panda to give it some depth
            self.model = loader.loadModel("models/panda")
            self.model.reparentTo(render)
            self.model.setPos(0.6,3.2,-1.8)
            self.model.setScale(0.2, 0.2, 0.2)

            self.taskMgr.add(self.loop)

        def loop(self, task):
            # Rotate panda
            self.model.setH(self.model.getH()+5)

            self.i += 1
            if self.i > 5: # Slow it down so we can see what happens better
                self. i = 0
                self.n += 1
                if self.n > 32:
                    self.n = 0
                    self.s += 1

                # Add random strings to first window in random colors
                ss = [
                    "ok", "cool", "that's amazing", 
                    "sweet", "alright", "yeah", 
                    "wow", "nice"]
                s = str()
                for i in range(6):
                    s += choice(ss) + " "
                self.t_wind.scrolldown()
                self.t_wind.addstr(0, 40, s, (choice(cc), choice(cc)))

                # Draw that classic idle/loading thingy in other window.
                # And it's blinking
                ll = "|\-/-"
                lc = "white", "yellow", "orange", "red"
                blink = lc[self.n%4]

                self.l_wind.scrollup()
                self.l_wind.addstr(0,0, ll[self.n%4], (blink, None))
                self.l_wind.addstr(1,0, "PURSES", (choice(cc), None))
                self.l_wind.addstr(7,0, ll[self.n%4], (blink, None))

                welcome = (
                    "hello there",
                    "I love you so much",
                    "I hope we can be friends",
                    "Ok cool thanks bye!",
                )
                self.s_wind.fill()
                self.s_wind.addstr(0,0, welcome[self.s%4], (blink, None))
        
                self.purses.fill() # Clear screen
                self.purses.copyfrom(self.t_wind) # Copy t_wind to main wind
                self.purses.copyfrom(self.l_wind) # Copy l_wind to main wind
                self.purses.copyfrom(self.s_wind) # Copy l_wind to main wind
                self.purses.refresh() # Put main wind to screen
            return task.cont
    app = Game()
    app.run()