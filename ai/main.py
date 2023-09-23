from ultralytics import YOLO
import cv2
import csv
import json
import math as m
import sys
import os

def ms_round(ms):
    return m.ceil(ms / 1000)

def get_file_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def tracking(video_path):
    try:
        model = YOLO('./rzd-cam-ai.pt')

        cap = cv2.VideoCapture(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)

        classes = [0, 1]

        ret = True

        count = 0

        output = {
            "filename": get_file_name(video_path),
            "frames": []
        }

        while ret:
            ret, frame = cap.read()
            count += 1
            if count % fps != 0:
                continue

            result = model.track(frame, persist=True, classes=classes, device=0)

            # frame_ = result[0].plot()

            object = json.loads(result[0].tojson())
            object.append({"time": ms_round(cap.get(cv2.CAP_PROP_POS_MSEC))})
            output.get("frames").append(object)

            # cv2.imshow('frame', frame_)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        json_path = "output/" + output.get("filename") + "_all_activities.json"
        with open(json_path, 'w') as f:
            json.dump(output, f)

        return json_path
    except Exception as error:
        print(error)
        return False


def analyze(json_path):
    try:
        count_phone = 0
        count_no_people = 0

        with open(json_path, "r") as read_file:
            output = json.load(read_file)

            output2 = {
                "filename": output.get("filename"),
                "frames": []
            }

            has_start = False
            for i, frames in enumerate(output.get("frames")):
                has_person = False
                has_phone = False

                print(count_phone, count_no_people)

                for frame in frames:
                    print(count_phone, count_no_people)
                    print(frame)

                    if frame.get("class") == 1 and not has_phone:
                        count_phone += 1
                        has_phone = True
                    elif not has_phone and frame.get("class") != 0:
                        count_phone = 0
                    if frame.get("class") == 0 and frame.get("confidence") >= 0.8:
                        has_person = True
                        count_no_people = 0
                if len(frames) == 0 or not has_person:
                    count_no_people += 1

                if i == 0 and (count_no_people != 0 or count_phone != 0):
                    types = []
                    if count_phone != 0:
                        types.append("phone")
                    if count_no_people != 0:
                        types.append("no people")
                    frames.append({"type": types})
                    output2.get("frames").append(frames)
                    has_start = True

                if (count_phone == 1 or count_no_people == 1) and not has_start:
                    types = []
                    if count_phone != 0:
                        types.append("phone")
                    if count_no_people != 0:
                        types.append("no people")
                    frames.append({"type": types})
                    output2.get("frames").append(frames)
                    has_start = True

                elif count_phone == 0 and count_no_people == 0 and has_start:
                    output2.get("frames").append(frames)
                    has_start = False

            if has_start:
                output2.get("frames").append(output.get("frames")[len(output.get("frames")) - 1])
            json_path = "output/" + output.get("filename") + "_bad_activities.json"
            with open(json_path, 'w') as f:
                json.dump(output2, f)
        return json_path
    except Exception as error:
        print(error)
        return False


def format_seconds(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def create_csv(jsons_path, output_path):
    try:
        rows = ["filename", 'cases_count', "timestamps"]

        with open(output_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(rows)

            for json_path in jsons_path:
                with open(json_path, "r") as read_file:
                    output = json.load(read_file)
                    output_frames = output.get("frames")
                    count = len(output_frames) // 2
                    times = []
                    for i in range(0, len(output_frames), 2):
                        times.append(format_seconds(output_frames[i][len(output_frames[i]) - 2].get("time")))
                    writer.writerow([output.get("filename"), count, times])
        return True
    except Exception as error:
        print(error)
        return False

def image_detect(image_path, time):
    try:
        model = YOLO('./rzd-cam-ai.pt')
        frame = cv2.imread(image_path)
        classes = [0, 1]
        result = model.track(frame, persist=True, classes=classes, device=0)
        frame_ = result[0].plot()
        cv2.imwrite('output/11111.jpg', frame_)
        object = json.loads(result[0].tojson())
        object.append({"time": time})
        output = object
        json_path = "output/" + get_file_name(image_path) + ".json"
        with open(json_path, 'w') as f:
            json.dump(output, f)
        return True
    except Exception as error:
        print(error)
        return False

def recording():
    cap = cv2.VideoCapture(0)
    while True:
        model = YOLO('./rzd-cam-ai.pt')
        ret, frame = cap.read()
        result = model.track(frame, persist=True, device=0)
        frame_ = result[0].plot()
        cv2.imshow('frame', frame_)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def main(argv):
    if argv[0] == "start":
        recording()
    elif argv[0].endswith(".mp4"):
        json_path = tracking(argv[0])
        if json_path != False:
            bad_json_path = analyze(json_path)
            if bad_json_path != False:
                create_csv([bad_json_path], "output/" + get_file_name(argv[0]) + ".csv")
    else:
        image_detect(argv[0], 1)
if __name__ == "__main__":
   main(sys.argv[1:])