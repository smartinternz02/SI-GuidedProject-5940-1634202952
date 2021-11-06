# load the video and processthe video frame
import cv2
# used for vehicle tracking
import dlib
# esttimates the time
import time
# speed calculation
import math
# read and write contents to CSV FIle
import os
# to get the time stamp
from datetime import datetime
# load Haar acscade calssifier
carCascade = cv2.CascadeClassifier('myhaar.xml')
# capture the available Vide0
video = cv2.VideoCapture('cars.mp4')
#Initialise the hieght and width of  a frame
WIDTH = 600
HEIGHT = 600

    
#declare function to etimate the speed  by (Speed = Distance / Time) Formula   
def estimateSpeed(location1, location2):
    global speed
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    # ppm = location2[2] / carWidht
    ppm = 8.8
    d_meters = d_pixels / ppm
    #print("d_pixels=" + str(d_pixels), "d_meters=" + str(d_meters))
    #Here Time is Frames per second
    fps = 18
    speed = d_meters * fps * 3.6
    return speed


#Define the Function to track the Multiple Objects in Frame
def trackMultipleObjects():
    #Bounding Boxes for Cars Detected
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 0

    #Initialize Car Properties
    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000
    # Write output to video file
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH,HEIGHT))


    while True:
        #Enter Tracking log
        logFile = open('log.csv', mode="a")
        # set the file pointer to end of the file
        pos = logFile.seek(0, os.SEEK_END)
        # If this is a empty log file then write the column headings
        if pos == 0:
            logFile.write("Year,Month,Day,Time,Speed (in MPH)n")
        #Set Date and Time
        ts = datetime.now()
        newDate = ts.strftime("%m-%d-%y")
        year = ts.strftime("%Y")
        month = ts.strftime("%m")
        day = ts.strftime("%d")
        time1 = ts.strftime("%H:%M:%S")
        start_time = time.time()
        #Reading a Video
        rc, image = video.read()
        
        if type(image) == type(None):
            break
        #Resize readed image
        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        #Writing back Resized image 
        cv2.imwrite("abc.jpg",resultImage)
        
        frameCounter = frameCounter + 1
        
        carIDtoDelete = []
        
        #Keep track of Cars Quality by ID
        for carID in carTracker.keys():
            trackingQuality = carTracker[carID].update(image)
            print(trackingQuality)
            print(carID)

            #Delete less quality Tracked Cars
            if trackingQuality < 7:
                carIDtoDelete.append(carID)
        #Set Car IDs to Delete in List , Present and Previous Locations    
        for carID in carIDtoDelete:
            print ('Removing carID ' + str(carID) + ' from list of trackers.')
            print ('Removing carID ' + str(carID) + ' previous location.')
            print ('Removing carID ' + str(carID) + ' current location.')
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        # Load Multiple Objects in A Frame as Gray scale and call Multiscale Object Detection
        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            #Set x, y, Height, width of  Car Rectangle
            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
            
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                
                matchCarID = None
            
                #Track Position of car
                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()
                    
                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())
                    
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    #Check for Matched Car ID in frame
                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID
                #Create a new Tracker 
                if matchCarID is None:
                    print ('Creating new tracker ' + str(currentCarID))
                    
                    #Set Dlib tracker for  Holding Tracker values for Long time
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1
        
        cv2.line(resultImage,(0,480),(1280,480),(255,0,0),5)


        #Get positions of Matched Cars
        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()
                    
            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())
            
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
            
            # Set new Car locations
            carLocation2[carID] = [t_x, t_y, t_w, t_h]
        #Set end time from Current Time
        end_time = time.time()

        # Restart the start Time from Current time
        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)
        
        #cv2.putText(resultImage, 'FPS: ' + str(int(fps)), (620, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Select Car Location of Present and Previous Locations
        for i in carLocation1.keys():    
            if frameCounter % 1 == 0:
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]
        
                # print 'previous location: ' + str(carLocation1[i]) + ', current location: ' + str(carLocation2[i])
                carLocation1[i] = [x2, y2, w2, h2]
        
                # print 'new previous location: ' + str(carLocation1[i])
                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])
                        info = "{},{},{},{},{},{}\n".format(year, month,
						day, time1, speed[i],0)
                        logFile.write(info)
                        

                    #if y1 > 275 and y1 < 285:
                    #If found a Moving car 
                    if speed[i] != None and y1 >= 180:
                       
                        #Put text on Image with Speed and it's ID
                        cv2.putText(resultImage, str(int(speed[i])) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                        
                        
                    
                    #print ('CarID ' + str(i) + ': speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')
                   
                    #else:
                    #    cv2.putText(resultImage, "Far Object", (int(x1 + w1/2), int(y1)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        #print ('CarID ' + str(i) + ' Location1: ' + str(carLocation1[i]) + ' Location2: ' + str(carLocation2[i]) + ' speed is ' + str("%.2f" % round(speed[i], 0)) + ' km/h.\n')
        #Show the image output
        cv2.imshow('result', resultImage)
        # Write the frame into the file 'output.avi'
        out.write(resultImage)
        logFile.close()
        

        #Wait for User Input
        if cv2.waitKey(1) & 0xFF == ord('q'):
            

            break
       
    #Destroy all Opened Windows
    cv2.destroyAllWindows()

#Call Function Multiple Objects
if __name__ == '__main__':
    trackMultipleObjects()
