import threading
import time
from copy import deepcopy

import pygame

import animation_handler
import renderer
import settings
import tracker


def parse_stage_file(stage):
    raw = ""
    with open(settings.stage_name_format.replace('$', str(stage)), 'r') as f:
        raw = f.readlines()
    return eval(raw[0])


class Game:
    def __init__(self):
        """
        Object initialization.
        """

        self._running = True
        self._force_quit = False
        self._display_surf = None
        self.size = self.weight, self.height = settings.SCREEN_DIMENSIONS[0], settings.SCREEN_DIMENSIONS[1]
        self.elapsed_time = 0
        self._initial_pole_stack = [[], [3], [2, 1]]
        self.animation_queue = []
        self.pole_stack = deepcopy(self._initial_pole_stack)
        self.stage = 1
        self.target_pole_stack = parse_stage_file(self.stage)
        self.fail_timer = None
        self.hovering_ball = -1
        # if an illegal move is done, this will say where the ball came from
        self.hovering_ball_origin = -1

    def on_init(self):
        """
        Initialization function for anything that is not object related
        :return: None
        """

        global game_map
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("London Towers")
        renderer.set_cursor()
        pygame.event.set_grab(True)
        tracker.begin()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA)
        self._running = True

    def on_event(self, event):
        # if event is a quit event, start an attempt of stopping main loop
        if event.type == pygame.QUIT:
            self._running = False
            self._force_quit = True

        # if the event is a mouse down, try to figure out what to do
        if event.type == pygame.MOUSEBUTTONDOWN:
            # keep track of mouse state
            settings.cursor_held = True

            # calculate the visual starting and ending points of each pole
            starting_pos = 1/8 * settings.SCREEN_DIMENSIONS[0]
            ending_pos = 3 / 4 * settings.SCREEN_DIMENSIONS[0]

            # move the ball on the selected pole to the hovering state
            try:
                if pygame.mouse.get_pos()[0] in range(int(starting_pos), int(starting_pos + 1/3 * ending_pos)):
                    self.ball_selected(self.pole_stack[0].pop())
                    self.hovering_ball_origin = 0
                elif pygame.mouse.get_pos()[0] in range(int(starting_pos), int(starting_pos + 2/3 * ending_pos)):
                    self.ball_selected(self.pole_stack[1].pop())
                    self.hovering_ball_origin = 1
                elif pygame.mouse.get_pos()[0] in range(int(starting_pos), int(starting_pos + ending_pos)):
                    self.ball_selected(self.pole_stack[2].pop())
                    self.hovering_ball_origin = 2
            except IndexError:
                # if no ball is in the pole stack, don't change anything.
                settings.current_text = "There is no ball in this pole."
                self.animation_queue.append("foreground.fadetext")

        if event.type == pygame.MOUSEBUTTONUP:
            settings.cursor_held = False

            # calculate the visual starting and ending points of each pole
            starting_pos = 1 / 8 * settings.SCREEN_DIMENSIONS[0]
            ending_pos = 3 / 4 * settings.SCREEN_DIMENSIONS[0]

            # move the ball on the selected pole to the hovering state
            if pygame.mouse.get_pos()[0] in range(0, int(starting_pos + 1 / 3 * ending_pos)):
                self.ball_released(0)
            elif pygame.mouse.get_pos()[0] in range(int(starting_pos), int(starting_pos + 2 / 3 * ending_pos)):
                self.ball_released(1)
            else:
                self.ball_released(2)

    def ball_selected(self, ball):
        tracker.first_move()
        tracker.add_move()
        self.hovering_ball = ball
        self.animation_queue.append("sprite.selected")

    def ball_released(self, pole):
        if self.hovering_ball != -1:
            renderer.hovering_ball_y = 4 / 5 * renderer.screen_h - renderer.screen_h / 10
            renderer.hovering_ball_t = settings.starting_hovering_ball_t
            # make sure the move is legal
            if len(self.pole_stack[pole]) < pole + 1:
                self.pole_stack[pole].append(self.hovering_ball)
            else:
                self.pole_stack[self.hovering_ball_origin].append(self.hovering_ball)
                settings.current_text = "There are too many balls in this pole."
                tracker.add_mistake()
                self.animation_queue.append("foreground.fadetext")
            self.animation_queue.append("sprite.stopbounce")
            self.hovering_ball = -1

    def on_loop(self):
        # check if mouse is on top of a tile
        mouse_x, mouse_y = pygame.mouse.get_pos()
        settings.cursor_type = "normal"
        if mouse_x in range(int(1 / 8 * settings.SCREEN_DIMENSIONS[0]),
                            int(1 / 8 * settings.SCREEN_DIMENSIONS[0] + 3 / 4 * settings.SCREEN_DIMENSIONS[0])):
            if mouse_y in range(int(1 / 5 * settings.SCREEN_DIMENSIONS[1]),
                                int(1 / 5 * settings.SCREEN_DIMENSIONS[1] + 3 / 5 * settings.SCREEN_DIMENSIONS[1])):
                if settings.cursor_held:
                    settings.cursor_type = "grabbing"
                else:
                    settings.cursor_type = "grab"

        # handle any animation discrepancies or changes
        animation_handler.handle(self.animation_queue)

        # check if the player won the stage
        if self.pole_stack == self.target_pole_stack:
            self.next_stage()

    def next_stage(self, failed=False):
        if not failed:
            settings.current_text = "Well done!"
        else:
            settings.current_text = "You ran out of time. The next stage has started"
        self.animation_queue.append("foreground.fadetext")
        if self.stage < settings.number_of_stages:
            self.stage += 1
            self.target_pole_stack = parse_stage_file(self.stage)
            self.pole_stack = deepcopy(self._initial_pole_stack)
            self.fail_timer_start()
            tracker.stage_completed()
        else:
            settings.current_text = "Those were all the stages. Great job!"
            self.animation_queue.append("foreground.fadetext")
            self._running = False

    def stage_failed(self, stage):
        tracker.add_move(failed=True)
        self.ball_released(0)
        self.next_stage(failed=True)

    def fail_timer_start(self):
        if self.fail_timer is not None:
            self.fail_timer.cancel()
        self.fail_timer = threading.Timer(120, self.stage_failed, [self.stage])
        self.fail_timer.start()

    def on_render(self):
        """
        Main renderer. draws HUD, vision, and optimizes rendering.
        :return: None
        """

        # render from renderer
        renderer.render_background(self._display_surf)

        # render sprites from renderer
        renderer.render_sprites(self._display_surf, self.pole_stack, self.hovering_ball, self.target_pole_stack)

        # render HUD and such from renderer
        renderer.render_foreground(self._display_surf)

        # update display (I love pygame)
        pygame.display.update()

    def on_cleanup(self):
        self.fail_timer.cancel()
        pygame.quit()

    def on_execute(self):
        """
        Main game loop container.
        :return: None
        """

        if self.on_init() is False:
            self._running = False
        last_time = time.time() - 1
        self.fail_timer_start()
        while self._running:
            current_time = time.time()
            self.elapsed_time = current_time - last_time
            last_time = current_time
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

        # analize the results once the test is over.
        tracker.analysis_start_time = time.time()
        if not self._force_quit:
            self._running = True
            settings.cursor_type = "normal"
            renderer.set_cursor()
            while self._running:
                if renderer.foreground_alpha < 128:
                    renderer.foreground_alpha += 1
                self.on_render()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self._running = False
            tracker.plot_results()
        self.on_cleanup()


if __name__ == "__main__":
    game = Game()
    game.on_execute()
