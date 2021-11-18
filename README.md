# BoneCade
A 2d implementation of a skeletal animation system for python arcade.

inspired by the book "Game Engine Design 2nd Edition" by Jason Gregory.

# Aims
joint tree structure linked to arcade.Sprites.\
effective data storage of animation clips which can be read from disk.\
global clock animation system (global start times, not integer frame counts, LERP animations).\
Blending between animations, e.g., running to walking to standing.\
multi-animation blending (shooting while running, using blending to look left, right, up, down).\
vertex weighted joint system (openGl integration).\
...inverse kinematics?

# NOTES
this is experimental. In no way do I expect people to actually use this.
It is here for my practice, and so people can get an idea of how to do 2d boned animations with arcade.

# Further Reading.
"Game Engine Design 2nd Edition" by Jason Gregory. (particularly chapter 11).