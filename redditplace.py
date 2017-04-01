#!/usr/bin/env python3
import sys,os,urllib.request
colors=[str(i) for i in [
    231, 253, 245, 16,
    213, 196, 202, 130,
    214, 112, 22,  51,
    33,  19,  170, 53
    ]]
data=urllib.request.urlopen(
        'https://www.reddit.com/api/place/board-bitmap'
        ).read()

def valueAt(x, y):
    """
    Get the color value at a given coordinate on the Place canvas
    """
    if(x<0 or x>999 or y<0 or y>999):
        return None
    byte=data[y*500+int((x)/2)+4]
    if x%2 == 0:
        return byte >> 4
    else:
        return byte & 15

prevColor=(None, None)
def colorChar(top, bott, optimize=True):
    """
    Print a character with the 256-color-mode colors top and bottom
    respectively coloring the top and bottom of the cell. If `optimize` is
    True, don't print color codes if last time the color was the same.
    """
    global prevColor
    if(top==None or bott==None):
        out='\033[0m'
        if top==bott==None:
            out+=" " if prevColor[0]!=None or prevColor[1]!=None else " "
            prevColor=(top,bott)
            return out
        out+='\033[38;5;'+colors[top or bott]+'m'
        out+='▄' if bott else '▀'
        prevColor=(top,bott)
        return out
    topCode='\033[38;5;' +colors[top] +'m' if top  != prevColor[0] else ""
    bottCode='\033[48;5;'+colors[bott]+'m' if bott != prevColor[1] else ""
    prevColor=(top,bott)
    return topCode+bottCode+'▄'

def printAt(x, y, w=None, h=None):
    """
    Print a `w` by `h` char rendering of the Place canvas, centered on `x`,`y`
    below
    """
    w=w or os.get_terminal_size()[0]
    h=h or os.get_terminal_size()[1]-1
    startX=int(x-w/2)
    startY=int(y-h)
    rows=[]
    for y in range(startY,startY+h*2,2):
        rows.append("".join(colorChar(valueAt(x,y), valueAt(x,y+1)) for x in range(startX,startX+w)))
    print("\n".join(rows) + "\033[0m")

def arg(n, default=None):
    """
    Get sys.argv[`n`], falling back to `default` if it isn't set
    """
    return sys.argv[n] if len(sys.argv) > n else default

printAt(int(arg(1, default=500)), int(arg(2, default=500)))
