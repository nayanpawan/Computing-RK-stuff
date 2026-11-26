import tkinter as tk
import random
import numpy as np
from descent import simulate, R, apoapsis_altitude          # CHANGED: use the same R as the physics

W, H = 1600, 1000
cx = W * 0.3
cy = H * 0.2

scale = 460 / 12.2e6     # whole mission
R_px = R * scale         # Titan radius in pixels


def to_pixels(x, y):                     # CHANGED: one place for scale, offset and y-flip
    return cx + x*scale, cy - y*scale


root = tk.Tk()
root.title('Titan Lander')
root.config(bg='black')

canvas = tk.Canvas(root, width=W, height=H, bg='black')
canvas.pack()

# stars
for i in range(200):
    x = random.randint(0, W)
    y = random.randint(0, H)
    size = random.choice([1, 1, 1, 2])      # mostly tiny, a few bigger
    canvas.create_oval(x, y, x+size, y+size, fill='white', outline='')

# Titan
canvas.create_oval(cx - R_px, cy - R_px, cx + R_px, cy + R_px, fill='orange', outline='')

# speed / altitude readout
info = canvas.create_text(20, 20, anchor='nw', fill='white', font=('Consolas', 14), text='')


# satellite
# trapezoid corners relative to the satellite centre
shape = [(-4, -6), (4, -6), (8, 6), (-8, 6)]

def sat_points(px, py):
    pts = []
    for sx, sy in shape:
        pts += [px + sx, py + sy]
    return pts

x_sat, y_sat = to_pixels(12e6, 2e6)      
sat = canvas.create_polygon(sat_points(x_sat, y_sat), fill='white', outline='grey')

# parachute: red canopy + two white strings, hidden until deployed
chute = canvas.create_polygon(0, 0, 0, 0, fill='red', outline='', state='hidden')
string_l = canvas.create_line(0, 0, 0, 0, fill='white', state='hidden')
string_r = canvas.create_line(0, 0, 0, 0, fill='white', state='hidden')

def chute_points(px, py):
    top = py - 30          # canopy top, 30 px above the satellite
    bottom = py - 20       # canopy bottom
    return [px - 10, top,  px + 10, top,  px + 16, bottom,  px - 16, bottom]

target = None      # will hold the surface point once selected
ring = 20

def on_click(event):
    global target

    dx = event.x - cx
    dy = event.y - cy
    dist = np.sqrt(dx**2 + dy**2)
    if abs(dist - R_px) > ring:
        return                   # outside the clickable ring: ignore

    # closest point on Titan's surface (pixels)
    sx = cx + R_px * dx/dist
    sy = cy + R_px * dy/dist

    # same point in metres, physics coordinates
    x = (sx - cx) / scale
    y = -(sy - cy) / scale
    target = (x, y)

    canvas.create_oval(sx-4, sy-4, sx+4, sy+4, fill='red', outline='')
    canvas.unbind('<Button>')       # ignore any further clicks

canvas.bind('<Button>', on_click)


t, z = simulate(np.radians(4.8834),tend=60000)

steps_per_frame = 100      # simulation steps advanced each frame
frame_ms = 10             # delay between frames, ms

apoapsis=apoapsis_altitude(np.radians(4.8834))/1000

def animate(i, prev_px, prev_py):
    i = min(i, len(t) - 1)
    px, py = to_pixels(z[0, i], z[1, i])

    # trail
    canvas.create_line(prev_px, prev_py, px, py, fill='cyan')

    # move satellite
    canvas.coords(sat, *sat_points(px, py))
    canvas.tag_raise(sat)          # keep it drawn above the trail

    # readout
    v = np.sqrt(z[2, i]**2 + z[3, i]**2)
    h = np.sqrt(z[0, i]**2 + z[1, i]**2) - R
    v_impact=0
    if h<=0:
        v_impact=v
        v=0
    canvas.itemconfig(info, text=f't = {t[i]:1.0f} s\nSpeed = {v:1.0f} m/s\nAltitude = {max(h, 0)/1e3:1.0f} km' + (f'\nIMPACT SPEED =  {v_impact:1.0f} m/s')+ (f'\nApoapsis =  {apoapsis:1.0f} Km'))

    if h < 450e3 and v < 400:
        canvas.itemconfig(chute, state='normal')
        canvas.itemconfig(string_l, state='normal')
        canvas.itemconfig(string_r, state='normal')

        canvas.coords(chute, *chute_points(px, py))
        canvas.coords(string_l, px - 16, py - 20, px - 6, py - 6)   # canopy corner to satellite
        canvas.coords(string_r, px + 16, py - 20, px + 6, py - 6)

        canvas.tag_raise(chute)
        canvas.tag_raise(string_l)
        canvas.tag_raise(string_r)


    if i < len(t) - 1:
        root.after(frame_ms, animate, i + steps_per_frame, px, py)


animate(0, x_sat, y_sat)

root.mainloop()