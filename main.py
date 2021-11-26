import arcade
from clock import GAME_CLOCK
from scenes.animator import animator_setup
from scenes.sample_animations import SampleScene


def main():
    # animator = animator_setup()  # Uncomment to play around with the animator!
    sample = SampleScene()  # Uncomment to see some sample animations!
    GAME_CLOCK.begin()
    arcade.run()


if __name__ == '__main__':
    main()
