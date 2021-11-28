#version 330

uniform Projection {
    mat4 matrix;
} proj;

uniform JointMatrix {
    mat4[32] skinned_matrix;
} joints;

uniform mat4 world;

in ivec4 joint_indices;
in vec3 joint_weights;

in vec3 vert_pos;
in vec2 vert_uv;

out vec2 frag_uv;

void main(){
    vec4 pos = vec4(vert_pos.xy, 1.0, 1.0);
    vec2 final_pos = pos.xy; // (joints.skinned_matrix[joint_indices[0]] * pos).xy;
    /*for (int i=0; i < 4; i++)
    {
        float weight = i < 3? joint_weights[i] : 1.0 - joint_weights[1] - joint_weights[2] - joint_weights[2];
        if (weight == 0) break;
        final_pos += (joints.skinned_matrix[joint_indices[i]] * pos).xy * weight;
    }*/
    pos = proj.matrix * world * vec4(final_pos, 1, 1);
    gl_Position = vec4(pos.xy, vert_pos.z, 1.0);
    frag_uv = vert_uv;
}
