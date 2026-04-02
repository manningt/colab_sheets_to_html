def make_room_names_list(spreadsheet):
   worksheet = spreadsheet.worksheet('Locations')
   rows = worksheet.get_all_values()
   room_names_list = []
   # 'Room Name' is the first column (index 0) and data starts from the third row (index 2)
   for row in rows[2:]:
      room_names_list.append(row[0])
   return room_names_list

