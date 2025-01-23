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

def draw_animation(surface, board, anim_progress, dt):
    for i, j in board.get_static_tiles():
        position = (120 + j * 120, 120 + i * 120)
        draw_tile(surface, board.get_tile(i, j), position)

    for animation in board.get_animations():
        if animation[0] == Animations.MoveTile:
            before, after = animation[1]
            t = anim_progress * anim_progress * (3 - 2*anim_progress)
            x = interpolate(before[1], after[1], t)
            y = interpolate(before[0], after[0], t)
            position = (int(120 + x * 120), int(120 + y * 120))
            draw_tile(surface, board.get_tile(before[0], before[1]), position)
        elif animation[0] == Animations.NewTile:
            t = anim_progress * (2 - anim_progress)
            location, number = animation[1]
            position = (120 + location[1] * 120, 120 + location[0] * 120)
            draw_tile(surface, number, position, int(100 * t))
        elif animation[0] == Animations.MergeTile:
            t = 0.5 * (anim_progress + 1) * (2 - anim_progress)
            _, after = animation[1]
            number = board.get_tile(after[0], after[1]) * 2
            position = (120 + after[1] * 120, 120 + after[0] * 120)
            draw_tile(surface, number, position, int(100 * t))

    anim_progress += dt / 0.1
    if anim_progress > 1:
        board.resolve_animations()
        anim_progress = 0
    return anim_progress

def draw_static(surface, board):
    for i in range(4):
        for j in range(4):
            tile = board.get_tile(i, j)
            if tile:
                position = (120 + j * 120, 120 + i * 120)
                draw_tile(surface, tile, position)

def draw_overlay(surface, board, overlay_progress):
    t = overlay_progress * (2 - overlay_progress)
    overlay = pygame.Surface((500, 500))
    overlay.fill((238, 228, 218))
    overlay.set_alpha(171 * t)
    surface.blit(overlay, (50, 50))

    if board.has_2048():
        text1_surface = font_large.render("You Won", True, TEXT_COLORS[2])
    else:
        text1_surface = font_large.render("Game Over", True, TEXT_COLORS[2])
    text1_surface.set_alpha(255 * t)
    text1_rect = text1_surface.get_rect()
    text1_rect.center = (300, 250)
    surface.blit(text1_surface, text1_rect)

    score_text = "Score: " + str(board.get_score())
    text2_surface = font_small.render(score_text, True, TEXT_COLORS[2])
    text2_surface.set_alpha(255 * t)
    text2_rect = text2_surface.get_rect()
    text2_rect.center = (300, 350)
    surface.blit(text2_surface, text2_rect)

def main():
    board = Board()
    board.queue_new_tile()
    board.resolve_animations()
    anim_progress = 0
    overlay_progress = -5

    window = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    while running:
        pygame.display.set_caption("2048 | Score: " + str(board.get_score()))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key in INPUTS:
                    if board.has_game_ended():
                        continue
                    if board.is_animating():
                        board.resolve_animations()
                        board.resolve_animations()
                        anim_progress = 0
                    board.play_move(INPUTS[event.key])

        draw_background(window)
        if board.has_game_ended():
            draw_static(window, board)
            if overlay_progress < 1:
                overlay_progress += dt / 0.2
            else:
                overlay_progress = 1
            if overlay_progress > 0:
                draw_overlay(window, board, overlay_progress)
        else:
            if board.is_animating():
                anim_progress = draw_animation(window, board, anim_progress, dt)
            else:
                draw_static(window, board)

        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()

if __name__ == "__main__":
    main()
