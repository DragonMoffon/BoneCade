#version 330

in vec2 frag_uv;

out vec4 frag_Color;

void main() {
    frag_Color = vec4(frag_uv, 0.2, 1.0);
}
