from manim import Axes

def create_axes():
    return Axes(
        x_range=[-4, 4],
        y_range=[-4, 4],
        tips=False
    )
