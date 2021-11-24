import arcade

import lin_al as la
from global_access import SCREEN_WIDTH, SCREEN_HEIGHT
from clock import GAME_CLOCK
import skeleton
import model
import transform
import animation


class PrimitiveSkinnedRenderer:
    """
    A skeleton and a primitive model.
    """

    def __init__(self, entity_skeleton, entity_model, position):
        self.skeleton: skeleton.Skeleton = entity_skeleton
        self.transform: transform.Transform = position
        self.model: model.PrimitiveModel = entity_model
        self.animation_set: animation.AnimationSet = animation.AnimationSet()
        self.last_world_space_joints = []

    def calculate_prim_point(self, index, segment, poses, weights, world_matrix):
        inverse_matrix = self.skeleton.joints[index].inv_bind_pose_matrix

        if not len(poses):
            final_point = segment.model_view_pos * world_matrix
        else:
            final_point = la.Vec2(0)
            for k, pose in enumerate(poses):
                joint_pose = pose[index]
                skinning_matrix = inverse_matrix * joint_pose
                final_point += segment.model_view_pos * skinning_matrix * world_matrix * weights[k]
        return final_point

    def draw(self):
        index = 0
        poses, weights = self.animation_set.get_poses()
        world_matrix = self.transform.to_matrix()

        world_space_joints = []
        while index < len(self.skeleton.joints):
            primitive_segment = self.model.segment_list[index]

            final_point = self.calculate_prim_point(index, primitive_segment, poses, weights, world_matrix)
            if primitive_segment.parent_primitive_index != -1:
                parent_point = world_space_joints[primitive_segment.parent_primitive_index]
                arcade.draw_line(final_point.x, final_point.y, parent_point.x, parent_point.y,
                                 primitive_segment.colour, primitive_segment.thickness)
            arcade.draw_point(final_point.x, final_point.y, primitive_segment.colour, primitive_segment.thickness*2)

            world_space_joints.append(final_point)
            index += 1

        self.last_world_space_joints = world_space_joints


def create_sample_prim_renderer():
    animation.generate_clips("Resources/poses/animations/basic_motion.json", 'run')

    entity_skeleton = skeleton.create_skeleton("Resources/skeletons/basic.json", "basic")
    entity_model = model.create_primitive_model("Resources/models/primitives/basic.json")

    position = transform.Transform(la.Vec2(100, SCREEN_HEIGHT-100), la.Vec2(50), 0)
    sample_prim = PrimitiveSkinnedRenderer(entity_skeleton, entity_model, position)
    sample_prim.animation_set.add_animation('run', 1, GAME_CLOCK.run_time, -1, 1/2)
    return sample_prim
