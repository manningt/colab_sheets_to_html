'''
These functions are intended to be called from a colab project.
The spreadsheet object is a google sheet.
'''
import enum

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

