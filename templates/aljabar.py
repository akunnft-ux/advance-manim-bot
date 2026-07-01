import numpy as np
from manim import *

from templates.base import BaseTemplate, CONTENT_WIDTH


class VectorScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "\\vec{a} + \\vec{b}")
        judul = p.get("judul", "Penjumlahan Vektor")
        topic_label = p.get("topic_label", "Aljabar Linear")

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Plane + Vectors —————
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=CONTENT_WIDTH,
            y_length=CONTENT_WIDTH,
            background_line_style={
                "stroke_color": "#B0B0B0",
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            },
            axis_config={"color": "#636E72", "font_size": 14, "include_numbers": True},
        )
        plane.center()
        plane.set_y(0.5)
        plane.scale(0.9)

        v1_coords = p.get("v1", [2, 1])
        v2_coords = p.get("v2", [1, 2])

        v1_vec = Vector(
            plane.c2p(v1_coords[0], v1_coords[1]),
            color="#4DABF7",
            stroke_width=6,
        )
        v2_vec = Vector(
            plane.c2p(v2_coords[0], v2_coords[1]),
            color="#FF6B9D",
            stroke_width=6,
        )
        v_sum = Vector(
            plane.c2p(v1_coords[0] + v2_coords[0], v1_coords[1] + v2_coords[1]),
            color="#9775FA",
            stroke_width=6,
        )

        v1_label = MathTex(
            "\\vec{a}", font_size=30, color="#4DABF7"
        ).next_to(v1_vec.get_end(), UL, buff=0.1)
        v2_label = MathTex(
            "\\vec{b}", font_size=30, color="#FF6B9D"
        ).next_to(v2_vec.get_end(), UR, buff=0.1)
        sum_label = MathTex(
            "\\vec{a} + \\vec{b}", font_size=28, color="#9775FA"
        ).next_to(v_sum.get_end(), RIGHT, buff=0.1)

        sum_formula = MathTex(rumus, font_size=32, color="#9775FA")
        sum_formula.to_edge(UP, buff=0.8)
        sum_formula.set_x(0)

        self.play(Create(plane), run_time=1.2)
        self.play(Write(sum_formula), run_time=1.0)

        self.play(GrowArrow(v1_vec), Write(v1_label), run_time=1.2)
        self.play(GrowArrow(v2_vec), Write(v2_label), run_time=1.2)

        v2_shift = v2_vec.copy()
        self.play(v2_shift.animate.shift(v1_vec.get_end()), run_time=1.0)

        self.play(GrowArrow(v_sum), Write(sum_label), run_time=1.2)
        self.section_break()

        vis_group = VGroup(plane, v1_vec, v2_vec, v_sum, v1_label, v2_label, sum_label, sum_formula, v2_shift)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)


class TransformScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "\\begin{pmatrix}1 & 2\\\\3 & 1\\end{pmatrix}")
        judul = p.get("judul", "Transformasi Linear")
        topic_label = p.get("topic_label", "Aljabar Linear")

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Grid transformation —————
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=CONTENT_WIDTH,
            y_length=CONTENT_WIDTH,
            background_line_style={
                "stroke_color": "#4DABF7",
                "stroke_width": 1,
                "stroke_opacity": 0.3,
            },
            axis_config={"color": "#636E72", "font_size": 14},
        )
        plane.center()
        plane.set_y(0.5)
        plane.scale(0.9)

        matrix = MathTex(rumus, font_size=32, color=self.get_topic_color())
        matrix.to_edge(UP, buff=0.8)
        matrix.set_x(0)

        self.play(Create(plane), Write(matrix), run_time=1.5)

        transform_matrix = np.array([[1.5, 0.8], [0.5, 1.2]])
        new_plane = plane.copy()
        new_plane.apply_matrix(transform_matrix)
        new_plane.set_color("#E17055")
        new_plane.set_opacity(0.4)

        self.play(
            Transform(plane, new_plane),
            run_time=3.0,
        )

        label = Text("Grid setelah transformasi", font_size=20, color="#E17055")
        label.next_to(plane, DOWN, buff=0.3)
        label.set_x(0)
        self.clamp_to_safe(label)
        self.play(Write(label), run_time=0.8)

        vis_group = VGroup(plane, matrix, label)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)
