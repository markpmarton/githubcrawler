# GitHub crawler

[This code was created for an older project in 2021. Since it has never been tested.]

## Requirements
All required packages are listed in the 'requirements.txt' file in the module's folder.
The project is based on the full version of the aiohttp package.
The recommanded install method is: 
```console
pip install aiohttp[speedups]
```
The module's folder contains the virtual environment the project was created with:
  - python version: 3.10.8
  - venv

## Setup
With using the venv in the module's folder no additional installation required.

#### Activating the venv:
```console
source ./githubcrawler/venv/bin/activate
```
#### Install packages
```console
pip install -r ./githubcrawler/requirements.txt
```

## Usage
The primary use mode is launching from the console.
The module can accept two parameters:
  - IN_PATH (-i) [REQUIRED]: Path of the file that contains the input JSON.
  - OUT_PATH (-o): Path of the file to store the collected data. The script overrides the content of the file. If the OUT_PATH parameter is not set, the script will store the data in the 'result.json' file in the current working directory.

With the -h flag the program returns the help.

### Launching
```console
python ./githubcrawler -i input.json -o res.json
```
or

```console
python ./githubcrawler -i input.json
```

### Logs
During the execution crawler logs will appear on the screen.
The structure is the following:

[time][log level][target url][used proxy][which download attempt is running][message]

When the script finishes, it shows the full path of the output file.

### Testing
The module implements unit tests and has a coverage about ~99%.
This result depends of the proxy the test cases use (it can be set in the file 'test_ghcrawler.py').
All the tests and the coverage statistics can be run with the 'run_test_coverage.sh' script in the 'utils' folder.
The main components of the project are in the following files:

```console
./githubcrawler/__main__.py
./githubcrawler/ghcrawler/__init__.py
```


