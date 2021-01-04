import math

import pygame
import settings


screen_w = settings.SCREEN_DIMENSIONS[0]
screen_h = settings.SCREEN_DIMENSIONS[1]

offset = 15
mini_screen_w = 1 / 4 * screen_w
mini_screen_h = 1 / 5 * screen_h - offset

foreground_alpha = 0
# defined as screen_h-screen_h/10 < hovering_ball_y < 1/5 * screen_h-screen_h/10
hovering_ball_y = 4 / 5 * (screen_h - screen_h / 10) - 1
hovering_ball_t = settings.starting_hovering_ball_t


def render_sprites(display_surf, pole_stack, hovering_ball, target_pole_stack):
    """
    Draws all the balls and their respective animations.
    """
    starting_pos_x = 1/4 * screen_w + (1/256 * screen_w)
    starting_pos_y = screen_h - screen_h / 10

    mini_starting_pos_x = 1/4 * mini_screen_w + (1/256 * mini_screen_w)
    mini_starting_pos_y = mini_screen_h - mini_screen_h / 10

    color_index = {
        1: (255, 0, 0),
        2: (0, 255, 0),
        3: (0, 0, 255)
    }

    for pole in range(len(pole_stack)):
        for ball in range(len(pole_stack[pole])):
            pygame.draw.circle(display_surf, color_index[pole_stack[pole][ball]], ((1 + pole) * starting_pos_x, (4-ball)/5 * starting_pos_y), 50)

    for pole in range(len(target_pole_stack)):
        for ball in range(len(target_pole_stack[pole])):
            pygame.draw.circle(display_surf, color_index[target_pole_stack[pole][ball]], ((1 + pole) * mini_starting_pos_x, (4 - ball) / 5 * mini_starting_pos_y), 8)

    if hovering_ball != -1:
        pygame.draw.circle(display_surf, color_index[hovering_ball], (pygame.mouse.get_pos()[0], hovering_ball_y), 50)

def set_cursor():
    if settings.cursor_type == "normal":
        cursor_text = (
            'X                       ',
            'XX                      ',
            'X.X                     ',
            'X..X                    ',
            'X...X                   ',
            'X....X                  ',
            'X.....X                 ',
            'X......X                ',
            'X.......X               ',
            'X........X              ',
            'X.........X             ',
            'X..........X            ',
            'X......XXXXX            ',
            'X...X..X                ',
            'X..X X..X               ',
            'X.X  X..X               ',
            'XX    X..X              ',
            '      X..X              ',
            '       XX               ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ')
    elif settings.cursor_type == "grab":
        cursor_text = (
            '         XX             ',
            '     XX X..XXX          ',
            '    X..XX..X..X         ',
            '    X..XX..X..XXX       ',
            '     X..X..X..X..X      ',
            '  XX X..X..X..X..X      ',
            ' X..X X.......X..X      ',
            ' X.. XX..........X      ',
            '  X..X..........X       ',
            '   X...........X        ',
            '   X...........X        ',
            '    X.........X         ',
            '     X........X         ',
            '      X......X          ',
            '      X......X          ',
            '      X......X          ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ')
    elif settings.cursor_type == "grabbing":
        cursor_text = (
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '     XXX XX XXXX        ',
            '     X..X..X..X.X       ',
            '    XXX.........X       ',
            '   X..X.........X       ',
            '  X.............X       ',
            '   X...........X        ',
            '   X...........X        ',
            '    X.........X         ',
            '     X........X         ',
            '      X......X          ',
            '      X......X          ',
            '      X......X          ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ',
            '                        ')
    cs, mask = pygame.cursors.compile(cursor_text)
    cursor = ((24, 24), (0, 0), cs, mask)
    pygame.mouse.set_cursor(*cursor)


def render_background(display_surf):
    # change the cursor to whatever it needs to be
    set_cursor()
    # draw game board
    # draw background color
    pygame.draw.rect(display_surf, (230, 230, 230),
                     pygame.Rect((0, 0), (screen_w, screen_h)))
    # draw background marker
    pygame.draw.rect(display_surf, (200, 200, 200), pygame.Rect((1 / 8 * screen_w, 1 / 5 * screen_h), (3 / 4 * screen_w, 3 / 5 * screen_h)))
    # draw background split-lines (vertical)
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((1 / 4 * screen_w, 3 / 5 * screen_h),
                                 (1 / 64 * screen_w, 1 / 5 * screen_h)))
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((2 / 4 * screen_w, 2 / 5 * screen_h),
                                 (1 / 64 * screen_w, 2 / 5 * screen_h)))
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((3 / 4 * screen_w, 1 / 5 * screen_h),
                                 (1 / 64 * screen_w, 3 / 5 * screen_h)))
    # draw background split-line (horizontal)
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((1 / 8 * screen_w, 4 / 5 * screen_h),
                                 (3 / 4 * screen_w, 1 / 15 * screen_h)))
    # draw target board
    pygame.draw.rect(display_surf, (200, 200, 200), pygame.Rect((0, 0), (mini_screen_w, mini_screen_h)))
    # draw background split-line (horizontal)
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((1 / 8 * mini_screen_w, 4 / 5 * mini_screen_h),
                                 (3 / 4 * mini_screen_w, 1 / 15 * mini_screen_h)))
    # draw background split-lines (vertical)
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((1 / 4 * mini_screen_w, 3 / 5 * mini_screen_h),
                                 (1 / 64 * mini_screen_w, 1 / 5 * mini_screen_h)))
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((2 / 4 * mini_screen_w, 2 / 5 * mini_screen_h),
                                 (1 / 64 * mini_screen_w, 2 / 5 * mini_screen_h)))
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((3 / 4 * mini_screen_w, 1 / 5 * mini_screen_h),
                                 (1 / 64 * mini_screen_w, 3 / 5 * mini_screen_h)))
    # draw background split-line (horizontal)
    pygame.draw.rect(display_surf, (176, 130, 48),
                     pygame.Rect((1 / 8 * mini_screen_w, 4 / 5 * mini_screen_h),
                                 (3 / 4 * mini_screen_w, 1 / 15 * mini_screen_h)))


def render_foreground(display_surf):
    # set alpha of fade
    s = pygame.Surface((screen_w, screen_h))
    s.set_alpha(foreground_alpha)
    s.fill((255, 255, 255))

    # draw text on foreground
    font = pygame.font.Font("freesansbold.ttf", 32)
    text_surface = font.render(settings.current_text, False, (0, 0, 0))
    # center text
    text_rect = text_surface.get_rect(center=(screen_w/2, screen_h/2))
    # blit text to alpha of fade
    s.blit(text_surface, text_rect)

    # blit alpha of fade to screen
    display_surf.blit(s, (0, 0))
