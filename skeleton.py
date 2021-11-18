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


import lin_al as la
from dataclasses import dataclass
from typing import List


class Joint:

    def __init__(self):
        self.inv_bind_pose_matrix: la.Matrix23
        self.joint_name: str
        self.parent: int


class Skeleton:

    def __init__(self):
        self.joint_count: int
        self.joints: List[Joint]


@dataclass()
class JointPose:
    angles: float
    translation: la.Vec2


@dataclass()
class SkeletonPose:
    skeleton: Skeleton
    joint_poses: List[JointPose]
    global_poses: List[la.Matrix23]