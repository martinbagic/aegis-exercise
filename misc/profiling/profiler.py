import aegis
import cProfile
import pstats
import pathlib

if __name__ == "__main__":

    here = pathlib.Path(__file__).parent.absolute()

    profiler = cProfile.Profile()
    profiler.enable()

    aegis.main(here / "1.yml")

    profiler.disable()
    with open(here / "1.profile", "w") as stream:
        stats = pstats.Stats(profiler, stream=stream).sort_stats("ncalls")
        stats.print_stats()
