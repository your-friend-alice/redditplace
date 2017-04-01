#!/usr/bin/env python3
import sys,os,urllib.request,time,threading,tty,termios,queue
colors=[str(i) for i in [
    231, 253, 245, 16,
    213, 196, 202, 130,
    214, 112, 22,  51,
    33,  19,  170, 53
    ]]
data=None
def update():
    global data
    d=urllib.request.urlopen(
            'https://www.reddit.com/api/place/board-bitmap'
            ).read()
    data=d

def updatePeriodically(delay=1, q=None):
    while True:
        time.sleep(delay) #TODO make this an interval instead of a delay
        update()
        q.put(None)

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
def colorChar(top, bott):
    """
    Print a character with the 256-color-mode colors top and bottom
    respectively coloring the top and bottom of the cell. If `optimize` is
    True, don't print color codes if last time the color was the same.
    """
    global prevColor
    if(top==None or bott==None):
        out='\033[0m'
        if top==None or bott==None:
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
    startY=int((y-h))
    rows=[]
    for y in range(startY,startY+h*2,2):
        rows.append("".join(colorChar(valueAt(x,y), valueAt(x,y-1)) for x in range(startX,startX+w)))
    print("\n".join(rows) + "\033[0m")

def arg(n, default=None):
    """
    Get sys.argv[`n`], falling back to `default` if it isn't set
    """
    return sys.argv[n] if len(sys.argv) > n else default

def clamp(val, minimum, maximum):
    return min(max(val, minimum), maximum)

def keyListen(q=None):
    while True: #TODO: add lock so a redraw won't be attempted while the terminal's all fucked up
        k=sys.stdin.read(1)
        q.put(k)

def hJump():
    return int(os.get_terminal_size()[0]/4)

def vJump():
    return int(os.get_terminal_size()[1]/4)

if arg(1) == "explore":
    center=[500,500]
    print("loading...")
    update()
    q=queue.Queue()
    threading.Thread(target=keyListen, kwargs={"q":q}, daemon=True).start()
    threading.Thread(target=updatePeriodically, kwargs={"q":q}, daemon=True).start()
    old=termios.tcgetattr(sys.stdin.fileno())
    while True:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
        printAt(*center)
        tty.setraw(sys.stdin.fileno())
        k=q.get()
        if k == None:
            pass
        elif k in ['q', 'x', '\x03', '\x04']:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
            print("")
            sys.exit(1)
        elif k in 'ha':
            center[0]-=hJump()
        elif k in 'ld':
            center[0]+=hJump()
        elif k in 'js':
            center[1]+=vJump()
        elif k in 'kw':
            center[1]-=vJump()
        center=[clamp(n,0,999) for n in center]
else:
    update()
    printAt(
            clamp(int(arg(1, default=500)), 0, 999),
            clamp(int(arg(2, default=500)), 0, 999)
            )
