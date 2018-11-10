import pygame
import numpy as np
import math

display = {
    'width': 1024,
    'height': 800,
    'center': np.array([400, 300], dtype='float64'),
    'background': pygame.image.load('./resources/bg.jpg')
}
drone = {
    'width': 100,
    'height': 88,
    'image': pygame.image.load('./resources/drone.png'),
    'pos': np.array([100, 100], dtype='float64'),
    'pos_history': [],
    'memory_len': 1000,
    'force': np.array([1, 1], dtype='float64'),
    'p': 0.0,
    'i': 0.0,
    'd': 0.0,
    'pull_force': 20
}
applied_force = np.array([0, 0])

# pygame stuff
pygame.init()
gameDisplay = pygame.display.set_mode((display['width'], display['height']))
pygame.display.set_caption("PID controller")
clock = pygame.time.Clock()


def on_click(x, y):
    pos = np.array([x, y], dtype='float64')
    force = (pos - drone['pos']) / drone['pos'] * drone['pull_force']
    drone['force'] += force
    print("Applying force => {}, {}  {},{}".format(
        force[0], force[1], drone['force'][0], drone['force'][1]))


def on_right_click(x, y):
    display['center'][0] = x
    display['center'][1] = y

    # Reset the history
    drone['pos_history'] = []


def get_proportional_error(center, position):
    distance_to_center = center - position
    return distance_to_center / np.array([display['width'], display['height']])


def update():

    # (P) Proportional force
    propportional_force = get_proportional_error(
        display['center'], drone['pos'])

    # (I) Integral force
    integral_force = np.array([0, 0], dtype='float64')
    for entry in drone['pos_history']:
        integral_force -= np.array(get_proportional_error(entry,
                                                          display['center']), dtype='float64')

    # (D) Derivative force
    derivative_force = np.array([0, 0])

    if len(drone['pos_history']) > 1:
        prev_error = get_proportional_error(
            drone['pos_history'][-1], display['center'])
        prev_prev_error = get_proportional_error(
            drone['pos_history'][-2], display['center'])
        derivative_force = prev_prev_error - prev_error

    # Apply the forces
    drone['force'] += propportional_force * drone['p'] + \
        integral_force * drone['i'] + derivative_force * drone['d']
    drone['pos'] += drone['force']

    # Add to history and pop if queue is too long
    drone['pos_history'].append(drone['pos'].tolist())
    if(len(drone['pos_history']) > drone['memory_len']):
        drone['pos_history'].pop()


def draw_drone(x, y):
    gameDisplay.blit(
        drone['image'], (x - int(drone['width'] / 2), y - int(drone['height'] / 2)))


def draw():
    # gameDisplay.blit(display['background'], [0, 0])
    draw_drone(drone['pos'][0], drone['pos'][1])
    pygame.draw.line(gameDisplay, (255, 0, 0), (drone['pos'][0], drone[
                     'pos'][1]), (applied_force[0], applied_force[1]))
    pygame.draw.circle(gameDisplay, (0, 0, 0), (int(
        display['center'][0]), int(display['center'][1])), 10, 5)


def set_applied_force(x, y):
    applied_force[0] = x
    applied_force[1] = y

# The game loop
quit = False
while not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True

        # user input
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                on_click(event.pos[0], event.pos[1])
            elif event.button == 3:
                on_right_click(event.pos[0], event.pos[1])

        if event.type == pygame.MOUSEMOTION:
            set_applied_force(event.pos[0], event.pos[1])

    # Clear the screen, update variables and draw the resources
    gameDisplay.fill((255, 255, 255))
    update()
    draw()

    # pygame stuff (like, framerate and such)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
