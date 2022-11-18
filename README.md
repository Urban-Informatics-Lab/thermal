# Satellite Collection Pipeline - Building Statistics
This repo is meant to consolidate some of the tooling required to use Google Earth Engine for the collection of data pertinent in building energy consumption.

The initial Preprint, Open Access form of the work can be found here:
SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4204469

### Steps for getting running
1. conda create --name thermal --file spec-file.txt
2. earthengine authenticate
3. mkdir ./data/<name>/
4. mkdir ./data/<name>/satellite
5. cp <building_footprints> ./data/<name>/footprints.geojson
6. python run.py --city <directory_name> --settings default\_settings.yml --export
 
