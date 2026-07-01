import numpy as np
from manim import *

from templates.base import BaseTemplate, CONTENT_WIDTH


class DerivativeScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "f(x) = x^2")
        judul = p.get("judul", "Turunan Fungsi")
        topic_label = p.get("topic_label", "Kalkulus")

        # ————— Intro —————
        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Visualization: Function + Tangent —————
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            x_length=CONTENT_WIDTH,
            y_length=4.5,
            axis_config={"include_numbers": True, "font_size": 16, "color": "#636E72"},
        )
        axes.center()
        axes.set_y(0.3)

        func_color = self.get_topic_color()

        graph = axes.plot(
            lambda x: x**2,
            x_range=[-2.2, 2.2],
            color=func_color,
            stroke_width=3,
        )

        graph_label = MathTex(rumus, font_size=28, color=func_color)
        graph_label.next_to(axes, UP, buff=0.15)
        graph_label.set_x(0)
        if graph_label.get_center()[1] + graph_label.height / 2 > 3.5:
            graph_label.set_y(3.5 - graph_label.height / 2)

        self.play(Create(axes), run_time=1.2)
        self.play(Write(graph_label), run_time=1.0)
        self.play(Create(graph), run_time=1.5)

        # Tangent line with ValueTracker
        t = ValueTracker(-1.8)

        dot = always_redraw(
            lambda: Dot(
                axes.c2p(t.get_value(), t.get_value() ** 2),
                color="#E17055",
                radius=0.06,
            )
        )
        tangent = always_redraw(
            lambda: self._get_tangent(axes, t.get_value())
        )

        self.play(FadeIn(dot), Create(tangent), run_time=1.0)

        # Slide tangent across the curve
        self.play(t.animate.set_value(1.8), run_time=4.0, rate_func=there_and_back)

        vis_group = VGroup(axes, graph, graph_label, dot, tangent)
        self.fade_out_group(vis_group)

        # ————— Conclusion —————
        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)

    def _get_tangent(self, axes, x):
        if abs(x) < 0.01:
            x = 0.01
        slope = 2 * x
        y = x**2
        dx = 1.0
        line = axes.plot(
            lambda v: slope * (v - x) + y,
            x_range=[x - dx, x + dx],
            color="#E17055",
            stroke_width=2.5,
        )
        return line


class IntegralScene(BaseTemplate):
    def construct(self):
        p = self.params
        rumus = p.get("rumus", "\\int_{0}^{2} x^2 \\, dx")
        judul = p.get("judul", "Integral Tentu")
        topic_label = p.get("topic_label", "Kalkulus")

        # ————— Intro —————
        intro_group = self.intro_phase(judul, topic_label)
        self.fade_out_group(intro_group)

        # ————— Visualization: Riemann rectangles —————
        axes = Axes(
            x_range=[-0.5, 2.5, 0.5],
            y_range=[-0.5, 4.5, 1],
            x_length=CONTENT_WIDTH,
            y_length=4.5,
            axis_config={"include_numbers": True, "font_size": 16, "color": "#636E72"},
        )
        axes.center()
        axes.set_y(0.3)

        color = self.get_topic_color()
        n = ValueTracker(4)

        graph = axes.plot(
            lambda x: x**2,
            x_range=[0, 2],
            color=color,
            stroke_width=3,
        )

        riemann = always_redraw(
            lambda: self._get_rectangles(axes, int(n.get_value()))
        )

        n_label = always_redraw(
            lambda: MathTex(f"n = {int(n.get_value())}", font_size=22, color="#636E72").to_corner(UR, buff=0.3)
        )

        self.play(Create(axes), run_time=1.2)
        self.play(Create(graph), run_time=1.2)
        self.play(FadeIn(riemann), run_time=1.0)
        self.play(Write(n_label), run_time=0.5)

        # Animate increasing rectangle count
        self.play(n.animate.set_value(12), run_time=2.5)
        self.play(n.animate.set_value(24), run_time=2.0)
        self.play(n.animate.set_value(50), run_time=2.0)

        formula = MathTex(rumus, font_size=30, color=color)
        formula.next_to(axes, DOWN, buff=0.3)
        formula.set_x(0)
        self.clamp_to_safe(formula)
        self.play(Write(formula), run_time=1.0)

        vis_group = VGroup(axes, graph, riemann, n_label, formula)
        self.fade_out_group(vis_group)

        # ————— Conclusion —————
        conc_group = self.conclusion_phase(judul, p.get("deskripsi", ""))
        self.wait(1.5)

    def _get_rectangles(self, axes, n):
        if n < 1:
            n = 1
        rects = VGroup()
        dx = 2.0 / n
        for i in range(n):
            x = i * dx
            y = x**2
            rect = Rectangle(
                width=axes.c2p(dx, 0)[0] - axes.c2p(0, 0)[0],
                height=axes.c2p(0, y)[1] - axes.c2p(0, 0)[1],
                color="#4DABF7",
                fill_opacity=0.4,
                stroke_width=0.5,
            )
            rect.move_to(axes.c2p(x + dx / 2, y / 2))
            rects.add(rect)
        return rects
