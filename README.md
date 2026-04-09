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
1. generate supporting dictionaries: object_column_names_enum, location_list, people_dict, category_dict
2. init object_location_array (per location array of objects)
3. init object_category_array (per category array of objects)
4. iterate through object sheet:
    - check if missing; report and skip
    - create object_list [{id: []}]
    - add to object_dict:
        - image URL
        - alt text 
        - figcaption
5. generate location pages:
    -iterate through object_location_array

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
