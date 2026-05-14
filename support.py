'''
These functions are intended to be called from a colab project.
The spreadsheet object is a google sheet.
'''
import collections
import enum
import glob
import os
try:
   import xattr
except Exception as e: print(e)
try:
   from dominate import document as dom_doc
   from dominate.tags import *
   from dominate.util import raw   
except Exception as e: print(e)

from markdown import Markdown

PEOPLE_IMAGE_TYPE_LIST = ["portrait", "silhouette", "bust", "miniature", "bronze" ]
TITLED_ARTWORK_TYPE_LIST = ["painting", "watercolor", "lithograph", "sculpture", "coat-of-arms", \
                             "book", "etching", "drawing", "copy", "engraving"]
CATEGORY_TYPE_LIST = ["Fine_Art", "Silver", "Ceramics", "Glass", "Metals", "Furniture", \
                      "Textiles", "Accessories", "Adornments", "Document_Artifacts", \
                      "Needlework", "Books", "Not_In_Collection", "On_Loan"]

class OBJ_ARRAY_IDX_E(enum.Enum): 
   IMG_FILE_ID = 0
   ALT = 1
   FIGCAPT = 2

class PEOPLE_ARRAY_IDX_E(enum.Enum): 
   DESCRIPTION = 0
   RELATIONSHIPTOJUDITH = 1
   URL = 2

def make_col_name_enum(worksheet):
  col_names = worksheet.row_values(1)
  col_names = [s.replace(' ', '_') for s in col_names]
#   col_name_enum = {col_name.replace(" ", "_"): i for i, col_name in enumerate(col_names)}
  col_name_e = enum.Enum('col_names', col_names, start=0)
#   print(f"{col_names=}\n{col_name_e=}")
  return col_name_e

def make_people_dict(worksheet):
   people_col_name_e = make_col_name_enum(worksheet)
   people_dict = {}
   for row in worksheet.get_all_values()[1:]:
      key = row[people_col_name_e.Full_Name.value]
      value = [row[people_col_name_e.Description.value], \
               row[people_col_name_e.RelationshipToJudith.value], \
               row[people_col_name_e.URL.value]]
      people_dict[key] = value
   return people_dict

def get_image_url(object_dict, images_folder):
   # fills in the thumbnail image parameter for each object
   #Drive foldername convention: 0000-FineArts, 0500-Furniture, 0700-Textiles, etc

   # get file ID (fid) of a PNG used if no object picture is found ('NoPicture.png' which is SHM-Interns > ObjectPhotos)
   files = glob.glob(os.path.join(images_folder, f"NoPicture.png"), recursive=False)
   no_picture_fid = xattr.getxattr(files[0], "user.drive.id").decode('utf-8')

   oid_with_no_image_files_list = []
   oid_with_invalid_file_id_list = []
   for oid in object_dict:
      # how much more efficient is it to have the xxxx-category foldername in the search?
      # search_path = f'{image_dir}/Object-Photos/0000-Fine_Art/oid0028_C*.*'
      # search_path = f'{image_dir}/Object-Photos/*/{oid}*.*'
      search_pattern = os.path.join(images_folder, f"**/{oid}*.*")
      files = glob.glob(search_pattern, recursive=True)
      img_filename = None
      if len(files) == 0:
         oid_with_no_image_files_list.append(oid)
         # print(f"No files found for {oid}")
      elif len(files) == 1:
         img_filename = files[0]
      else:
         non_detail_files = []
         for f in files:
            if "detail" not in f:
               non_detail_files.append(f)
         if len(non_detail_files) == 0:
            print(f'Error finding img file: {files}')
         elif len(non_detail_files) == 1:
            img_filename = non_detail_files[0]
         else:
            print(f"Multiple images for {oid}")
      if img_filename:
         fid = xattr.getxattr(img_filename, "user.drive.id").decode('utf-8') #linux
         # fid = subprocess.getoutput(f"xattr -p 'user.drive.id' '{img_filename}'") #macos
         if len(fid) == 33:
            object_dict[oid][OBJ_ARRAY_IDX_E.IMG_FILE_ID.value] = fid
         else:
            print(f"Invalid fid: {fid} for {oid}")
            oid_with_invalid_file_id_list.append(oid)

        # if no image pic was found:
      if not object_dict[oid][OBJ_ARRAY_IDX_E.IMG_FILE_ID.value]:
         object_dict[oid][OBJ_ARRAY_IDX_E.IMG_FILE_ID.value] = no_picture_fid

   return oid_with_no_image_files_list, oid_with_invalid_file_id_list

def make_obj_dict(inventory_rows, col_enum, locations_list, location_year, entries=None):
   #example object_dict = {"oid0028_C":[None,None,None], "oid1300":[None,None,None]} 
   # this function fills in 2nd entry in array, which is the 'alt' parameter for the html image
   # other functions fill in the 1st & 3rd array entry
   # this function returns:
   #   - the object_dict
   #   - a dict of objects per location (the location has a year argument)
   #   - a dict of unrecognized locations, with objects in those locations.  This is used to correct the spreadsheet

   location_column = None
   for column_enum in col_enum:
      if column_enum.name.startswith(location_year):
         location_column = column_enum.value
         break
   if not location_column:
      print(f'Error: a column with a location year of {location_year} not found')
      return {}, {}, {}

   # locations_list = [location.replace(' ', '_') for location in locations_list]
   locations_dict = dict.fromkeys(locations_list) # a list of objects per location
   locations_dict = {key: [] for key in locations_dict}

   unrecognized_locations_dict = {}
   object_dict = {}
   if entries is None:
      entries = len(inventory_rows)
   else:
      entries += 1 #skip first row

   for row_num, row in enumerate(inventory_rows[1:entries]):
      oid = row[col_enum.ID.value]
      if oid[0:3].lower() != 'oid' or not oid[3:7].isnumeric():
         print(f'skipping row {row_num} due to invalid OID={oid}')
         continue

      desc = row[col_enum.Original_Description.value].strip()
      if len(desc) < 1:
         print(f'skipping row {row_num} due to no description')
         continue

      location = row[location_column]
      if not location:
         location = "Unknown"
      if location in locations_dict:
         locations_dict[location].append(oid)
      else:
         print(f"{location=} not in locations_dict for {oid}")
         if location in unrecognized_locations_dict:
            unrecognized_locations_dict[location].append(oid)
         else:
            unrecognized_locations_dict[location] = [oid]
         continue
      alt = f'{oid}: {desc}'
      object_dict[oid] = [None, alt, None]
   return object_dict, locations_dict, unrecognized_locations_dict

def create_html_files(page_name_list, obj_per_page_dict, output_dir_path, object_dict):
  # create a list of docs, one for each item in page_name_list:
   html_page_list = []
   for page_name in page_name_list:
      if page_name not in obj_per_page_dict:
         print(f'error: {page_name} not in {obj_per_page_dict} dictionary')
         continue
      if len(obj_per_page_dict[page_name])== 0:
         print(f'warning: no objects in {page_name}')
         continue
      doc = dom_doc(title=page_name)
      with doc.head:
         link(rel='stylesheet', href='shm-binder.css')
         script(type='text/javascript', src='shm-binder.js')
         meta(name="viewport", content="width=device-width, initial-scale=1")
      with doc.body:
         div(f'{page_name} -  Click on an image for more info on the object.', _class="page_title")
         span(_class ="popuptext", _id="myPopup")
         for oid in obj_per_page_dict[page_name]:
            file_id = object_dict[oid][OBJ_ARRAY_IDX_E.IMG_FILE_ID.value]
            img_src = f'https://drive.google.com/a/sargenthouse.org/thumbnail?id={file_id}'
            img_alt = object_dict[oid][OBJ_ARRAY_IDX_E.ALT.value]
            with div(_class="column"):
               with figure():
                  img(src=img_src, alt=img_alt, title=img_alt, style="width:100%", _class ="image-click")
                  with figcaption(_id="oidCaption"):
                     for line in object_dict[oid][OBJ_ARRAY_IDX_E.FIGCAPT.value]:
                        raw(line)
                        br()
         
         html_page_list.append(doc)

   if not os.path.exists(output_dir_path):
      os.makedirs(output_dir_path)
   os.chdir(output_dir_path)
   # write out each page
   for page in html_page_list:
      out_filename = page.title.replace(" ", "_") + '.html'
      with open(out_filename, 'w') as f:
         f.write(page.render())

def make_figcaptions(inventory_rows, col_enum, object_dict, people_dict, entries=None):
   # changes the figcapture parameter per object with the html for the object
   if entries is None:
      entries = len(inventory_rows)
   else:
      entries += 1 #skip first row
   for row in inventory_rows[1:entries]:
      oid = row[col_enum.ID.value]
      if oid not in object_dict:
         print(f'Error: {oid} in inventory sheet but not in object_dict')
         continue
 
      obj_Object_Type = row[col_enum.Object_Type.value]
      obj_Subj_style = row[col_enum.Subject_Style.value]
      # print(f'{oid} {obj_Object_Type=} {obj_Subj_style=} ')
      obj_Narrative = row[col_enum.Narrative.value]
      obj_Creation_Date = row[col_enum.Creation_Date.value]
      obj_Creator = row[col_enum.Creator.value]
      obj_Medium = row[col_enum.Medium.value]
      # obj_Origin = row[col_enum.Origin.value]
      # obj_Dimensions = row[col_enum.Dimensions.value]
      # obj_Provenance = row[col_enum.Provenance.value]
      obj_Donor = row[col_enum.Donor.value]
      obj_Date_of_Gift = row[col_enum.Date_of_Gift.value]

      persons_desc = None
      persons_to_jsm = None

      figcapt_list = []
      is_person_or_titled_artwork = False
      if obj_Object_Type.lower() in PEOPLE_IMAGE_TYPE_LIST:
         is_person_or_titled_artwork = True
         persons_name = obj_Subj_style # if a person, the subj_style column has the person's name
         name_has_url = False
         if persons_name in people_dict:
            persons_url = people_dict[persons_name][PEOPLE_ARRAY_IDX_E.URL.value]
            persons_desc = people_dict[persons_name][PEOPLE_ARRAY_IDX_E.DESCRIPTION.value]
            persons_to_jsm = people_dict[persons_name][PEOPLE_ARRAY_IDX_E.RELATIONSHIPTOJUDITH.value]
            if len(persons_url) > 0:
               figcapt_list.append(f'<a target="_blank" href="{persons_url}">{persons_name}</a>')
               name_has_url = True
         if not name_has_url:
            figcapt_list.append(persons_name)

      # add relationship to Judith
      if persons_to_jsm:
         figcapt_list.append(f'<i>{persons_to_jsm}</i>')

      # add title if object type is in TITLED_ARTWORK_TYPE_LIST:
      if obj_Object_Type in TITLED_ARTWORK_TYPE_LIST:
         is_person_or_titled_artwork = True
         figcapt_list.append(f'<b><i>{obj_Subj_style}</i></b>')  #obj_Subj_style is the artwork title
      # only put object type if NOT a portrait, minature, etc; persons_name will be populated in so
      elif not is_person_or_titled_artwork:
         figcapt_list.append(obj_Object_Type)

      # add style and medium
      if obj_Medium:
         if is_person_or_titled_artwork or not obj_Subj_style:
            figcapt_list.append(obj_Medium)
         else:
            figcapt_list.append(f'{obj_Medium}, {obj_Subj_style}')

      # add creator & creation date
      creator_has_url = False
      creator_desc = None
      if not obj_Creation_Date or 'unknown' in obj_Creation_Date.lower():
         obj_Creation_Date = 'unknown year'
      if not obj_Creator or 'unknown' in obj_Creator.lower():
         obj_Creator = 'an unknown creator'
      elif obj_Creator in people_dict:
         creator_url = people_dict[obj_Creator][PEOPLE_ARRAY_IDX_E.URL.value]
         creator_desc = people_dict[obj_Creator][PEOPLE_ARRAY_IDX_E.DESCRIPTION.value]
         if creator_url:
            figcapt_list.append(f'by <a target="_blank" href="{obj_Creator}">{obj_Creator}</a> in {obj_Creation_Date}')
            creator_has_url = True
      if not creator_has_url:
         figcapt_list.append(f'by {obj_Creator} in {obj_Creation_Date}')

      if creator_desc:
         figcapt_list.append(f'Creator {Markdown().convert(creator_desc)}')

      # add subject (person) description
      if persons_desc:
         figcapt_list.append(f'<br>Subject {Markdown().convert(persons_desc)}')

      if obj_Narrative:
         figcapt_list.append(f'<br>{Markdown().convert(obj_Narrative)}')

      # add donor and donation date
      if not obj_Donor and not obj_Date_of_Gift:
         figcapt_list.append(f'<br>Unknown donor and donation date')
      elif obj_Donor and not obj_Date_of_Gift:
         figcapt_list.append(f'<br>Donated by {obj_Donor}; donation date unknown')
      else:
         figcapt_list.append(f'<br>Donated by {obj_Donor} in {obj_Date_of_Gift}')

      # add Object ID
      file_id = object_dict[oid][OBJ_ARRAY_IDX_E.IMG_FILE_ID.value]
      large_img_src = f'https://drive.google.com/file/d/{file_id}'
      figcapt_list.append(f'<br><a target="_blank" href="{large_img_src}">{oid}</a>')

      object_dict[oid][OBJ_ARRAY_IDX_E.FIGCAPT.value] = figcapt_list
'''
      object_dict[oid][OBJ_ARRAY_IDX_E.FIGCAPT.value] = [\
         '<a target="_blank" href="https://en.wikipedia.org/wiki/John_Singer_Sargent">Sargent, John Singer (1856-1925)</a>',
         '<a target="_blank" href="https://en.wikipedia.org/wiki/Augustus_Saint-Gaudens">Augustus Saint-Gaudens (1848-1907)</a> in 1880',
         'Cast Bronze',
         '',
         'Portrait cast on bronze Medallion (circular) Inscribed: "My Friend John Sargent. Paris IVLX M.D.CC.LLXX"',
         '',
         '<a target="_blank" href="https://drive.google.com/file/d/1NHQ9LaVEm2rdY0YeGQXb0MYtgGsw45LE/view">oid0001</a>'
      ]
'''
