import numpy as np

class SpaceCanvasMap():
    def __init__(self, space_left, space_right, space_top, space_bottom, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.space_width = space_right - space_left
        self.space_height = space_bottom - space_top

        self.space_left = space_left
        self.space_right = space_right
        self.space_top = space_top
        self.space_bottom = space_bottom
        self.center = np.array([
            np.mean([space_left, space_right]),
            np.mean([space_top, space_bottom])
        ])

        self.space_translate = np.array([space_left, space_top])
        self.space_scale = np.array([
            self.space_width / self.canvas_width,
            self.space_height / self.canvas_height
        ])

        self.canvas_translate = -self.space_translate
        self.canvas_scale = 1 / self.space_scale

    def space_to_canvas(self, point):
        a = self.canvas_scale * (self.canvas_translate + np.flip(point[1:], axis=0))
        return a

    def canvas_to_space(self, point):
        return np.append(self.space_translate + (self.space_scale * point), [0])
