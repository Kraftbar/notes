# -*- coding: utf-8 -*-
# for Python3 (needs Unicode)

"""
TODO:
 - Needs relative dir in final naming
 - Needs to consider empty folders
 - Also, test linux platfrom 
 - also check if it is considering filename length cap (win/linux)
"""

import os, shutil, sys

def splitPath(p):
    """Returns a list of folder names in path to p

    From user1556435 at http://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python"""
    a,b = os.path.split(p)
    return (splitPath(a) if len(a) and len(b) else []) + [b]

def safeprint(s):
    """This is needed to prevent the Windows console (command line) from choking on Unicode characters in paths.
    
    From Giampaolo Rodolà at http://stackoverflow.com/questions/5419/python-unicode-and-the-windows-console"""
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            print(s.encode('utf8').decode(sys.stdout.encoding))
        else:
            print(s.encode('utf8'))

def flatten(root, doit):
    """Flattens a directory by moving all nested files up to the root and renaming uniquely based on the original path.

    Converts all occurances of "SEP" to "REPL" in names (this allows un-flatting later, but at the cost of the replacement).
    
    If doit is True, does action; otherwise just simulates.
    
    """
    
    SEP  = "_"
    REPL = "?"

    folderCount = 0
    fileCount = 0

    if not doit:
        print("Simulating:")

    for path, dirs, files in os.walk(root, topdown=False):

        if path != root:

            for f in files:

                sp = splitPath(path)

                np = ""

                for element in sp[1:]:
                    e2 = element.replace(SEP, REPL)
                    np += e2 + SEP

                f2 = f.replace(SEP, REPL)
                newName = np + f2

                safeprint("Moved:   "+ newName )
                if doit:
                    shutil.move(os.path.join(path, f), os.path.join(root, newName))
                fileCount += 1

            safeprint("Removed: "+ path)
            if doit:
                os.rmdir(path)
            folderCount += 1

    if doit:
        print("Done.")        
    else:
        print("Simulation complete.")


    print("Moved files:", fileCount)
    print("Removed folders:", folderCount)

if __name__ == "__main__":
    print("")

    print("Flatten v1.00 (c) 2014 Nerdfever.com")
    print("Use and modification permitted without limit; credit to NerdFever.com requested.")

    if len(sys.argv) < 2:
        print("Flattens all files in a path recursively, moving them all to the")
        print("root folder, renaming based on the path to the original folder.")
        print("Removes all now-empty subfolders of the given path.")
        print("")
        print("Syntax: flatten [path] [DOIT]")
        print("")
        print("The DOIT parameter makes flatten do the action; without it the action is only simualted.")
        print("Examples:")
        print("  flatten //machine/path/foo          Simulates flattening all contents of the given path")
        print("  flatten //machine/path/bar DOIT     Actually flattens given path")
    else:
        if len(sys.argv) == 3 and sys.argv[2] == "DOIT":
            flatten(sys.argv[1], True)
        else:
            flatten(sys.argv[1], False)
