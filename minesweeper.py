import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        if len(cells) == count:
            self.cells = set()
            self.mines = set(cells)
            self.safes = set()
            self.count = 0
        elif count == 0:
            self.cells = set()
            self.mines = set()
            self.safes = set(cells)
            self.count = count
        else:
            self.cells = set(cells)
            self.mines = set()
            self.safes = set()
            self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.safes.add(cell)
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # neighbor vectors
        self.neighbor_vectors = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                                  (0, 1), (1, -1), (1, 0), (1, 1))

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        # print(f"marking mine {cell}")
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # print(f"marking safe {cell}")
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def update_knowledge(self, cells, count):
        """
        Called when add_knowledge is called and a new sentence is formed,
        to add the sentence into the knowledge base and infer more sentences

        This function should:
            1) add the new sentence to the AI's knowledge base
                based off of cells and count
            2) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            3) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # form new sentence and mark safes and mines from the sentence
        sentence = Sentence(cells, count)
        if sentence not in self.knowledge:
            # print(f"adding sentence {sentence}")
            self.knowledge.append(sentence)

        safes = set(sentence.safes)
        mines = set(sentence.mines)
        # check if sentence reveals new info
        for st in self.knowledge:
            # print(f"check sentence {st}")
            if st.count == 0:
                # all safe
                safes.update(st.cells)
            elif len(st.cells) == st.count:
                # mines
                mines.update(st.cells)

        # while new safes or mines found
        while len(safes) > 0 or len(mines) > 0:
            # update knowledge base
            for safe in safes:
                self.mark_safe(safe)
            for mine in mines:
                self.mark_mine(mine)
            # reset
            safes.clear()
            mines.clear()
            # check if sentence reveals new info
            for st in self.knowledge:
                # print(f"check sentence {st}")
                if st.count == 0:
                    # all safe
                    safes.update(st.cells)
                elif len(st.cells) == st.count:
                    # print(f"found new mines {st.cells}")
                    # mines
                    mines.update(st.cells)

        # apply deduction rule
        l0 = 0
        while l0 < len(self.knowledge):
            l0 = len(self.knowledge)
            for s1 in self.knowledge.copy():
                for s2 in self.knowledge.copy():
                    if s1 == s2 or s1.count == 0 or s2.count == 0:
                        continue
                    # found subset, update with diff set with diff count
                    if s1.cells <= s2.cells:
                        self.update_knowledge(s2.cells - s1.cells, s2.count - s1.count)
                    elif s1.cells > s2.cells:
                        self.update_knowledge(s1.cells - s2.cells, s1.count - s2.count)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = set()
        for vec in self.neighbor_vectors:
            neighbor = (cell[0] + vec[0], cell[1] + vec[1])
            if (neighbor[0] in range(0, self.height) and 
                neighbor[1] in range(0, self.width) and
                neighbor not in self.moves_made):
                if neighbor in self.mines:
                    count -= 1
                elif neighbor not in self.safes:
                    neighbors.add(neighbor)

        self.update_knowledge(neighbors, count)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
            
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        move = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
        while move in self.moves_made or move in self.mines:
            move = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))

        return move
        