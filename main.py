import tkinter as tk

root = tk.Tk()
root.title("Boo 👻")

label = tk.Label(root, text="👻 Boo is alive!", font=("Segoe UI Emoji", 20))
label.pack(padx=30, pady=30)

root.mainloop()