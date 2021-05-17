# AEGIS

## Setup instructions

<details>
  <summary>Setup for macOS & Linux</summary>

### I. Check if Python3 is installed

1. Run terminal. (Command + Space. Type in **Terminal**. Launch.)
1. Run `python3 --version`.
   - If you get a message `Python 3.x.x` (x can be any number), Python3 is installed. Proceed with the next section.
   - If you get an error message (e.g. `name 'python3' is not defined`), Python3 is not installed.
     Proceed with the step 3.
1. Download Python3. Go to www.python.org/downloads/. Click on the yellow button **Download Python 3.9.5** (the .pkg file has ~30 MB).
1. Run the installation package. Use default settings.
1. Restart terminal.
1. Run `python3 --version`. Now you should get a message `Python 3.x.x` (x can be any number)
1. Do not close the terminal.

### II. Download AEGIS

1. Go to www.github.com/martinbagic/aegis-exercise
1. Click on the green button **Code**.
1. Click on **Download ZIP**.
1. Move the downloaded folder to desktop.

### III. Navigate to the working directory

1. Run: `cd ~/Desktop/aegis-exercise/`
   - If you ever close the terminal, always run this command to return to the working directory.

### IV. Install dependencies in a [virtual environment](https://docs.python.org/3/tutorial/venv.html)

1. Run: `python3 -m venv venv`
1. Run: `. venv/bin/activate`
   - Last line in terminal should now start with **(venv)**.
1. Run: `python3 -m pip install -r requirements.txt`
   - If you get a message **The "gcc" command requires the command line developer tools. Would you like to install the tools now?**, click **Install**. After installation, rerun this step 3.
   - This might take a few minutes.

### V. Test AEGIS

1. Run: `python3 main.py -h`
   - If it returns information about the **usage**, **positional arguments**, **optional arguments** and others, you can proceed with the next part (**How to run AEGIS**).
   - If it returns **No such file or directory**, check if you are in the correct directory (run `cd ~/Desktop/aegis-exercise/`) and try again.
   - If it returns **ModuleNotFoundError**, check that your virtual environment is activated (run `. venv/bin/activate`) and try again.

</details>

<details>
  <summary>Setup for Windows</summary>

### 0. Install Visual CPP Build Tools

1. Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/
1. Click the purple button **Download build tools**.
1. Run the downloaded file **vs_BuildTools.exe**.
1. Click Continue.
1. Check **C++ build tools box** (the box has an icon with a screen and two purple pluses).
1. Click Install.

### I. Check if Python3 is installed

1. Run terminal from desktop.
   - Shift + right-click on desktop.
   - Click **Open PowerSHell window here**.
1. Run `py -3 --version`.
   - If you get a message `Python 3.x.x` (x can be any number), Python3 is installed. Proceed with the next section (**II. Download AEGIS**).
   - If you get an error message (e.g. `Python was not found`), Python3 is not installed.
     Proceed with the step 3.
1. Download Python3. Go to www.python.org/downloads/. Click on the yellow button **Download Python 3.9.5** (the .exe file has ~28 MB).
1. Run the installation package. Check box **Add Python 3.9 to PATH**. Click on **Install Now**.
1. Close and open the terminal again as in step 1.
1. Run `py -3 --version`. Now you should get a message `Python 3.x.x` (x can be any number)
1. Do not close the terminal.

### II. Download AEGIS

1. Go to www.github.com/martinbagic/aegis-exercise
1. Click on the green button **Code**.
1. Click on **Download ZIP**.
1. Move the downloaded folder to desktop.
1. Right-click on the zip file and click **Extract here**.

### III. Navigate to the working directory

1. Run: `cd aegis-exercise`
   - Your command line path should be **?:\Users\\?\Desktop\aegis-exercise**

### IV. Install dependencies in a [virtual environment](https://docs.python.org/3/tutorial/venv.html)

1. Run: `py -3 -m venv venv`
1. Run: `.\venv\Scripts\activate`
   - If the shell returns a new line with **(venv)** at the beginning, virtual environment is
     successfully activated, so you can proceed with the step 3.
   - If the shell returns an error **cannot be loaded because running scripts is disabled**:
     - Run: `Set-ExecutionPolicy Unrestricted -Scope Process`
     - When prompted, write **Y** and confirm by pushing **Enter**.
     - Repeat this step by running: `.\venv\Scripts\activate`
1. Run: `py -3 -m pip install -r requirements.txt`
   - This will take about 5 minutes depending on your machine.

### V. Test AEGIS

1. Run: `py -3 main.py -h`
   - If it returns information about the **usage**, **positional arguments**, **optional arguments** and others, you can proceed with the next part (**How to run AEGIS**).
   - If it returns **No such file or directory**, check if you are in the correct directory (`?:\Users\?\Desktop\aegis-exercise` where first ? is your disk, and the second ? your username) and try again.
   - If it returns **ModuleNotFoundError**, check that your virtual environment is activated (run `.\venv\Scripts\activate`) and try again.

</details>

## How to run AEGIS?

To run AEGIS, run the following command in the terminal:

- `python3 aegis.py -c CONFIG_FILE` (macOS & Linux)
- `py -3 aegis.py -c CONFIG_FILE` (Windows)

but instead of `CONFIG_FILE` write the name of the actual config file you intend to use.
You can also run the simulation without `-c CONFIG_FILE`; it will then use the default parameters.

### Custom parameters

If you want to change the parameters of the simulation, you should create a new config file
in the folder _config_custom_ and add your parameters of interest in it.
For example, look at the custom config file _bigger_population.yml_.
It has a single parameter `MAX_POPULATION_SIZE` which has been set to 1500.
When you look in the default config file (\__DEFAULT.yml_), you will see that the
`MAX_POPULATION_SIZE` has previously been set to 300. So, when you run the command
`python3 aegis.py -c bigger_population.yml`, your simulation will
have the bigger population size of 1500.

Note that names of all config files should end in _.yml_ file extension.

You can open _.yml_ files with TextEdit (macOS) or Notepad (Windows)
or a code editor (e.g. Visual Studio Code) or other tools.

## How to visualize the simulation results?

Open another terminal in the same folder. To use the visualization tool, run in the second terminal:

- `python3 -m http.server --directory Visor/` (macOS & Linux)
- `py -3 -m http.server --directory Visor/` (Windows)

Open a browser of choice (e.g. Chrome) and write into URL bar `http://localhost:8000/`

## Explore

1. Try different population sizes (`MAX_POPULATION_SIZE`).
   - Do some populations go extinct? Why?
   - Do bigger populations have more or fewer bits with high values? Why?
1. Try different mutation rates (`GENOME_CONST: muta`). What happens when mutation rates are high and what when they are low? Why?
1. Try different maturation ages (`MATURATION_AGE`). What happens to the reproduction genes? Why?
1. Try different number of bits per locus (`BITS_PER_LOCUS`, e.g. 4 or 16). What differences do you observe? Why?
1. Try setting `OVERSHOOT_EVENT` to `treadmill_boomer` and `treadmill_zoomer`. What effects does this have on the population? Why?
1. Try setting reproduction mode `REPR_MODE` to `sexual`. What happens? Why?
1. How would you change the parameters if you wanted to make the population go extinct? What would ou do to make it be more stable (not go extinct)?
1. How would you change the parameters to extend lifespan of the individuals and what to reduce it?
1. Run a simulation with config file _AP_number.yml_. What do you observe? Why?
1. Can you detect evolutionary differences when changing other parameters?
