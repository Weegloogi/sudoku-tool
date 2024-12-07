from __future__ import annotations

import sys
import itertools
from dataclasses import dataclass, field
from typing import Union

import tools


# colors for highlights
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Cell:
    def __init__(self, id: int, digit=None):
        self.id = id

        self.isSolved: bool = False
        self.digit: int = 0  # 0 if the digit is not yet solved
        self.options: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.sees: list[Cell] = []

        self.row = id // 9
        self.col = id % 9
        self.box = (self.row // 3) * 3 + (self.col // 3)

        if digit:
            self.options = []
            self.isSolved = True

    def __repr__(self):
        return f"Cell(row={self.row}, col={self.col})"

    def __str__(self):
        return f"r{self.row + 1}c{self.col + 1}"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id, self.digit, hash(tuple(self.options))))

    def add_see(self, see: Cell):
        if see != self:
            self.sees.append(see)

    def add_sees(self, sees: list[Cell]):

        for cell in sees:
            if (cell not in self.sees) and (cell != self):
                self.add_see(cell)


@dataclass
class Highlight:
    """
    Information about a cell highlight
    cell: the cell to highlight
    cellColor: background color of the cell
    digitColors: background color of the candidates (if any)
    """
    cell: Cell  # the cell
    cellColor: Union[tuple[int, int, int], type(None)]  # the background color of a cell (rgb)
    digitColors: list[tuple[int, tuple[int, int, int]]]  # the list of digits to highlight in cell (digit, rgb)


@dataclass
class Elimination:
    """
    Information about an elimination
    is_useful: whether this elimination has any data in solved_cells or eliminated_candidates
    solved_cells: list of cells where a digit is placed with this elimination
    eliminated_candidates: list of cells for which a candidate is eliminated
    message: the log message that is written with this elimination
    highlights: which cells to highlight for a solver that supports this feature
    """
    solved_cells: list[tuple[Cell, int]]
    eliminated_candidates: list[tuple[Cell, int]]
    message: str
    highlights: list[Highlight]
    is_useful: bool = field(default=False)


class Puzzle:
    def __init__(self):
        # initialize board
        self.board: list[list[Cell]] = [[Cell(y * 9 + x) for x in range(9)] for y in range(9)]

        self.cells: list[Cell] = []
        self.boxes: list[list[Cell]] = [[] for _ in range(9)]
        self.columns: list[list[Cell]] = [[] for _ in range(9)]
        self.rows: list[list[Cell]] = self.board  # self.board is stored as a list of rows so we can just copy it

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
                self.cells.append(cell)

        for box in self.boxes:
            for cell in box:
                cell.add_sees(box)

    def import_board(self, board_str):
        if len(board_str) != 81:
            raise ValueError("Length of a board string must equal to 81")

        # empty the current board
        self.__init__()

        for i, c in enumerate(board_str):
            if c == '0':
                continue

            if not '0' < c <= '9':
                raise ValueError(f"Character at index {i} is not 0-9")

            puzzle.add_clue(self.cells[i].row, self.cells[i].col, int(c))


    def is_solved(self) -> bool:
        """
        Checks if the puzzle is solved
        :return: True if the puzzle is solved, False otherwise
        """
        for cell in self.cells:
            if not cell.isSolved:
                return False

        return True

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

    def print_board(self, large=True, outstream=sys.stdout):

        if large:
            for row in range(9):
                print("         |         |         ", file=outstream)
                for col in range(9):
                    cell = self.board[row][col]
                    if cell.isSolved:
                        print(f" {cell.digit} ", end="", file=outstream)
                    else:
                        print(" . ", end="", file=outstream)

                    if col in [2, 5]:
                        print("|", end="", file=outstream)

                print("\n         |         |         ", file=outstream)
                if row in [2, 5]:
                    print("---------+---------+---------", file=outstream)
        else:
            for row in range(9):
                for col in range(9):
                    cell = self.board[row][col]
                    if cell.isSolved:
                        print(cell.digit, end="", file=outstream)
                    else:
                        print(".", end="", file=outstream)

                    if (col in [2, 5]):
                        print("|", end="", file=outstream)

                print("\n", end="", file=outstream)
                if (row in [2, 5]):
                    print("---+---+---", file=outstream)

    def apply_elimination(self, elim: Elimination) -> bool:
        for c, d in elim.solved_cells:
            c.isSolved = True
            c.options = [d]
            c.digit = d

        for c,d in elim.eliminated_candidates:
            c.options.remove(d)

        return elim.is_useful


    # naked singles
    def check_solved_cells(self) -> Elimination:
        """
        Checks every cell if it only has one possible digit left, in which case the cell is solved and we can fill in that digit
        returns True if any cells were solved, False otherwise
        """

        elim = Elimination([], [], "Naked singles, the following digits can be placed:", [])

        for cell in self.cells:
            if len(cell.options) == 1:
                d = cell.options[0]

                elim.solved_cells.append((cell, d))
                elim.message += f"\n- {d} placed in r{cell.row + 1}c{cell.col + 1}"
                elim.highlights.append(Highlight(cell, None, [d, GREEN]))
                elim.is_useful = True

        return elim

    def check_hidden_singles(self) -> Elimination:
        """
        Checks for every house if there is a digit that only has 1 available cell remaining.
        If there is one such digit, we can fill in that digit in that cell.
        returns True if we found any hidden singles, False otherwise
        """

        elim = Elimination([], [], "Hidden singles, the following digits can be placed:", [])

        for digit in range(1, 10):
            houses = [(self.boxes, "Box"), (self.rows, "Row"), (self.columns, "Column")]
            for _houses in houses:
                for house in _houses[0]: # look at an individual box/row/column
                    possibilities = []
                    for cell in house:
                        if digit in cell.options:
                            possibilities.append(cell)

                    if len(possibilities) == 1:
                        cell = possibilities[0]

                        x = ""
                        if _houses[1] == "Box":
                            x = f"Box {cell.box + 1}"
                        elif _houses[1] == "Row":
                            x = f"Row {cell.row + 1}"
                        elif _houses[1] == "Column":
                            x = f"Column {cell.col + 1}"

                        elim.solved_cells.append((cell, digit))
                        elim.highlights.append(Highlight(cell, None, [(digit, GREEN)]))
                        elim.message += f"\n- {digit} exclusive to r{cell.row + 1}c{cell.col + 1} in {x}: {digit} can be placed there"
                        elim.is_useful = True

        return elim

    def check_pointing_pairs(self) -> list[Elimination]:
        """
        Checks every box if the all remaining options for a digit see the same cell,
        in which case that digit can be removed from that cell.
        returns True if any digits were eliminated, otherwise False
        """
        elims = []

        for digit in range(1,10):

            for i, box in enumerate(self.boxes):
                remaining_options = [c for c in box if digit in c.options]

                # a pointing pair can only occur if there are 2 or 3 remaining cells
                if len(remaining_options) == 2:
                    seen_by_all = list(set(remaining_options[0].sees) & set(remaining_options[1].sees))
                elif len(remaining_options) == 3:
                    seen_by_all = list(set(remaining_options[0].sees) &
                                       set(remaining_options[1].sees) &
                                       set(remaining_options[2].sees))
                else:
                    continue

                eliminated_cells = [c for c in seen_by_all if digit in c.options]

                if len(eliminated_cells) > 0:

                    elims.append(Elimination(solved_cells=[],
                                             eliminated_candidates=[(c, digit) for c in eliminated_cells],
                                             message=f"Pointing pair in box {i+1}: {digit} can be eliminated from {', '.join([f'r{c.row}c{c.col}' for c in eliminated_cells])}",
                                             highlights=[Highlight(c, None, [(digit, RED)]) for c in eliminated_cells],
                                             is_useful=True))

        return elims

    def check_box_line_reduction(self) -> list[Elimination]:
        """
        Checks for every line if a digit is restricted to a single box,
        in which case, the digit can be removed from any cell in that box that is not on the line.
        """

        elim = []
        pass_successful = True
        while pass_successful:
            pass_successful = False

            for digit in range(1,10):

                for _house in ((self.rows, "row"), (self.columns, "column")):
                    for i, line in enumerate(_house[0]):
                        remaining_options = [c for c in line if digit in c.options]
                        boxes = set()
                        for option in remaining_options:
                            boxes.add(option.box)

                        if len(boxes) == 1:
                            elims = []
                            for cell in self.boxes[remaining_options[0].box]:
                                if cell not in line:
                                    if digit in cell.options:
                                        elims.append(cell)

                            if len(elims) > 0:
                                _return = True
                                pass_successful = True

                                elim.append(Elimination(solved_cells=[],
                                                        eliminated_candidates=[(c, digit) for c in elims],
                                                        message=f"Box line reduction in {_house[1]} {i + 1}: {digit} can be eliminated from {', '.join([f'r{c.row}c{c.col}' for c in elims])}",
                                                        highlights=[Highlight(c, None, [(digit, RED)]) for c in
                                                                    elims]))

        return elim

    def check_naked_n_tuples(self, n: int) -> list[Elimination]:
        """
        Checks for every row/column/box if there is a set of n digits that are exclusive to n cells
        """

        if n < 2:
            raise ValueError("Cannot check for naked n-tuples with n<2 in this function")

        elim: list[Elimination] = []
        pass_successful = True
        while pass_successful:
            pass_successful = False

            for _house in ((self.boxes, "Box"), (self.rows, "Row"), (self.columns, "Column")):
                for house in _house[0]:

                    for digits in set(itertools.combinations(range(1,10), n)):
                       for cells in set(itertools.combinations(house, n)):
                            if tools.any(cells, lambda x: x.isSolved):
                                continue

                            # check if for all selected cells, every cell's candidates is a subset of the selected digits
                            if tools.all(cells, lambda x: set(x.options) <= set(digits)):

                                # naked n-tuple found

                                # filter all cells that don't have any digits of the naked pair as candidates
                                elims = {}
                                for d in digits:
                                    elims[d] = []

                                for c in house:
                                    if c in cells:
                                        continue

                                    for d in digits:
                                        if d in c.options:
                                            elims[d].append(c)

                                if tools.any(elims, lambda x: len(elims[x]) > 0):
                                    pass_successful = True
                                    _return = True

                                    logmsg = ""
                                    match _house[1]:
                                        case "Box":
                                            logmsg = f"Naked {n}-tuple ({''.join([str(x) for x in digits])} found in Box {cells[0].box + 1}: The following can be eliminated:"
                                        case "Row":
                                            logmsg = f"Naked {n}-tuple ({''.join([str(x) for x in digits])} found in Row {cells[0].row + 1}: The following can be eliminated:"
                                        case "Column":
                                            logmsg = f"Naked {n}-tuple ({''.join([str(x) for x in digits])} found in Column {cells[0].col + 1}: The following can be eliminated:"

                                    for d in elims:
                                        if len(elims[d]) > 0:
                                            logmsg += f"\n{d} removed from {', '.join([str(x) for x in elims[d]])}"

                                    for d in elims:
                                        for c in elims[d]:
                                            c.options.remove(d)

                                    elim.append(Elimination(solved_cells=[],
                                                            eliminated_candidates=[(c, d) for d in elims for c in elims[d]],
                                                            message=logmsg,
                                                            highlights=[Highlight(c, None, [(d, RED)]) for d in elims for c in elims[d]],
                                                            is_useful=True))
        return elim

    def check_y_wing(self, log=False):
        _return = False
        pass_successful = True
        while pass_successful:
            pass_successful = False

            bi_values = tools.filter(puzzle.cells, lambda x: len(x.options) == 2)

            # select pivot
            for pivot in bi_values:

                # select A, B
                for cells in itertools.combinations(bi_values, 2):

                    if pivot in cells:
                        continue

                    # pivot must see both A and B
                    # but A must not see B
                    if cells[0] not in pivot.sees:
                        continue
                    if cells[1] not in pivot.sees:
                        continue
                    if cells[0] in cells[1].sees:
                        continue

                    # there must be exactly 3 different numbers
                    unique_digits = set(pivot.options)
                    tools.accumulate(cells, lambda x: tools.accumulate(x.options, unique_digits.add))

                    if len(unique_digits) != 3:
                        continue

                    # the 3 different numbers must each occur twice
                    all_cells = set(cells)
                    all_cells.add(pivot)

                    bad = False
                    for d in unique_digits:
                        total = 0
                        for x in all_cells:
                            if d in x.options:
                                total += 1

                        if total != 2:
                            bad = True

                    if bad:
                        continue



                    Z = next(iter(unique_digits.difference(set(pivot.options))))

                    seen_by_both = [x for x in cells[0].sees if x in cells[1].sees]
                    elims = [x for x in seen_by_both if Z in x.options]

                    if len(elims) > 0:
                        _return = True
                        pass_successful = True

                        if log:
                            print(f"Y-wing hinged at {pivot} on {cells[0]} and {cells[1]}: {Z} can be eliminated from {', '.join([str(x) for x in elims])}")

                        for c in elims:
                            c.options.remove(Z)

        return _return


    def solve_puzzle(self):

        while not self.is_solved():

            res = self.check_solved_cells()
            if self.apply_elimination(res):
                continue

            res = self.check_hidden_singles()
            if self.apply_elimination(res):
                continue

            res = self.check_pointing_pairs()
            if any(self.apply_elimination(elim) for elim in res):
                continue

            res = self.check_box_line_reduction()
            if any(self.apply_elimination(elim) for elim in res):
                continue

            # checking naked n-tuple for 5,6,7, covers hidden n-tuple for 2,3,4
            res_list = (self.check_naked_n_tuples(n) for n in range(2, 8))
            if any(self.apply_elimination(elim) for res in res_list for elim in res):
                continue

            if self.check_y_wing(True):
                continue

            break


if __name__ == "__main__":
    puzzle = Puzzle()
    puzzle.add_clue(0, 0, 9)
    puzzle.add_clue(0, 3, 8)
    puzzle.add_clue(0,  5, 5)
    puzzle.add_clue(0, 8, 2)
    puzzle.add_clue(2, 1, 5)
    puzzle.add_clue(2, 3, 2)
    puzzle.add_clue(2, 4, 9)
    puzzle.add_clue(2, 5, 6)
    puzzle.add_clue(2, 7, 7)
    puzzle.add_clue(3, 1, 9)
    puzzle.add_clue(3, 4, 3)
    puzzle.add_clue(3, 7, 1)
    puzzle.add_clue(4, 2, 8)
    puzzle.add_clue(4, 6, 5)
    puzzle.add_clue(5, 1, 2)
    puzzle.add_clue(5, 4, 5)
    puzzle.add_clue(5, 7, 8)
    puzzle.add_clue(6, 1, 7)
    puzzle.add_clue(6, 3, 6)
    puzzle.add_clue(6, 4, 2)
    puzzle.add_clue(6, 5, 9)
    puzzle.add_clue(6, 7, 3)
    puzzle.add_clue(8, 0, 1)
    puzzle.add_clue(8, 3, 7)
    puzzle.add_clue(8, 5, 3)
    puzzle.add_clue(8, 8, 8)
    puzzle.solve_puzzle()
    puzzle.print_board(large=False)
