import tkinter as tk
from tkinter import filedialog, messagebox
import polars as pl
import json

class JSONLViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("JSONL Viewer")
        self.master.geometry("800x600")

        self.data = None
        self.current_index = 0

        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_button = tk.Button(self.master, text="Open JSONL File", command=self.load_file)
        self.file_button.pack(pady=10)

        # Navigation
        self.nav_frame = tk.Frame(self.master)
        self.nav_frame.pack(pady=10)

        self.prev_10_button = tk.Button(self.nav_frame, text="<<", command=lambda: self.skip_records(-10), state=tk.DISABLED)
        self.prev_10_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = tk.Button(self.nav_frame, text="Previous", command=self.show_previous, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.show_next, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.next_10_button = tk.Button(self.nav_frame, text=">>", command=lambda: self.skip_records(10), state=tk.DISABLED)
        self.next_10_button.pack(side=tk.LEFT, padx=5)

        self.index_label = tk.Label(self.nav_frame, text="")
        self.index_label.pack(side=tk.LEFT, padx=5)

        # Content display
        self.content_frame = tk.Frame(self.master)
        self.content_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        self.left_frame = tk.Frame(self.content_frame)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.left_label = tk.Label(self.left_frame, text="Current Record")
        self.left_label.pack()
        self.left_text = tk.Text(self.left_frame, wrap=tk.WORD, height=20, width=60)
        self.left_text.pack(expand=True, fill=tk.BOTH)

        self.right_frame = tk.Frame(self.content_frame)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.right_label = tk.Label(self.right_frame, text="Next Record")
        self.right_label.pack()
        self.right_text = tk.Text(self.right_frame, wrap=tk.WORD, height=20, width=60)
        self.right_text.pack(expand=True, fill=tk.BOTH)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSONL files", "*.jsonl")])
        if file_path:
            try:
                self.data = pl.read_ndjson(file_path)
                self.current_index = 0
                self.update_display()
                self.next_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Loaded {len(self.data)} records")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_display(self):
        if self.data is not None and len(self.data) > 0:
            record = self.data.row(self.current_index)
            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(tk.END, record[2])
            self.right_text.delete(1.0, tk.END)
            self.right_text.insert(tk.END, record[3])
            self.index_label.config(text=f"Record {self.current_index + 1} of {len(self.data)}")

            self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_index < len(self.data) - 1 else tk.DISABLED)
            self.prev_10_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_10_button.config(state=tk.NORMAL if self.current_index < len(self.data) - 1 else tk.DISABLED)


    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.update_display()

    def skip_records(self, count):
        if self.data is not None:
            new_index = self.current_index + count
            if 0 <= new_index < len(self.data):
                self.current_index = new_index
            elif new_index < 0:
                self.current_index = 0
            else:
                self.current_index = len(self.data) - 1
            self.update_display()

def main():
    root = tk.Tk()
    app = JSONLViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
