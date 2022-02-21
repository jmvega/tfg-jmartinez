# Test face mesh mediapipe with three threads

from threading import Thread
import sys
sys.path.append('../..')
from piVideoStream.PiVideoStream import PiVideoStream
from graphicInterface.GraphicInterface import GraphicInterface
from faceMesh.FaceMesh import FaceMesh
import cv2
import time
import mediapipe as mp
import argparse

# Variables to calculate and show FPS
counter, fps = 0, 0
fps_avg_frame_count = 10
text_location = (20, 24)
text_color = (0, 0, 255)  # red
font_size = 1
font_thickness = 1
start_time = time.time()

# Init time of program
init_time = time.time()

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--savefps',
                    action='store_true',
                    default=False, required=False,
                    help='Activa el guardado de fps en fichero .csv')
    parser.add_argument('--savebugs',
                    action='store_true',
                    default=False, required=False,
                    help='Activa el guardado de fallos del algoritmo en fichero .csv')
    parser.add_argument('--time',
                    type=int,
                    default=30, required=False,
                    help='Duracion en segundos del guardado de datos (int). Default: 30s')
    return parser.parse_args()

def savefps(fps, max_time, fps_file):
    fps_file.write('{:.1f}, {:.1f}\n'.format(fps, (time.time() - init_time)))
    if (time.time() - init_time) >= max_time:
        print("FPS save is over")
        return False
    return True

def savebugs(results, max_time, bugs_file):
    if results.multi_face_landmarks:
        bugs_file.write('0, {:.1f}\n'.format((time.time() - init_time)))
    else:
        bugs_file.write('1, {:.1f}\n'.format((time.time() - init_time)))
    if (time.time() - init_time) >= max_time:
            print("BUGS save is over")
            return False
    return True

def calculate_fps():
    global counter, fps, start_time
    counter += 1
    if counter % fps_avg_frame_count == 0:
        end_time = time.time()
        fps = fps_avg_frame_count / (end_time - start_time)
        start_time = time.time()
    return fps

if __name__ == '__main__':
    args = parse_arguments()
    if args.savefps:
        fps_file = open('../dataFPS/mediapipeTest/fps_mediapipe_test2.csv', 'w')
    if args.savebugs:
        bugs_file = open('../dataBugs/mediapipeTest/bugs_mediapipe_test2.csv', 'w')

    # Start video stream
    vs = PiVideoStream(resolution=(640, 480)).start()
    time.sleep(2.0)

    # Start graphic interface
    gi = GraphicInterface(vs.read()).start()

    # Init FaceMesh
    facemesh = FaceMesh()

    while(True):
        if vs.stopped or gi.stopped:
            break

        image = vs.read()
        image = cv2.flip(image, 0)

        facemesh.process(image)
        image = facemesh.draw(image)

        # Calculate the FPS
        fps = calculate_fps()

        # Save FPS
        if args.savefps:
            args.savefps = savefps(fps, args.time, fps_file)

        # Save bugs
        if args.savebugs:
            args.savebugs = savebugs(facemesh.get_results(), args.time, bugs_file)
            
        gi.put_image(image)
        fps_text = 'FPS = {:.1f}'.format(fps)
        gi.put_text(fps_text, text_location, text_color, font_size,
                    font_thickness)
        
    cv2.destroyAllWindows()
    vs.stop()
    gi.stop()
