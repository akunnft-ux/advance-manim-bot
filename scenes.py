import numpy as np
from manim import *

config.frame_height = 8
config.frame_width = 4.5
config.pixel_height = 1920
config.pixel_width = 1080

TOPIC_COLORS = {
    "kalkulus": "#4DABF7",
    "aljabar-linear": "#9775FA",
    "geometri-3d": "#FF6B9D",
    "probstat": "#51CF66",
}

SCENE_COLORS = {
    "intro": {"main": "#2D3436", "accent": "#0984E3", "bg": "#FAFAFA"},
    "visualization": {"main": "#2D3436", "accent": "#E17055", "bg": "#FFFFFF"},
    "conclusion": {"main": "#2D3436", "accent": "#00B894", "bg": "#F8F9FA"},
}


MAX_FRAME_WIDTH = 4.5
CONTENT_WIDTH = 3.9
BOTTOM_LIMIT = -3.0


def wrap_text(text, max_width, font_size, font=""):
    words = text.split()
    if not words:
        return []
    lines = []
    current = [words[0]]
    for word in words[1:]:
        test = Text(" ".join(current + [word]), font_size=font_size, font=font)
        if test.width > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def make_text_block(lines, font_size, color, max_width, **kwargs):
    if not lines:
        return None
    texts = [Text(line, font_size=font_size, color=color, **kwargs) for line in lines]
    block = VGroup(*texts)
    block.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
    return block


def get_topic_color(topic: str) -> str:
    return TOPIC_COLORS.get(topic, "#636E72")


class SimpleCharacter(VGroup):
    def __init__(self, expression="default", **kwargs):
        super().__init__(**kwargs)
        self.expression = expression
        self._build()

    def _build(self):
        body = RoundedRectangle(width=0.8, height=0.9, corner_radius=0.3, color="#2D3436", fill_opacity=0.1)
        head = Circle(radius=0.3, color="#2D3436", fill_opacity=0.1)
        head.shift(UP * 0.65)

        eye_r = 0.05
        left_eye = Circle(radius=eye_r, color="#2D3436", fill_opacity=1)
        right_eye = Circle(radius=eye_r, color="#2D3436", fill_opacity=1)
        left_eye.shift(UP * 0.7 + LEFT * 0.1)
        right_eye.shift(UP * 0.7 + RIGHT * 0.1)

        if self.expression == "explain":
            arm = Line(LEFT * 0.3, LEFT * 0.3 + UP * 0.2, color="#2D3436", stroke_width=3)
            arm.shift(DOWN * 0.1)
            self.add(arm)

        mouth = Arc(angle=0.3, color="#2D3436", stroke_width=2)
        mouth.shift(UP * 0.55)

        self.add(body, head, left_eye, right_eye, mouth)

    def change_expression(self, new_expression):
        new_char = SimpleCharacter(expression=new_expression)
        return Transform(self, new_char)


class IntroScene(Scene):
    def construct(self):
        data = self.data
        judul = data.get("judul", "")
        topic = data.get("topic", "")
        complexity = data.get("complexity", "medium")
        colors = SCENE_COLORS["intro"]
        self.camera.background_color = colors["bg"]

        topic_color = get_topic_color(topic)
        topic_lines = wrap_text(topic.replace("-", " ").title(), CONTENT_WIDTH, 20)
        topic_label = Text(topic_lines[0], font_size=20, color=topic_color)
        topic_bg = RoundedRectangle(
            width=min(topic_label.width + 0.6, CONTENT_WIDTH + 0.4),
            height=topic_label.height + 0.2,
            corner_radius=0.15, color=topic_color, fill_opacity=0.15, stroke_width=1,
        )
        topic_label.move_to(topic_bg.get_center())
        topic_group = VGroup(topic_bg, topic_label)
        topic_group.to_edge(UP, buff=0.5)
        topic_group.set_x(0)

        tier_badge = Text(complexity.upper(), font_size=14, color=colors["accent"], weight=BOLD)
        tier_badge.next_to(topic_group, RIGHT, buff=0.3)

        title_lines = wrap_text(judul, CONTENT_WIDTH, 28)
        title = make_text_block(title_lines, 28, colors["main"], CONTENT_WIDTH, weight=BOLD)
        if title:
            title.next_to(topic_group, DOWN, buff=0.5)
            title.set_x(0)

        divider = Line(LEFT * 1.5, RIGHT * 1.5, color=colors["accent"], stroke_width=2)
        if title:
            divider.next_to(title, DOWN, buff=0.3)
        else:
            divider.next_to(topic_group, DOWN, buff=0.5)
        divider.set_x(0)

        self.play(
            FadeIn(topic_group, scale=0.8),
            Write(tier_badge),
            run_time=0.8,
        )
        if title:
            self.play(Write(title), run_time=1.0)
        self.play(Create(divider), run_time=0.5)

        if data.get("character") and data["character"].get("appear"):
            char = SimpleCharacter(expression=data["character"].get("expression", "default"))
            char.scale(0.6)
            pos = data["character"].get("position", "bottom_right")
            if pos == "bottom_left":
                char.to_corner(DL, buff=0.5)
            else:
                char.to_corner(DR, buff=0.5)
            if char.get_center()[1] < BOTTOM_LIMIT:
                char.set_y(BOTTOM_LIMIT)
            self.play(FadeIn(char, shift=UP * 0.3), run_time=0.5)
            self.add(char)

        self.wait(data.get("duration", 6) - 2.5)


class VizScene(ThreeDScene):
    def construct(self):
        data = self.data
        elements = data.get("elements", ["title"])
        animations = data.get("animations", ["write"])
        camera_spec = data.get("camera", None)
        is_3d = data.get("3d", False)
        duration = data.get("duration", 8)
        colors = SCENE_COLORS["visualization"]
        self.camera.background_color = colors["bg"]

        if is_3d:
            self._build_3d_scene(elements, animations, camera_spec, duration, colors)
        else:
            self._build_2d_scene(elements, animations, duration, colors)

    def _apply_animations(self, mobject, animations):
        for anim_name in animations:
            if anim_name == "write":
                self.play(Write(mobject), run_time=1.5)
            elif anim_name == "fade_in":
                self.play(FadeIn(mobject), run_time=1.5)
            elif anim_name == "create":
                self.play(Create(mobject), run_time=1.5)
            elif anim_name == "grow_from_center":
                self.play(GrowFromCenter(mobject), run_time=1.5)
            elif anim_name == "indicate":
                self.play(Indicate(mobject), run_time=1.0)
            else:
                self.play(Write(mobject), run_time=1.5)

    def _build_2d_scene(self, elements, animations, duration, colors):
        mobjects = []
        for el in elements:
            m = self._create_element_2d(el)
            if m:
                mobjects.append(m)

        if mobjects:
            group = VGroup(*mobjects)
            group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            group.move_to(ORIGIN)

            self._apply_animations(group, animations)
            self.wait(duration - 2)
            self.play(FadeOut(group), run_time=0.5)

    def _build_3d_scene(self, elements, animations, camera_spec, duration, colors):
        self.set_camera_orientation(
            phi=camera_spec.get("phi", 75) * DEGREES if camera_spec else 75 * DEGREES,
            theta=camera_spec.get("theta", -45) * DEGREES if camera_spec else -45 * DEGREES,
            distance=camera_spec.get("distance", 6) if camera_spec else 6,
        )

        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-4, 4, 1],
            x_length=6, y_length=6, z_length=6,
        )
        axes_labels = axes.get_axis_labels()

        mobjects_3d = [axes, axes_labels]
        for el in elements:
            m = self._create_element_3d(el)
            if m:
                mobjects_3d.append(m)

        group = VGroup(*mobjects_3d)

        for anim_name in animations:
            if anim_name == "create":
                self.play(Create(group, run_time=2))
            elif anim_name == "write":
                self.play(Write(group, run_time=2))
            elif anim_name == "lagged_start":
                self.play(LaggedStart(*[Create(m) for m in mobjects_3d], lag_ratio=0.2, run_time=2.5))
            else:
                self.play(Write(group, run_time=2))

        zoom = camera_spec.get("zoom", 1.0) if camera_spec else 1.0
        if zoom != 1.0:
            self.play(self.camera.frame.animate.scale(zoom), run_time=1.5)

        remaining = duration - 3
        if remaining > 2:
            self.begin_ambient_camera_rotation(rate=0.15)
            self.wait(remaining)
            self.stop_ambient_camera_rotation()
        else:
            self.wait(max(remaining, 0.5))

        self.play(FadeOut(group), run_time=0.5)

    def _create_element_2d(self, el_name):
        if el_name == "title":
            return Text("Visualization", font_size=24, color="#2D3436", weight=BOLD)
        elif el_name == "equation":
            return MathTex("f(x) = x^2", font_size=28, color="#2D3436")
        elif el_name == "label":
            return Text("Label", font_size=18, color="#636E72")
        elif el_name == "number_line":
            return NumberLine(x_range=[-3, 3, 1], length=CONTENT_WIDTH, include_numbers=True, font_size=18)
        elif el_name == "grid":
            return NumberPlane(x_range=[-3, 3], y_range=[-5, 5])
        elif el_name == "axes":
            return Axes(x_range=[-2, 2, 1], y_range=[-2, 2, 1], x_length=CONTENT_WIDTH, y_length=3, axis_config={"include_numbers": True, "font_size": 16})
        elif el_name == "vector":
            return Vector(RIGHT * 1.5, color="#E17055")
        else:
            return None

    def _create_element_3d(self, el_name):
        if el_name == "sphere":
            return Sphere(radius=1.5, resolution=(24, 24), checkerboard_colors=[BLUE_D, BLUE_E])
        elif el_name == "torus":
            return Torus(r1=1.5, r2=0.5, resolution=(24, 16), checkerboard_colors=[PURPLE_D, PURPLE_E])
        elif el_name == "surface":
            return Surface(
                lambda u, v: np.array([
                    1.5 * np.cos(u) * np.cos(v),
                    1.5 * np.cos(u) * np.sin(v),
                    1.5 * np.sin(u),
                ]),
                v_range=[0, TAU],
                u_range=[-PI / 2, PI / 2],
                checkerboard_colors=[TEAL_D, TEAL_E],
                resolution=(15, 32),
            )
        elif el_name == "dot_cloud":
            points = np.random.rand(100, 3) * 4 - 2
            return DotCloud(points=points, color=BLUE)
        elif el_name == "axes":
            return ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-3, 3, 1])
        elif el_name == "equation":
            eq = MathTex("f(x, y) = x^2 + y^2", font_size=36, color=WHITE)
            eq.add_fixed_in_frame_mobjects()
            eq.to_corner(UL)
            return eq
        else:
            return None


class VizScene2D(VizScene):
    def construct(self):
        self.data["3d"] = False
        VizScene.construct(self)


class ConclusionScene(Scene):
    def construct(self):
        data = self.data
        colors = SCENE_COLORS["conclusion"]
        self.camera.background_color = colors["bg"]

        judul = data.get("judul", "")
        duration = data.get("duration", 6)

        summary_text = Text("Kesimpulan", font_size=28, color=colors["accent"], weight=BOLD)
        summary_text.to_edge(UP, buff=1.0)
        self.play(Write(summary_text), run_time=0.8)

        desc_lines = wrap_text(judul, CONTENT_WIDTH, 22)
        desc = make_text_block(desc_lines, 22, colors["main"], CONTENT_WIDTH)
        if desc:
            desc.next_to(summary_text, DOWN, buff=0.5)
            desc.set_x(0)
            if desc.get_center()[1] - desc.height / 2 < BOTTOM_LIMIT:
                desc.set_y(BOTTOM_LIMIT + desc.height / 2)
            self.play(FadeIn(desc, shift=UP), run_time=0.8)

        cta = Text("Follow untuk video matematika setiap hari!", font_size=18, color="#636E72")
        cta.next_to(desc if desc else summary_text, DOWN, buff=0.4)
        cta.set_x(0)
        if cta.get_center()[1] - cta.height / 2 < BOTTOM_LIMIT:
            cta.set_y(BOTTOM_LIMIT + cta.height / 2)
        self.play(Write(cta), run_time=0.8)

        remaining = duration - 2.5
        if remaining > 0:
            self.wait(remaining)
