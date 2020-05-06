from cx_Freeze import setup, Executable

base = None

executables = [Executable("Searcher.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "SearcheExe",
    options = options,
    version = "1",
    description = 'Projet exécutable permettant de retourner une enquéte',
    executables = executables
)