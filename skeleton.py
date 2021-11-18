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