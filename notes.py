import os
from pathlib import Path
import sys
from commonfunctions import getaisummary, getfilelist
from configparser import ConfigParser

config = ConfigParser()
config.read("assistantconfig.ini")

notespath = Path(config["DEFAULTS"]["notespath"])
pathstoskip = [r'C:\Users\geoha\Documents\Obsidian Notes\Mind Vault\3 - Tags', r'C:\Users\geoha\Documents\Obsidian Notes\Mind Vault\5 - Templates']

def gettxtfilecontents(filepath: str) -> str:
    text = ''

    if filepath.endswith(".md"):
        with open(filepath, 'r') as f:
            for line in f:
                text += line.strip("#")

    if filepath.endswith(".txt"):
        with open(filepath, 'r') as f:
            for line in f:
                text += line.strip("\n")

    return text, filepath

if __name__ == "__main__":
    try:
        if Path(sys.argv[1].strip('"')).is_file():
            if "summarize" in sys.argv:
                getaisummary(gettxtfilecontents(os.path.abspath(sys.argv[1])), os.path.abspath(sys.argv[1]))
            
            else:
                text, path = gettxtfilecontents(os.path.abspath(sys.argv[1]))
                print(f"{path}: \n {text}")

        elif Path(sys.argv[1].strip('"')).is_dir():
            files = getfilelist(Path(sys.argv[1].strip('"')))
            
            for file in files:
                text, path = gettxtfilecontents(file)


                if "summarize" in sys.argv:
                    getaisummary(text, path)

    except Exception as e:
        print(F"Exception occured: {e}")