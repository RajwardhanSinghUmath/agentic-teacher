from manim import Surface

def create_surface():
    return Surface(
        lambda u, v: [u, v, 0.3*(u**2 + v**2)],
        u_range=[-3, 3],
        v_range=[-3, 3]
    )
