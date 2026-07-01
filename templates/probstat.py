import numpy as np
from manim import *

from templates.base import BaseTemplate, CONTENT_WIDTH


def gaussian(x, mu=0, sigma=1):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


class DistribusiScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}")
        judul = p.get("judul", "Distribusi Normal")
        topic_label = p.get("topic_label", "Probabilitas & Statistika")

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Normal distribution curve —————
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 0.45, 0.1],
            x_length=CONTENT_WIDTH,
            y_length=3.5,
            axis_config={"include_numbers": True, "font_size": 16, "color": "#636E72"},
        )
        axes.center()
        axes.set_y(0.2)

        color = self.get_topic_color()

        graph = axes.plot(
            lambda x: gaussian(x, 0, 1),
            x_range=[-3.8, 3.8],
            color=color,
            stroke_width=3,
        )

        fill = axes.get_area(
            graph,
            x_range=[-1, 1],
            color=color,
            opacity=0.3,
        )

        formula = MathTex(rumus, font_size=24, color=color)
        formula.next_to(axes, UP, buff=0.1)
        formula.set_x(0)
        if formula.get_center()[1] + formula.height / 2 > 3.5:
            formula.set_y(3.5 - formula.height / 2)

        self.play(Create(axes), run_time=1.2)
        self.play(Write(formula), run_time=1.0)
        self.play(Create(graph), run_time=1.5)
        self.play(FadeIn(fill), run_time=1.0)

        label_68 = MathTex("68\\%", font_size=26, color=color)
        label_68.move_to(axes.c2p(0, 0.15))
        self.play(Write(label_68), run_time=0.6)

        # Add second filled area
        fill2 = axes.get_area(
            graph,
            x_range=[-2, 2],
            color=color,
            opacity=0.15,
        )

        self.play(Transform(fill, fill2), run_time=1.2)
        label_95 = MathTex("95\\%", font_size=26, color=color)
        label_95.move_to(axes.c2p(0, 0.1))
        self.play(Transform(label_68, label_95), run_time=0.6)

        vis_group = VGroup(axes, graph, fill, formula, label_68)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)


class BayesScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "P(A|B) = \\frac{P(B|A)P(A)}{P(B)}")
        judul = p.get("judul", "Teorema Bayes")
        topic_label = p.get("topic_label", "Probabilitas & Statistika")

        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Venn-like probability visualization —————
        outer = Circle(radius=2.0, color="#636E72", stroke_width=2, fill_opacity=0.05)
        outer.set_y(0.5)
        outer.set_x(0)

        a_circle = Circle(radius=1.3, color="#4DABF7", fill_opacity=0.2)
        a_circle.shift(LEFT * 0.5)
        a_circle.set_y(0.5)

        b_circle = Circle(radius=1.3, color="#FF6B9D", fill_opacity=0.2)
        b_circle.shift(RIGHT * 0.5)
        b_circle.set_y(0.5)

        a_label = MathTex("P(A)", font_size=30, color="#4DABF7")
        a_label.move_to(a_circle.get_center() + LEFT * 0.6)

        b_label = MathTex("P(B)", font_size=30, color="#FF6B9D")
        b_label.move_to(b_circle.get_center() + RIGHT * 0.6)

        intersection = Intersection(a_circle, b_circle, color="#9775FA", fill_opacity=0.4)
        inter_label = MathTex("P(A \\cap B)", font_size=24, color="#9775FA")
        intersection_center = (a_circle.get_center() + b_circle.get_center()) / 2
        inter_label.move_to(intersection_center)

        formula = MathTex(rumus, font_size=30, color=self.get_topic_color())
        formula.to_edge(UP, buff=0.8)
        formula.set_x(0)

        self.play(Create(outer), run_time=0.6)
        self.play(Create(a_circle), Write(a_label), run_time=1.2)
        self.play(Create(b_circle), Write(b_label), run_time=1.2)
        self.play(FadeIn(intersection), Write(inter_label), run_time=1.0)
        self.play(Write(formula), run_time=1.0)

        vis_group = VGroup(outer, a_circle, b_circle, intersection, a_label, b_label, inter_label, formula)
        self.fade_out_group(vis_group)

        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)
