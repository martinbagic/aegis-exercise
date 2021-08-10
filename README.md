## Input

As input, the user can specify parameters (to customize the simulation conditions) and supply [pickled](https://docs.python.org/3/library/pickle.html) demes (to restore pre-evolved populations).

### 1. Parameters

This section explains where AEGIS pulls the parameters from. The available parameters and their values are described in
[another section](#list-of-parameters).

Parameters can be specified by:

1. **Passing arguments when calling `aegis.Aegis`**, e.g. `aegis.Aegis(CYCLE_NUM=2000, MAX_LIFESPAN=90)`. This is relevant when Aegis is run via a script (e.g. in `tests/`).
1. **Command line arguments**, in JSON format, e.g. `python3 main.py --params_extra '{"CYCLE_NUM": 2000, "MAX_LIFESPAN": 90}`. Those will be processed in the `macroconfig.Macroconfig` class. This is useful if one wants to slightly modify the parameters without having to create a separate config file. The command line input is documented in the output.
1. **Config files**, in YML format, e.g. `input/config_preset/_DEFAULT.yml`. The default (`_DEFAULT.yml`) is always applied, but other config files can be added to, by specifying them in the command line, e.g. `python3 main.py --config_files extra.yml`. This is useful when many parameters need to be modified, or when the parameterization encodes a distinct scenario.

The priority decreases along this list, i.e. the parameters passed as arguments when calling `Aegis` override
those passed as command line arguments, which override those in config files. Furthermore, when multiple
config files are specified (e.g. `--config_file config_1.yml another_file.yml configc.yml`), the first file (`config_1.yml`) has the highest priority, while the last specified file (`configc.yml`) has the least priority.

### 2. Pre-evolved demes

Seeding the simulation with pickles containing pre-evolved demes can be done using the `--reload_deme` flag (e.g. `python3 main.py --reload_deme path/to/pickle`).

## Output

Output contains the **summary of input specification**, a **copy of pickled demes** (if used), **data for visualization using Visor**, and **other fine-grained data** (including genotypic, phenotypic, population genetic, etc.). All output files are saved in the directory `output/{jobid}/` (jobid is either specified in the command line or, if not specified in the cmd, it takes the name of the first given config file; per default `_DEFAULT`).

### 1. Summary of input specification

This is a `input_summary.json` file important for reproducibility. It contains all final parameters.

### 2. Pickled deme

Pickled demes can be found in the folder `pickles/`. The files will be named by the stage number at which the deme was pickled.

### 3. Data for Visor

Data for visor is saved in the folder `visor/` and it is used by _visor_ to visualize the evolution of the simulated population. It contains multiple files:

1. `genotypes.csv`
1. `phenotypes.csv`
1. `demography.csv`
1. `phylogeny.csv`
1. `stats.csv`

### 4. Other data

Other data is saved in the folder `data/` using the [feather](https://github.com/wesm/feather) format. The file naming
specified the stage at which the data was captured, and also the kind of data captured:

1. `{stage}.genotypes`
1. `{stage}.phenotypes`
1. `{stage}.demography`

## List of parameters

## Command line options

## Visor

Visor is the visualization tool complementary to AEGIS.

<!-- TODO Add more -->
