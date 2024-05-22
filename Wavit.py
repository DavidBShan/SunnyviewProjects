import cv2
import mediapipe as mp
import pyautogui
import pygame
import pygame.gfxdraw  # Import gfxdraw for anti-aliased circles
import random
import numpy as np
import time
from PIL import Image

# Constants
max_line_width = 30  # Adjust this as needed
max_splat_radius = 80
splat_frequency = 3
drawings = []
current_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def calculate_distance(landmark1, landmark2):
    return ((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2) ** 0.5

def change_color_if_pinching(landmarks, frame_width, frame_height):
    global current_color
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    distance = calculate_distance(thumb_tip, index_tip)

    # Threshold to consider if the fingers are pinching
    pinch_threshold = 0.02  # Adjust this threshold based on testing

    if distance < pinch_threshold:
        current_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def draw_line_with_splats(x1, y1, x2, y2, color):
    global drawings
    width = random.randint(1, max_line_width)
    drawings.append(('line', x1, y1, x2, y2, width, color))

    if random.randint(0, splat_frequency) == 0:
        for _ in range(random.randint(1, 5)):
            splat_x = random.randint(-max_splat_radius, max_splat_radius) + x2
            splat_y = random.randint(-max_splat_radius, max_splat_radius) + y2
            radius = random.randint(1, max_splat_radius)
            drawings.append(('circle', splat_x, splat_y, radius, color))


def process_frame_for_gesture():
    global frame_counter, last_x, last_y
    frame_counter += 1
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (800, 600))
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hands = None
    if frame_counter % skip_frames == 0:
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            landmarks = hand.landmark
            change_color_if_pinching(landmarks, frame_width, frame_height)
            index_tip = landmarks[8]
            index_x, index_y = int(index_tip.x * frame_width), int(index_tip.y * frame_height)
            new_x, new_y = int(np.interp(index_x, [0, frame_width], [0, screen_width])), int(np.interp(index_y, [0, frame_height], [0, screen_height]))

            if last_x is not None and last_y is not None:
                draw_line_with_splats(last_x, last_y, new_x, new_y, current_color)

            last_x, last_y = new_x, new_y
            return True
    return False


# Initialize Pygame
pygame.init()
resolution = (3840, 2160)  # Example of a higher resolution
screen = pygame.display.set_mode(resolution)
last_x, last_y = None, None

# Initialize variables for hand tracking
cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands(max_num_hands=1)
screen_width, screen_height = pyautogui.size()
frame_reduction = 0.3 # Reduce the frame size by this factor
skip_frames = 1 # Process every nth frame
frame_counter = 0

last_color_change_time = time.time()

running = True
while running:
    screen.fill((255, 255, 255))

    current_time = time.time()
    if current_time - last_color_change_time > 7:
        current_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        last_color_change_time = current_time

    is_drawing = process_frame_for_gesture()

    for command in drawings:
        if command[0] == 'line':
            pygame.draw.line(screen, command[6], (command[1], command[2]), (command[3], command[4]), 8)
        elif command[0] == 'circle':
            pygame.gfxdraw.filled_circle(screen, command[1], command[2], command[3], command[4])
            pygame.gfxdraw.aacircle(screen, command[1], command[2], command[3], command[4])

    # Draw square cursor at the hand location
    if last_x is not None and last_y is not None:
        cursor_size = 40  # Adjust the size of the square cursor as needed
        pygame.draw.rect(screen, (0, 0, 255), (last_x - cursor_size // 2, last_y - cursor_size // 2, cursor_size, cursor_size))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                screen.fill((255, 255, 255))
                drawings.clear()

    pygame.display.flip()

cap.release()
pygame.quit()