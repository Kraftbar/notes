# WSL-r


### latex update on save
recuirement: inotify-tools     
>   ```sh    
>    # Runs pdflatex and displays pdf with windows default pdf viewer
>    inotifywait -q -m -e close_write ####FILE ON SAVE#### |
>    while read -r filename event; do
>      pdflatex ####FILE ON SAVE#### && wslview ####FILE ON SAVE####.pdf
>    done    
>   ```
