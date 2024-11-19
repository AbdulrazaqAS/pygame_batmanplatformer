import neat

from constants import *
from game import Game
from os import path

from screen import Screen


class Launcher(Game):
    def __init__(self):
        super().__init__('CameraDemo', (WIDTH, HEIGHT))

        # asset directories
        self.img_dir = path.join(self.dir, 'assets', 'img')
        self.map_dir = path.join(self.dir, 'assets', 'map')

        # settings
        self.fps = 60

    def start(self, genomes, config):
        screen = Screen(self, self.fps, genomes, config)
        self.set_screen(screen)


if __name__ == "__main__":
    # Load Config
    config_path = "neat_config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)

    #population = neat.Checkpointer.restore_checkpoint("./saves/startrek1-checkpoint-359_no_thrust")
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    checkpoint_reporter = neat.checkpoint.Checkpointer(5, None, './saves/startrek1-checkpoint-')
    #population.add_reporter(checkpoint_reporter)

    launcher = Launcher()

    # Run Simulation For A Maximum of 1000 Generations
    population.run(launcher.start, 1000)
