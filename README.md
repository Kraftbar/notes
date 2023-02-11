# sed-awk-r


echo "before middle after" | sed 's/before \(.*\) after.*/\1/'         
echo "before middle after" | awk ' /(before)(.*)after/ {print $2 }'
