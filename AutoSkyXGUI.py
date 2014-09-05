import Tkinter as tk
import MPCweb

root = tk.Tk()
scrollbar = tk.Scrollbar(root, orient="vertical")
lb = tk.Listbox(root, width=50, height=20, yscrollcommand=scrollbar.set)
scrollbar.config(command=lb.yview)
scrollbar.pack(side="right", fill="y")

lb.pack(side="left",fill="both", expand=True)
x = MPCweb.MPCweb()
neos = x.getneocp()

for item in neos:
    lb.insert("end", str(item.__dict__.values()))
    
root.mainloop()
