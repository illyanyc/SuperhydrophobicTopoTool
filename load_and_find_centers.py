# load_and_find_centers.py method is called to perform feature boundary
# calculation, trace the boundary around the feature, find center of mass,
# produce boundary traced image
#
# The method reult is: Boundary Tranced Image, Center of Mass Coordinated
# as an array
# ----------------------------------------------------------------------

import imutils
import cv2
import numpy as np

def process_image(img_path,max,min,units,elev):

    _max=float(max)
    _min=float(min)
    _units=units

    pixel_elev=(_max-_min)/255

    attributes = []
    circle_coutours= []

    image_path = img_path
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(thresh,1,2)

    #find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    global i
    i=0

    for c in cnts:
        pixels_temp = []
        pixels = []

        M = cv2.moments(c)
        moments = c
        if M["m00"] == 0:
            M["m00"] = 1

        area = cv2.contourArea(c)

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        cimg = np.zeros_like(image)
        cv2.drawContours(cimg, [c], -1, color=255, thickness=-1)

        pts = np.where(cimg == 255)

        pixels_temp.append(image[pts[0], pts[1]])
        #print pixels_temp
        for j in pixels_temp:
            for k in j:
                px = np.average(k)
                pixels.append([px])

        #print pixels
        try:
            average = np.average(pixels) * pixel_elev + _min
            stdev = np.std(pixels) * pixel_elev + _min

            max = np.max(pixels) * pixel_elev + _min
            #print "Max: ",max,"Avg: ",average

            area_at_half_height_arr = []

            for j in pixels:
                if j >= average:
                    area_at_half_height_arr.append(i)
            area_at_half_height = len(area_at_half_height_arr)

            font = cv2.FONT_HERSHEY_PLAIN

            if area > 30:
                # draw the contour and center of the shape on the image
                cv2.circle(image, (cX, cY), 2, (71, 99, 255), -1)
                if elev == True:
                    cv2.putText(image, str(np.round(max,0)),(cX,cY), font, 1, (200,255,155), 1, cv2.LINE_AA)
                circle_coutours.append([i, average, stdev, max, cX, cY])
                try:
                    coordinates = [i, cX, cY, moments, area,area_at_half_height]
                    attributes.append(coordinates)
                except:
                    print "No attribute"
        except: print ""
        cv2.drawContours(image, [c], -1, (0, 150, 255), 1)

        i = i+1

    count_of_features = len(attributes)
    print "Count of features: ",count_of_features

    cv2.imwrite(image_path + "_temp.png", image)
    return attributes,circle_coutours
