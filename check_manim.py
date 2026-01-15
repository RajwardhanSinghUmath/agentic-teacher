
from manim import *
import os

class TestScene(Scene):
    def construct(self):
        sq = Square()
        self.add(sq)
        self.wait(1)

if __name__ == "__main__":
    try:
        scene = TestScene()
        scene.render()
        print("Render Success!")
    except Exception as e:
        print(f"Render Failed: {e}")
