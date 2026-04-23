'''
These functions are intended to be called from a colab project.
The spreadsheet object is a google sheet.
'''
import enum
import glob
import os
try:
   import xattr
except Exception as e: print(e)
try:
   from dominate import document as dom_doc
   from dominate.tags import *
except Exception as e: print(e)

from markdown import Markdown

PEOPLE_IMAGE_TYPE_LIST = ["portrait", "silhouette", "bust", "miniature", "bronze" ]
TITLED_ARTWORK_TYPE_LIST = ["painting", "watercolor", "lithograph", "sculpture", "coat-of-arms", \
                             "book", "etching", "drawing", "copy", "engraving"]
CATEGORY_TYPE_LIST = ["Fine_Art", "Silver", "Ceramics", "Glass", "Metals", "Furniture", \
                      "Textiles", "Accessories", "Adornments", "Document_Artifacts", \
                      "Needlework", "Books", "Not_In_Collection", "On_Loan"]

IGNORE_OBJECT_LIST = ["returned", "deaccessioned", "unassigned"]

class OBJ_ARRAY_IDX_E(enum.Enum): 
   THUMBNAIL = 0
   ALT = 1
   FIGCAPT = 2

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
   oid_with_no_image_files_list = []
   oid_with_invalid_file_id_list = []
   for oid in object_dict:
      # how much more efficient is it to have the xxxx-category foldername in the search?
      # search_path = f'{image_dir}/Object-Photos/0000-Fine_Art/oid0028_C*.*'
      # search_path = f'{image_dir}/Object-Photos/*/{oid}*.*'
      search_pattern = os.path.join(images_folder, f"*/{oid}*.*")
      files = glob.glob(search_pattern, recursive=True)
      img_filename = None
      if len(files) == 0:
         oid_with_no_image_files_list.append(oid)
         print(f"No files found for {oid}")
      elif len(files) == 1:
         img_filename = files[0]
      else:
         non_detail_files = []
         for f in files:
            if "detail" not in f:
               non_detail_files.append(f)
         img_filename = non_detail_files[0]
         if len(non_detail_files) > 1:
            print(f"Multiple images for {oid}")
      if img_filename:
         fid = xattr.getxattr(img_filename, "user.drive.id").decode('utf-8') #linux
         # fid = subprocess.getoutput(f"xattr -p 'user.drive.id' '{img_filename}'") #macos
         if len(fid) == 33:
            object_dict[oid][OBJ_ARRAY_IDX_E.THUMBNAIL.value] = f'https://drive.google.com/a/sargenthouse.org/thumbnail?id={fid}'
         else:
            print(f"Invalid fid: {fid} for {oid}")
            oid_with_invalid_file_id_list.append(oid)

   return oid_with_no_image_files_list, oid_with_invalid_file_id_list

def make_obj_dict(inventory_rows, col_enum, locations_dict, entries=None):
   #example object_dict = {"oid0028_C":[None,None,None], "oid1300":[None,None,None]}   # objject_dict = 
   # fills in 2nd parameter in array (alt)
   # as well as creating a list of objects per location and category
   unrecognized_locations_dict = {}
   object_dict = {}
   if entries is None:
      entries = len(inventory_rows)
   entries += 1 #skip first row
   for row_num, row in enumerate(inventory_rows[1:entries]):
      oid = row[col_enum.ID.value]
      if len(oid) != 7:
         print(f'skipping row {row_num} due to invalid OID={oid}')
         continue

      desc = row[col_enum.Original_Description.value]
      if len(desc) < 1:
         print(f'skipping row {row_num} due to no description')
         continue

      location = row[col_enum.Location.value]
      if location in locations_dict:
         locations_dict[location].append(oid)
      else:
         print(f"{location=} not in locations_dict for {oid}")
         if location in unrecognized_locations_dict:
            unrecognized_locations_dict[location].append(oid)
         else:
            unrecognized_locations_dict[location] = [oid]
         continue
      alt = f'{oid} {desc}'
      object_dict[oid] = [None, alt, None]
   return object_dict, unrecognized_locations_dict

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
         with div(page_name, _class ="page_title"):
            for oid in obj_per_page_dict[page_name]:
               img_src = object_dict[oid][OBJ_ARRAY_IDX_E.THUMBNAIL.value]
               img_alt = object_dict[oid][OBJ_ARRAY_IDX_E.ALT.value]
               with div(_class ="column"):
                  with figure():
                     img(src=img_src, alt=img_alt, style="width:100%")
                     with figcaption():
                        object_dict[oid][OBJ_ARRAY_IDX_E.FIGCAPT.value]
                        # a("Winthrop", href="https://en.wikipedia.org/wiki/Winthrop_Sargent")
                        # p(i("Judith's brother"))
         
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

   for row in inventory_rows[1:entries]:
      oid = row[col_enum.ID.value]
      if len(oid) != 7:
         continue
      if oid not in object_dict:
         print(f'Error: {oid} in inventory sheet but not in object_dict')
 
      obj_Object_Type = row[col_enum.Object_Type.value]
      # if obj_Object_Type not in PEOPLE_IMAGE_TYPE_LIST and obj_Object_Type not in TITLED_ARTWORK_TYPE_LIST:
      #    print(f'Skipping {oid}: invalid object type= {obj_Object_Type}')
      #    continue

      obj_Subj_style = row[col_enum.Subject_Style.value]

      obj_Desc = row[col_enum.Original_Description.value]
      obj_Creation_Date = row[col_enum.Creation_Date.value]
      obj_Origin = row[col_enum.Origin.value]
      obj_Medium = row[col_enum.Medium.value]
      obj_Dimensions = row[col_enum.Dimensions.value]
      obj_Provenance = row[col_enum.Provenance.value]
      obj_Donor = row[col_enum.Donor.value]
      obj_Date_of_Gift = row[col_enum.Date_of_Gift.value]

      print(f'{oid} {obj_Object_Type=} {obj_Subj_style=} ')

      figcapt = ''
      # test obj_Object_Type column - if in PEOPLE_IMAGE_TYPE_LIST check people_dict & get description, URL & relationship
      if obj_Object_Type in PEOPLE_IMAGE_TYPE_LIST:
         figcapt += obj_Subj_style

      # add title if object type is in TITLED_ARTWORK_TYPE_LIST:

      # add style & description

      # add creator

      # add creation date

      # add creator description

      # add subject (person) description

      # add narrative

      object_dict[OBJ_ARRAY_IDX_E.FIGCAPT.value] = figcapt
