'''
These functions are intended to be called from a colab project.
The spreadsheet object is a google sheet.
'''
import enum

PEOPLE_IMAGE_TYPE_LIST = ["portrait", "silhouette", "bust", "miniature", "bronze" ]
TITLED_ARTWORK_TYPE_LIST = ["painting", "watercolor", "lithograph", "sculpture", "coat-of-arms", \
                             "book", "etching", "drawing", "copy", "engraving"]
CATEGORY_TYPE_LIST = ["fine_arts", "silver", "ceramics", "glass", "metals", "furniture5", "furniture6", \
                      "textiles7", "textiles8", "textiles9", "accessories", "adornments", "doc_artifacts", \
                      "needlework", "books", "not_in_collection", "on_loan"]
IGNORE_OBJECT_LIST = ["returned", "deaccessioned", "unassigned"]

def make_room_names_list(spreadsheet):
   worksheet = spreadsheet.worksheet('Locations')
   rows = worksheet.get_all_values()
   room_names_list = []
   # 'Room Name' is the first column (index 0) and data starts from the third row (index 2)
   for row in rows[2:]:
      room_names_list.append(row[0].replace(" ", "_"))
   return room_names_list

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

