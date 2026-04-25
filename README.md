# Overview
A set of functions used to generate web pages that contain thumbnails and captions from a google sheet that is used as a database.

Here is an example caption:
```
<span class="popuptext show" id="myPopup" style="width: 360px; left: 241.5px; top: 10px;">
    <b>Dr. John Dixwell (1777-1834)</b>
    <i>Judith's first cousin's (once removed) husband</i>
    <br> by <a target="_blank" href="https://en.wikipedia.org/wiki/James_Frothingham">James Frothingham (1786-1864)</a>
    (circa 1817) oil on canvas.<br>
    <div style="text-align:left">
        <p>James Frothingham (1786-1864) is noted for his beautifully detailed faces. An example are the lovely
            highlights and shadows of Henrietta Sargent portrait.</p>
    </div>
        <div style="text-align:left">
            <p>Dr. John Dixwell (1777-1834) A physician who practiced in Boston. He married Esther Sargent in 1805.</p>
        </div>
    <p>Married Esther Sargent in 1805,</p><a target="_blank" href="https://drive.google.com/file/d/1eQzLcsPnJ-Kw2PGI6WmBUG-fv6H7jSWs/view">oid0059</a>
</span>
```
# processing steps:
1. do Google authenication and open inventory spreadsheet
2. generate supporting dictionaries: object_column_names_enum, location_list, people_dict, category_dict
3. create object_dict and fill in object_location_dict (per location array of objectIDs)
    - the object_dict uses the OID as the key, and has an array of items:
        - image URL
        - alt text (this is filled from the Original_Description when creating key=OID in the obj_dict)
        - figcaption
    - the locations include 'missing' 'deaccessioned' 'on-loan', 'Cape Ann Museum' etc.
    - a dictionary of unrecognized locations is also created, with an list of OIDs per unrecognized location
    - a list of OID's in unrecognized locations
4. find a thumbnail photo URL for each object by iterating through the object_dict
5. generate the figure caption HTML using data in Object_Type, Subject_Style, etc columns.
6. generate location pages:
    -iterate through object_location_dict and populate doc using dominate library.

## 

# figure caption generation
## people:
* subject comes from Subject_Style if Object_type in PEOPLE_IMAGE_TYPE_LIST
* relationship to JSM comes from people_list
* creator
* creation date
* media
* creator description from people_list
* subject description from people_list
* Narrative from Narrative
* object ID with link to full size picture

## people columns and people dict:
people column enum:  
```
  for column in people_col_name_e:
      print(column.name, column.value)
Full_Name 0
Description 1
RelationshipToJudith 2
URL 3
Comment 4
Father 5
Mother 6
Spouse 7
Marriage_Date 8
Marriage_Location 9
```
The dict is {"Full_Name": [Description, RelationshipToJudith, URL]}

## not people (china, glass, furniture, etc):
* object_type

