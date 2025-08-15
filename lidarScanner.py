import math
import pygame
import time
from pyrplidar import PyRPlidar

# Screen setup
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
MIN_DISTANCE = 50     # mm (5 cm)
MAX_DISTANCE = 3000   # mm (300 cm)
SCALE = (WIDTH // 2) / MAX_DISTANCE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

def polar_to_cartesian(angle_deg, distance_mm):
    angle_rad = math.radians(angle_deg)
    r = distance_mm * SCALE
    x = CENTER[0] + int(r * math.cos(angle_rad))
    y = CENTER[1] - int(r * math.sin(angle_rad))
    return x, y

def radar_with_circles_and_colors():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sparklers Lidar Radar System")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 20)
    font_title = pygame.font.SysFont(None, 28, bold=True)

    lidar = PyRPlidar()
    lidar.connect(port="/dev/ttyUSB0", baudrate=460800, timeout=3)
    lidar.set_motor_pwm(500)
    time.sleep(2)
    scan_generator = lidar.force_scan()

    running = True
    try:
        points = []
        prev_angle = None

        for scan in scan_generator():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if MIN_DISTANCE <= scan.distance <= MAX_DISTANCE:
                points.append((scan.angle, scan.distance))

            # Detect sweep completion
            if prev_angle is not None and scan.angle < prev_angle:
                # Clear screen
                screen.fill(BLACK)

                # Draw reference circles + labels
                for r in range(500, MAX_DISTANCE + 1, 500):  # every 50 cm
                    pygame.draw.circle(screen, DARK_GREEN, CENTER, int(r * SCALE), 1)
                    label = font_small.render(f"{r//10} cm", True, WHITE)  # mm → cm
                    screen.blit(label, (CENTER[0] + int(r * SCALE) - 25, CENTER[1]))

                # Draw all points with distance-based colors
                for ang, dist in points:
                    px, py = polar_to_cartesian(ang, dist)
                    if dist <= 1000:       # 0.05–1.0 m
                        color = RED
                    elif dist <= 2000:     # 1.0–2.0 m
                        color = YELLOW
                    else:                  # 2.0–3.0 m
                        color = GREEN
                    pygame.draw.circle(screen, color, (px, py), 2)

                # Draw title text at bottom
                title_surface = font_title.render("Sparklers Lidar Radar System", True, WHITE)
                screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, HEIGHT - 40))

                pygame.display.flip()
                clock.tick(60)
                points.clear()

            prev_angle = scan.angle

            if not running:
                break

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        lidar.stop()
        lidar.set_motor_pwm(0)
        lidar.disconnect()
        pygame.quit()

if __name__ == "__main__":
    radar_with_circles_and_colors()
