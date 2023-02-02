# lists file without extension
find | sed 's/^.*\///' | sed 's/*.\.//' | sed 's/\.[^.]*$//'
