import arcade

from skinned_renderer import create_sample_prim_renderer, create_sample_sprite_renderer, create_sample_mesh_renderer
from model import load_mesh_model
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
        arcade.set_background_color(arcade.color.WHITE)
        GAME_CLOCK.begin()

        self.selected_joint = -1
        self.test_prim_entity = create_sample_prim_renderer()

        self.test_sprite_renderer = create_sample_sprite_renderer()

        self.test_mesh_renderer = create_sample_mesh_renderer(self.ctx)

        load_mesh_model("robot")

    def on_update(self, delta_time: float):
        GAME_CLOCK.increment(delta_time)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text("Prim Renderer", SCREEN_WIDTH/6, SCREEN_HEIGHT/2,
                         anchor_x='center', anchor_y='top', color=arcade.color.BLACK)
        self.test_prim_entity.draw()

        arcade.draw_text("Sprite Renderer", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         anchor_x='center', anchor_y='top', color=arcade.color.BLACK)
        self.test_sprite_renderer.find_render_data()
        self.test_sprite_renderer.draw()

        arcade.draw_text("Mesh Renderer", 5*SCREEN_WIDTH / 6, SCREEN_HEIGHT / 2,
                         anchor_x='center', anchor_y='top', color=arcade.color.BLACK)
        self.test_mesh_renderer.draw()

        if not GAME_CLOCK.is_counting:
            arcade.draw_text(f"PAUSED - time elapsed since last pause: {GAME_CLOCK.concurrent_run_time}s",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, anchor_x='center', color=arcade.color.BLACK)
        else:
            arcade.draw_text(f"time elapsed: {GAME_CLOCK.run_time}s, run speed: {GAME_CLOCK.run_speed}",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200, anchor_x='center', color=arcade.color.BLACK)

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
        self.test_mesh_renderer.transform.scale += Vec2(scroll_y)
        self.test_mesh_renderer.update_world_matrix()
