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
        # Images of figures
        self.resources = [[], []]
        # Drawing Board
        self.drawBoard()
        # Loading images
        self.LoadResources()
        # Global game vars
        self.Player1 = None
        self.Player2 = None
        self.Players = (0,1)
        self.ActivePlayer = None
        self.ActiveFigure = None
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
    
    def LoadResources(self):
        size = self.cellSize
        for side in [0,1]:
            for kind in [0,1,2,3,4,5]:
                img = Image.open('resources/{}/{}.png'.format(side, kind))
                # Resizing, so it will fit for cell size on any screens
                img = img.resize((size,size), Image.ANTIALIAS)
                self.resources[side].append(ImageTk.PhotoImage(img))

    # Returns 1 if (x,y) cell allocated by Active Player, -1 - if unActive, 0 - if cell is empty
    def GetAllocation(self, x, y):
        if (x, y) in self.Players[self.ActivePlayer].figures:
            return 1
        if (x,y) in self.GetUnActivePlayer().figures:
            return -1
        return 0

    # Checks, if ActiveFigure can make move to (x2,y2) cell
    # Note that we don't to check if (x2, y2) allocated by active player's,
    # Bcs if (x2, y2) allocated by active player and was clicked - it selected as active figure,
    # it property provided by Click method
    def MoveIsPossible(self, x2, y2):
        # Player and Figure, which tries to move
        player = self.Players[self.ActivePlayer]
        figure = player.figures[self.ActiveFigure]
        # Figure position
        x1 = figure.x
        y1 = figure.y
        # Infantry case
        if figure.kind == 0:
            dy = 2 * figure.side - 1
            # Forward direction case
            if x1 == x2:
                # If move forward on one cell or on two cells on first step
                if (y2 - y1 == dy) or ((y2 - y1 == 2 * dy) and (not figure.isFirstStepDone)):
                    return self.GetAllocation(x2, y2) == 0
                return False
            # Beating enemy case
            if abs(x1 - x2) == 1:
                # If figure moves forward
                if (y2 - y1 == dy):
                    # If cell really allocated by enemy
                    return self.GetAllocation(x2, y2) == -1
                return False
            return False
        # Tower case
        if figure.kind == 1:
            if x1 == x2:
                # We must have only points between (x1,y1) and (x2, y2)
                # Because (x1, y1) - for sure allocated by active player's figure and lies on board,
                # (x2,y2) - for sure lies on board and is allocated by passive player's figure
                # or empty - it's guaranted by Click method
                if (y2 > y1):
                    start = y1 + 1
                    end = y2
                else:
                    start = y2 + 1
                    end = y1
                # If between (x1,y1) and (x2,y2) exits not epty cell - return False
                for j in range(start, end):
                    if self.GetAllocation(x1, j) != 0:
                        return False
                return True
            if y1 == y2:
                if (x2 > x1):
                    start = x1 + 1
                    end = x2
                else:
                    start = x2 + 1
                    end = x1
                # If between (x1,y1) and (x2,y2) exits not epty cell - return False
                for i in range(start, end):
                    if self.GetAllocation(i, y1) != 0:
                        return False
                return True
            return False
        # Horse case
        if figure.kind == 2:
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            return (dx and dy and (dx + dy == 3))
        # Officer case
        if figure.kind == 3:
            # If moving isn't diagonally
            if abs(x1 - x2) != abs(y1 - y2):
                return False
            # Need to check if line between (x1, y1) and (x2, y2) is free, as in case with tower
            # Vectors of moving from (x1, y1) and (x2, y2)
            vx = 1 if x2 > x1 else -1
            vy = 1 if y2 > y1 else -1
            x = x1
            y = y1
            for i in range(1, abs(x1 - x2)):
                # Next point on line
                x += vx
                y += vy
                # If point isn't empty: return false
                if self.GetAllocation(x, y) != 0:
                    return False
            return True
        # Queen case
        if figure.kind == 4:
            if (x1 == x2) or (y1 == y2) or (abs(x1 - x2) == abs(y1 - y2)):
                return self.CheckLine(x1, y1, x2, y2)
            return False
        # King case
        if figure.kind == 5:
            return (abs(x1 - x2) <= 1 and abs(y1 -y2) <= 1)
        # Actually, this return needless, just for code culture
        return False

    # Invokes, when user clicks on board
    def Click(self):
        def _Click(event):
            # Calculate position of clicked Cell
            i, j = self.GetCell(event.x, event.y)
            # If we cliced on one of Active Player's figures:
            if self.GetAllocation(i, j) == 1:
                # If is previously selected figure - we need to unselect it
                if self.ActiveFigure:
                    self.Players[self.ActivePlayer].figures[self.ActiveFigure].Deactivate()
                # Activate selected figure
                self.Players[self.ActivePlayer].figures[(i,j)].Activate()
                self.ActiveFigure = (i,j)
            else:
                # So, we clicked on empty cell or cell, located by enemy
                # We can continue, only in case if some figure was selected
                if self.ActiveFigure:
                    # If Active figure can make move to (i,j) position - then run next block
                    if self.MoveIsPossible(i, j):
                        self.Players[self.ActivePlayer].figures[self.ActiveFigure].SetPosition(i, j)
                        # Change Active Player to opposite
                        self.ActivePlayer = abs(1 - self.ActivePlayer)
                        self.ActiveFigure = None
        return _Click

    # Return True if line between (x1, y1) and (x2, y2) defined correctly and is empty
    def CheckLine(self, x1, y1, x2, y2):
        if x1 == x2:
            vy = 1 if y2 > y1 else -1
            x = x1
            y = y1
            for i in range(1, abs(y1 - y2)):
                y = y + vy
                if self.GetAllocation(x,y) != 0:
                    return False
            return True
        if y1 == y2:
            vx = 1 if x2 > x1 else -1
            x = x1
            y = y1
            for i in range(1, abs(x1 - x2)):
                x = x + vx
                if self.GetAllocation(x,y) != 0:
                    return False
            return True
        if abs(x1 - x2) == abs(y1 - y2):
            vx = 1 if x2 > x1 else -1
            vy = 1 if y2 > y1 else -1
            x = x1
            y = y1
            for i in range(1, abs(x1 - x2)):
                x = x + vx
                y = y + vy
                if self.GetAllocation(x,y) != 0:
                    return False
            return True
        return False

    # Logic for restarting or running first game
    def NewGame(self):
        # If first game happened - clean Board after it
        if self.Player1:
            self.Player1.CleanFigures()
            self.Player2.CleanFigures()
        self.Player1 = Player(self,0)
        self.Player2 = Player(self,1)
        self.Players = (self.Player1, self.Player2)
        self.ActivePlayer = 0
        self.ActiveFigure = None

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

    # Returns object of unactive player
    def GetUnActivePlayer(self):
        return self.Players[abs(1 - self.ActivePlayer)]

class Player:
    def __init__(self, board, side):
        # I think it's better from OOP conceptions:
        # - Player plays on Board - so Player has Board field to comunicate with Board
        # - Figure belong to player - so Figure has Player field, and can comunicate with him
        # - Also Figure can communicate with Board - through Player.
        # In my opinion, such Ierarchy more natural
        # side: 0 - white player, who goes first, 1 - black
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

    # Cleans all Players's Figures from Board
    def CleanFigures(self):
        for key, figure in self.figures.items():
            self.board.canvas.delete(figure.id)

class Figure:
    # Initializating of figure, it takes kind of figure and side, and coordinates on Board
    # Kind: { 0 - Infantry, 1 - Tower, 2 - Horse, 3 - Officer, 4 - Queen, 5 - King }
    # Side: 0 - White, 1 - Black. White - means, side which goes first
    def __init__(self, player, kind, side, x, y):
        self.player = player
        self.kind = kind
        self.side = side
        # Needed for ability of infantry to make longer first step
        self.isFirstStepDone = False
        # Figure coordinates. It means cell coordinates, tot pixel
        self.x = x
        self.y = y
        # Id for canvas
        self.id = None
        self.Draw()

    def Draw(self):
        img = self.player.board.resources[self.side][self.kind]
        size = self.player.board.cellSize
        self.id = self.player.board.canvas.create_image(self.x * size,self.y * size,image = img, anchor=tk.NW)

    # Litle shifting, it indicates that this figure is active now
    def Activate(self, p=1):
        self.player.board.canvas.move(self.id, 0, p * (2 * self.player.side - 1) * (self.player.board.cellSize // 5))

    # Undoing of activating for activated figure
    def Deactivate(self):
        self.Activate(-1)

    # Change position from (self.x, self.y) to new (x,y)
    def SetPosition(self, x, y):
        cellSize = self.player.board.cellSize
        # If Cell allocated by enemy figure - remove it
        opponent = self.player.board.GetUnActivePlayer()
        if (x,y) in opponent.figures:
            opponent.figures[(x,y)].Remove()
        # Changing position on canvas
        self.player.board.canvas.coords(self.id, cellSize * x, cellSize * y)
        # Update dictionary of figures: create new key for this Figure and delete old one
        self.player.figures[(x,y)] = self
        del self.player.figures[(self.x, self.y)]
        # Update cooordinates
        self.x = x
        self.y = y
        # Tell that Player already made first step
        self.isFirstStepDone = True

    # Removes Figure from canvas and from Player's figures list
    def Remove(self):
        self.player.board.canvas.delete(self.id)
        del self.player.figures[(self.x, self.y)]

Board = Board()

# Since we didn't render all objects inside Board initializing
# And now we just testing - we need to run mainloop outside the Board class

#Board.Player2.figures[(0,0)].SetPosition(3,3)
Board.root.mainloop()