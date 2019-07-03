# Purses3d

The goal is to keep panda3d in control as much as possible while providing a console of sorts to print to, not to emulate ncurses as closely as possible. It's currently pretty barebones but with some workarounds can be made to do anything ncurses can except beep().


* Only works with monospaced fonts that contain the U+2588 "full block" unicode character for solid character backgrounds. For this reason hack.ttf is in this repo, which is MIT licensed.
* Meant to be used to make ascii/text-based games, GUIs, HUDs, etc.
* Either combine with panda3d's other capabilities or consider this the wrong way to draw text to a screen.

To see a colorful display of functionality, run
```
 $ git clone http://github.com/momojohobo/panda3d-purses
 $ cd panda3d-purses
 $ pip install -r requirements.txt
 $ python purses3d/__init__.py 
```
It is also avaiable on pypi.
```
 $ pip install panda3d-purses3d
```

TODO: 
* Steal more handy functions from ncurses.

### License
Either MIT or Public Domain (CC0), take your pick.

## How to use:

```
# Import sys, panda3d and purses
import sys
from direct.showbase.ShowBase import ShowBase
from purses3d import Purses, Window

# Run panda3d
base = ShowBase()
base.accept("escape", sys.exit)
base.run()

# Initialize purses with a console size of 40x20 characters
# It will be automatically scaled to fill the entire screen
purses = Purses(40, 20)

# Make a window in the center, taking up half the screen
window = Window(x=10, y=5, columns=20, lines=10)  

# Move that window's cursor to where we want to write
window.move(3, 0)

# Write something in that window
window.addstr("hello world")

# Or move and print in one go
window.addstr(3, 0, "hello world")

# Copy it to the main purses window
purses.copyfrom(window)

# Because Purses() is also a window, we can write something on it too
purses.addstr(0, 0, "purses!")

# Update the screen
purses.refresh()
```

## Colors / Properties

To add colors (amongst other need things) we'll need panda3d's TextPropertiesManager

```
from panda3d.core import TextProperties, TextPropertiesManager

# Get panda3d's global property manager
manager = TextPropertiesManager.getGlobalPtr()

# Make some property, in this case something telling it to print the text red (in rgba)
red = TextProperties()
red.setTextColor((1,0,0,1))

# Add it to panda's global mananger
manager.addProperties("myRedColor", red) 

# And use it to print the characters foreground (with a transparent background)
purses.addstr(0, 0, "purses!", ("myRedColor", None))

# ...or to print the characters background in that color
purses.addstr(0, 0, "purses!", (None, "myRedColor"))

purses.refresh()

# We can reposition this purses instance too so it doesn't take up the entire screen
purses.node.setScale(0.5)
purses.node.setPos(-0.3, 0, 0)

# Or parent it to the world as a 3d object COOOL!
purses.node.reparentTo(render)

```
You can change any properties found in the panda3d TextProperties class, though they're mostly untested. Especially changing text size could screw things up I imagine.


## Text input

Because panda3d is a realtime system and curses is not, text input is handled a little differently.

```
# Get user input string at (10, 5) from main purses screen
string = purses.getstr(10, 5)

# You can also supply a different window to echo the string to
# Or give it fg and bg attributes
string = purses.getstr(10, 5, window=my_window, attr=("red", "blue"))

# If the string is closed (with enter), it is returned instead of None.
if string:
    # If used types hello
    if string == "hello":
        # Print this answer
        purses.addstr("why hello there buddy!")

```


### Functions so far
```
purses.move(x, y) # Place the cursor at position
purses.increment(n=1) # Increment the cursor location

purses.scrollup() # Scroll everything in window up
purses.scrolldown() # Scroll everything in window down

purses.fill(character) # Fills the entire window with a char (or empty if none is specified)
purses.delete(x, y) # Delete a single character
purses.addch(x, y, char, properties) # Add a single character
purses.addstr(x, y, string, properties) # Add a string 

# Draw horizontal and vertical lines respectively
purses.linehori(start_x, start_y, length, character, properties)
purses.linevert(start_x, start_y, length, character, properties)

# Draw a border around the window, left, right, top, bottom and its corners.
# Each character should be complete with properties ("c", (None, None))
purses.border(ls, rs, ts, bs, tl, tr, bl, br) 
purses.box(horizontal_sides, vertical_sides)

# These calls only work from the main Purses() window.
purses.refresh() # Refresh screen (place its state to the screen)
# Return the mouse coordinates in characters, only callable from Purses()
# If window is specified it will return its relative coordinates
purses.getmouse(window) 
# Return a string as written by user
purses.getstr(x, y, window=None, attr=(None, None))
```
