# lists file without extension
find | sed 's/^.*\///' | sed 's/*.\.//' | sed 's/\.[^.]*$//'
# exeption for dot files
find | sed 's/^.*\///' | sed '/^\./!s/\.[^.]*$//'
