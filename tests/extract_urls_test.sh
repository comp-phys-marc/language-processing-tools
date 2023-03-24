python ../download.py -u https://www.xml.com -f file.html
python ../extract.py -s file.html -f any -t URL -o found.xml
python ../encode.py -n found -f found.xml -t HTML -p 1
python ../store.py -s found --index train-data-2 --api_key 45def035-6ef4-4637-be71-d7ffe74c8149
python ../store.py -c found -t 3 --index train-data-2 --api_key 45def035-6ef4-4637-be71-d7ffe74c8149