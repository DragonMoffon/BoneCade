# The main skeleton classes. These will start by being rendered as arcade.draw_lines (child to parent)
#   The aims are to get sprites working with the skeleton, and then to generated 2d meshes with joint weights.
#
#   The system I am following has the skeleton and all the other classes as simple data classes. These are then used
#   by the animation system to make a list of model space to world space matrices which are passed each update to the
#   render engine.
#
#   This leaves most of the joint calculations on the CPU. Since there is no proper support for compute shaders within
#   arcade this may be the largest bottleneck. I could send stripped down joint data along to the render engine. This
#   would allow me to construct the final model space to world space matrices in the vertex shader.
#
#   An issue for later, and something that will need to be profiled.

from typing import List

import lin_al as la


class Joint:

    def __init__(self):
        self.inv_bind_pose_matrix: la.Matrix33 = None
        self.joint_name: str = None
        self.parent: int = None


class Skeleton:

    def __init__(self):
        self.joint_count: int = None
        self.joints: List[Joint] = None


class JointPose:

    def __init__(self):
        self.angle: float = None
        self.translation: la.Vec2 = None


class SkeletonPose:

    def __init__(self):
        self.skeleton: Skeleton = None
        self.joint_poses: List[JointPose] = None
        self.global_poses: List[la.Matrix33] = None
