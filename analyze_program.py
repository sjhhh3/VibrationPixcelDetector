import csv
from datetime import datetime
from collections import OrderedDict

from cv2 import cv2
import matplotlib.pyplot as plt

VIDEO_NAME = None
TRACKER_TYPES = OrderedDict({
    'BOOSTING': cv2.TrackerBoosting_create(),
    'MIL': cv2.TrackerMIL_create(),
    'KCF': cv2.TrackerKCF_create(),
    'TLD': cv2.TrackerTLD_create(),
    'MEDIANFLOW': cv2.TrackerMedianFlow_create(),
    'MOSSE': cv2.TrackerMOSSE_create(),
    'CSRT': cv2.TrackerCSRT_create(),
    })
POI_TYPES = {
    '0': "Central Point",
    '1': "Left-Top Point",
    '2': "Right-Top Point",
    '3': "Right-Bottom Point",
    '4': "Left-Bottom Point",
    }
GRAPH_TYPES = {'0': "Vertical", '1': "Horizontal"}

class Tracker:
    """
    Tracker Selection
    """
    def __init__(self, type_number):
        self.tracker_types = list(TRACKER_TYPES.keys())
        assert 0 <= type_number < len(self.tracker_types)
        self.tracker_types_funcs = list(TRACKER_TYPES.values())
        self.number = type_number
        self.tracker_name = self.tracker_types[type_number]
    
    def get_tracker(self):
        return self.tracker_types_funcs[self.number]


class POI:
    """
    Point of Interest Selection
    """
    def __init__(self, point_type_index, graph_index):
        self.point_types = POI_TYPES
        assert point_type_index in self.point_types
        self.tracker_name = self.point_types[point_type_index]
        self.point_index = int(point_type_index)
        self.graph_index = graph_index
        self.points = []

    def store_point(self, points):
        self.points.append(points[self.point_index])

    def create_plot(self):
        """
        Generate Vertical (for "0") or Horizontal (for "1")
        """
        p = Plot(self.tracker_name, self.points)
        if self.graph_index is None or self.graph_index == "0":
            p.generate_vertical()
        else:
            p.generate_horizontal()

    def export_data(self):
        """
        CSV file name = Video Name + DateTime
        """
        name = VIDEO_NAME.split('/')[-1] + '-' + datetime.today().strftime("%Y%m%d%H%M%S")
        with open(f'{name}.csv', 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            for point in self.points:
                wr.writerow(point)


class Plot:
    def __init__(self, name, points):
        self.tracker_name = name
        self.points = points

    def generate_vertical(self):
        base = self.points[0][1]
        points = [p[1]-base for p in self.points]
        self.generate_plot(points, self.tracker_name+" Vertical Movement ")

    def generate_horizontal(self):
        base = self.points[0][0]
        points = [p[0]-base for p in self.points]
        self.generate_plot(points, self.tracker_name+" Horizontal Movement ")

    def max_annotate(self, x, y, plt):
        """
        Max and min annotation, in the left side of the graph
        """
        ymax = max(y)
        ymin = min(y)
        text = "Highest POI Motivation={:.1f} Pixel".format(ymax)
        text2 = "Lowest POI Motivation={:.1f} Pixel".format(ymin)
        plt.text(1, ymax, text, ha='left', rotation=0, wrap=True)
        plt.text(1, ymin, text2, ha='left', rotation=0, wrap=True)

    def generate_plot(self, points, name):
        y = points
        x = range(len(y))
        plt.plot(x, y)
        plt.title(name + 'Graph')
        plt.xlabel('Frame')
        plt.ylabel('Relative Pixel Movement')
        self.max_annotate(x, y, plt)
        plt.show()


class VideoInit:
    def __init__(self, video, tracker_number):
        """
        Capture the first frame as a sample to select the Region of Interest (ROI).
        Obtain the video resolution size, fps.
        Initialize the select_roi() to select the ROI.
        """
        global VIDEO_NAME
        VIDEO_NAME = video
        self.bbox = None
        self.points = None
        self.cap = cv2.VideoCapture(video)
        _, self.frame = self.cap.read()
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.select_roi()
        self.tracker = Tracker(tracker_number)
        self.tracker_instance = self.tracker.get_tracker()
        self.tracker_instance.init(self.frame, self.bbox)

    def select_roi(self):
        """
        Select ROI, close window after press 'Enter'.
        self.bbox stores the ROI.
        """
        select_roi_window_name = "SelectROI, User Mouse To Drag, Press Enter to Analyze"
        cv2.namedWindow(select_roi_window_name, cv2.WINDOW_NORMAL)
        self.bbox = cv2.selectROI(select_roi_window_name, self.frame, False)
        cv2.destroyAllWindows()

    def run_analyze(self, point_index, graph_index):
        """
        self.points stores the user selection of POI Type, Graph Type.
        p1: Left-Top, p2: Right-Bottom, p3: Right-Top, p4: Left-Bottom, p5: Center
        Draw ROI Rectangle, Diagonal Lines and Center Point to every frame
        """
        run_analyze_window_name = "Analyzing, ESC to Exit"
        cv2.namedWindow(run_analyze_window_name, cv2.WINDOW_NORMAL)
        self.points = POI(point_index, graph_index)

        while True:
            playing, self.frame = self.cap.read()
            if not playing:
                break
            ok, self.bbox = self.tracker_instance.update(self.frame)
            if ok:
                top, bottom, left, right = (
                    self.bbox[1],
                    self.bbox[1] + self.bbox[3],
                    self.bbox[0],
                    self.bbox[0] + self.bbox[2],
                    )
                p1 = (int(left), int(top))
                p2 = (int(right), int(bottom))
                p3 = (int(right), int(top))
                p4 = (int(left), int(bottom))
                p5 = (int((left + right) / 2), int((top + bottom) / 2))
                self.points.store_point([p1, p2, p3, p4, p5])

                cv2.rectangle(self.frame, p1, p2, (255, 0, 0), 2, 1)
                cv2.line(self.frame, p1, p2, (255, 0, 0), 2, 1)
                cv2.line(self.frame, p3, p4, (255, 0, 0), 2, 1)
                cv2.circle(self.frame, p5, 6, (0, 0, 255), -1)
            else:
                cv2.putText(self.frame, "Tracking failure detected",(self.width//2, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            cv2.putText(self.frame, self.tracker.tracker_name + " Tracker",(self.width//2, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (50, 170, 50), 3)
            cv2.putText(self.frame, "FPS : " + str(int(self.fps)),(self.width//2, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (50, 170, 50), 3)
            cv2.putText(self.frame, "Frame : " + str(self.cap.get(cv2.CAP_PROP_POS_FRAMES)),(self.width//2, 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (50, 170, 50), 3)

            cv2.imshow(run_analyze_window_name, self.frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.points.create_plot()


if __name__ == '__main__':
    pass


