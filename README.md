# Panda3d Purses

The goal is to keep panda3d in control as much as possible while providing a console of sorts to print to, not to emulate ncurses as closely as possible. It's currently pretty barebones but with some workarounds can be made to do anything ncurses can except beep().


* Only works with monospaced fonts that contain the U+2588 "full block" unicode character for solid character backgrounds. For this reason hack.ttf is in this repo, which is MIT licensed.
* Meant to be used to make ascii/text-based games, GUIs, HUDs, etc.
* Doesn't draw larger consoles (like 150x150) very well (yet), YMMV. 
* Doesn't work well with software rendering at all.
* Either combine with panda3d's advanced capabilities or consider this the wrong way to draw text to a screen.

Run purses.py to see a colorful display of functionality.


TODO: 
    Decrease expensive grid iteration somehow.
    Steal more handy functions from ncurses.

### License
Either MIT or Public Domain (CC0), take your pick.

## How to use:

```
# Import sys, panda3d and purses
import sys
from direct.showbase.ShowBase import ShowBase
from purses import Purses, Window

# Run panda3d
base = ShowBase()
base.accept("escape", sys.exit)
base.run()

# Initialize purses with a console size of 40x20 characters
# It will be automatically scaled to fill the entire screen
purses = Purses(40, 20)

# Make a window in the center, taking up half the screen
window = Window(x=10, y=5, width=20, height=10)  

# Write something in that window
window.addstr(x=0, y=0, string="hello world")

# Copy it to the main purses window
purses.copyfrom(window)

# Because Purses() is also a window, we can write something on it too
purses.addstr(x=0, y=0, "purses!")

# Update the screen
purses.refresh()
```

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
```
You can change any properties found in the panda3d TextProperties class, though they're mostly untested. Especially changing text size could screw things up I imagine.

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

# Refresh screen, only callable from Purses()
purses.refresh() 

# Return the mouse coordinates in characters, only callable from Purses()
# If window is specified it will return its relative coordinates
purses.getmouse(window) 
```
