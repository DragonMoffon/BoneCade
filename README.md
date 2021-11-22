# BoneCade
A 2d implementation of a skeletal animation system for python arcade.

inspired by the book "Game Engine Design 2nd Edition" by Jason Gregory.

# Aims
joint tree structure rendered with arcade primitives\
joint tree structure linked to arcade.Sprites.\/
vertex weighted joint system (openGl integration).\
effective data storage of animation clips which can be read from disk. &#x2713;\
global clock animation system (global start times, non-integer sample rates, LERP animations). &#x2713;\
Blending between animations, e.g., running to walking to standing.\
multi-animation blending (shooting while running, using blending to look left, right, up, down).\
...inverse kinematics?

# Systems to build.
Sprite Model.\
Mesh Model.\
Refactor Entity. Split rendering from rest.\
Refactor Model. Split into model and transform.\
Create different Windows. 
* Sample Scene
* Simple Animator
* Model creator/manipulator

# NOTES
this is experimental. In no way do I expect people to use this by itself.
It is here for my practice, and so people can get an idea of how to do 2d boned animations with arcade.

# Further Reading.
"Game Engine Design 2nd Edition" by Jason Gregory. (particularly chapter 4 and chapter 11).