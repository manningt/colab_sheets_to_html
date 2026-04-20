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
test_object_list = [{"oid0028_C":[None,None,None]}, {"oid1300":[None,None,None]}]

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

def get_image_url(object_list, images_folder):
   #Drive foldername convention: 0000-FineArts, 0500-Furniture, 0700-Textiles, etc
   oid_with_no_image_files_list = []
   oid_with_invalid_file_id_list = []
   for index, obj in enumerate(object_list):
      # how much more efficient is it to have the xxxx-category foldername in the search?
      # search_path = f'{image_dir}/Object-Photos/0000-Fine_Art/oid0028_C*.*'
      # search_path = f'{image_dir}/Object-Photos/*/{oid}*.*'
      oid = next(iter(obj))  #get the key, which is the oid
      search_pattern = os.path.join(images_folder, f"*/{oid}*.*")
      files = glob.glob(search_pattern, recursive=True)
      img_filename = None
      if len(files) == 0:
         oid_with_no_image_files_list.append(oid)
         print(f"No files found for {obj}")
      elif len(files) == 1:
         img_filename = files[0]
      else:
         non_detail_files = []
         for f in files:
            if "detail" not in f:
               non_detail_files.append(f)
         img_filename = non_detail_files[0]
         if len(non_detail_files) > 1:
            print(f"Multiple images for {obj}")
      if img_filename:
         fid = xattr.getxattr(img_filename, "user.drive.id").decode('utf-8') #linux
         # fid = subprocess.getoutput(f"xattr -p 'user.drive.id' '{img_filename}'") #macos
         if len(fid) == 33:
            object_list[index][oid][OBJ_ARRAY_IDX_E.THUMBNAIL.value] = f'https://drive.google.com/a/sargenthouse.org/thumbnail?id={fid}'
         else:
            print(f"Invalid fid: {fid} for {oid}")
            oid_with_invalid_file_id_list.append(oid)

   return oid_with_no_image_files_list, oid_with_invalid_file_id_list

def make_obj_list(inventory_rows, col_enum, locations_dict, entries=None):
   unrecognized_locations_dict = {}
   object_list = []
   if entries is None:
      entries = len(inventory_rows)
   entries += 1 #skip first row
   for row in inventory_rows[1:entries]:
      alt = f'{row[col_enum.ID.value]} {row[col_enum.col_names.Original_Description.value]}'
      object_list.append({row[col_enum.ID.value]: [None,alt,None]})
      # append object to locations_dict
      if row[col_enum.Location.value] in locations_dict:
         locations_dict[row[col_enum.Location.value]].append(row[col_enum.ID.value])
      else:
         print(f"{row[col_enum.Location.value]=} not in locations_dict for {row[col_enum.ID.value]}")
         if row[col_enum.Location.value] in unrecognized_locations_dict:
            unrecognized_locations_dict[row[col_enum.Location.value]].append(row[col_enum.ID.value])
         else:
            unrecognized_locations_dict[row[col_enum.Location.value]] = [(row[col_enum.ID.value])]
   return object_list, unrecognized_locations_dict

def create_html_files(page_name_list, obj_per_page_dict, output_dir_path):
  # create a list of docs, one for each list item:
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
         div(_class ="page_title").add(page_name)
         for obj in obj_per_page_dict[page_name]:
            div(img(src=obj[OBJ_ARRAY_IDX_E.THUMBNAIL.value], alt=obj[OBJ_ARRAY_IDX_E.ALT.value], \
               style="width:100%", _class='column'))
      html_page_list.append(doc)

   if not os.path.exists(output_dir_path):
      os.makedirs(output_dir_path)
   os.chdir(output_dir_path)
   # write out each page
   for idx, page_name in enumerate(page_name_list):
      out_filename = page_name.replace(" ", "_") + '.html'
      with open(out_filename, 'w') as f:
         f.write(html_page_list[idx].render())
