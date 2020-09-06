needs python libs
    wget             
    pandas            
    re            
    matplotlib            


```shell
    wget -O dataHopkins.csv https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv 
    x=$(cat dataHopkins.csv | grep  "Province" | tr "," "\n")
    y=$(cat dataHopkins.csv | grep  "Norway" | tr "," "\n" )
    y=$(cat dataHopkins.csv | grep  "Norway" | tr "," "\n" | awk '{print $0-s; s=$0}' )
    paste <(echo "$x") <(echo "$y") --delimiters ',' | tail -n +40 | gnuplot -e "set datafile sep ',' ; set xdata time;  set timefmt '%m/%d/%Y'; plot '-' using 1:2 with line ; set autoscale y;" -p
    rm dataHopkins.csv  
```
