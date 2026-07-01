from manim import *

config.frame_height = 8
config.frame_width = 4.5
config.pixel_height = 1920
config.pixel_width = 1080

TOP_LIMIT = 3.5
BOTTOM_LIMIT = -3.5
CONTENT_WIDTH = 3.9

TOPIC_COLORS = {
    "kalkulus": "#4DABF7",
    "aljabar-linear": "#9775FA",
    "geometri-3d": "#FF6B9D",
    "probstat": "#51CF66",
}


class BaseTemplate(ThreeDScene):
    params = {}
    topic = ""

    def get_topic_color(self):
        return TOPIC_COLORS.get(self.topic, "#0984E3")

    def make_heading(self, text, font_size=32, color="#2D3436"):
        lines = self._wrap(text, CONTENT_WIDTH, font_size)
        texts = [Text(line, font_size=font_size, color=color, weight=BOLD) for line in lines]
        block = VGroup(*texts)
        block.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        return block

    def make_label(self, text, font_size=24, color="#636E72"):
        lines = self._wrap(text, CONTENT_WIDTH, font_size)
        texts = [Text(line, font_size=font_size, color=color) for line in lines]
        block = VGroup(*texts)
        block.arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        return block

    def _wrap(self, text, max_width, font_size):
        words = text.split()
        if not words:
            return []
        lines = []
        current = [words[0]]
        for word in words[1:]:
            test = Text(" ".join(current + [word]), font_size=font_size)
            if test.width > max_width:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return lines if lines else [text]

    def clamp_to_safe(self, mobject, top=TOP_LIMIT, bottom=BOTTOM_LIMIT):
        top_edge = mobject.get_center()[1] + mobject.height / 2
        bottom_edge = mobject.get_center()[1] - mobject.height / 2
        if top_edge > top:
            mobject.set_y(top - mobject.height / 2)
        if bottom_edge < bottom:
            mobject.set_y(bottom + mobject.height / 2)

    def make_topic_badge(self, topic_label, font_size=18):
        color = self.get_topic_color()
        text = Text(topic_label, font_size=font_size, color=color)
        bg = RoundedRectangle(
            width=text.width + 0.5,
            height=text.height + 0.2,
            corner_radius=0.15,
            color=color,
            fill_opacity=0.15,
            stroke_width=1,
        )
        text.move_to(bg.get_center())
        group = VGroup(bg, text)
        group.to_edge(UP, buff=0.4)
        group.set_x(0)
        return group

    def make_divider(self, color=None, width=2.0):
        c = color or self.get_topic_color()
        return Line(LEFT * width / 2, RIGHT * width / 2, color=c, stroke_width=2)

    def fade_in_group(self, group, run_time=1.0):
        self.play(FadeIn(group, scale=0.9), run_time=run_time)

    def fade_out_group(self, group, run_time=0.5):
        self.play(FadeOut(group), run_time=run_time)

    def show_math(self, latex, font_size=36, color="#2D3436"):
        return MathTex(latex, font_size=font_size, color=color)

    def section_break(self, duration=0.5):
        self.wait(duration)

    def intro_phase(self, judul, topic_label, complexity="medium"):
        badge = self.make_topic_badge(topic_label)
        self.play(FadeIn(badge, scale=0.8), run_time=0.6)

        tier = Text(complexity.upper(), font_size=14, color=self.get_topic_color(), weight=BOLD)
        tier.next_to(badge, RIGHT, buff=0.2)
        self.play(Write(tier), run_time=0.3)

        title = self.make_heading(judul, font_size=28, color="#2D3436")
        title.next_to(badge, DOWN, buff=0.4)
        title.set_x(0)
        self.clamp_to_safe(title, top=badge.get_bottom()[1] - 0.2)
        self.play(Write(title), run_time=0.8)

        divider = self.make_divider()
        divider.next_to(title, DOWN, buff=0.3)
        divider.set_x(0)
        self.play(Create(divider), run_time=0.4)

        return VGroup(badge, tier, title, divider)

    def conclusion_phase(self, judul, deskripsi=""):
        heading = Text("Kesimpulan", font_size=28, color=self.get_topic_color(), weight=BOLD)
        heading.to_edge(UP, buff=1.0)
        self.play(Write(heading), run_time=0.6)

        lines = self._wrap(judul, CONTENT_WIDTH, 22)
        texts = [Text(line, font_size=22, color="#2D3436") for line in lines]
        block = VGroup(*texts)
        block.arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        block.next_to(heading, DOWN, buff=0.4)
        block.set_x(0)
        self.clamp_to_safe(block)
        self.play(FadeIn(block, shift=UP * 0.2), run_time=0.6)

        if deskripsi:
            desc_text = self.make_label(deskripsi, font_size=18, color="#636E72")
            desc_text.next_to(block, DOWN, buff=0.3)
            desc_text.set_x(0)
            self.clamp_to_safe(desc_text)
            self.play(Write(desc_text), run_time=0.6)
        else:
            desc_text = None

        cta = Text("Follow untuk video matematika setiap hari!", font_size=16, color="#636E72")
        last = desc_text if desc_text else block
        cta.next_to(last, DOWN, buff=0.3)
        cta.set_x(0)
        self.clamp_to_safe(cta)
        self.play(Write(cta), run_time=0.5)

        return VGroup(heading, block, cta)
