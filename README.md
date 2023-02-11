# sed-awk-r


echo "before middle after" | sed 's/before \(.*\) after.*/\1/'         
echo "before middle after" | awk ' /(before)(.*)after/ {print $2 }'
string="before middle after";string="${string#*before?}"; string="${string%*?after}"; echo $string
