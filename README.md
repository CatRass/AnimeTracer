
# AnimeTracer [![pypresence](https://img.shields.io/badge/using-pypresence-1f1f24.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence) [![pypresence](https://img.shields.io/badge/using-MalApi-1f1f24.svg?style=for-the-badge&logo=github&logoWidth=20)](https://github.com/darenliang/mal-api) [![pypresence](https://img.shields.io/badge/using-AnilistPython-1f1f24.svg?style=for-the-badge&logo=github&logoWidth=20)](https://github.com/ReZeroE/AnilistPython)
AnimeTracer is a desktop application made in Python to track your progress in anime shows and movies, stored in lists.
AnimeTracer can be used with and without an internet connection, provided the shows you want to edit are in your lists before disconnecting from the internet.

### Program Permissions
- [x]  Creates Files (in install directory)
- [x] Accesses Files (in install directory)
- [x] Deletes Files (in install directory)
- [x] Connects to Discord Account (Rich Presence)
- [x] Connects to the Internet

## Installation
You can download the latest version of source code or compiled application in [releases](github.com/CatRass/AnimeTracer/releases), however a Windows `.msi` or `.exe` installer is planned.

You can also clone the whole repository using Git:
```bash
git clone https://github.com/CatRass/AnimeTracer.git
```

## Building from Source
### Windows
For Windows platforms I use the PyInstaller tool [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/)
If you want to compile manually, you might have to install PyInstaller with:

```pip install pyinstaller```

The pyinstaller command I use through auto-py-to-exe to compile release versions is:
```python
pyinstaller --noconfirm --onefile --windowed --add-data "C:/Path/To/Favicon/Folder/Location/favicon.png;."  "C:/Path/To/Main/Script/Location/main.py"
```
### MacOS
To package for MacOS X, I plan to use [py2app](https://pypi.org/project/py2app/).

For MacOS X (at least on Catalina 10.15.7)  if you are planning to run the program from the source code, be sure to give your terminal full permissions, as outlined [here](https://stackoverflow.com/a/59250494/12884111) to avoid the error:
```/Library/Frameworks/Python.framework/Versions/3.10/bin/python3: can't open file 'main.py': [Errno 1] Operation not permitted```

Nonetheless you will have to run the program in ```sudo``` if you are to use it from source, as it requires administrator permissions to create files and folders. 

The current MacOS build also has an issue where it not only inherits the system's appearance, but also seems to send the "Back" button on the Show Editor screen into the void. Beacause of this, it will be released later than the Windows and Linux builds.
### Linux
To package Linux builds, I also use auto-py-to-exe to generate my PyInstaller command. However to start auto-py-to-exe, I use a different command:
```python -m auto_py_to_exe```
The PyInstaller  command generated by auto-py-to-exe is the same as windows.
When compiling from source on Linux, keep in mind that many comments contain links to library bindings, which apparently get read by the Linux Python Interpreter, causing errors.
There are a few issues with the Linux Python Source code, being:

- The app window icon that is present on Windows cannot be displayed on Linux
- Loading cursor implemented through lines ```main.config(cursor="wait")``` returns an error
- Discord Rich Presence does not work despite Discord running

However the Linux Release has the inexplicable benefit of not having any issues with the episodes box in the show editor.
### Dependencies
If you are planning on using the source `.py` file, or compile it yourself, you will need to install some external libraries. they are all available on PyPi, and can be installed through pip.
- Tkinter - ```pip install tk```
- mal-api - [PyPi](https://pypi.org/project/mal-api/)
- AnilistPython - [PyPi](https://pypi.org/project/AnilistPython/)
- PyPresence - [PyPi](https://pypi.org/project/pypresence/)
- PIL - [PyPi](https://pypi.org/project/Pillow/)

A full list of dependencies is viewable in the requirements.txt file. Note that the requirements file does not include compilers.

## License
[MIT](https://choosealicense.com/licenses/mit/)
