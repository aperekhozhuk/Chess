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
        self.cellBg = ('bisque', 'brown')
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
    def NewGame(self):
        self.Player1 = Player(self,0)
        self.Player2 = Player(self,1)

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

class Player:
    def __init__(self, board, side):
        # I think it's better from OOP conceptions:
        # - Player plays on Board - so Player has Board field to comunicate with Board
        # - Figure belong to player - so Figure has Player field, and can comunicate with him
        # - Also Figure can communicate with Board - through Player.
        # In my opinion, such Ierarchy more natural
        self.side = side
        self.board = board
        self.figures = {}
        self.SetFigures()

    # Draws Player's Figures on Board.
    # Also it pushes figures to dictionary with keys whic is a coordinates
    # It will easy to acces to figure after clicking on Board
    def SetFigures(self):
        # Drawing Infantry, Calculating of j - fucking magic of boolean algebra
        j = 1 + 5 * (1 - self.side)
        # Cicle for X coordinate
        for i in range(8):
            self.figures[(i, j)] = Figure(self, 0, self.side, i, j)
        # Drawing Towers, Horses, Officers
        j = 7 * (1 - self.side)
        for i in range(3):
            self.figures[(i,j)] = Figure(self, i + 1, self.side, i, j)
            self.figures[(7 - i,j)] = Figure(self, i + 1, self.side, 7 - i, j)
        # Drawing of Queen
        self.figures[(3, j)] = Figure(self, 4, self.side, 3, j)
        # Drawing of King
        self.figures[(4, j)] = Figure(self, 5, self.side, 4, j)

class Figure:
    # Initializating of figure, it takes kind of figure and side, and coordinates on Board
    # Kind: { 0 - Infantry, 1 - Tower, 2 - Horse, 3 - Officer, 4 - Queen, 5 - King }
    # Side: 0 - White, 1 - Black. White - means, side which goes first
    def __init__(self, player, kind, side, x, y):
        self.player = player
        self.kind = kind
        self.side = side
        # Figure coordinates. It means cell coordinates, tot pixel
        self.x = x
        self.y = y
        # We need to store image, else garbage collector will clean it
        self.img = None
        # Id for canvas
        self.id = None
        self.Draw()

    def Draw(self):
        img = Image.open('resources/{}/{}.png'.format(self.side, self.kind))
        # Resizing, so it will fit for cell size on any screens
        size = self.player.board.cellSize
        img = img.resize((size,size), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.id = self.player.board.canvas.create_image(self.x * size,self.y * size,image = self.img, anchor=tk.NW)

Board = Board()

# Since we didn't render all objects inside Board initializing
# And now we just testing - we need to run mainloop outside the Board class
Board.root.mainloop()