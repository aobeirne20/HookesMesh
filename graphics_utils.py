from tkinter import *

def setup_graphics(name="Mesh Visual", width=800, height=800):
    gui = Tk()
    gui.geometry("{}x{}".format(width, height))
    gui.resizable(0, 0)
    gui.title(name)
    canvas = Canvas(
        gui,
        width=width,
        height=height,
        bg='#000000',
        highlightthickness=0,
        borderwidth=0
    )
    canvas.pack(fill="both")
    canvas.create_rectangle(0, 0, width, height, fill="#000")

    return gui, canvas
