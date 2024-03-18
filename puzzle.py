from __future__ import annotations


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

        if col < 0 or col >= 8:
            raise ValueError("Column must be between 0 and 8")

        if digit < 1 or digit >= 10:
            raise ValueError("Digits must be between 1 and 9")

        # mark the cell as solved
        self.board[row][col].isSolved = True
        self.board[row][col].digit = digit
        self.board[row][col].options.clear()

        # remove the option from any cell
        for cell in self.board[row][col].sees:
            cell.options.remove(digit)


if __name__ == "__main__":
    import pprint

    puzzle = Puzzle()
    pprint.pprint(puzzle.get_cell(4, 4).sees)