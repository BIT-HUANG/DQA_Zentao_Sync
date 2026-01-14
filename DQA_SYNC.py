import sys
import os

if getattr(sys, "frozen", False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, 'libmirror')
    sys.path.append(lib_path)


from ui import Win as MainWin
from control import Controller as MainController


app = MainWin(MainController())

if __name__ == "__main__":
    app.mainloop()