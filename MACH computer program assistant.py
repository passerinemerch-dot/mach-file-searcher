print("Hello Microsoft.")
import turtle
import math

# Setup
screen = turtle.Screen()
screen.bgcolor("white")
mach = turtle.Turtle()
mach.speed(0)
mach.hideturtle()

# --- Drawing helpers and animated crow character ---------------------------------
def draw_filled_ellipse(t: turtle.Turtle, center: tuple[float, float], width: float, height: float,
                        color: str = "black", steps: int = 80) -> None:
    """Draw a filled ellipse centered at `center` with given `width` and `height`.

    Uses a parametric approximation with `steps` segments.
    """
    cx, cy = center
    points = []
    for i in range(steps + 1):
        theta = 2 * math.pi * i / steps
        x = cx + (width / 2.0) * math.cos(theta)
        y = cy + (height / 2.0) * math.sin(theta)
        points.append((x, y))

    t.penup()
    t.goto(points[0])
    t.pendown()
    t.color(color)
    t.begin_fill()
    for x, y in points[1:]:
        t.goto(x, y)
    t.end_fill()
    t.penup()


def draw_leg_segments(t: turtle.Turtle, hip: tuple[float, float], thigh_angle_deg: float,
                      thigh_len: float, shank_angle_deg: float, shank_len: float,
                      toe_angles: tuple = (-30, 0, 30), toe_length: float = 10) -> None:
    """Draw a two-segment leg (thigh + shank) from hip with toes at the ankle.

    Angles are in degrees where 0 is to the right and 90 is up.
    """
    hx, hy = hip
    ta = math.radians(thigh_angle_deg)
    sa = math.radians(shank_angle_deg)
    knee_x = hx + thigh_len * math.cos(ta)
    knee_y = hy + thigh_len * math.sin(ta)
    ankle_x = knee_x + shank_len * math.cos(sa)
    ankle_y = knee_y + shank_len * math.sin(sa)

    t.penup()
    t.goto(hx, hy)
    t.pendown()
    t.goto(knee_x, knee_y)
    t.goto(ankle_x, ankle_y)

    # toes
    for ang in toe_angles:
        rad = math.radians(ang)
        tx = ankle_x + toe_length * math.cos(rad)
        ty = ankle_y + toe_length * math.sin(rad)
        t.penup()
        t.goto(ankle_x, ankle_y)
        t.pendown()
        t.goto(tx, ty)

    t.penup()


def draw_beak(t: turtle.Turtle, base: tuple[float, float], length: float = 22, color: str = "dimgray"):
    bx, by = base
    t.penup()
    t.goto(bx, by)
    t.setheading(0)
    t.color(color)
    t.begin_fill()
    t.pendown()
    t.forward(length)
    t.left(140)
    t.forward(length * 0.45)
    t.left(100)
    t.forward(length * 0.45)
    t.end_fill()
    t.penup()


def draw_wing(t: turtle.Turtle, center: tuple[float, float], width: float, height: float, tilt: float = -20):
    # simple wing as a rotated ellipse approximation (using polygon)
    cx, cy = center
    points = []
    steps = 24
    for i in range(steps + 1):
        theta = math.pi * i / steps  # half-ellipse
        x = (width / 2.0) * math.cos(theta)
        y = (height / 2.0) * math.sin(theta)
        # rotate by tilt
        r = math.radians(tilt)
        xr = x * math.cos(r) - y * math.sin(r)
        yr = x * math.sin(r) + y * math.cos(r)
        points.append((cx + xr, cy + yr))

    t.penup()
    t.goto(points[0])
    t.pendown()
    t.begin_fill()
    for x, y in points[1:]:
        t.goto(x, y)
    # close back to center
    t.goto(cx, cy)
    t.end_fill()
    t.penup()


def draw_character(t: turtle.Turtle, pos: tuple[float, float], body_w: float, body_h: float,
                   leg_phase: float = 0.0, wing_phase: float = 0.0) -> None:
    """Draw the crow centered at `pos`.

    leg_phase controls the walk pose (radians). wing_phase controls wing tilt.
    """
    cx, cy = pos
    t.clear()
    t.penup()

    # body
    draw_filled_ellipse(t, (cx, cy), body_w, body_h, color="black")

    # small eye (white highlight) and dark pupil
    eye_x = cx + body_w * 0.15
    eye_y = cy + body_h * 0.18
    t.goto(eye_x, eye_y)
    t.dot(8, "white")
    t.goto(eye_x + 2, eye_y + 1)
    t.dot(4, "black")

    # beak (pointed, darker)
    beak_base = (cx + body_w * 0.48, cy + body_h * 0.02)
    draw_beak(t, beak_base, length=26, color="dimgray")

    # wing (one side visible) - tilt varies with wing_phase
    t.color("black")
    wing_tilt = -20 + 10 * math.sin(wing_phase)
    draw_wing(t, (cx + body_w * 0.0, cy + body_h * 0.02), body_w * 0.7, body_h * 0.6, tilt=wing_tilt)

    # tail as a small fan of triangles at the back
    tail_base = (cx - body_w * 0.5, cy - body_h * 0.05)
    t.color("black")
    for i, ang in enumerate((-20, -5, 10)):
        t.penup()
        t.goto(tail_base)
        t.pendown()
        t.setheading(ang - 180)
        t.forward(body_w * 0.18)
        t.backward(body_w * 0.18)
    t.penup()

    # legs: simple kinematics using phase to alternate stepping
    hip_y = cy - body_h / 2.0 + 4
    left_hip = (cx - body_w * 0.18, hip_y)
    right_hip = (cx + body_w * 0.18, hip_y)

    # leg lengths
    thigh = 18
    shank = 26

    # phase offsets: left leads right by pi
    left_phase = leg_phase
    right_phase = leg_phase + math.pi

    # compute angles for thigh and shank (simple oscillation)
    def leg_angles(phase):
        # thigh swings between -110 (back) and -70 (forward)
        thigh_angle = -90 + 20 * math.sin(phase)
        # shank relative more bent when thigh forward
        shank_angle = thigh_angle - 50 - 10 * math.sin(phase)
        return thigh_angle, shank_angle

    t.color("black")
    # left leg
    ta, sa = leg_angles(left_phase)
    draw_leg_segments(t, left_hip, ta, thigh, sa, shank, toe_angles=(-50, 0, 40), toe_length=10)
    # right leg
    ta, sa = leg_angles(right_phase)
    draw_leg_segments(t, right_hip, ta, thigh, sa, shank, toe_angles=(-50, 0, 40), toe_length=10)

    # label
    t.color("black")
    t.goto(cx - 20, cy + body_h * 0.6)
    t.write("Mach", font=("Arial", 18, "italic"))


# Animation: make the crow walk across a short distance
screen.tracer(0)
start_x = 0
start_y = -20
body_w = 120
body_h = 80

frames_per_step = 18
steps = 12
walk_distance = 160
dx_per_step = walk_distance / (steps * frames_per_step)

phase = 0.0
wing_phase = 0.0
mach.hideturtle()
mach.speed(0)
for f in range(steps * frames_per_step):
    # move body forward slowly and bob
    x = start_x + dx_per_step * f
    bob = 3 * math.sin(phase * 2)
    draw_character(mach, (x, start_y + bob), body_w, body_h, leg_phase=phase, wing_phase=wing_phase)
    screen.update()
    phase += (2 * math.pi) / frames_per_step
    wing_phase += 0.5

# leave final pose on screen
screen.tracer(1)
mach.showturtle()
mach.penup()
mach.goto(start_x + walk_distance, start_y + 10)

turtle.done()

print("My name is MACH — welcome to the session.")

print("MACH stands for Machine Assistant: Cognitive Help. I basically search files on this PC.")
print("You can type keywords and I will look for files that match in a chosen domain.")
print("Before we start, I need your name.")
while True:
    name = input("Please enter your name: ").strip()
    # allow spaces and basic punctuation in names but require at least one letter
    if any(ch.isalpha() for ch in name):
        print(f"Hello, {name}! Welcome!")
        break
    else:
        print("Please enter a name containing letters (e.g. 'Alex').")
print(f"So now {name}, we can start. My purpose is to assist you by searching files on this PC.")
import os
import argparse
import sys

def find_files(keyword, search_path, allowed_extensions):
    """Recursively search for files whose filename contains `keyword` (case-insensitive)
    and whose extension is in `allowed_extensions`.
    Returns a list of absolute file paths.
    """
    matches = []
    try:
        for root, dirs, files in os.walk(search_path):
            for file in files:
                try:
                    if keyword.lower() in file.lower():
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            matches.append(os.path.join(root, file))
                except Exception:
                    # skip files with odd names
                    continue
    except Exception as e:
        print(f"Error walking {search_path}: {e}")
    return matches

def summarize_file(file_path, preview_chars=300):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(preview_chars)  # Preview first N characters
            return content.replace('\n', ' ') + "..."
    except Exception:
        return "Preview unavailable (non-text or access denied)."


print(f"{name}, where should I begin the search?")
print("1. Documents\n2. Downloads\n3. Desktop\n4. Entire PC")
choice = input("Choose your domain (1-4): ").strip()

paths = {
    "1": os.path.expanduser("~/Documents"),
    "2": os.path.expanduser("~/Downloads"),
    "3": os.path.expanduser("~/Desktop"),
    "4": os.path.abspath(os.sep)  # typically 'C:\\' on Windows
}
search_directory = paths.get(choice, os.path.expanduser("~"))

if not os.path.exists(search_directory):
    print(f"Selected directory '{search_directory}' does not exist. Falling back to home directory.")
    search_directory = os.path.expanduser("~")


# Keyword input
keyword = input(f"Type a keyword to search for, {name}: ").strip()

#  File type filter
allowed_extensions = ['.txt', '.docx', '.pdf', '.png']

#  Search and summarize
results = find_files(keyword, search_directory, allowed_extensions)

if results:
    print(f"\n{name}, I found {len(results)} files with the keyword '{keyword}'. Showing up to 10 results:\n")
    for i, result in enumerate(results[:10], 1):
        print(f"{i}. {result}")
        if result.lower().endswith('.txt'):
            summary = summarize_file(result)
            print(f"   ↳ Preview: {summary}")
else:
    print(f"\n{name}, I didn't find any files matching '{keyword}' in the chosen domain.")


def interactive_loop(name, search_directory, allowed_extensions):
    while True:
        keyword = input(f"\n{name}, enter another keyword to search or type 'exit' to quit: ").strip()
        if keyword.lower() == 'exit':
            print(f"{name}, session will end. Thanks for using MACH.")
            break

        results = find_files(keyword, search_directory, allowed_extensions)

        if results:
            print(f"\n{name}, I found {len(results)} files with the keyword '{keyword}'. Showing up to 10 results:\n")
            for i, result in enumerate(results[:10], 1):
                print(f"{i}. {result}")
                if result.lower().endswith('.txt'):
                    summary = summarize_file(result)
                    print(f"   ↳ Preview: {summary}")
        else:
            print(f"\n{name}, I didn't find any files matching '{keyword}' in the chosen domain. Type 'exit' to quit or try another keyword.")


if __name__ == '__main__':
    # allow a quick dry-run mode when invoked with --dry-run for testing without walking huge trees
    parser = argparse.ArgumentParser(description='MACH — Machine Assistant: file search helper')
    parser.add_argument('--dry-run', action='store_true', help='Do a quick sample search in the chosen directory')
    args, unknown = parser.parse_known_args()

    if args.dry_run:
        print('Dry run: searching only top-level of the chosen directory for speed...')
        # limit os.walk by breaking after first iteration inside find_files would be ideal, but we'll run a small quick check here
        sample_results = []
        try:
            for entry in os.scandir(search_directory):
                if entry.is_file() and keyword.lower() in entry.name.lower() and any(entry.name.lower().endswith(ext) for ext in allowed_extensions):
                    sample_results.append(entry.path)
        except Exception as e:
            print(f"Dry-run error: {e}")

        print(f"Found {len(sample_results)} sample results (dry-run).")
    # enter interactive loop
    interactive_loop(name, search_directory, allowed_extensions)
