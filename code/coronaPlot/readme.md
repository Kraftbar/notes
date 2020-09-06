needs python libs
    wget             
    pandas            
    re            
    matplotlib            


    ```shell
    wget -O dataHopkins.csv https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv 
    x=$(cat dataHopkins.csv | grep  "Province" | tr "," "\n")
    y=$(cat dataHopkins.csv | grep  "Norway" | tr "," "\n" )
    y=$(cat dataHopkins.csv | grep  "Norway" | tr "," "\n" | awk '{s=$0;getline;print -s+$0;next}' )
paste <(echo "$x") <(echo "$y") --delimiters ',' | tail -n +200 | gnuplot -e "set datafile sep ',' ; set xdata time;  set timefmt '%m/%d/%Y'; plot '-' u 1:2; " -p
rm dataHopkins.csv  
```
