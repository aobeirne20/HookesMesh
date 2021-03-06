import numpy as np
import tkinter as tk

def setup_graphics(width, height, name="Mesh Visual"):
    gui = tk.Tk()
    gui.geometry("{}x{}".format(width, height))
    gui.resizable(0, 0)
    gui.title(name)
    canvas = tk.Canvas(gui, width=width, height=height, bg='#000000', highlightthickness=0, borderwidth=0)
    canvas.pack(fill="both")
    canvas.create_rectangle(0, 0, width, height, fill="#000")
    canvas.configure(scrollregion=canvas.bbox("ALL"))
    return gui, canvas


class SpaceCanvasMap:
    def __init__(self, space_left, space_right, space_top, space_bottom, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.space_width = space_right - space_left
        self.space_height = space_bottom - space_top
        self.space_left = space_left
        self.space_right = space_right
        self.space_top = space_top
        self.space_bottom = space_bottom

        self.center = np.array([np.mean([space_left, space_right]), np.mean([space_top, space_bottom])])
        self.space_translate = np.array([space_left, space_top])
        self.space_scale = np.array([self.space_width / self.canvas_width, self.space_height / self.canvas_height])

        self.canvas_translate = -self.space_translate
        self.canvas_scale = 1 / self.space_scale

    def space_to_canvas(self, point):
        a = self.canvas_scale * (self.canvas_translate + np.flip(point[1:], axis=0))
        return a

    def canvas_to_space(self, point):
        return np.append(self.space_translate + (self.space_scale * point), [0])


class MeshVisual:
    def __init__(self, mesh, space_left=-4, space_right=4, space_top=4, space_bottom=-4, visual_width=800,
                 visual_height=800, point_radius=4, fill="#FFF"):

        self.mesh = mesh
        space_height, space_depth =  self.mesh.m[0, :, :].shape
        space_height
        print(space_height, space_depth)


        self.space_canvas_map = SpaceCanvasMap(space_left, space_right, space_top, space_bottom, visual_width, visual_height)
        self.gui, self.canvas = setup_graphics(visual_width, visual_height)
        self.point_radius = point_radius
        self.fill = fill
        self.handles = []

        for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
            rigid = rigid.item()
            canvas_x, canvas_y = self.space_canvas_map.space_to_canvas(rigid.pos)
            print(canvas_x)
            print(canvas_y)
            print("-----------------------")

            if hasattr(rigid, "vel") == 1:

                handle = self.canvas.create_oval(
                    canvas_x - self.point_radius,
                    canvas_y - self.point_radius,
                    canvas_x + self.point_radius,
                    canvas_y + self.point_radius,
                    fill=self.fill)

            else:

                handle = self.canvas.create_rectangle(
                    canvas_x - self.point_radius,
                    canvas_y - self.point_radius,
                    canvas_x + self.point_radius,
                    canvas_y + self.point_radius,
                    fill=self.fill)

            self.handles.append(handle)

    def update(self):
        for rigid, handle in zip(np.nditer(self.mesh.m, flags=["refs_ok"]), self.handles):
            rigid = rigid.item()
            canvas_x, canvas_y = self.space_canvas_map.space_to_canvas(rigid.pos)
            self.canvas.coords(
                handle,
                canvas_x - self.point_radius,
                canvas_y - self.point_radius,
                canvas_x + self.point_radius,
                canvas_y + self.point_radius
            )
            self.canvas.itemconfig(handle, fill=self.fill)

        self.gui.update()
