import numpy as np

from graphics_utils import *
from SpaceCanvasMap import SpaceCanvasMap

class MeshVisual:
    def __init__(   self,
                    mesh,
                    space_left=-1.5,
                    space_right=4.5,
                    space_top=-4,
                    space_bottom=4,
                    visual_width=400,
                    visual_height=400,
                    point_radius=4,
                    fill="#FFF"):

        self.mesh = mesh
        self.space_canvas_map = SpaceCanvasMap(
            space_left,
            space_right,
            space_top,
            space_bottom,
            visual_width,
            visual_height
        )
        self.gui, self.canvas = setup_graphics(width=visual_width, height=visual_height)
        self.point_radius = point_radius
        self.fill = fill

        self.handles = []
        for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
            rigid = rigid.item()
            canvas_x, canvas_y = self.space_canvas_map.space_to_canvas(rigid.pos)

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
