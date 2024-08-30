import string
import easyocr


reader = easyocr.Reader(['en'],gpu=False)


dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}




def get_bus(number_plate,bus_track_ids):
    
    x1,y1,x2,y2,score,class_id=number_plate
    
    isFounded=False
    for j in range(len(bus_track_ids)):
            bus_x1,bus_y1,bus_x2,bus_y2,bus_id=bus_track_ids[j]
            if x1>bus_x1 and y1>bus_y1 and x2<bus_x2 and y2 < bus_y2:
                bus_index=j
                isFounded=True
                break
                
    if isFounded:
        return bus_track_ids[bus_index]
    return -1,-1,-1,-1,-1

def is_compiled_format(text):
    if len(text)!=9:
        return False
    if  (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and\
        (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys())and\
        (text[2] in ['0','1','2','3','4','5','6','7','8','9'] or text[2] in dict_char_to_int.keys()) and\
        (text[3] in ['0','1','2','3','4','5','6','7','8','9'] or text[3] in dict_char_to_int.keys()) and\
        (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys())and\
        (text[5] in ['0','1','2','3','4','5','6','7','8','9'] or text[2] in dict_char_to_int.keys()) and\
        (text[6] in ['0','1','2','3','4','5','6','7','8','9'] or text[3] in dict_char_to_int.keys()) and\
        (text[7] in ['0','1','2','3','4','5','6','7','8','9'] or text[2] in dict_char_to_int.keys()) and\
        (text[8] in ['0','1','2','3','4','5','6','7','8','9'] or text[3] in dict_char_to_int.keys()):
            return True
    else:
        return False
        
                
def format_text(text):
    number_plate=''
    mapping={0:dict_int_to_char,1:dict_int_to_char,2:dict_char_to_int,3:dict_char_to_int,4:dict_int_to_char,
             5:dict_char_to_int,6:dict_char_to_int,7:dict_char_to_int,8:dict_char_to_int}
    
    for i in [0,1,2,3,4,5,6,7,8]:
        if text[i] in mapping[i].keys():
            number_plate+=mapping[i][text[i]]
        else:
            number_plate+=text[i]
    return number_plate 


def read_number_plate(number_plate_crop_img):
    detections=reader.readtext(number_plate_crop_img)
    for detection in detections:
        bbox,text,score=detection
        text=text.upper().replace(' ','')
        text=text.replace('.','')
        if is_compiled_format(text):
            return format_text(text),score
    return None,None
    
    
# def write_csv(results, output_path):
#     """
#     Write the results to a CSV file.

#     Args:
#         results (dict): Dictionary containing the results.
#         output_path (str): Path to the output CSV file.
#     """
#     with open(output_path, 'w') as f:
#         f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'bus_id', 'bus_bbox',
#                                                 'number_plate_bbox', 'number_plate_bbox_score', 'number_plate_text',
#                                                 'number_plate_score'))

#         for frame_nmr in results.keys():
#             for car_id in results[frame_nmr].keys():
#                 print(results[frame_nmr][car_id])
#                 if 'bus' in results[frame_nmr][car_id].keys() and \
#                    'number plate' in results[frame_nmr][car_id].keys() and \
#                    'text' in results[frame_nmr][car_id]['number plate'].keys():
#                     f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
#                                                             car_id,
#                                                             '[{} {} {} {}]'.format(
#                                                                 results[frame_nmr][car_id]['bus']['bbox'][0],
#                                                                 results[frame_nmr][car_id]['bus']['bbox'][1],
#                                                                 results[frame_nmr][car_id]['bus']['bbox'][2],
#                                                                 results[frame_nmr][car_id]['bus']['bbox'][3]),
#                                                             '[{} {} {} {}]'.format(
#                                                                 results[frame_nmr][car_id]['number plate']['bbox'][0],
#                                                                 results[frame_nmr][car_id]['number plate']['bbox'][1],
#                                                                 results[frame_nmr][car_id]['number plate']['bbox'][2],
#                                                                 results[frame_nmr][car_id]['number plate']['bbox'][3]),
#                                                             results[frame_nmr][car_id]['number plate']['bbox_score'],
#                                                             results[frame_nmr][car_id]['number plate']['text'],
#                                                             results[frame_nmr][car_id]['number plate']['number_plate_score'])
#                             )
#         f.close()