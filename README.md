### Steps for getting running
1. conda create --name thermal --file spec-file.txt
2. earthengine authenticate
3. mkdir ./data/<name>/
4. mkdir ./data/<name>/satellite
5. cp <building_footprints> ./data/<name>/footprints.geojson
6. python run.py --city <directory_name> --settings default\_settings.yml --export
 

