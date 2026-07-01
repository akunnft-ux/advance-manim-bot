import numpy as np
from manim import *

from templates.base import BaseTemplate


class SphereScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "x^2 + y^2 + z^2 = r^2")
        judul = p.get("judul", "Geometri Bola")
        topic_label = p.get("topic_label", "Geometri 3D")

        self.set_camera_orientation(
            phi=70 * DEGREES, theta=-45 * DEGREES, distance=7
        )

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        self.set_camera_orientation(
            phi=70 * DEGREES, theta=-45 * DEGREES, distance=7
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=4, y_length=4, z_length=4,
        )
        axes.set_stroke(opacity=0.4)

        sphere = Sphere(
            radius=1.8,
            resolution=(24, 16),
            checkerboard_colors=["#4DABF7", "#2B7BD4"],
        )

        formula = MathTex(rumus, font_size=30, color="#4DABF7")
        formula.add_fixed_in_frame_mobjects()
        formula.to_corner(UL, buff=0.4)

        self.play(Create(axes), Write(formula), run_time=1.2)
        self.play(Create(sphere), run_time=2.0)

        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()

        vis_group = VGroup(axes, sphere, formula)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)


class CrossSectionScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "z = x^2 + y^2")
        judul = p.get("judul", "Irisan Bidang 3D")
        topic_label = p.get("topic_label", "Geometri 3D")

        self.set_camera_orientation(
            phi=65 * DEGREES, theta=-30 * DEGREES, distance=8
        )

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        self.set_camera_orientation(
            phi=65 * DEGREES, theta=-30 * DEGREES, distance=8
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 4, 1],
            x_length=4, y_length=4, z_length=4,
        )
        axes.set_stroke(opacity=0.4)

        surface = Surface(
            lambda u, v: axes.c2p(u, v, u**2 + v**2),
            u_range=[-1.5, 1.5],
            v_range=[-1.5, 1.5],
            checkerboard_colors=["#FF6B9D", "#E0557A"],
            resolution=(15, 15),
        )

        formula = MathTex(rumus, font_size=30, color="#FF6B9D")
        formula.add_fixed_in_frame_mobjects()
        formula.to_corner(UL, buff=0.4)

        self.play(Create(axes), Write(formula), run_time=1.2)
        self.play(Create(surface), run_time=2.0)

        self.begin_ambient_camera_rotation(rate=0.25)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()

        vis_group = VGroup(axes, surface, formula)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)
