from manim import Dot, Text, VGroup

def create_dot(label=None, position=None):
    dot = Dot()
    if label:
        text = Text(label, font_size=24).next_to(dot, DOWN)
        return VGroup(dot, text)
    return dot
