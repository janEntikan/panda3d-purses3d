from os import path
from panda3d.core import TextNode, TextPropertiesManager, TextProperties
from panda3d.core import TextFont, SamplerState


EMPTY_CHAR = None
EMPTY_ATTR = (None, None)
ESCAPE_CHARS = "\b\f\r\v"
DEFAULT_FONT = path.join(path.dirname(__file__), 'hack.ttf')

l = "abcdefghijklmnopqrstuvwxyz"
l+= "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
l+= "1234567890-=\\`!@#$%^&*()_"
l+= "+|~[]{};':,./<>? "+'"'
LEGAL_INPUT = l

# These are mostly for testing, make your own damn properties!
colors = {
    "red"    : (1,0,0,1),
    "orange" : (1,0.5,0,1),
    "yellow" : (1,1,0,1),
    "green"  : (0,1,0,1),
    "blue"   : (0,0,1,1),
    "cyan"   : (0,1,1,1),
    "magenta": (1,0,1,1),
    "black"  : (0,0,0,1),
    "grey"   : (0.5,0.5,0.5,1),
    "white"  : (1,1,1,1),
}

manager = TextPropertiesManager.getGlobalPtr()
for color in colors:
    tp = TextProperties()
    tp.setTextColor(colors[color])
    manager.setProperties(color, tp)

# Emulating curses str/ch overloading here (messy)
def overloadcurse(window, args):
    if not type(args[0]) == str:
        if type(args[0]) == int and type(args[1]) == int:
            x, y = args[0], args[1]
            if len(args) > 2:
                if type(args[2]) == str:
                    string = args[2]
                    if len(args) > 3:
                        attr = args[3]
                    else:
                        attr = EMPTY_ATTR
                else:
                    TypeError(str, " expected, got ", type(args[2]))
            else:
                raise TypeError("No string supplied")
        else:
            raise TypeError("Supplied x without a y")
    else:
        x, y  = window.cursor
        string = args[0]
        if len(args) > 1:
            attr = args[1]
        else:
            attr = EMPTY_ATTR
    return x, y, string, attr


class Window:
    def __init__(self, x, y, columns, lines):
        self.cursor = [0,0]
        self.x, self.y = x, y
        self.columns = columns
        self.lines = lines
        self.input = ""
        self.fill() # Creates self.grid

    # Move cursor to position
    def move(self, x, y):
        self.cursor = [x, y]

    # Increment the cursor
    def increment(self, x=1, y=0):
        for i in range(y):
            self.cursor[1] += 1
            if self.cursor[1] >= self.lines:
                self.scrolldown()
                self.cursor[1] -= 1
        for i in range(x):
            self.cursor[0] += 1
            if self.cursor[0] >= self.columns:
                self.cursor[1] += 1
                self.cursor[0] = 0
                if self.cursor[1] >= self.lines:
                    self.scrolldown()
                    self.cursor[1] -= 1
        
    # Scroll the grid 
    def scrolldown(self):
        self.grid.pop(0)
        self.grid.append([])
        for i in range(self.columns):
            self.grid[self.lines-1].append(EMPTY_CHAR)

    def scrollup(self):
        self.grid.pop()
        r = []
        for i in range(self.columns):
            r.append(EMPTY_CHAR)
        self.grid.insert(0, r)

    # Remove a single line, append at bottom
    def deleteline(self, y):
        self.grid.pop(y)
        self.grid.append([])
        for i in range(self.columns):
            self.grid[self.lines-1].append(EMPTY_CHAR)

    # Remove a single character
    def delete(self, x, y):
        self.grid[y][x] = EMPTY_CHAR

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
        for y in range(self.lines):
            self.grid.append([])
            for x in range(self.columns):
                self.grid[y].append(ch)

    # Add a single character
    def addch(self, *args):
        x, y, char, attr = overloadcurse(self, args)
        self.cursor = [x, y]
        self.addchar(x, y, char, attr)

    def addchar(self, x, y, char, attr=EMPTY_ATTR):
        if char == "\n":
            self.cursor[0] = 0
            self.increment(y=1)
        elif char == "\t":
            self.increment(4)
        elif char in ESCAPE_CHARS:
            pass
        else:
            try:
                self.grid[y][x] = (char, attr)
            except IndexError:
                raise IndexError("Trying to write outside of window!", x, y)
            self.increment()

    #  Add a string
    def addstr(self, *args):
        x, y, string, attr = overloadcurse(self, args)
        self.cursor = [x, y]
        for s, char in enumerate(string):
            self.addchar(self.cursor[0], self.cursor[1], char, attr)

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
        w = self.columns-1
        h = self.lines-1
        # Top, down, left right bars
        self.line_hori(0, 0, self.columns, ts)
        self.line_hori(0, h, self.columns, bs)
        self.line_vert(0, 0, self.lines, ls)
        self.line_vert(w, 0, self.lines, rs)
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
    def __init__(self, columns, lines, font=DEFAULT_FONT):
        self.columns = columns
        self.lines = lines
        Window.__init__(self, 0, 0, self.columns, self.lines)
        self.textnodes = (TextNode("PursesFG"), TextNode("PursesBG"))

        self.setup_keys()
        self.font = loader.loadFont(font)

        # Set to nearest filter so background color doesn't have lines (or actually fix?).
        self.font.setMagfilter(SamplerState.FT_nearest)
        self.font.setMinfilter(SamplerState.FT_nearest)

        self.w = self.font.getSpaceAdvance()/2
        self.h = self.font.getLineHeight()/2
        self.cw = (self.w*self.columns)
        self.ch = (self.h*self.lines)

        self.node = render2d.attachNewNode("purses")

        # Background color is a seperate textnode that 
        # only prints a unicode full block with properties. 
        # Not ideal but it works and is faster then tons of cards.
        # Caveat: doesn't work with fonts without block character.
        for n, node in enumerate(self.textnodes):
            node.setFont(self.font)
            np = self.node.attachNewNode(node)
            np.setScale(1/self.cw, 1, 1/self.ch)
            np.setPos(-1 ,n+100,1-(self.h/15))

        self.mousewatcher = base.mouseWatcherNode
        self.getmouse()

    # Set grid to a single string and throw it to the screen. (messy)
    def refresh(self):
        strings = [[], []]
        properties = [None, None]
        for y in range(self.lines):
            for x in range(self.columns):
                char = self.grid[y][x]
                if char:
                    for i, attr in enumerate(char[1]):
                        if not properties[i] == attr:
                            properties[i] = attr
                            if properties[i]:
                                strings[i].append("\1"+properties[i]+"\1")
                            else:
                                strings[i].append("\2")
                    strings[0].append(char[0])
                else:
                    if not properties == [None, None]:
                        properties = [None, None]
                        strings[0].append("\2")
                    strings[0].append(" ")
                if properties[1]:
                    strings[1].append("█") # Full block unicode character 
                else:
                    strings[1].append(" ")
            strings[0].append("\n")
            strings[1].append("\n")
        for n, node in enumerate(self.textnodes):
            node.setText("".join(strings[n]))

    def getmouse(self, window=None):
        if self.mousewatcher.hasMouse():
            x = (self.mousewatcher.getMouseX()+1)/2
            y = (-self.mousewatcher.getMouseY()+1)/2
            x = int(x*self.columns)
            y = int(y*self.lines)
            if window:
                x -= window.x
                y -= window.y
            return x, y
        return None

    def setup_keys(self):
        base.buttonThrowers[0].node().setKeystrokeEvent("purses_in")
        base.accept("purses_in", self.get_ascii)
        base.accept("enter", self.get_special, ["return"])
        base.accept("backspace", self.get_special, ["backspace"])
        base.accept("left", self.get_special, ["left"])
        base.accept("right", self.get_special, ["right"])
        base.accept("up", self.get_special, ["up"])
        base.accept("down", self.get_special, ["down"])
        self.special_input = ""
        self.ascii_input = ""

    # Catch things like return, backspace and arrows
    def get_special(self, key):
        self.special_input = key

    # Catch last pressed key as ascii
    def get_ascii(self, key):
        self.ascii_input = key

    # Return it
    def getch(self):
        return self.ascii_input

    # update string logic for window
    def getstr(self, x, y, window=None, attr=EMPTY_ATTR):
        prep = "> "
        out = None
        if not window:
            window = self
        if not self.ascii_input == "":
            ch = self.ascii_input
            self.ascii_input = ""
            if ch in LEGAL_INPUT:
                window.input += ch
        if not self.special_input == "":
            ch = self.special_input
            self.special_input = ""
            if ch == "return":
                if len(window.input)>0:
                    out = window.input
                    window.delete(x+len(window.input)+len(prep), y)
                    window.input = ""
                    window.scrolldown()
            elif ch == "backspace":
                window.delete(x+len(window.input)+len(prep), y)
                window.input = window.input[:-1]
        window.addstr(x, y, prep+window.input+"_", attr)
        return out


# Some colorful display of capability and debuggery.
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

            # Test escape characters, exposes attribute bug
            self.t_wind.move(4,4)
            self.t_wind.addstr("this\nis\n\tgoing\btorockyourworld")

            # Some lazy counters
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
            if self.i > 1: # Slow it down so we can see what happens better
                self. i = 0
                self.n += 1
                if self.n >= 32:
                    self.n = 0
                    self.s += 1

                # Add random strings to first window in random colors
                ss = [
                    "ok", "cool", "that's amazing", 
                    "sweet", "alright", "yeah", 
                    "wow", "nice"]
                s = str()
                for i in range(4):
                    s += choice(ss) + " "
                self.t_wind.scrolldown()
                self.t_wind.move(0,40)
                self.t_wind.addstr(s, (choice(cc), choice(cc)))

                # Draw that classic idle/loading thingy in other window.
                # And it's blinking
                ll = "|\\-/-"
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

                self.purses.getstr(x=5, y=10)

                self.purses.refresh() # Put main wind to screen
            return task.cont
    app = Game()
    app.run()