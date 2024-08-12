from argparse import ArgumentParser
from dataclasses import dataclass 
from itertools import chain, pairwise


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("rows", type=int, help="how many rows")
    parser.add_argument("cols", type=int, help="how many cols")
    parser.add_argument("-0", "--zero", action="store_true", help="zero based indices for matrix")
    parser.add_argument("-l", "--label", default="F", help="matrix label")
    return parser.parse_args()


def main():
    args = parse_args()
    mat = Matrix(args.label, args.zero, args.rows, args.cols)
    print(mat.mat_def)
    print(mat.cell_defs)
    print(mat.elem_defs)
    print(mat.arc_defs)
    print("\nAutoLabel All\n")


@dataclass
class Cell:
    label: str
    offset: int

    i: int
    j: int

    @property
    def row(self) -> int:
        return self.i + self.offset

    @property
    def col(self) -> int:
        return self.j + self.offset


@dataclass
class Matrix:
    label: str
    zero_based: bool

    m: int
    n: int

    @property
    def offset(self) -> int:
        return 1 if self.zero_based else 1

    @property
    def row_idxs(self):
        return range(self.m)

    @property
    def col_idxs(self):
        return range(self.n)

    @property
    def idxs(self) -> list[tuple[int, int]]:
        return [(i, j) for i in self.row_idxs for j in self.col_idxs]

    @property
    def cells(self) -> list[list[Cell]]:
        cell_label = self.label.lower()
        rows = self.row_idxs
        cols = self.col_idxs
        if self.zero_based:
            return [
                [Cell(cell_label, 1, i, j) for j in cols] for i in rows
            ]
        return [
            [Cell(cell_label, 0, i + 1, j + 1) for j in cols] for i in rows
        ]

    @property
    def mat_def(self) -> str:
        return f"Matrix {self.label}\nDim({self.label}, {self.m}, {self.n})\n"

    @property
    def cell_defs(self) -> str:
        lines = []
        for row in self.cells:
            start = "Cell "
            rest = ", ".join([f"{cell.label}_{cell.i}{cell.j}" for cell in row])
            lines.append(start + rest)
        return "\n".join(lines) + "\n"

    @property
    def elem_defs(self) -> str:
        lines = []
        for row_of_cells in self.cells:
            for cell in row_of_cells:
                line = (
                    f"Elem({cell.label}_{cell.i}{cell.j}, "
                    f"{self.label}, {cell.row}, {cell.col})"
                )
                lines.append(line)
            lines.append("")

        return "\n".join(lines[:-1]) + "\n"

    @property
    def arc_defs(self):
        lines = []
        for n, (prv, nxt) in enumerate(pairwise(chain(*self.cells))):
            prv_label, g, h = prv.label, prv.i, prv.j
            line = (
                f"Arrow a_{n:02} := "
                f"Arc(f_{g}{h}, {nxt.label}_{nxt.i}{nxt.j})"
            )
            lines.append(line)

        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()

