import arcade
from typing import List

import lin_al as la
import skeleton
import model
import animation


class PrimitiveSkinnedEntity:
    """
    A skeleton and a primitive model.
    """

    def __init__(self, entity_skeleton, entity_model, entity_pose):
        self.skeleton: skeleton.Skeleton = entity_skeleton
        self.model: model.PrimitiveModel = entity_model
        self.current_pose: skeleton.SkeletonPose = entity_pose
        self.last_world_space_joints = []

    def draw(self):
        index = 0
        world_space_joints = []
        while index < len(self.skeleton.joints):
            skeleton_joint = self.skeleton.joints[index]
            joint_pose = self.current_pose.model_poses[index]
            primitive_segment = self.model.segment_list[index]

            skinning_matrix = skeleton_joint.inv_bind_pose_matrix * joint_pose
            current_point = primitive_segment.model_view_pos * skinning_matrix * self.model.world_matrix

            if primitive_segment.parent_primitive_index != -1:
                parent_point = world_space_joints[primitive_segment.parent_primitive_index]
                arcade.draw_line(current_point.x, current_point.y, parent_point.x, parent_point.y,
                                 primitive_segment.colour, primitive_segment.thickness)

            arcade.draw_point(current_point.x, current_point.y, primitive_segment.colour, primitive_segment.thickness*2)

            world_space_joints.append(current_point)

            index += 1

        self.last_world_space_joints = world_space_joints
