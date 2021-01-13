# Skrypt autorstwa Mikołaja Pietrka
# https://github.com/mikolajpietrek

rm tests/*.mr 2>/dev/null
rm errors/*.mr 2>/dev/null

if [ "$1" == "tests" ] ; then
	path="tests"
elif [ "$1" == "errors" ] ; then
	path="errors"
elif [ "$1" == "gebala_tests" ] ; then
	path="gebala_tests"
else
	echo "uruchamianie: podaj 'tests' lub 'errors' lub 'gebala_tests' jako parametr"
	exit 1
fi

for FILE in $path/*.imp; do
	printf '\n%.0s' {1..20}
	#tput reset
	echo $FILE
	echo
	FN="${FILE%%.*}"
	cat "$FN.imp"
	python3 kompilator.py "$FN.imp" "$FN.mr"
	./maszyna_wirtualna/maszyna-wirtualna-cln "$FN.mr"
	read -p "Nacisnij dowolny klawisz, aby testowac dalej... " -n1 -s
done

echo
