from __future__ import annotations

import sys


class Cell:
    def __init__(self, id: int, digit=None):
        self.id = id

        self.isSolved: bool = False
        self.digit: int = 0  # 0 if the digit is not yet solved
        self.options: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sees: list[Cell] = []

        if digit:
            self.options = []
            self.isSolved = True

    def __repr__(self):
        return f"Cell(row={self.id // 9}, col={self.id % 9})"

    def __str__(self):
        return f"Cell(row={self.id // 9 + 1}, col={self.id % 9 + 1})"

    def __eq__(self, other):
        return self.id == other.id

    def add_see(self, see: Cell):
        if see != self:
            self.sees.append(see)

    def add_sees(self, sees: list[Cell]):

        for cell in sees:
            if (cell not in self.sees) and (cell != self):
                self.add_see(cell)


class Puzzle:
    def __init__(self):
        # initialize board
        self.board: list[list[Cell]] = [[Cell(y * 9 + x) for x in range(9)] for y in range(9)]

        self.boxes = [[] for _ in range(9)]
        self.columns = [[] for _ in range(9)]
        self.rows = self.board # self.board is stored as a list of rows so we can just copy it

        # for every cell, add all the cells that it sees
        for row in range(9):
            for col in range(9):
                self.board[row][col].add_sees(self.board[row])  # every cell sees all other cells in that row
                self.board[row][col].add_sees(
                    [x[col] for x in self.board])  # every cell sees all other cells in that column

                box = (row // 3) * 3 + (col // 3)
                cell = self.board[row][col]
                self.boxes[box].append(cell)
                self.columns[col].append(cell)

        for box in self.boxes:
            for cell in box:
                cell.add_sees(box)

    def get_cell(self, row: int, col: int) -> Cell:
        if row < 0 or row >= 9:
            raise ValueError("Row must be between 0 and 8")

        if col < 0 or col >= 9:
            raise ValueError("Column must be between 0 and 8")

        return self.board[row][col]

    def add_clue(self, row: int, col: int, digit: int):
        if row < 0 or row >= 9:
            raise ValueError("Row must be between 0 and 8")

        if col < 0 or col >= 9:
            raise ValueError("Column must be between 0 and 8")

        if digit < 1 or digit >= 10:
            raise ValueError("Digits must be between 1 and 9")

        # mark the cell as solved
        self.board[row][col].isSolved = True
        self.board[row][col].digit = digit
        self.board[row][col].options.clear()

        # remove the option from any cell
        for cell in self.board[row][col].sees:
            if digit in cell.options:
                cell.options.remove(digit)

    def print_board(self, large=True, outstream = sys.stdout):

        if large:
            for row in range(9):
                print("         |         |         ", file=outstream)
                for col in range(9):
                    cell = self.board[row][col]
                    if cell.isSolved:
                        print(f" {cell.digit} ", end="", file=outstream)
                    else:
                        print(" . ", end="", file=outstream)

                    if (col in [2,5]):
                        print("|", end="", file=outstream)

                print("\n         |         |         ", file=outstream)
                if (row in [2,5]):
                    print("---------+---------+---------", file=outstream)
        else:
            for row in range(9):
                for col in range(9):
                    cell = self.board[row][col]
                    if cell.isSolved:
                        print(cell.digit, end="", file=outstream)
                    else:
                        print(".", end="", file=outstream)

                    if (col in [2,5]):
                        print("|", end="", file=outstream)

                print("\n", end="", file=outstream)
                if (row in [2,5]):
                    print("---+---+---", file=outstream)

    # naked singles
    def check_solved_cells(self, log=False):
        """
        Checks every cell if it only has one possible digit left, in which case the cell is solved and we can fill in that digit
        """

        pass_successful = True
        while pass_successful:
            pass_successful = False

            for row in range(9):
                for col in range(9):
                    cell = self.board[row][col]

                    if len(cell.options) == 1:
                        pass_successful = True
                        digit = cell.options[0]
                        self.add_clue(row, col, cell.options[0])

                        if log:
                            print(f"Naked single: r{row + 1}c{col + 1} must be a {digit}")


    def check_hidden_singles(self, log=False):
        """
        Checks for every house if there is a digit that only has 1 available cell remaining.
        If there is one such digit, we can fill in that digit in that cell.
        """
        pass_successful = True
        while pass_successful:
            pass_successful = False

            for digit in range(1, 10):
                # check boxes
                houses = [(self.boxes, "Box"), (self.rows, "Row"), (self.columns, "Column")]

                for _houses in houses:

                    for house in _houses[0]:
                        possibilities = []
                        for cell in house:
                            if digit in cell.options:
                                possibilities.append(cell)

                        if len(possibilities) == 1:
                            pass_successful = True

                            cell = possibilities[0]
                            r, c = cell.id // 9, cell.id % 9
                            digit = possibilities[0]

                            self.add_clue(r, c, digit)

                            if log:
                                if _houses[1] == "Box":
                                    print(f"Hidden Single in Box {(r//3) * 3 + (c//3)}: r{r}c{c} must be a {digit}")
                                elif _houses[1] == "Row":
                                    print(f"Hidden Single in Row {r}: r{r}c{c} must be a {digit}")
                                elif _houses[1] == "Column":
                                    print(f"Hidden Single in Column {c}: r{r}c{c} must be a {digit}")


if __name__ == "__main__":
    import pprint

    puzzle = Puzzle()
    puzzle.add_clue(0, 0, 1)
    puzzle.add_clue(0, 1, 2)
    puzzle.add_clue(0, 2, 3)
    puzzle.add_clue(0, 3, 4)
    puzzle.add_clue(0, 4, 5)
    puzzle.add_clue(0, 5, 6)
    puzzle.add_clue(0, 6, 7)
    puzzle.add_clue(0, 7, 8)
    puzzle.check_solved_cells(log=True)
    puzzle.print_board(large=False)
