# WSL-r


### latex update on save
recuirement: inotify-tools     
>   ```sh    
>    # Runs pdflatex and displays pdf with windows default pdf viewer
>    inotifywait -q -m -e close_write main.tex |
>    while read -r filename event; do
>      pdflatex main.tex && wslview main.pdf
>    done    
>   ```
