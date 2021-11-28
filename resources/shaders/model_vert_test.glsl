#version 330

uniform Projection {
    mat4 matrix;
} proj;

uniform mat4 world;

in int[4] joint_indices;
in float[3] joint_weights;

in vec3 vert_pos;
in vec2 vert_uv;

out vec2 frag_uv;

void main() {
    frag_uv = vert_uv;
    vec4 pos = proj.matrix * world * vec4(vert_pos.xy, 1, 1);
    gl_Position = vec4(pos.xy, vert_pos.z, 1);
}
