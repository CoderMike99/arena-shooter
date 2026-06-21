import math
import pygame
import random


# Returns direction tuple of right joystick, or left joystick if right is idle
def joystick_direction(joystick):
    left_stick_axis_x = joystick.get_axis(0)
    left_stick_axis_y = joystick.get_axis(1)
    right_stick_axis_x = joystick.get_axis(2)
    right_stick_axis_y = joystick.get_axis(3)
    
    if abs(right_stick_axis_x) > 0.1 or abs(right_stick_axis_y) > 0.1:
        return normalize_vector(apply_deadzone(right_stick_axis_x), apply_deadzone(right_stick_axis_y))
    elif abs(left_stick_axis_x) > 0.1 or abs(left_stick_axis_y) > 0.1:
        return normalize_vector(apply_deadzone(left_stick_axis_x), apply_deadzone(left_stick_axis_y))
    else:
        return None
    

def normalize_vector(vector_x, vector_y):
    length = math.sqrt(vector_x ** 2 + vector_y ** 2)
    return (vector_x / length, vector_y / length) if length != 0 else (0,0)

def random_unit_vector():
    return pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()

def normalize_angle(angle):
    """Normalisiert einen Winkel auf den Bereich [-180, 180]."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def direction_to(from_pos, to_pos) -> pygame.math.Vector2:
    if to_pos != from_pos:
        return (to_pos - from_pos).normalize()
    return pygame.math.Vector2(0, 0)

def apply_deadzone(value, deadzone=0.1):
    if abs(value) < deadzone:
        return 0.0
    sign = 1 if value > 0 else -1
    return sign * (abs(value) - deadzone) / (1.0 - deadzone)

# f(0) = 0, f(duration) = 1
def dash_sigmoid(t, duration):
    x = (t / duration - 0.5) * 10
    return 1 / (1 + math.exp(-x))

def dash_curve(t, duration, steepness=3):
    x = t / duration
    return (1 - math.exp(-steepness * x)) / (1 - math.exp(-steepness))


def dash_rush_from(t, duration):
    x = t / duration  # normalisiert auf [0, 1]
    return 1 - (1 - x) ** 3  # kubisch rush-from

def dash_ease_out_exp(t, duration):
    x = t / duration
    return 1 - math.exp(-5 * x)  # 5 kontrolliert wie schnell es abfällt

def dash_delta(t, duration):
    return dash_curve(t, duration) - dash_curve(t-1, duration)
    #return dash_ease_out_exp(t, duration) - dash_ease_out_exp(t-1, duration)
    #return dash_linear(t, duration) - dash_linear(t-1, duration)
    #return dash_rush_from(t, duration) - dash_rush_from(t-1, duration)