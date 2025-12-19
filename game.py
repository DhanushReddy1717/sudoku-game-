import tkinter as tk
from tkinter import messagebox
from copy import deepcopy

# A sample puzzle; 0 means empty
PUZZLES = [
    [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],

        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],

        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    [
        [0,0,0, 2,6,0, 7,0,1],
        [6,8,0, 0,7,0, 0,9,0],
        [1,9,0, 0,0,4, 5,0,0],

        [8,2,0, 1,0,0, 0,4,0],
        [0,0,4, 6,0,2, 9,0,0],
        [0,5,0, 0,0,3, 0,2,8],

        [0,0,9, 3,0,0, 0,7,4],
        [0,4,0, 0,5,0, 0,3,6],
        [7,0,3, 0,1,8, 0,0,0],
    ]
]

def is_valid(board, r, c, val):
    # row/col
    for i in range(9):
        if board[r][i] == val: return False
        if board[i][c] == val: return False
    # box
    br, bc = (r//3)*3, (c//3)*3
    for i in range(3):
        for j in range(3):
            if board[br+i][bc+j] == val: return False
    return True

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def solve_board(board):
    empty = find_empty(board)
    if not empty: return True
    r, c = empty
    for v in range(1, 10):
        if is_valid(board, r, c, v):
            board[r][c] = v
            if solve_board(board):
                return True
            board[r][c] = 0
    return False

class SudokuApp:
    def __init__(self, root):
        self.root = root
        root.title("Sudoku (Python Tkinter)")
        self.board_original = deepcopy(PUZZLES[0])
        self.board = deepcopy(self.board_original)
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.selected = None
        self.note_mode = tk.BooleanVar(value=False)

        self.build_ui()
        self.render()

    def build_ui(self):
        top = tk.Frame(self.root, padx=8, pady=8)
        top.pack()

        # Toolbar
        toolbar = tk.Frame(top)
        toolbar.pack(fill="x", pady=(0,8))

        tk.Button(toolbar, text="New", command=self.load_next_puzzle).pack(side="left", padx=4)
        tk.Button(toolbar, text="Clear", command=self.clear_to_puzzle).pack(side="left", padx=4)
        tk.Button(toolbar, text="Hint", command=self.hint_one).pack(side="left", padx=4)
        tk.Button(toolbar, text="Solve", command=self.solve_all).pack(side="left", padx=4)
        tk.Checkbutton(toolbar, text="Notes", variable=self.note_mode).pack(side="left", padx=12)

        self.status = tk.Label(toolbar, text="", fg="#2563eb")
        self.status.pack(side="right")

        # Grid
        self.grid = tk.Frame(top, bg="#111827")
        self.grid.pack()

        self.cells = [[None]*9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                frame = tk.Frame(self.grid, width=50, height=50)
                frame.grid(row=r, column=c, padx=(0 if c%3 else 2, 2), pady=(0 if r%3 else 2, 2))
                frame.grid_propagate(False)

                cell = tk.Canvas(frame, bg="#111827", highlightthickness=0)
                cell.pack(fill="both", expand=True)
                cell.bind("<Button-1>", lambda e, rr=r, cc=c: self.select_cell(rr, cc))
                cell.bind("<Key>", lambda e, rr=r, cc=c: self.on_key(rr, cc, e))
                self.cells[r][c] = cell

        # Keypad (optional, use keyboard too)
        kp = tk.Frame(top)
        kp.pack(pady=8)
        for v in range(1,10):
            tk.Button(kp, text=str(v), width=3, command=lambda x=v: self.place_value_key(x)).pack(side="left", padx=2)
        tk.Button(kp, text="Erase", width=5, command=lambda: self.place_value_key(0)).pack(side="left", padx=8)

    def render(self):
        for r in range(9):
            for c in range(9):
                cell = self.cells[r][c]
                cell.delete("all")

                # Borders thicker every 3
                width = 1
                if c in (0,3,6): cell.create_line(0,0,0,50, fill="#374151", width=2)
                if r in (0,3,6): cell.create_line(0,0,50,0, fill="#374151", width=2)
                if c == 8: cell.create_line(50,0,50,50, fill="#374151", width=2)
                if r == 8: cell.create_line(0,50,50,50, fill="#374151", width=2)

                val = self.board[r][c]
                orig = self.board_original[r][c] != 0
                bg = "#0b1220" if orig else "#111827"
                cell.configure(bg=bg)

                if self.selected and self.selected == (r,c):
                    cell.create_rectangle(2,2,48,48, outline="#60a5fa", width=2)

                if val != 0:
                    color = "#9ca3af" if orig else "#e5e7eb"
                    cell.create_text(25,25, text=str(val), fill=color, font=("Segoe UI", 16, "bold"))
                else:
                    # Render notes
                    if self.notes[r][c]:
                        for n in self.notes[r][c]:
                            row = (n-1)//3
                            col = (n-1)%3
                            x = 12 + col*16
                            y = 12 + row*16
                            cell.create_text(x, y, text=str(n), fill="#6b7280", font=("Segoe UI", 8))

    def set_status(self, msg):
        self.status.config(text=msg)

    def select_cell(self, r, c):
        if self.board_original[r][c] != 0:
            self.selected = None
            self.render()
            self.set_status("Fixed clue; can't edit")
            return
        self.selected = (r,c)
        self.cells[r][c].focus_set()
        self.set_status(f"Selected ({r+1},{c+1})")
        self.render()

    def on_key(self, r, c, e):
        if e.keysym in [str(i) for i in range(10)] or e.char in "0123456789":
            val = int(e.char)
            self.apply_value(r, c, val)
        elif e.keysym in ("BackSpace", "Delete"):
            self.apply_value(r, c, 0)
        elif e.keysym in ("Escape",):
            self.selected = None
            self.render()

    def place_value_key(self, val):
        if not self.selected: return
        r, c = self.selected
        self.apply_value(r, c, val)

    def apply_value(self, r, c, val):
        if self.board_original[r][c] != 0:
            self.set_status("Fixed clue; can't edit")
            return

        if self.note_mode.get() and val != 0 and self.board[r][c] == 0:
            if val in self.notes[r][c]:
                self.notes[r][c].remove(val)
            else:
                self.notes[r][c].add(val)
            self.set_status(f"Note {val} toggled")
            self.render()
            return

        self.notes[r][c].clear()

        if val == 0:
            self.board[r][c] = 0
            self.set_status("Erased")
            self.render()
            return

        # Validate against current board view
        temp = deepcopy(self.board)
        temp[r][c] = 0
        if not is_valid(temp, r, c, val):
            self.flash_cell(r, c, conflict=True)
            self.set_status("Conflict with row/column/box")
            return

        self.board[r][c] = val
        self.flash_cell(r, c, conflict=False)
        self.set_status(f"Placed {val}")
        self.render()

        # Check completion
        if self.is_complete():
            messagebox.showinfo("Sudoku", "Solved! Nice work.")

    def flash_cell(self, r, c, conflict=False):
        cell = self.cells[r][c]
        color = "#7f1d1d" if conflict else "#064e3b"
        original_bg = cell["bg"]
        cell.configure(bg=color)
        self.root.after(200, lambda: (cell.configure(bg=original_bg), self.render()))

    def is_complete(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        # Optional: full validity check
        temp = deepcopy(self.board)
        for r in range(9):
            row = [x for x in temp[r] if x != 0]
            if len(set(row)) != len(row): return False
        for c in range(9):
            col = [temp[r][c] for r in range(9) if temp[r][c] != 0]
            if len(set(col)) != len(col): return False
        for br in range(0,9,3):
            for bc in range(0,9,3):
                box = []
                for i in range(3):
                    for j in range(3):
                        v = temp[br+i][bc+j]
                        if v != 0: box.append(v)
                if len(set(box)) != len(box): return False
        return True

    def hint_one(self):
        temp = deepcopy(self.board)
        if not solve_board(temp):
            self.set_status("No solution from current state")
            return
        # Fill first empty with solution's value
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    self.board[r][c] = temp[r][c]
                    self.notes[r][c].clear()
                    self.flash_cell(r, c, conflict=False)
                    self.set_status(f"Hint: ({r+1},{c+1}) = {temp[r][c]}")
                    self.render()
                    return
        self.set_status("No empty cells for hint")

    def solve_all(self):
        temp = deepcopy(self.board)
        if not solve_board(temp):
            self.set_status("No solution from current state")
            return
        self.board = temp
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.render()
        self.set_status("Solved!")

    def clear_to_puzzle(self):
        self.board = deepcopy(self.board_original)
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.selected = None
        self.render()
        self.set_status("Cleared to puzzle")

    def load_next_puzzle(self):
        # Rotate through the predefined puzzles
        idx = PUZZLES.index(self.board_original) if self.board_original in PUZZLES else 0
        next_idx = (idx + 1) % len(PUZZLES)
        self.board_original = deepcopy(PUZZLES[next_idx])
        self.clear_to_puzzle()
        self.set_status("New puzzle loaded")

def main():
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
