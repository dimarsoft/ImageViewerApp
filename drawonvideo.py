from pathlib import Path
import cv2
from enum import Enum
import argparse

import numpy as np


class Labels(Enum):
    human = 0
    helmet = 1
    uniform = 2


# турникет, потом вынести в настройку
line_a = -0.2
line_b = 0.68

# цвета обектов

label_colors = {
    Labels.human: (255, 255, 0),
    Labels.helmet: (255, 0, 255),
    Labels.uniform: (255, 255, 255)
}


# получить координату y для х
def get_y(x):
    return line_a * x + line_b


# проверка человека: выше/ниже турникета
def test_human(label):
    y_turniket = get_y(label.x)

    if y_turniket > label.y:
        label.above = True
    else:
        label.above = False


# разбор строки: получаем тип и координаты bb
def parse_row(info):
    box = info.split(" ")
    if np.char.isnumeric(box[0].replace('\n', '')):
        return DetectedLabel(Labels(int(box[0])), float(box[1]), float(box[2]), float(box[3]), float(box[4]))

    return None


# разбор всех строк в файле

def read_labels(labels_file):
    labels = []
    try:
        with open(labels_file, 'r') as handle:
            box_info = handle.readlines()
            for txt in box_info:
                lab = parse_row(txt)
                if lab is not None:
                    if lab.label is Labels.human:
                        test_human(lab)
                    labels.append(lab)
            return labels
    except FileNotFoundError as e:
        print(labels_file, e)
        return labels
    return labels


class DetectedLabel:
    def __init__(self, label, x, y, width, height):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.above = None

    def label_str(self):
        if self.label is Labels.human:
            return "human"
        if self.label is Labels.uniform:
            return "uniform"
        if self.label is Labels.helmet:
            return "helmet"
        return ""


class DetectedTrackLabel(DetectedLabel):
    def __init__(self, label, x, y, width, height, track_id, frame):
        super(DetectedTrackLabel, self).__init__(label, x, y, width, height)

        self.track_id = track_id
        self.frame = frame

    def get_caption(self):
        return f"{self.track_id}: {self.label_str()}"


class FrameInfo:
    def __init__(self, labels):
        self.labels = labels


def draw_info(frame, number, frame_w, frame_h, labels_path, suffix):
    path_to_file = Path(labels_path) / f"{suffix}_{number}.txt"

    # турникет рисуем один раз

    y1 = int(get_y(0) * frame_h)
    y2 = int(get_y(1) * frame_h)
    cv2.line(frame, (0, y1), (frame_w, y2), (0, 0, 255), 1)

    if path_to_file.exists():
        labels = read_labels(path_to_file)

        humans = 0

        for lab in labels:
            hh = int(lab.height * frame_h)
            ww = int(lab.width * frame_w)

            x = int(lab.x * frame_w - ww / 2)
            y = int(lab.y * frame_h - hh / 2)

            # рамка объекта

            cv2.rectangle(frame, (x, y), (x + ww, y + hh), label_colors[lab.label], 1)

            # если человек, то рисуем центр масс
            if lab.label is Labels.human:
                x = int(x + ww / 2)
                y = int(y + hh / 2)

                if lab.above is True:
                    color = (0, 0, 255)
                else:
                    color = (0, 255, 0)

                cv2.circle(frame, (x, y), 10, color, -1)

                humans += 1

        if humans > 0:
            cv2.putText(frame, f"humans: {humans} ", (0, 40), 0, 1, (255, 255, 255), 2, cv2.LINE_AA)

    pass


def draw_on_frame(frame, draw_rect, frame_w, frame_h, frame_info: FrameInfo):
    # турникет рисуем один раз

    y1 = int(get_y(0) * frame_h)
    y2 = int(get_y(1) * frame_h)
    cv2.line(frame, (0, y1), (frame_w, y2), (0, 0, 255), 1)

    if frame_info.labels is not None:
        labels = frame_info.labels

        humans = 0

        for lab in labels:
            hh = int(lab.height * frame_h)
            ww = int(lab.width * frame_w)

            x = int(lab.x * frame_w - ww / 2)
            y = int(lab.y * frame_h - hh / 2)

            # рамка объекта

            if draw_rect:
                cv2.rectangle(frame, (x, y), (x + ww, y + hh), label_colors[lab.label], 1)

            # если человек, то рисуем центр масс
            if lab.label is Labels.human:
                x = int(x + ww / 2)
                y = int(y + hh / 2)

                if lab.above is True:
                    color = (0, 0, 255)
                else:
                    color = (0, 255, 0)

                cv2.circle(frame, (x, y), 10, color, -1)

                humans += 1

        if humans > 0:
            cv2.putText(frame, f"humans: {humans} ", (0, 40), 0, 1, (255, 255, 255), 2, cv2.LINE_AA)


def draw_track_on_frame(frame, draw_rect, frame_w, frame_h, frame_info: DetectedTrackLabel):
    # турникет рисуем один раз

    y1 = int(get_y(0) * frame_h)
    y2 = int(get_y(1) * frame_h)
    cv2.line(frame, (0, y1), (frame_w, y2), (0, 0, 255), 1)

    # if frame_info.labels is not None:
    lab = frame_info

    humans = 0

    hh = int(lab.height * frame_h)
    ww = int(lab.width * frame_w)

    x = int(lab.x * frame_w - ww / 2)
    y = int(lab.y * frame_h - hh / 2)

    cv2.putText(frame, frame_info.get_caption(), (x, y), 0, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # рамка объекта

    if draw_rect:
        cv2.rectangle(frame, (x, y), (x + ww, y + hh), label_colors[lab.label], 1)

    # если человек, то рисуем центр масс
    if lab.label is Labels.human:
        x = int(x + ww / 2)
        y = int(y + hh / 2)

        if lab.above is True:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        cv2.circle(frame, (x, y), 10, color, -1)


def read_all_labels(labels_path, suffix, frames):
    frames_info = []

    for number in range(frames):
        path_to_file = Path(labels_path) / f"{suffix}_{number}.txt"
        labels = None
        if path_to_file.exists():
            labels = read_labels(path_to_file)

        frames_info.append(FrameInfo(labels))
    return frames_info


# разбор строки: получаем тип и координаты bb
def parse_track_row(info, w, h):
    box = info.split(" ")
    if np.char.isnumeric(box[0].replace('\n', '')):
        width = float(box[4]) / w
        height = float(box[5]) / h

        x_center = float(box[2]) / w + width / 2
        y_center = float(box[3]) / h + height / 2

        return DetectedTrackLabel(Labels(int(box[10])),
                                  x_center, y_center, width, height,
                                  int(box[1]), int(box[0]))

    return None


def parse_track_txt(labels_path, suffix, w, h):
    labels = []
    path_to_track_txt = Path(labels_path) / f"{suffix}.txt"
    try:
        with open(path_to_track_txt, 'r') as handle:
            box_info = handle.readlines()
            for txt in box_info:
                lab = parse_track_row(txt, w, h)
                if lab is not None:
                    if lab.label is Labels.human:
                        test_human(lab)
                    labels.append(lab)
            return labels
    except FileNotFoundError as e:
        print(path_to_track_txt, e)
    return labels


def draw_track_on_video(src_video_path, output_video_path, labels_path):
    path_v = Path(src_video_path)
    suffix = path_v.stem

    # reading the input
    input_video = cv2.VideoCapture(src_video_path)

    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    # ширина
    w = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # высота
    h = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # количесто кадров в видео
    frames_in_video = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"input = {src_video_path}, w = {w}, h = {h}, fps = {fps}, frames_in_video = {frames_in_video}")

    tracks_info = parse_track_txt(labels_path, suffix, w, h)

    output_video = cv2.VideoWriter(
        output_video_path, cv2.VideoWriter_fourcc(*'mp4v'),
        fps, (w, h))

    image_frames = []

    # считываем все фреймы из видео
    for i in range(frames_in_video):
        ret, frame = input_video.read()
        image_frames.append(frame)

    # наложение трека

    for track in tracks_info:
        draw_track_on_frame(image_frames[track.frame], True, w, h, track)

    # запись в выходной файл
    for i in range(frames_in_video):
        output_video.write(image_frames[i])

    output_video.release()
    input_video.release()


def draw_on_video(src_video_path, output_video_path, labels_path):
    path_v = Path(src_video_path)
    suffix = path_v.stem

    # reading the input
    input_video = cv2.VideoCapture(src_video_path)

    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    # ширина
    w = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # высота
    h = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # количесто кадров в видео
    frames_in_video = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"input = {src_video_path}, w = {w}, h = {h}, fps = {fps}, frames_in_video = {frames_in_video}")

    frames_info = read_all_labels(labels_path, suffix, frames_in_video)

    output_video = cv2.VideoWriter(
        output_video_path, cv2.VideoWriter_fourcc(*'mp4v'),
        fps, (w * 2, h))

    frame_id = 0

    while True:
        ret, frame = input_video.read()
        if ret:

            draw_on_frame(frame, True, w, h, frames_info[frame_id])

            output_video.write(frame)
            # cv2.imshow("output", frame)

            print(f"frame processed = {frame_id}")

            frame_id += 1

            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
        else:
            break

    cv2.destroyAllWindows()
    output_video.release()
    input_video.release()


def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


def draw_on_second_video(src_video_path, output_video_path, labels_path):
    path_v = Path(src_video_path)
    suffix = path_v.stem

    # reading the input
    input_video = cv2.VideoCapture(src_video_path)

    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    # ширина
    w = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    # высота
    h = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # количество кадров в видео
    frames_in_video = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"input = {src_video_path}, w = {w}, h = {h}, fps = {fps}, frames_in_video = {frames_in_video}")

    frames_info = read_all_labels(labels_path, suffix, frames_in_video)

    output_video = cv2.VideoWriter(
        output_video_path, cv2.VideoWriter_fourcc(*'mp4v'),
        fps, (w * 2, h))

    frame_id = 0

    new_frame = create_blank(w * 2, h)
    frame_copy = create_blank(w, h)

    black_color = (0, 0, 0)

    while True:
        ret, frame = input_video.read()
        if ret:

            frame_copy[:] = black_color

            draw_on_frame(frame_copy, False, w, h, frames_info[frame_id])

            new_frame[0:int(h), 0:int(w)] = frame
            new_frame[0:int(h), int(w):int(w * 2)] = frame_copy

            output_video.write(new_frame)
            # cv2.imshow("output", frame)

            print(f"frame processed = {frame_id}")

            frame_id += 1

            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
        else:
            break

    cv2.destroyAllWindows()
    output_video.release()
    input_video.release()


def draw_folder(input_folder, output_folder, label_folder):
    videos_path = Path(input_folder)

    # iterate directory
    for entry in videos_path.iterdir():
        # check if it is a file
        if entry.is_file() and entry.suffix == ".mp4":
            # print(entry.name, " ", entry.suffix)

            videos_out_path = Path(output_folder) / f"{entry.stem}_post.mp4"

            print("src = ", entry.name, ", output = ", str(videos_out_path))

            draw_on_video(str(entry), str(videos_out_path), label_folder)


def create_video(input_folder, output_folder, label_folder):
    input_path = Path(input_folder)

    if input_path.is_dir():
        draw_folder(input_folder, output_folder, label_folder)
    else:
        draw_on_second_video(input_folder, output_folder, label_folder)


# пример запуска в питоне
def run_example():
    src_video_path = "d:\\AI\\2023\\corridors\\dataset-v1.1\\test\\11.mp4"
    output_video_path = "D:\\AI\\2023\\11_out3.mp4"
    labels_path = "D:\\AI\\2023\\Track\\"

    draw_track_on_video(src_video_path, output_video_path, labels_path)


run_example()

# python.exe drawvideo.py --input "путь к входному видео" --output "результирующее видео" --labels "путь к
# распознанной информации"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='', help='path to input video')
    parser.add_argument('--output', type=str, default='', help='path to input new video')
    parser.add_argument('--labels', type=str, default='', help='path to labels folder')

    opt = parser.parse_args()

    # create_video(opt.input, opt.output, opt.labels)
