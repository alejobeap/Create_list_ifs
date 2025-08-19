while read date; do
    matches=(GEOC/*"$date"*)
    if [ -e "${matches[0]}" ]; then
        for folder in "${matches[@]}"; do
            echo "Deleting folder $folder"
            rm -rf "$folder"
        done
    else
        echo "No folder found for $date"
    fi
done < baselinesmayor2delete.txt
