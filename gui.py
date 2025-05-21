import tkinter as tk
from tkinter import ttk
from syntax_analyzer import analyze, lexical_analyze
from lark import Lark, Transformer, v_args, Token
import sys
import io

# Define preserved keywords
KEYWORDS = [
    "if", "end", "while", "loop", "in", "loop_while", "true", "false", "print"
]

# === Helper Functions ===

def highlight_keywords(code):
    for tag in text_input.tag_names():
        text_input.tag_remove(tag, "1.0", tk.END)

    for keyword in KEYWORDS:
        start = "1.0"
        while True:
            start = text_input.search(rf"\b{keyword}\b", start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(keyword)}c"
            text_input.tag_add("keyword", start, end)
            start = end

    text_input.tag_config("keyword", foreground="blue", font=("Courier New", 12, "bold"))

# === Analysis Functions ===

def run_syntax_analysis(code):
    syntax_output.delete("1.0", tk.END)

    # Redirect stdout in case analyze() prints
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        result, runtime_error = analyze(code)
    except Exception as e:
        result = ""
        runtime_error = str(e)

    sys.stdout = old_stdout
    printed_output = redirected_output.getvalue()

    syntax_output.insert("1.0", result or printed_output)
    if runtime_error:
        syntax_output.insert(tk.END, f"\n\nRuntime Error:\n{runtime_error}")

def run_lexical_analysis(code):
    lexical_output.delete("1.0", tk.END)

    try:
        result = lexical_analyze(code)
    except Exception as e:
        result = f"Error during lexical analysis:\n{e}"

    lexical_output.insert("1.0", result)

# === Combined Analyze Button ===

def on_analyze():
    code = text_input.get("1.0", "end-1c")
    highlight_keywords(code)
    run_syntax_analysis(code)
    run_lexical_analysis(code)

# === GUI Setup ===

root = tk.Tk()
root.title("MiniScript Analyzer")
root.geometry("1000x600")

# Layout containers
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

# === Code Input ===
input_scrollbar = tk.Scrollbar(left_frame)
input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_input = tk.Text(
    left_frame, font=("Courier New", 12), wrap="word", yscrollcommand=input_scrollbar.set
)
text_input.pack(fill=tk.BOTH, expand=True)
input_scrollbar.config(command=text_input.yview)

# === Syntax Output ===
syntax_label = tk.Label(right_frame, text="Syntax Analysis", font=("Arial", 12, "bold"))
syntax_label.pack(anchor="w")

syntax_output = tk.Text(
    right_frame, height=15, width=40, bg="#f0f0f0", fg="black",
    font=("Courier New", 11), wrap="word"
)
syntax_output.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# === Lexical Output ===
lexical_label = tk.Label(right_frame, text="Lexical Analysis", font=("Arial", 12, "bold"))
lexical_label.pack(anchor="w")

lexical_output = tk.Text(
    right_frame, height=15, width=40, bg="#f5f5f5", fg="black",
    font=("Courier New", 11), wrap="word"
)
lexical_output.pack(fill=tk.BOTH, expand=True)

# === Analyze Button ===
button = ttk.Button(root, text="Analyze", command=on_analyze)
button.pack(pady=5)

root.mainloop()
