import arcade

from skinned_renderer import create_sample_prim_renderer
from model import create_sprite_model
from clock import GAME_CLOCK
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
from lin_al import Vec2

# simple 2d bone animation system using python arcade.
# This was inspired by the book "Game Engine Design 2nd Edition" by Jason Gregory.
# It is in no way expected to be usable without modification, but should hopefully give a basic method for others to
# implement.


class SampleScene(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        # arcade.set_background_color(arcade.color.WHITE)
        GAME_CLOCK.begin()

        self.selected_joint = -1
        self.test_prim_entity = create_sample_prim_renderer()

        self.test_sprite_model = create_sprite_model("resources/models/sprites/robot.json")

    def on_update(self, delta_time: float):
        GAME_CLOCK.increment(delta_time)

        self.test_sprite_model.on_update()

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text("Prim Renderer", 100, SCREEN_HEIGHT-112, anchor_x='center')
        self.test_prim_entity.draw()

        self.test_sprite_model.draw()

        if not GAME_CLOCK.is_counting:
            arcade.draw_text(f"PAUSED - time elapsed since last pause: {GAME_CLOCK.concurrent_run_time}s",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, anchor_x='center')
        else:
            arcade.draw_text(f"time elapsed: {GAME_CLOCK.run_time}s, run speed: {GAME_CLOCK.run_speed}",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200, anchor_x='center')

    # -- BUTTON EVENTS --

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            GAME_CLOCK.toggle()
        elif symbol == arcade.key.EQUAL:
            GAME_CLOCK.run_speed += 0.1
        elif symbol == arcade.key.MINUS:
            GAME_CLOCK.run_speed -= 0.1

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.test_prim_entity.transform.scale += Vec2(scroll_y)
