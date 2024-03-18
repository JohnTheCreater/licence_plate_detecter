import ast

import cv2
import numpy as np
import pandas as pd


def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)  #-- top-left
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)  #-- bottom-left
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)  #-- top-right
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)  #-- bottom-right
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


results = pd.read_csv('./test_interpolated.csv')

# load video
video_path = '/home/john/road_track/Copy of VID_20240312_124102.mp4'
cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the codec
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('./out1.mp4', fourcc, fps, (width, height))

license_plate = {}
for bus_id in np.unique(results['bus_id']):
    max_ = np.amax(results[results['bus_id'] == bus_id]['number_plate_score'])
    license_plate[bus_id] = {'license_crop': None,
                             'license_plate_number': results[(results['bus_id'] == bus_id) &
                                                             (results['number_plate_score'] == max_)]['number_plate_text'].iloc[0]}
    cap.set(cv2.CAP_PROP_POS_FRAMES, results[(results['bus_id'] == bus_id) &
                                             (results['number_plate_score'] == max_)]['frame_nmr'].iloc[0])
    ret, frame = cap.read()

    x1, y1, x2, y2 = ast.literal_eval(results[(results['bus_id'] == bus_id) &
                                              (results['number_plate_score'] == max_)]['number_plate_bbox'].iloc[0].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))

    license_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
    license_crop = cv2.resize(license_crop, (int((x2 - x1) * 400 / (y2 - y1)), 400))

    license_plate[bus_id]['license_crop'] = license_crop



frame_nmr = -1

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# read frames
ret = True
while ret:
    ret, frame = cap.read()
    frame_nmr += 1
    if ret:
        df_ = results[results['frame_nmr'] == frame_nmr]
        for row_indx in  range(len(df_)):
            # draw bus
            bus_x1, bus_y1, bus_x2, bus_y2 = ast.literal_eval(df_.iloc[row_indx]['bus_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
            draw_border(frame, (int(bus_x1), int(bus_y1)), (int(bus_x2), int(bus_y2)), (0, 255, 0), 25,
                        line_length_x=200, line_length_y=200)

            # draw license plate
            x1, y1, x2, y2 = ast.literal_eval(df_.iloc[row_indx]['number_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 12)

            # crop license plate
            license_crop = license_plate[df_.iloc[row_indx]['bus_id']]['license_crop']

            H, W, _ = license_crop.shape

            try:
                frame[int(bus_y1) - H - 100:int(bus_y1) - 100,
                      int((bus_x2 + bus_x1 - W) / 2):int((bus_x2 + bus_x1 + W) / 2), :] = license_crop

                frame[int(bus_y1) - H - 400:int(bus_y1) - H - 100,
                      int((bus_x2 + bus_x1 - W) / 2):int((bus_x2 + bus_x1 + W) / 2), :] = (255, 255, 255)

                (text_width, text_height), _ = cv2.getTextSize(
                    license_plate[df_.iloc[row_indx]['bus_id']]['license_plate_number'],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    4.3,
                    17)
                
                print(license_plate[df_.iloc[row_indx]['bus_id']]['license_plate_number'])
                cv2.putText(frame,
                            license_plate[df_.iloc[row_indx]['bus_id']]['license_plate_number'],
                            (int((bus_x2 + bus_x1 - text_width) / 2), int(bus_y1 - H - 250 + (text_height / 2))),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2.0,
                            (0, 0, 0),
                            17)

            except:
                pass

        out.write(frame)
        frame = cv2.resize(frame, (1280, 720))

        # cv2.imshow('frame', frame)
        # cv2.waitKey(0)

out.release()
cap.release()
