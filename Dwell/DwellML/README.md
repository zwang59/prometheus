# DwellML
=========

PreRequisites
-------------

Windows
~~~~~~~
Install MiniConda (py3, 64 bit) from https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

After installation, you should see a entry for "Anaconda" in Windows start menu.
For any conda commands, always launch and use the Terminal ("Anaconda Prompt") from this menu.


Installation
------------

1. Git clone or copy over the folder containing this file

2. From the terminal (use Conda terminal on windows), create a devenv for the project
```
    $ conda env create -f env.yml
```

3. Switch to the devenv
```
    $ conda activate dwellml-dev
    $ pip install -e .
```

4. Test installation by running all tests
```
    $ python -m unittest discover dwellml
```
