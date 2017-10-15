
# import the necessary packages
import argparse
import imutils
import cv2
import numpy

def process_image(img_path):
    attributes = []
    image_path = img_path
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(thresh,1,2)


    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]


    global i
    i=0
    for c in cnts:
        i=i+1
        M = cv2.moments(c)
        moments = c
        if M["m00"] == 0:
            M["m00"] = 1

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        try:
            coordinates = [i, cX, cY, moments]
            attributes.append(coordinates)
        except:
            print "no attribute"

        # draw the contour and center of the shape on the image
        cv2.drawContours(image, [c], -1, (0, 255, 0), 1)
        cv2.circle(image, (cX, cY), 2, (71, 99, 255), -1)
        # cv2.putText(image, "center", (cX - 20, cY - 20),
        # cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # show the image
        #cv2.imshow("Image", image)

        # cv2.waitKey(0)


    cv2.imwrite(image_path + "_temp.png", image)
    return attributes