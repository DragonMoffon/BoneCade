import json
import math

import skeleton
from typing import List, Dict

from clock import GAME_CLOCK
from global_access import clamp
from lin_al import Matrix33, Vec2, lerp


class FramePose:
    """
    An individual skeleton pose. This is a "key frame" for an animation which the system interpolates between

    once loaded into memory FramePoses do not change.
    """

    def __init__(self, joint_poses):
        self.joint_poses: List[skeleton.JointPose] = joint_poses
        meta_data = None


class Clip:
    """
    A collection of FramePoses with information on the run speed.

    Once loaded into memory clips do not change.
    """

    def __init__(self, target_skeleton, frames, fps, is_looping):
        self.skeleton: skeleton.Skeleton = target_skeleton
        self.frames: List[FramePose] = frames
        self.frame_count = len(frames)
        self.frames_per_second = fps
        self.duration: float = fps * self.frame_count
        self.is_looping: bool = is_looping


clip_cache: Dict[str, Clip] = {}


def generate_frame(frame_data: List[List[float]]):
    frame_poses = []
    for pose_data in frame_data:
        pose = skeleton.JointPose(*pose_data)
        frame_poses.append(pose)

    return FramePose(frame_poses)


def generate_clip(clip_data: dict, target_skeleton):
    frames = []
    for frame in clip_data['frames']:
        frames.append(generate_frame(frame))

    clip_cache[clip_data['id']] = Clip(target_skeleton, frames, clip_data['fps'], clip_data['loop'])


def generate_clips(file, target):
    json_data = json.load(open(file))
    target_skeleton = skeleton.create_skeleton(f"resources/skeletons/{json_data['target']}.json", json_data['target'])
    for clip in json_data['clips']:
        generate_clip(clip, target_skeleton)

    return clip_cache[target]


def convert_clip(poses: List[skeleton.SkeletonPose], clip_id: str, loop: bool, fps: float):
    target_skeleton = poses[0].skeleton
    frame_poses = []
    for pose in poses:
        frame_pose = FramePose(pose.joint_poses)
        frame_poses.append(frame_pose)

    clip_cache[clip_id] = Clip(target_skeleton, frame_poses, fps, loop)


def save_clips(file: str, target: str, clips: List[str]):
    save_data = {'target': target, 'clips': []}
    for clip_target in clips:
        clip = clip_cache[clip_target]
        clip_data = {'id': clip_target, 'loop': clip.is_looping, 'fps': clip.frames_per_second, 'frames': []}
        for frame in clip.frames:
            frame_data = []
            for joint_pose in frame.joint_poses:
                frame_data.append([joint_pose.angle, joint_pose.translation.x, joint_pose.translation.y])
            clip_data['frames'].append(frame_data)
        save_data['clips'].append(clip_data)
    json.dump(save_data, open(file, 'w'), indent=4)


class Animation:
    """
    A runtime object. It manages everything about itself, and handles meta_data (if implemented)

    loop num is self explanatory, but -1 means loop forever. In this special case an animation will
    not stop until told too with smooth_stop.
    """

    def __init__(self, clip, weight, start_time, loop_num, playback):
        self.clip: Clip = clip
        self.weight: float = weight
        self.start_time: float = start_time
        self.current_time: float = (GAME_CLOCK.run_time - start_time) * playback / clip.duration
        self.loop_num: int = loop_num
        self.playback: float = playback

    def smooth_stop(self):
        self.current_time = (GAME_CLOCK.run_time - self.start_time) * self.playback / self.clip.duration
        self.loop_num = math.floor(self.current_time) + 1

    def frame_t(self):
        self.current_time = (GAME_CLOCK.run_time - self.start_time) * self.playback / self.clip.duration
        if self.loop_num >= 0:
            return clamp(self.current_time, 0, self.loop_num) % 1
        return self.current_time % 1

    def get_pose(self):
        sample = self.frame_t() * self.clip.frame_count
        last_frame = math.floor(sample)
        next_frame = (last_frame + 1) % self.clip.frame_count

        next_weight = sample % 1
        last_weight = 1 - next_weight

        poses = []
        model_poses = []
        for index, last_pose in enumerate(self.clip.frames[last_frame].joint_poses):
            next_pose = self.clip.frames[next_frame].joint_poses[index]

            last_vec, next_vec = Vec2(last_pose.angle, 1, True), Vec2(next_pose.angle, 1, True)

            true_angle = lerp(last_vec, next_vec, next_weight).theta
            true_translation = last_pose.translation * last_weight + next_pose.translation * next_weight

            true_pose = skeleton.JointPose(true_angle, true_translation.x, true_translation.y)
            poses.append(true_pose)

            joint_parent = self.clip.skeleton.joints[index].parent
            if joint_parent != -1:
                last_matrix = model_poses[joint_parent]
            else:
                last_matrix = Matrix33()

            model_poses.append(true_pose.to_matrix() * last_matrix)

        return model_poses

    def is_done(self):
        if self.loop_num != -1 and self.current_time >= self.loop_num:
            return True
        return False


def solve_weights(weights):
    weight_sum = sum(weights)
    return tuple(map(lambda weight: weight/weight_sum, weights))


class AnimationSet:

    def __init__(self):
        self.animations: List[Animation] = []

    def add_animation(self, clip_id, weight, start_time, loop_num, playback):
        clip = clip_cache.get(clip_id, None)
        if clip is None:
            print(f"Clip Id {clip_id} is not cached, make sure the animation you are asking for has been loaded")
        else:
            new_anim = Animation(clip, weight, start_time, loop_num, playback)
            self.animations.append(new_anim)

    def get_poses(self):
        poses, weights = [], []
        protected_copy = tuple(self.animations)
        for anim in protected_copy:
            if anim.is_done():
                self.animations.remove(anim)
                continue

            pose = anim.get_pose()
            poses.append(pose)
            weights.append(anim.weight)

        return poses, solve_weights(weights)
