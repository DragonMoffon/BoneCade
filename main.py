import arcade
from clock import GAME_CLOCK
from scenes.sample_animations import SampleScene


def main():
    window = SampleScene()
    GAME_CLOCK.begin()
    arcade.run()


if __name__ == '__main__':
    main()
