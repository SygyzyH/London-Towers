import math
from threading import Timer

import renderer
import time

import settings


def oscillation(t, a=.03, tau=100, w=12):
    """
    harmonic oscillation function. phi omitted;
    """
    return a * (math.e ** (tau / t)) * math.cos(w * t)


def handle(animation_queue):
    def append_foreground_fadetext_out():
        animation_queue.append("foreground.fadetext.out")

    if len(animation_queue) == 0:
        return
    animation = animation_queue.pop(0)
    if animation == "foreground.fadetext":
        if renderer.foreground_alpha < 128:
            renderer.foreground_alpha += 1
            animation_queue.append("foreground.fadetext")
        else:
            Timer(1, append_foreground_fadetext_out).start()

    elif animation == "foreground.fadetext.out":
        if renderer.foreground_alpha > 0:
            renderer.foreground_alpha -= 1
            animation_queue.append("foreground.fadetext.out")

    elif animation == "sprite.selected":
        # this animation has been deprecated. too jiggly
        """if renderer.hovering_ball_y > 1/5 * (renderer.screen_h - renderer.screen_h / 10):
            renderer.hovering_ball_y -= 5
            animation_queue.append("sprite.selected")
        else:"""
        renderer.hovering_ball_y = 4 / 5 * (renderer.screen_h - renderer.screen_h / 10) - 1
        settings.bouncing = True
        animation_queue.append("sprite.bounce")

    elif animation == "sprite.bounce":
        hovering_ball_y_definition = renderer.screen_h - renderer.screen_h / 10
        if hovering_ball_y_definition > renderer.hovering_ball_y > 1/5 * hovering_ball_y_definition:
            renderer.hovering_ball_y = oscillation(renderer.hovering_ball_t)/422 * 10 + 1/4 * hovering_ball_y_definition + 1
            renderer.hovering_ball_t += .01
        if settings.bouncing:
            animation_queue.append("sprite.bounce")

    elif animation == "sprite.stopbounce":
        settings.bouncing = False
        animation_queue.append("sprite.stopbounce.cleanup")

    elif animation == "sprite.stopbounce.cleanup":
        renderer.hovering_ball_y = 4 / 5 * (renderer.screen_h - renderer.screen_h / 10) + 1
