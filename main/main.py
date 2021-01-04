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
        # this is used to indicate a force close by the user, such that the window will not open another analysis window.
        self._force_quit = False
        
        # window settings
        self._display_surf = None
        self.size = self.weight, self.height = settings.SCREEN_DIMENSIONS[0], settings.SCREEN_DIMENSIONS[1]
        
        # used to un-tie rendering and FPS.
        self.elapsed_time = 0
        
        # game settings
        self._initial_pole_stack = [[], [3], [2, 1]]
        self.animation_queue = []
        self.pole_stack = deepcopy(self._initial_pole_stack)
        self.stage = 1
        self.target_pole_stack = parse_stage_file(self.stage)
        self.fail_timer = None
        self.hovering_ball = -1
        # in case an illegal move happens, this variable will point back to the origin of the selected ball.
        self.hovering_ball_origin = -1

    def on_init(self):
        """
        Initialization function for anything that is not object related.
        """
        
        # pygame init
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("London Towers")
        pygame.event.set_grab(True)
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA)
        
        # select the normal cursor
        renderer.set_cursor()
        
        # start tracking player actions
        tracker.begin()
       
        self._running = True

    def on_event(self, event):
        """
        Event handler for pygame events.
        """
        
        # if event is a quit event, start an attempt of stopping main loop
        if event.type == pygame.QUIT:
            self._running = False
            self._force_quit = True

        # if the event is a mouse down, try to figure out what action it represents
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
                # if no ball is in the pole stack, don't change anything. notify the user
                settings.current_text = "There is no ball in this pole."
                self.animation_queue.append("foreground.fadetext")
        
        # if the event is a mouse up, try to figure out what should happen to the hovering ball
        if event.type == pygame.MOUSEBUTTONUP:
            # keep track of mouse state
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
        # once a ball has been selected, track the selection and when it happened. check if its the first move as well
        tracker.first_move()
        tracker.add_move()
        
        # apply changes to hovering ball
        self.hovering_ball = ball
        self.animation_queue.append("sprite.selected")

    def ball_released(self, pole):
        if self.hovering_ball != -1:
            # visualy reset the hovering ball's position
            renderer.hovering_ball_y = 4 / 5 * renderer.screen_h - renderer.screen_h / 10
            # t is the time of the oscilation function. used for the visual bounciness
            renderer.hovering_ball_t = settings.starting_hovering_ball_t
            
            # make sure there is enough space in the selected pole to put the ball
            if len(self.pole_stack[pole]) < pole + 1:
                # if so, move it
                self.pole_stack[pole].append(self.hovering_ball)
            else:
                # return ball to its original position
                self.pole_stack[self.hovering_ball_origin].append(self.hovering_ball)
                
                # add mistake to tracker
                tracker.add_mistake()
                
                # notify the user
                settings.current_text = "There are too many balls in this pole."
                self.animation_queue.append("foreground.fadetext")
            
            # interrupt the bounce effect
            self.animation_queue.append("sprite.stopbounce")
            
            # apply change to the ball
            self.hovering_ball = -1

    def on_loop(self):
        """
        Used to take care of frame - to - frame interactions.
        Most changes done in this functions are graphic in nature, but this will also take care of win detection.
        """
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        settings.cursor_type = "normal"
        
        # if the mouse is ontop of a pole
        if mouse_x in range(int(1 / 8 * settings.SCREEN_DIMENSIONS[0]),
                            int(1 / 8 * settings.SCREEN_DIMENSIONS[0] + 3 / 4 * settings.SCREEN_DIMENSIONS[0])):
            if mouse_y in range(int(1 / 5 * settings.SCREEN_DIMENSIONS[1]),
                                int(1 / 5 * settings.SCREEN_DIMENSIONS[1] + 3 / 5 * settings.SCREEN_DIMENSIONS[1])):
                if settings.cursor_held:
                    # and is being held down, change it to "grabbing" mode
                    settings.cursor_type = "grabbing"
                else:
                    # if the mouse is not held down, change it to "grab", to indicate it can be pressed.
                    settings.cursor_type = "grab"

        # handle any animation discrepancies or changes
        animation_handler.handle(self.animation_queue)

        # check if the player finished the stage
        if self.pole_stack == self.target_pole_stack:
            self.next_stage()

    def next_stage(self, failed=False):
        # give the user a notification based on whether or not the passed the stage in the time limit
        if not failed:
            settings.current_text = "Well done!"
        else:
            settings.current_text = "You ran out of time. The next stage has started"
        self.animation_queue.append("foreground.fadetext")
        
        # check if the user has finished all the stages
        if self.stage < settings.number_of_stages:
            # if they didnt, move to the next stage
            self.stage += 1
            self.target_pole_stack = parse_stage_file(self.stage)
            self.pole_stack = deepcopy(self._initial_pole_stack)
            
            # reset time limit
            self.fail_timer_start()
            
            # track the stage complition
            tracker.stage_completed()
        else:
            # if the user finished all the stages, notify them.
            settings.current_text = "Those were all the stages. Great job!"
            self.animation_queue.append("foreground.fadetext")
            
            # end the game
            self._running = False

    def stage_failed(self, stage):
        """
        This function will be called whenever 2 minutes have gone by without interruption from the player finishing a stage.
        If this function is called, the player has failed a level by playing for too long. notify them, track this mishap, and move to the next level.
        """
        
        # track the fail in the time limit
        tracker.add_move(failed=True)
        
        # release the ball (if they had one)
        self.ball_released(self.hovering_ball_origin)
        
        # move to the next stage
        self.next_stage(failed=True)

    def fail_timer_start(self):
        # if there is a currently running timer, interrupt it.
        if self.fail_timer is not None:
            self.fail_timer.cancel()
        
        # start a new timer
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

        # update display 
        pygame.display.update()

    def on_cleanup(self):
        """
        This function will be called when the pygame thread has finished all execution, and the matplotlib analysis is done.
        Its purpose is to make sure the program exists properly.
        """
        
        # clear any existing threads
        self.fail_timer.cancel()
        
        # quit
        pygame.quit()

    def on_execute(self):
        """
        Main game loop container.
        """

        if self.on_init() is False:
            self._running = False
        
        # keep track of the previus frame
        last_time = time.time() - 1
        
        # start fail timer
        self.fail_timer_start()
        while self._running:
            current_time = time.time()
            # get time delta. time dialation fixing is not needed here, since other than threaded events no changes can occur between frames,
            # without user input.
            self.elapsed_time = current_time - last_time
            # update time for next frame
            last_time = current_time
            
            # handle events
            for event in pygame.event.get():
                self.on_event(event)
            
            # allow a frame to be calculated
            self.on_loop()
            
            # render frame
            self.on_render()

        # analize the results once the test is over.
        tracker.analysis_start_time = time.time()
        if not self._force_quit:
            # return the window to regular settings
            self._running = True
            settings.cursor_type = "normal"
            renderer.set_cursor()
            
            # another run loop, just to render the final graphic
            while self._running:
                if renderer.foreground_alpha < 128:
                    renderer.foreground_alpha += 1
                self.on_render()
                
                # await input from tester to start analysis
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self._running = False
            
            # start analysis and draw
            tracker.plot_results()
            
        # quit 
        self.on_cleanup()


if __name__ == "__main__":
    game = Game()
    game.on_execute()
