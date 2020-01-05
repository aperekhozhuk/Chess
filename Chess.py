import tkinter as tk
from PIL import Image, ImageTk

class Board:
    def __init__(self):
        # Window settings
        self.root = tk.Tk()
        self.root.resizable(0,0)
        self.root.title('Chess')
        # Size of window - 80% percent of least dimension of screen
        self.size = 8 * (min(self.root.winfo_screenheight(), self.root.winfo_screenwidth()) // 10)
        # Size of cells
        self.cellSize = self.size // 8
        self.canvas = tk.Canvas(width = self.size, height = self.size)
        self.canvas.pack()
        self.canvas.bind('<Button-1>',self.Click())
        self.root.bind('<Return>',self.NewGameEventHandler())
        # Label for showing message about result of game
        self.alert = None
        # Colors for cells background
        self.cellBg = ('black','white')
        # Drawing Board
        self.drawBoard()
        # Starting first game
        self.NewGame()
        # Starting window process. Upd: to early to start mainloop. Firstly we need to render all objects
        #self.root.mainloop()
    
    # Draws all cells. Actually runs only 1 timer per program executing
    def drawBoard(self):
        for i in range(8):
            for j in range(8):
                x1 = self.cellSize * i
                y1 = self.cellSize * j
                x2 = x1 + self.cellSize
                y2 = y1 + self.cellSize
                self.canvas.create_rectangle(x1,y1,x2,y2,fill = self.cellBg[(i + j)%2])
    
    # Invokes, when user clicks on board
    def Click(self):
        def _Click(event):
            i, j = self.GetCell(event.x, event.y)
        return _Click
    
    # Logic for restarting or running first game
    def NewGame(self, mode = 1): 
        pass

    # Wrapper, event handler, that runs NewGame function, when Enter pressed
    def NewGameEventHandler(self):
        def _NewGame(event):
            self.NewGame()
        return _NewGame

    # Returns coordinates of cell by coordinates of cursor
    def GetCell(self,x,y):
        i = x // self.cellSize
        j = y // self.cellSize
        return i, j

class Figure:
    # Initializating of figure, it takes kind of figure and side, and coordinates on Board
    # Kind: { 0 - Infantry, 1 - Tower, 2 - Horse, 3 - Officer, 4 - Queen, 5 - King }
    # Side: 0 - White, 1 - Black. White - means, side which goes first
    def __init__(self, board, kind, side, x, y):
        self.board = board
        self.kind = kind
        self.side = side
        self.x = x
        self.y = y
        # We need to store image, else garbage collector will clean it
        self.img = None
        self.Draw()

    def Draw(self):
        img = Image.open('resources/{}/{}.png'.format(self.side, self.kind))
        self.img = ImageTk.PhotoImage(img)
        self.board.canvas.create_image(self.x,self.y,image = self.img, anchor=tk.NW)

Board = Board()

# Just for test now
f = Figure(Board, 0,0,20,20)
f.Draw()

# Since we didn't render all objects inside Board initializing
# And now we just testing - we need to run mainloop outside the Board class
Board.root.mainloop()