# image_processing.py method is called to perform Delaunay
# triangulation on the center's of mass; plot lines, calculate lines
# lenght.
#
# The method reult is: Delaunay plot, Distribution of Feature's Widths,
# Distribution of Feature's Pitch, Distribution of Distance between
# the features.
# ----------------------------------------------------------------------
import matplotlib.patches as patches
from scipy.spatial import Delaunay
import sagitta_calculation as sag
import matplotlib.pyplot as plt
from twilio.rest import Client
from time import strftime
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import cv2
import math
import plots

def triangulate(attribute_array, file, sms, overlay, values, width, height, units, phone, tri, circle_coutours, ca, _wet, _pitch_plot, _height_plot, _distance_plot, _diameter_plot):
    #init method

    start = strftime("%Y-%m-%d %H:%M:%S")
    print "Calculation Started: ",start

    #declare arrays and variables and bools for use in calculations
    feature_pitch = []
    feature_distance = []
    feature_areas = []
    send_sms = sms
    overlay_image = overlay
    _phone = phone
    _tri = tri
    n_wetted = 0
    n_not_wetted = 0
    n_sagitta = 0
    arr_sagitta = []

    #if dimentions are entered: pixel to distance conversion ratio
    dimentions_entered = values
    if dimentions_entered == True:
        _width = float(width)
        _height = float(height)
        _units = units
    wet=_wet
    im = plt.imread(file + "_temp.png")
    countours=circle_coutours
    _ca=ca

    #preparing the image file for analysis
    image_path = file
    image = cv2.imread(image_path, 0)
    width = image.shape[1]
    height = image.shape[0]
    working_array = []

    #extract centers of mass only, from the attributes
    for a in attribute_array:
        x=a[1]
        y=a[2]
        working_array.append([x,y])

    #extract areas only from the attributes
    for b in attribute_array:
        area = b[4]
        feature_areas.append(area)

    #array of points
    attributes = np.array(working_array)
    points = np.array(attributes)

    #Delaunay triangulation
    #region
    tri = Delaunay(points)

    #image overlay prep
    if overlay_image == True:
        implot = plt.imshow(im)

    #plotting points
    plt.triplot(points[:,0], points[:,1], tri.simplices.copy(), color='r')
    plt.plot(points[:, 0], points[:, 1], 'o', color='w')

    #get areas as average_diameter
    feature_diameters = []
    for i in feature_areas:
        d = round(2 * np.sqrt(i / np.pi), 2)
        feature_diameters.append(d)
    average_diameter = np.average(feature_diameters)

    # for j, p in enumerate(points):
    #endregion

    #plot points, calculate distances between points
    for j, s in enumerate(tri.simplices):
        p = points[s].mean(axis=0)

        if _tri == True:
            plt.text(p[0], p[1], '#%d' % j, ha='center') # label triangles

        plt.xlim(0, width);
        plt.ylim(0, height)

    triangles = plt.figure(2)
    ax = triangles.add_subplot(111)
    ax.autoscale(False)
    ax.imshow(im)

    #calculates the pitch, distance between features, feature heights, sagitta (miniscus), wetting probability
    # and plots wetting map - all in one loop over the centers of mass.
    for i,s in enumerate(tri.simplices):
        s = tri.simplices[i,:]
        p_arr = points[tri.simplices[i,:]]
        #print "simplex: ",s," at: ",i
        vert_wetted = []
        triangle_coords = []

        verteces = [[0,1],[1,2],[2,0]]
        for v in verteces:
            xy1 = p_arr[v[0]]
            xy2 = p_arr[v[1]]

            x1 = xy1[0]
            y1 = xy1[1]
            x2 = xy2[0]
            y2 = xy2[1]

            triangle_coords.append([x1,y1])

            elevation1=[]
            elevation2=[]

            for c in countours:
                elev_x=c[4]
                elev_y=c[5]

                if elev_x == x1:
                    if elev_y==y1:
                        elevation1.append(c[3])

            for c in countours:
                elev_x = c[4]
                elev_y = c[5]

                if elev_x == x2:
                    if elev_y == y2:
                        elevation2.append(c[3])

            average_elevation_between_two_points = np.average(elevation1+elevation2)
            #plt.text(x1,y1,str(np.round(elevation1,0)))
            #print "Average Elevation: ",average_elevation_between_two_points

            #x_axis value
            diff_x = x2-x1
            diff_y = y2-y1
            abs_diff_x = np.abs(diff_x)
            abs_diff_y = np.abs(diff_y)
            x_squared = abs_diff_x ** 2
            y_squared = abs_diff_y ** 2
            sum_x_y = x_squared + y_squared
            x_axis_value = np.sqrt(sum_x_y)
            pitch=x_axis_value

            #y_axis value
            y_axis_value = np.abs(elevation2[0]-elevation1[0])

            #adjust the values for dimentions entered
            if dimentions_entered == True:
                ratio = _width / width
                pitch=round(pitch*ratio,2)

            if dimentions_entered == True:
                ratio = _width / width
                average_diameter = round(average_diameter * ratio, 2)
            #print "pitch: ",pitch

            sagitta_locations = []
            for b in attribute_array:
                area = b[4]
                _cX=b[1]
                _cY=b[2]
                sagitta_locations.append([area,_cX,_cY])

            #get radii for the sagitta calcualtions
            sagitta_radius1 = average_diameter
            sagitta_radius2 = average_diameter

            for c in sagitta_locations:
                _cX = c[1]
                _cY = c[2]
                if _cX == x1:
                    if _cY == y1:
                        _area=c[0]
                        _diameter=round(2 * np.sqrt(_area / np.pi), 2)
                        sagitta_radius1 = _diameter
                        #print "Radius 1:", sagitta_radius1

            for c in sagitta_locations:
                _cX = c[1]
                _cY = c[2]
                if _cX == x2:
                    if _cY == y2:
                        _area = c[0]
                        _diameter = round(2 * np.sqrt(_area / np.pi), 2)
                        sagitta_radius2 = _diameter
                        #print "Radius 1:", sagitta_radius2

            #calculate Saggita
            x_for_saggita=pitch-sagitta_radius1/2-sagitta_radius2/2
            if x_for_saggita  <= 0:
                x_for_saggita=pitch

            _sagitta = sag.sagitta(_ca, average_elevation_between_two_points, x_for_saggita, 0.0728)
            arr_sagitta.append(_sagitta)

            #if _saggita >= average_elevation_between_two_points:
            if math.isnan(_sagitta) == False:
                wet_scale = average_elevation_between_two_points-_sagitta
            else:
                wet_scale = 0
                _sagitta = 0

            vert_wetted.append(wet_scale)
                #print "WETTED!"
            #print "Saggita: ",_sagitta

            #populate the feature diamter list
            feature_pitch.append(pitch)

            #populate the feature distance list
            calculated_distance = pitch-sagitta_radius1-sagitta_radius2
            feature_distance.append(calculated_distance)

        avg_vert_wetted = np.average(vert_wetted)
        t_p=np.array(triangle_coords)
        #print t_p

        #draw triangles for the surface wetting map
        if wet == True:
            p = points[s].mean(axis=0)
            if avg_vert_wetted > 0:
                Y = ['red', 'red', 'red',]
                #plt.text(p[0], p[1],"*",fontsize=15,color='green')  # label triangles
                #t1 = plt.Polygon(t_p, color=Y[0])
                #triangles.gca().add_patch(t1)
                poly = matplotlib.patches.Polygon(t_p,closed=True,color='green',alpha=0.4)
                n_not_wetted += 1

                ax.add_patch(poly)
            else:
                Y = ['green', 'green', 'green', ]
                #plt.text(p[0], p[1],"*",fontsize=15,color='red')  # label triangles
                #t1 = plt.Polygon(t_p, color=Y[0])
                #triangles.gca().add_patch(t1)
                poly = matplotlib.patches.Polygon(t_p,closed=True,color='red',alpha=0.4)
                n_wetted += 1
                ax.add_patch(poly)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    triangles.show()
    #endregion

    #final answer
    #region
    areas_avg =np.average(feature_areas)
    average_pitch = round(np.average(feature_pitch),2)
    average_diameter = np.average(feature_diameters)
    stdev_pitch = round(np.std(feature_pitch),2)
    stdev_diameter=round(np.std(feature_diameters))
    average_distance=round(np.std(feature_distance))
    stdev_distance=round(np.std(feature_distance))
    units = "pixels"

    _feature_diameters = []
    _feature_pitch = []
    _feature_distance = []

    #correct average and stdev values for dimentions entered by user
    if dimentions_entered == True:
        ratio = _width/width
        average_distance=round(average_distance*ratio*2)
        stdev_distance=round(stdev_distance*ratio*2)
        average_diameter = round(average_diameter*ratio,2)
        units = _units

        for i in feature_diameters:
            new_i=round(i*ratio,2)
            _feature_diameters.append(new_i)

        _feature_pitch=feature_pitch
        _feature_distance=feature_distance

        #for i in feature_distance:
        #    new_i=round(i*ratio*2)
         #   _feature_distance.append(new_i)


    #endregion
    #final answer message
    end = strftime("%Y-%m-%d %H:%M:%S")
    print "Calculation Ended: ",end

    #send SMS notification
    #region
    work = False

    if send_sms == True:
        account_sid = ""
        auth_token = ""
        client = Client(account_sid, auth_token)
        message_for_sms = []
        message_for_sms.append("AFM Calculation complete! , the average_distance distance between the features is:")
        message_for_sms.append(str(int(average_pitch)))
        message_for_sms.append(" +/ ")
        message_for_sms.append(str(stdev_pitch))
        message_for_sms.append(" ")
        message_for_sms.append(_units)
        message_for_sms.append(" The calculation started at: ")
        message_for_sms.append(str(start))
        message_for_sms.append(" and ended at: ")
        message_for_sms.append(str(end))
        message_for_sms.append(".")
        message_for_sms.append(" File name: ")
        message_for_sms.append(file)
        message_to_send = ''.join(message_for_sms)
        print message_for_sms
        message = client.messages.create(
            to=_phone,
            from_="+14155247927",
            body=message_to_send)
        print(message.sid)
    #endregion
    #show overlayed image
    plt.show()
    all_tri= float(n_wetted)+float(n_not_wetted)
    print "Triangle count: ",all_tri,"; Wetted: n=", float(n_wetted), ", ",\
        float(n_wetted)/float(all_tri)*100,"% ","; Not Wetted: n=",\
        float(n_not_wetted), ", ",float(n_not_wetted)/float(all_tri)*100,"% "
    print "Sagitta Average: ",round(np.average(arr_sagitta),1), " ",units

    #Plots:
    #plotting daimeter distributions
    if _diameter_plot == True:
        if dimentions_entered == True:
            d = _feature_diameters
        else: d = feature_diameters
        plot_name='Distribution of feature diameters'
        x_axis='Diameter, '
        plots.histogram_plot(d,units,plot_name,x_axis)

    #plotting feature's pitch
    if _pitch_plot == True:
        if dimentions_entered == True:
            d = _feature_pitch
        else: d = feature_pitch
        temp = d
        d = []
        for i in temp:
            if i < average_pitch+3.5*stdev_pitch:
                d.append(i)
        plot_name = 'Distribution of feature pitch'
        x_axis = 'Pitch, '
        plots.histogram_plot(d, units, plot_name, x_axis)

    #calculating and plotting distance between features
    if _distance_plot == True:
        if dimentions_entered == True:
            d = _feature_distance
        else:
            d = feature_distance

        temp = d
        d = []
        for i in temp:
            if i < average_distance:
                if i > 0:
                    if i < average_pitch+3.0 * stdev_pitch:
                        d.append(i)

        plot_name = 'Distance between the features'
        x_axis = 'Distance, '
        plots.histogram_plot(d, units, plot_name, x_axis)

    # calculating and plotting feature heights
    if _height_plot == True:
        _countours = countours
        d = []
        for i in _countours:
            _elev = i[3]
            d.append(_elev)

        plot_name = "Distribution of feature's heights"
        x_axis = 'Height, '
        plots.histogram_plot(d, units, plot_name, x_axis)

    print "Complete"
        #endregion





