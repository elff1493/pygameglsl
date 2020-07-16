import pygame
import random


# pygame stuff
pygame.init()
window = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("game of life on cpu")

# set random start
for x in range(window.get_width()):
    for y in range(window.get_height()):
        r = random.choice([255, 0])
        window.set_at((x, y), (r, r, r))

# set up varables
around = ((-1, 1), (0, 1), (1, 1),
          (-1, 0),          (1, 0),
          (-1, -1), (0, -1), (1, -1)
          )

running = True
buffer = window.copy()
w, h = window.get_size()
while running:
    t = pygame.time.get_ticks()

    for event in pygame.event.get():  # so we can quit
        if event.type == pygame.QUIT:
            running = False

    for x in range(w):
        for y in range(h):
            n = 0
            c = int(window.get_at((x, y)) == (255, 255, 255))
            for i in around:
                x = (x + i[0] + w) % w
                y = (y + i[1] + h) % h
                n += int(window.get_at((x, y)) == (255, 255, 255))
            if (n == 2 and c == 1) or (n == 3):
                buffer.set_at((x, y), (255, 255, 255))
            else:
                buffer.set_at((x, y), (0, 0, 0))
    window.blit(buffer, (0, 0))
    pygame.display.flip()
    print("time (millisecond): ", pygame.time.get_ticks() - t)

pygame.quit()
