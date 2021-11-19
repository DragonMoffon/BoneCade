import math

import arcade

from clock import GAME_CLOCK
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
from lin_al import Vec2
import model


# simple 2d bone animation system using python arcade.
# This was inspired by the book "Game Engine Design 2nd Edition" by Jason Gregory.
# It is in no way expected to be usable without modification, but should hopefully give a basic method for others to
# implement.
# Aims:
#   bone/joint tree structure linked to arcade.Sprites
#   global clock animation system (global start times, not integer frame counts, LERP animations)
#   Blending between animations e.g. running to walking to standing.
#   multi-animation blending (shooting while running, using blending to look left, right, up, down)
#   vertex weighted bone/joint system. openGl integration


class Window(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        GAME_CLOCK.begin()

        self.test_prim_model = model.create_primitive_model("models/primitives/basic.json",
                                                            Vec2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2),
                                                            0)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            GAME_CLOCK.toggle()

    def on_update(self, delta_time: float):
        GAME_CLOCK.increment(delta_time)

    def on_draw(self):
        arcade.start_render()
        self.test_prim_model.draw()

        if not GAME_CLOCK.is_counting:
            arcade.draw_text(f"PAUSED - time elapsed since last pause: {GAME_CLOCK.concurrent_run_time}s",
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2, anchor_x='center')


def main():
    window = Window()
    arcade.run()


if __name__ == '__main__':
    main()
