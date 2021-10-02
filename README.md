# WSL-r

recuirement: inotify-tools     

### latex update on save
>   ```sh    
>    inotifywait -q -m -e close_write ####FILE ON SAVE#### |
>    while read -r filename event; do
>      pdflatex ####FILE ON SAVE#### && wslview test.pdf
>    done    
>   ```
