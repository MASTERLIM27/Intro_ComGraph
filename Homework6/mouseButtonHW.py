"""
Modified on Feb 20 2020
@author: lbg@dongseo.ac.kr
"""

import pygame
from sys import exit
import numpy as np

width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)

background_image_filename = '/Users/andreaslim/Documents/GitHub/Intro_ComGraph/image/curve_pattern.png'

background = pygame.image.load(background_image_filename).convert()
width, height = background.get_size()
screen = pygame.display.set_mode((width, height), 0, 32)
pygame.display.set_caption("ImagePolylineMouseButton")

# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

pts = [] 
count = 0
margin = 6
#screen.blit(background, (0,0))
screen.fill(WHITE)

# https://kite.com/python/docs/pygame.Surface.blit
clock= pygame.time.Clock()


# Drawing helpers
def drawPoint(pt, color=GREEN, thick=3):
    pygame.draw.circle(screen, color, pt, thick)

def drawLine(pt0, pt1, color, thick):
    x0, y0 = pt0
    x1, y1 = pt1

    steps = max(abs(x1 - x0), abs(y1 - y0))
    if steps == 0:
        drawPoint(pt0, color, thick)
        return

    for i in range(steps + 1):
        t = i / steps
        x = int((1 - t) * x0 + t * x1)
        y = int((1 - t) * y0 + t * y1)
        drawPoint((x, y), color, thick)

def drawPolylines(color=GREEN, thick=3):
    if count < 2: return
    for i in range(count - 1):
        pygame.draw.line(screen, color, pts[i], pts[i + 1], thick)

def lagrange_interp(x, points):
    total = 0
    n = len(points)
    for j in range(n):
        xj, yj = points[j]
        Lj = 1
        for m in range(n):
            if m != j:
                xm, _ = points[m]
                if xj == xm:
                    continue
                Lj *= (x - xm) / (xj - xm)
        total += yj * Lj
    return int(total)

def drawLagrangeCurve(points, color, thick, steps_per_segment=100):
    if len(points) < 2:
        return
    
    sorted_pts = sorted(points, key=lambda p: p[0])
    
    if len(sorted_pts) == 2:
        pygame.draw.line(screen, color, sorted_pts[0], sorted_pts[1], thick)
        return
    
    prev_point = None
    
    for i in range(len(sorted_pts) - 1):
        x_start = sorted_pts[i][0]
        x_end = sorted_pts[i+1][0]
        
        start_idx = max(0, i - 1)
        end_idx = min(len(sorted_pts), i + 3)
        interp_points = sorted_pts[start_idx:end_idx]
        
        segment_length = x_end - x_start
        for step in range(steps_per_segment + 1):
            t = step / steps_per_segment
            x = int(x_start + t * segment_length)
            y = lagrange_interp(x, interp_points)
            
            current_point = (x, y)
            if prev_point is not None:
                pygame.draw.line(screen, color, prev_point, current_point, thick)
            prev_point = current_point

def bezier_interp(t, p0, p1, p2, p3):
    x = int((1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0])
    y = int((1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1])
    return (x, y)

def drawCubicBezierSegment(p0, p1, p2, p3, color, thick, steps=100):
    prev = p0
    for i in range(1, steps + 1):
        t = i / steps
        curr = bezier_interp(t, p0, p1, p2, p3)
        pygame.draw.line(screen, color, prev, curr, thick)
        prev = curr

def drawCubicBezierCurve(points, color, thick, steps_per_segment=100):
    if len(points) < 4:
        return
    for i in range(0, len(points) - 3, 3):
        p0, p1, p2, p3 = points[i:i+4]
        drawCubicBezierSegment(p0, p1, p2, p3, color, thick, steps_per_segment)

def hermite_interp(p0, p1, m0, m1, t):
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2

    x = int(h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0])
    y = int(h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1])
    return (x, y)

def compute_tangent(points, i):
    if i == 0:
        dx = (points[1][0] - points[0][0])
        dy = (points[1][1] - points[0][1])
    elif i == len(points) - 1:
        dx = (points[i][0] - points[i - 1][0])
        dy = (points[i][1] - points[i - 1][1])
    else:
        dx = (points[i + 1][0] - points[i - 1][0]) / 2
        dy = (points[i + 1][1] - points[i - 1][1]) / 2
    return (dx, dy)

def drawCubicHermiteCurve(points, color, thick, steps_per_segment=50):
    if len(points) < 2:
        return
    
    tangents = [compute_tangent(points, i) for i in range(len(points))]

    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        m0 = tangents[i]
        m1 = tangents[i + 1]

        prev = p0
        for step in range(1, steps_per_segment + 1):
            t = step / steps_per_segment
            curr = hermite_interp(p0, p1, m0, m1, t)
            pygame.draw.line(screen, color, prev, curr, thick)
            prev = curr

# Main loop
done = False
pressed = 0
old_pressed = 0
old_button1 = 0

while not done:   
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    time_passed = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed = -1
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed = 1
        elif event.type == pygame.QUIT:
            done = True
        else:
            pressed = 0

    button1, button2, button3 = pygame.mouse.get_pressed()
    x, y = pygame.mouse.get_pos()
    pt = [x, y]

    # Clear and redraw background
    screen.blit(background, (0, 0))
    screen.fill(WHITE)

    # Add point on mouse click
    if old_pressed == -1 and pressed == 1 and old_button1 == 1 and button1 == 0:
        if not any(abs(p[0] - pt[0]) < 5 and abs(p[1] - pt[1]) < 5 for p in pts):
            pts.append(pt)
            count += 1
            print(f"Added pt {pt}")
        else:
            print("Point too close to existing point, skipping")

    # Draw all points
    for p in pts:
        pygame.draw.rect(screen, BLUE, (p[0] - margin, p[1] - margin, 2 * margin, 2 * margin), 5)

    # Draw interpolated curve
    if len(pts) >= 4:
        drawPolylines(GREEN, 1)
        drawCubicHermiteCurve(pts, BLUE, 2, 50)

    pygame.display.update()
    old_button1 = button1
    old_pressed = pressed

pygame.quit()
