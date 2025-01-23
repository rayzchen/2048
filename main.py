from board import Board, Animations
import pygame
pygame.init()

BACKGROUND_COLOR = (250, 248, 239)
BOARD_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)

TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
}

INPUTS = {
    pygame.K_DOWN: 0,
    pygame.K_UP: 1,
    pygame.K_RIGHT: 2,
    pygame.K_LEFT: 3,
    pygame.K_s: 0,
    pygame.K_w: 1,
    pygame.K_d: 2,
    pygame.K_a: 3,
}

font_large = pygame.font.Font("freesansbold.ttf", 60)
font_medium = pygame.font.Font("freesansbold.ttf", 50)
font_small = pygame.font.Font("freesansbold.ttf", 40)

# measured by digit count
FONTS = {
    1: font_large,
    2: font_large,
    3: font_medium,
    4: font_small,
}

def draw_tile(surface, number, position, size=100):
    tile_rect = (position[0] - size//2, position[1] - size//2, size, size)
    pygame.draw.rect(surface, TILE_COLORS[number], tile_rect, border_radius=3)

    font = FONTS[len(str(number))]
    text_surface = font.render(str(number), True, TEXT_COLORS[number])
    if size != 100:
        text_surface = pygame.transform.smoothscale_by(text_surface, size/100)

    text_rect = text_surface.get_rect()
    text_rect.center = position
    surface.blit(text_surface, text_rect)

def draw_background(surface):
    surface.fill(BACKGROUND_COLOR)
    pygame.draw.rect(surface, BOARD_COLOR, (50, 50, 500, 500), border_radius=5)
    for i in range(4):
        for j in range(4):
            rect = (70 + i*120, 70 + j*120, 100, 100)
            pygame.draw.rect(surface, EMPTY_COLOR, rect, border_radius=3)

def interpolate(a, b, x):
    return a + (b - a) * x

def main():
    board = Board()
    board.queue_new_tile()
    board.resolve_animations()
    anim_progress = 0

    window = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key in INPUTS:
                    if board.is_animating():
                        board.resolve_animations()
                        anim_progress = 0
                    board.play_move(INPUTS[event.key])

        draw_background(window)

        if board.is_animating():
            for i, j in board.get_static_tiles():
                position = (120 + j * 120, 120 + i * 120)
                draw_tile(window, board.get_tile(i, j), position)

            for animation in board.get_animations():
                if animation[0] == Animations.MoveTile:
                    before, after = animation[1]
                    t = anim_progress * anim_progress * (3 - 2*anim_progress)
                    x = interpolate(before[1], after[1], t)
                    y = interpolate(before[0], after[0], t)
                    position = (int(120 + x * 120), int(120 + y * 120))
                    draw_tile(window, board.get_tile(before[0], before[1]), position)
                elif animation[0] == Animations.NewTile:
                    t = anim_progress * (2 - anim_progress)
                    location, number = animation[1]
                    position = (120 + location[1] * 120, 120 + location[0] * 120)
                    draw_tile(window, number, position, int(100 * t))
                elif animation[0] == Animations.MergeTile:
                    t = 0.5 * (anim_progress + 1) * (2 - anim_progress)
                    _, after = animation[1]
                    number = board.get_tile(after[0], after[1]) * 2
                    position = (120 + after[1] * 120, 120 + after[0] * 120)
                    draw_tile(window, number, position, int(100 * t))

            anim_progress += dt / 0.1
            if anim_progress > 1:
                board.resolve_animations()
                anim_progress = 0
        else:
            for i in range(4):
                for j in range(4):
                    tile = board.get_tile(i, j)
                    if tile:
                        position = (120 + j * 120, 120 + i * 120)
                        draw_tile(window, tile, position)

        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()
