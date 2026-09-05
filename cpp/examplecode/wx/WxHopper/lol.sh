#!/bin/bash
FILE=.gitignore
if [ -f $FILE ]; then
   echo "The file '$FILE' exists."
else
   touch .gitignore
   echo ".vscode" >> read.txt   
fi
