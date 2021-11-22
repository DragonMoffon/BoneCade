import math
from copy import deepcopy

import arcade
from typing import List

import bone_entity
import skeleton
import animation
from clock import GAME_CLOCK
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
from lin_al import Vec2, Matrix33
import model


# simple 2d bone animation system using python arcade.
# This was inspired by the book "Game Engine Design 2nd Edition" by Jason Gregory.
# It is in no way expected to be usable without modification, but should hopefully give a basic method for others to
# implement.
# Aims:
#   bone/joint tree structure linked to arcade.Sprites
#   global clock animation system (global start times, not integer frame counts, LERP animations) DONE
#   Blending between animations e.g. running to walking to standing.
#   multi-animation blending (shooting while running, using blending to look left, right, up, down)
#   vertex weighted bone/joint system. openGl integration


class Window(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        GAME_CLOCK.begin()

        self.test_prim_model = model.create_primitive_model("models/primitives/basic.json",
                                                            Vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
                                                            0)

        entity_skeleton = skeleton.create_skeleton("skeletons/basic.json", "basic")
        entity_model = model.create_primitive_model("models/primitives/basic.json",
                                                    Vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
                                                    0)
        self.floating_pose = skeleton.get_pose("poses/basic_poses.json", "t_pose", 2)
        self.selected_joint = -1
        self.test_prim_entity = bone_entity.PrimitiveSkinnedEntity(entity_skeleton, entity_model, self.floating_pose)
        animation.generate_clips("poses/animations/basic_motion.json", 'run')

        self.test_prim_entity.animation_set.add_animation('run', 1, GAME_CLOCK.run_time, -1, 1/2)

        self.saved_poses: List[skeleton.SkeletonPose] = []

        self.rect_pos = Vec2(0, SCREEN_HEIGHT/2)
        self.rect_texture = arcade.load_texture("run reference.png")

    def on_update(self, delta_time: float):
        GAME_CLOCK.increment(delta_time)

    def on_draw(self):
        arcade.start_render()
        # self.test_prim_model.draw()

        self.floating_pose.calculate_model_poses()

        arcade.draw_lrwh_rectangle_textured(self.rect_pos.x, self.rect_pos.y, 1600, 90, self.rect_texture)

        i = 0
        for pose in self.saved_poses:
            temp_matrix = Matrix33.all_matrix(Vec2(50 + 50*i, SCREEN_HEIGHT-100), Vec2(30), 0)
            pose.temp_draw(temp_matrix)

            i += 1

        self.test_prim_entity.draw()
        arcade.draw_text(f"time elapsed: {GAME_CLOCK.run_time}s, run speed: {GAME_CLOCK.run_speed}",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200, anchor_x='center')

        if not GAME_CLOCK.is_counting:
            arcade.draw_text(f"PAUSED - time elapsed since last pause: {GAME_CLOCK.concurrent_run_time}s",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, anchor_x='center')

    def save_current_pose(self):
        saved_pose = deepcopy(self.floating_pose)
        self.saved_poses.append(saved_pose)

    def save_current_animation(self):
        target_skeleton = self.saved_poses[0].skeleton.skeleton_id
        animation.convert_clip(self.saved_poses, 'run', True, 1/30)

        animation.save_clips("poses/animations/basic_motion.json", target_skeleton, ['run'])

    # -- BUTTON EVENTS --

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            GAME_CLOCK.toggle()
        elif symbol == arcade.key.EQUAL:
            GAME_CLOCK.run_speed += 0.1
        elif symbol == arcade.key.MINUS:
            GAME_CLOCK.run_speed -= 0.1
        elif symbol == arcade.key.SPACE:
            pass
            # self.save_current_pose()
        elif symbol == arcade.key.ENTER:
            pass
            # self.save_current_animation()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        closest_joint = self.test_prim_entity.last_world_space_joints[0]
        distance = float('inf')
        for joint in self.test_prim_entity.last_world_space_joints:
            dist = Vec2(x - joint.x, y - joint.y).square_length
            if dist < distance:
                closest_joint = joint
                distance = dist

        if distance <= 100:
            self.selected_joint = self.test_prim_entity.last_world_space_joints.index(closest_joint)
        else:
            self.selected_joint = -1

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        self.selected_joint = -1

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        if (dx != 0 or dy != 0) and self.selected_joint >= 0:
            world_translation = Vec2(dx, dy, point=False)
            t_model = self.test_prim_entity.model
            joint_parent_index = self.test_prim_entity.skeleton.joints[self.selected_joint].parent
            if joint_parent_index >= 0:
                world_joint_matrix = (Matrix33.inverse_all_matrix(t_model.pos, t_model.scale, t_model.rotation) *
                                      Matrix33.lazy_inverse(
                                      self.test_prim_entity.current_pose.model_poses[joint_parent_index]))
            else:
                world_joint_matrix = Matrix33.inverse_all_matrix(t_model.pos, t_model.scale, t_model.rotation)

            pose_angle = self.floating_pose.joint_poses[self.selected_joint].translation.theta

            length = self.floating_pose.joint_poses[self.selected_joint].translation.square_length

            self.floating_pose.joint_poses[self.selected_joint].translation += (world_translation *
                                                                                world_joint_matrix)

            if not modifiers & arcade.key.LCTRL:
                self.floating_pose.joint_poses[self.selected_joint].translation.square_length = length

            after_angle = self.floating_pose.joint_poses[self.selected_joint].translation.theta

            if joint_parent_index != -1:
                self.floating_pose.joint_poses[self.selected_joint].angle += after_angle - pose_angle
        else:
            motion = Vec2(dx, 0, point=False)
            self.rect_pos += motion

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y != 0 and self.selected_joint >= 0:
            self.floating_pose.joint_poses[self.selected_joint].angle += scroll_y / 25 * math.pi
        else:
            self.test_prim_entity.model.scale = self.test_prim_entity.model.scale + Vec2(scroll_y)


def main():
    window = Window()
    arcade.run()


if __name__ == '__main__':
    main()
