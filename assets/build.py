"""Generate the animated SVGs used by the profile README.

Text is converted to outlines (Inter / JetBrains Mono) so the SVGs look the
same everywhere, since GitHub serves README images without web fonts.

    pip install fonttools
    python assets/build.py
"""
import html
import math
import os
import random

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    "black": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "medium": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
    "monob": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf",
}
_cache = {}

# portfolio palette
BLUE, PURPLE, PINK, RED, CYAN = "#4facfe", "#a855f7", "#ff00cc", "#ff4d6d", "#06b6d4"
BG = "#0b0b0f"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def font(name):
    if name not in _cache:
        f = TTFont(FONTS[name])
        _cache[name] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[name]


def glyphs(text, name, size, x=0.0, y=0.0, tracking=0.0):
    """Return [(char, path_d, x_start, advance)] for text laid out from x."""
    f, gs, cmap, upm = font(name)
    s = size / upm
    out = []
    for ch in text:
        gname = cmap.get(ord(ch)) or cmap[ord("?")]
        pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        gs[gname].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        adv = gs[gname].width * s
        out.append((ch, pen.getCommands(), x, adv))
        x += adv + tracking
    return out


def width(text, name, size, tracking=0.0):
    g = glyphs(text, name, size, tracking=tracking)
    return g[-1][2] + g[-1][3] if g else 0


def text_path(text, name, size, x, y, tracking=0.0, anchor="start"):
    if anchor == "middle":
        x -= width(text, name, size, tracking) / 2
    return "".join(d for _, d, _, _ in glyphs(text, name, size, x, y, tracking))


def write(name, svg):
    with open(os.path.join(HERE, name), "w") as fh:
        fh.write(svg)
    print("wrote", name, len(svg) // 1024, "KB")


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 380
    rnd = random.Random(7)

    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" '
        f'r="{rnd.choice([0.8, 1, 1.2, 1.6]):.1f}" class="star" '
        f'style="animation-delay:{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(2.5, 5):.2f}s"/>'
        for _ in range(70)
    )

    # name: every letter flies in from a different side, like the portfolio intro
    name, size = "Sahil Shaikh", 118
    x0 = (W - width(name, "black", size, -2)) / 2
    letters, css = [], []
    i = 0
    for ch, d, x, adv in glyphs(name, "black", size, x0, 205, -2):
        if ch == " ":
            continue
        ang = rnd.uniform(0, 2 * math.pi)
        dx, dy = math.cos(ang) * 520, math.sin(ang) * 260
        rot = rnd.choice([-1, 1]) * rnd.uniform(90, 300)
        css.append(
            f"@keyframes f{i}{{0%{{opacity:0;transform:translate({dx:.0f}px,{dy:.0f}px) rotate({rot:.0f}deg) scale(.3)}}"
            f"70%{{opacity:1}}100%{{opacity:1;transform:none}}}}"
            f".l{i}{{animation:f{i} 1.1s cubic-bezier(.2,.9,.25,1.15) {0.25 + i * 0.09:.2f}s both}}"
        )
        letters.append(f'<path class="l l{i}" d="{d}"/>')
        i += 1

    role = text_path("SOFTWARE ENGINEER", "semi", 26, W / 2, 262, tracking=9, anchor="middle")
    stack = text_path("Java  ·  Spring Boot  ·  React  ·  Full Stack", "medium", 19, W / 2, 302, anchor="middle")
    loc = text_path("Pune, India", "medium", 15, W / 2, 338, tracking=2, anchor="middle")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sahil Shaikh - Software Engineer">
<title>Sahil Shaikh - Software Engineer</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b0b0f"/><stop offset=".55" stop-color="#140a24"/><stop offset="1" stop-color="#0b0b0f"/>
  </linearGradient>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{BLUE}"/><stop offset=".33" stop-color="{PURPLE}"/><stop offset=".66" stop-color="{PINK}"/><stop offset="1" stop-color="{BLUE}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="line" gradientUnits="userSpaceOnUse" x1="{W / 2 - 260}" x2="{W / 2 + 260}" y1="0" y2="0">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{PURPLE}" stroke-opacity=".07"/></pattern>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
  .blob{{animation:drift 14s ease-in-out infinite alternate}}
  .b2{{animation-duration:18s;animation-direction:alternate-reverse}}
  .b3{{animation-duration:11s}}
  @keyframes drift{{0%{{transform:translate(0,0)}}50%{{transform:translate(140px,40px)}}100%{{transform:translate(-120px,-30px)}}}}
  .star{{fill:#fff;animation:tw ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.1}}50%{{opacity:.9}}}}
  .l{{fill:url(#ink);transform-box:fill-box;transform-origin:center}}
  .glow{{fill:url(#ink);opacity:0;animation:fade 1.2s 1.6s both, pulse 3.5s 2.8s ease-in-out infinite}}
  @keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:.8}}}}
  .up{{opacity:0;animation:up .9s cubic-bezier(.2,.8,.2,1) both}}
  @keyframes up{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
  @keyframes fade{{to{{opacity:.5}}}}
  .bar{{stroke-dasharray:520;stroke-dashoffset:520;animation:draw 1.2s 1.9s ease-out forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  .scan{{animation:scan 5s 3s linear infinite;opacity:0}}
  @keyframes scan{{0%{{transform:translateX(-300px);opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateX({W}px);opacity:0}}}}
  {"".join(css)}
  {REDUCED}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <g filter="url(#blur)" opacity=".55">
    <circle class="blob" cx="230" cy="90" r="150" fill="{BLUE}"/>
    <circle class="blob b2" cx="980" cy="300" r="170" fill="{PINK}"/>
    <circle class="blob b3" cx="620" cy="40" r="130" fill="{PURPLE}"/>
  </g>
  {stars}
  <path class="glow" filter="url(#glow)" d="{"".join(p[p.index('d="') + 3:-3] for p in letters)}"/>
  {"".join(letters)}
  <path class="bar" d="M{W / 2 - 260} 228H{W / 2 + 260}" stroke="url(#line)" stroke-width="3" stroke-linecap="round"/>
  <path class="up" style="animation-delay:2.1s" fill="#e5e7eb" d="{role}"/>
  <path class="up" style="animation-delay:2.4s" fill="#9ca3af" d="{stack}"/>
  <g class="up" style="animation-delay:2.7s" fill="{PURPLE}"><path d="{loc}"/></g>
  <rect class="scan" x="0" y="0" width="160" height="{H}" fill="url(#sheen)"/>
  <rect width="{W}" height="{H}" rx="18" fill="none" stroke="{PURPLE}" stroke-opacity=".35"/>
</g>
</svg>'''
    write("header.svg", svg)


# ---------------------------------------------------------------- terminal
def terminal():
    W, LH, size = 900, 34, 17
    cmds = [
        ("whoami", "Sahil Shaikh, Software Engineer from Pune, India"),
        ("cat education.txt", "MCA @ MIT World Peace University  |  BCA (CGPA 8.6)"),
        ("cat stack.txt", "Java  Spring Boot  React  MySQL  Next.js  Docker"),
        ("ls ~/projects --live", "life-os/  aviro/  resume-enhancer/  portfolio/"),
        ("leetcode --stats", "300+ problems solved  |  contest rating 1713"),
        ("echo $STATUS", "Open to Software Engineer roles & internships"),
    ]
    H = 70 + len(cmds) * LH * 2 + 40
    cw = width("M", "mono", size)
    rows, css, t = [], [], 0.6
    y = 82
    for i, (cmd, out) in enumerate(cmds):
        prompt = text_path("sahil@dev", "monob", size, 28, y)
        px = 28 + cw * 9
        sep = text_path(":~$", "monob", size, px, y)
        cx = px + cw * 4
        cmd_d = text_path(cmd, "mono", size, cx, y)
        type_dur = 0.045 * len(cmd)
        cmd_w = cw * len(cmd) + 2
        css.append(
            f".r{i}{{animation:show .01s {t - 0.3:.2f}s forwards}}"
            f".o{i}{{animation:show .35s {t + type_dur + 0.25:.2f}s forwards}}"
        )
        rows.append(
            f'<g class="hid r{i}"><path fill="{CYAN}" d="{prompt}"/><path fill="{PURPLE}" d="{sep}"/>'
            f'<clipPath id="k{i}"><rect x="{cx}" y="{y - 20}" width="0" height="28">'
            f'<animate attributeName="width" begin="{t:.2f}s" dur="{type_dur:.2f}s" calcMode="discrete" fill="freeze" '
            f'values="{";".join(f"{cw * n:.1f}" for n in range(len(cmd) + 1))};{cmd_w:.1f}"/></rect></clipPath>'
            f'<path fill="#f3f4f6" clip-path="url(#k{i})" d="{cmd_d}"/></g>'
        )
        arrow = text_path("›", "monob", size, 28, y + LH)
        out_d = text_path(out, "mono", size, 28 + cw * 2, y + LH)
        color = "#34d399" if i == len(cmds) - 1 else "#c4b5fd"
        rows.append(f'<g class="hid o{i}"><path fill="{PINK}" d="{arrow}"/><path fill="{color}" d="{out_d}"/></g>')
        t += type_dur + 0.9
        y += LH * 2
    # blinking cursor on the final prompt
    final = text_path("sahil@dev", "monob", size, 28, y)
    final_sep = text_path(":~$", "monob", size, 28 + cw * 9, y)
    rows.append(
        f'<g class="hid" style="animation:show .01s {t:.2f}s forwards"><path fill="{CYAN}" d="{final}"/>'
        f'<path fill="{PURPLE}" d="{final_sep}"/>'
        f'<rect class="cur" x="{28 + cw * 13:.1f}" y="{y - 16}" width="{cw:.1f}" height="21" fill="{PINK}"/></g>'
    )
    title = text_path("sahil@dev: ~/about-me", "mono", 13, W / 2, 30, anchor="middle")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="About Sahil Shaikh">
<title>About Sahil Shaikh</title>
<defs>
  <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
</defs>
<style>
  .hid{{opacity:0}}
  @keyframes show{{to{{opacity:1}}}}
  .cur{{animation:blink 1s step-end infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
  {"".join(css)}
  @media (prefers-reduced-motion: reduce){{.hid{{opacity:1}}*{{animation:none!important}}}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="#0d1117" stroke="url(#edge)" stroke-width="2"/>
<path d="M1 46V15a14 14 0 0 1 14-14h{W - 30}a14 14 0 0 1 14 14v31z" fill="#161b22"/>
<circle cx="26" cy="23" r="7" fill="#ff5f56"/><circle cx="50" cy="23" r="7" fill="#ffbd2e"/><circle cx="74" cy="23" r="7" fill="#27c93f"/>
<path fill="#8b949e" d="{title}"/>
{"".join(rows)}
</svg>'''
    write("terminal.svg", svg)


# ---------------------------------------------------------------- section titles
def section(slug, label):
    W, H = 900, 64
    t = text_path(label, "black", 30, 26, 43, tracking=0.5)
    tw = width(label, "black", 30, 0.5)
    alt = html.escape(label)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">
<title>{alt}</title>
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" spreadMethod="reflect">
    <stop offset="0" stop-color="{BLUE}"/><stop offset=".33" stop-color="{PURPLE}"/><stop offset=".66" stop-color="{PINK}"/><stop offset="1" stop-color="{BLUE}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="{tw + 44:.0f}" x2="{W}" y1="0" y2="0"><stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .t{{animation:in .8s cubic-bezier(.2,.8,.2,1) both}}
  @keyframes in{{from{{opacity:0;transform:translateX(-30px)}}to{{opacity:1;transform:none}}}}
  .bar{{transform-box:fill-box;transform-origin:top;animation:grow .6s both}}
  @keyframes grow{{from{{transform:scaleY(0)}}}}
  .ln{{stroke-dasharray:{W};stroke-dashoffset:{W};animation:draw 1.4s .4s ease-out forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  .dot{{animation:run 3.5s 1.6s ease-in-out infinite;opacity:0}}
  @keyframes run{{0%{{transform:translateX(0);opacity:0}}15%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateX({W - tw - 70:.0f}px);opacity:0}}}}
  {REDUCED}
</style>
<rect class="bar" x="4" y="14" width="6" height="36" rx="3" fill="url(#ink)"/>
<path class="t" fill="url(#ink)" d="{t}"/>
<path class="ln" d="M{tw + 44:.0f} 33H{W - 4}" stroke="url(#fade)" stroke-width="2" stroke-linecap="round"/>
<circle class="dot" cx="{tw + 44:.0f}" cy="33" r="4" fill="{PINK}"/>
</svg>'''
    write(f"title-{slug}.svg", svg)


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1200, 170
    quote = text_path("If it's beautiful, I'll build it.  If it's broken, I'll fix it.", "semi", 24, W / 2, 70, anchor="middle")
    sig = text_path("— Sahil Shaikh", "medium", 16, W / 2, 104, tracking=1, anchor="middle")

    def wave(amp, y, phase):
        pts = [f"M0 {H}"] + [
            f"L{x} {y + amp * math.sin((x / W) * 4 * math.pi + phase):.1f}" for x in range(0, W * 2 + 1, 20)
        ] + [f"L{W * 2} {H}Z"]
        return "".join(pts)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="If it's beautiful, I'll build it. If it's broken, I'll fix it.">
<title>If it's beautiful, I'll build it. If it's broken, I'll fix it.</title>
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" spreadMethod="reflect">
    <stop offset="0" stop-color="{BLUE}"/><stop offset=".33" stop-color="{PURPLE}"/><stop offset=".66" stop-color="{PINK}"/><stop offset="1" stop-color="{BLUE}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0" dur="6s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="c"><rect width="{W}" height="{H}"/></clipPath>
</defs>
<style>
  .w{{animation:slide 9s linear infinite}}
  .w2{{animation-duration:13s}}
  @keyframes slide{{to{{transform:translateX(-{W}px)}}}}
  .q{{animation:in 1.2s .2s both}}
  @keyframes in{{from{{opacity:0;transform:translateY(12px)}}}}
  {REDUCED}
</style>
<g clip-path="url(#c)">
  <path class="w w2" d="{wave(10, 138, 1.5)}" fill="{PURPLE}" opacity=".35"/>
  <path class="w" d="{wave(8, 148, 0)}" fill="url(#ink)" opacity=".75"/>
</g>
<path class="q" fill="url(#ink)" d="{quote}"/>
<path class="q" fill="#9ca3af" d="{sig}"/>
</svg>'''
    write("footer.svg", svg)


if __name__ == "__main__":
    header()
    terminal()
    for slug, label in [
        ("about", "About Me"),
        ("stack", "Tech Stack"),
        ("projects", "Featured Projects"),
        ("stats", "GitHub & LeetCode Stats"),
        ("connect", "Let's Connect"),
    ]:
        section(slug, label)
    footer()
