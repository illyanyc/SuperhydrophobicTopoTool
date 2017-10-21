# image_processing.py method is called to perform Delaunay
# triangulation on the center's of mass; plot lines, calculate lines
# lenght.
#
# The method reult is: Delaunay plot, Distribution of Feature's Widths,
# Distribution of Feature's Pitch, Distribution of Distance between
# the features.
# ----------------------------------------------------------------------

from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from time import strftime
from twilio.rest import Client
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patches as patches
import pyperclip
import math
from matplotlib.ticker import FormatStrFormatter
matplotlib.use('TkAgg')

#method for calculating the sagitta
def saggita(ca,height,pitch,surface_tension):
    _ca=float(ca)
    _height=float(height)
    _pitch=float(pitch)
    _surface_tension=float(surface_tension)

    a1=180.0-_ca
    a2=180-90-a1
    b=180-90-a2

    y=np.tan(np.deg2rad(_ca))*(_pitch/2)
    x=_pitch/2
    r=np.sqrt((x)**2+(y)**2)
    s=r-np.sqrt((r)**2-(_pitch)**2)
    return s

def triangulate(attribute_array, file, sms, overlay, values, width, height, units, phone, tri, circle_coutours, ca, _wet, _pitch_plot, _height_plot, _distance_plot, _diameter_plot):
    #init method

    start = strftime("%Y-%m-%d %H:%M:%S")
    print start

    #declare arrays and variables for use in calculations
    feature_pitch = []
    feature_distance = []
    feature_areas = []
    txt_doc = []
    #bools
    send_sms = sms
    overlay_image = overlay
    _phone = phone
    _tri = tri

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
        print "simplex: ",s," at: ",i
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
            print "Average Elevation: ",average_elevation_between_two_points

            diff_x = x2-x1
            diff_y = y2-y1
            abs_diff_x = np.abs(diff_x)
            abs_diff_y = np.abs(diff_y)
            x_squared = abs_diff_x ** 2
            y_squared = abs_diff_y ** 2
            sum_x_y = x_squared + y_squared
            x_axis_value = np.sqrt(sum_x_y)
            pitch=x_axis_value
            y_axis_value = np.abs(elevation2[0]-elevation1[0])

            if dimentions_entered == True:
                ratio = _width / width
                pitch=round(pitch*ratio,2)

            if dimentions_entered == True:
                ratio = _width / width
                average_diameter = round(average_diameter * ratio, 2)

            new_pitch = np.sqrt((x_axis_value)**2+(y_axis_value)**2)

            print "pitch: ",pitch
                #,"new_pitch: :",new_pitch

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
                        print "Radius 1:", sagitta_radius1

            for c in sagitta_locations:
                _cX = c[1]
                _cY = c[2]
                if _cX == x2:
                    if _cY == y2:
                        _area = c[0]
                        _diameter = round(2 * np.sqrt(_area / np.pi), 2)
                        sagitta_radius2 = _diameter
                        print "Radius 1:", sagitta_radius2

            #calculate Saggita
            x_for_saggita=pitch-sagitta_radius1/2-sagitta_radius2/2
            if x_for_saggita  <= 0:
                x_for_saggita=pitch

            _sagitta = saggita(_ca,average_elevation_between_two_points,x_for_saggita,0.0728)

            #if _saggita >= average_elevation_between_two_points:
            if math.isnan(_sagitta) == False:
                wet_scale = average_elevation_between_two_points-_sagitta
            else:
                wet_scale = 0
                _sagitta = 0

            vert_wetted.append(wet_scale)
                #print "WETTED!"
            print "Saggita: ",_sagitta

            #populate the feature diamter list
            feature_pitch.append(pitch)

            #populate the feature distance list
            calculated_distance = pitch-sagitta_radius1-sagitta_radius2
            feature_distance.append(calculated_distance)

        avg_vert_wetted = np.average(vert_wetted)
        #print "AVERAGE WETTED!:",avg_vert_wetted
        t_p=np.array(triangle_coords)
        print t_p

        triangle_color=""

        #draw triangles for the surface wetting map
        if wet == True:
            p = points[s].mean(axis=0)
            if avg_vert_wetted > 0:
                Y = ['red', 'red', 'red',]
                #plt.text(p[0], p[1],"*",fontsize=15,color='green')  # label triangles
                #t1 = plt.Polygon(t_p, color=Y[0])
                #triangles.gca().add_patch(t1)
                poly = matplotlib.patches.Polygon(t_p,closed=True,color='green',alpha=0.5)

                ax.add_patch(poly)
            else:
                Y = ['green', 'green', 'green', ]
                #plt.text(p[0], p[1],"*",fontsize=15,color='red')  # label triangles
                #t1 = plt.Polygon(t_p, color=Y[0])
                #triangles.gca().add_patch(t1)
                poly = matplotlib.patches.Polygon(t_p,closed=True,color='red',alpha=0.5)

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

        for i in feature_distance:
            new_i=round(i*ratio*2)
            _feature_distance.append(new_i)

    #endregion
    #final answer message
    _box = []
    _box.append("Average Pitch: ")
    _box.append(str(average_pitch))
    _box.append(" ")
    _box.append(units)
    _box.append(" StDev: ")
    _box.append(str(stdev_pitch))
    _box.append(" ")
    _box.append(units)
    t_box = ''.join(_box)
    end = strftime("%Y-%m-%d %H:%M:%S")
    print end

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

    #Plots:
    #plotting daimeter distributions
    if _diameter_plot == True:
        if dimentions_entered == True:
            d = _feature_diameters
        else: d = feature_diameters

        average_diameter = np.average(d)
        stdev_diameter = np.std(d)

        mean_ = []
        mean_.append("Mean Diameter: ")
        mean_.append(str(average_diameter))
        mean_.append(" Stdev: ")
        mean_.append(str(stdev_diameter))
        mean_.append(" ")
        mean_.append(str(units))
        mean_label = ''.join(mean_)
        fig, ax = plt.subplots()
        d_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=15)
        x_label = "Diameter, "+str(units)
        plt.xlabel(x_label,fontsize=15)
        plt.ylabel('Count, n',fontsize=15)
        plt.title('Distribution of feature diameters', fontsize=15)

        plt.grid(True)
        # Set the ticks to be at the edges of the bins.
        ax.set_xticks(bins)
        # Set the xaxis's tick labels to be formatted with 1 decimal place...
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))

        # Change the colors of bars at the edges...
        fiftyfifth, _fiftyfifth = np.percentile(d, [50, 50])
        for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
            if rightside < fiftyfifth:
                patch.set_facecolor('grey')
            elif leftside > _fiftyfifth:
                patch.set_facecolor('grey')

        # Label the raw counts and the percentages below the x-axis...

        bin_centers = 0.5 * np.diff(bins) + bins[:-1]
        for count, x in zip(counts, bin_centers):
            # Label the raw counts
            ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                        xytext=(0, 65), textcoords='offset points', va='top', ha='center',rotation=90)

            # Label the percentages
            #percent = '%1.0f%%' % (100 * float(count) / counts.sum())
            #ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
            #           xytext=(0, 45), textcoords='offset points', va='top', ha='center')
        plt.axvline(x=average_diameter, color="red", linestyle='dashed', linewidth=2)
        #plt.text(0, 0, mean_label, color='black', bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(fontsize=15)

        # Give ourselves some more room at the bottom of the plot
        plt.subplots_adjust(bottom=0.15)
        plt.show(d_plot)

    #plotting feature's pitch
    if _pitch_plot == True:
        if dimentions_entered == True:
            d = _feature_pitch
        else: d = feature_pitch

        temp = d
        d = []

        for i in temp:
            if i < average_pitch+2.5*stdev_pitch:
                d.append(i)

        average_pitch = np.average(d)
        stdev_pitch = np.std(d)

        _mean = []
        _mean.append("Mean Pitch: ")
        _mean.append(str(average_pitch))
        _mean.append(" Stdev: ")
        _mean.append(str(stdev_pitch))
        _mean.append(" ")
        _mean.append(str(units))
        mean_label = ''.join(_mean)
        fig, ax = plt.subplots()
        f_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=15)
        x_label = "Pitch, " + str(units)
        plt.xlabel(x_label,fontsize=15)
        plt.ylabel('Count, n',fontsize=15)
        plt.title('Distribution of feature pitch',fontsize=15)

        plt.grid(True)
        # Set the ticks to be at the edges of the bins.
        ax.set_xticks(bins)
        # Set the xaxis's tick labels to be formatted with 1 decimal place...
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))

        # Change the colors of bars at the edges...
        fiftyfifth, _fiftyfifth = np.percentile(d, [50, 50])
        for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
            if rightside < fiftyfifth:
                patch.set_facecolor('grey')
            elif leftside > _fiftyfifth:
                patch.set_facecolor('grey')
        max_y_bin = np.max(bins)
        # Label the raw counts and the percentages below the x-axis...
        bin_centers = 0.5 * np.diff(bins) + bins[:-1]
        for count, x in zip(counts, bin_centers):
            # Label the raw counts
            ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                        xytext=(0, 65), textcoords='offset points', va='top', ha='center',rotation=90)

            # Label the percentages
            # percent = '%1.0f%%' % (100 * float(count) / counts.sum())
            # ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
            #           xytext=(0, 45), textcoords='offset points', va='top', ha='center')
        plt.axvline(x=average_pitch, color="red", linestyle='dashed', linewidth=2)
        #plt.text(0, 0, mean_label, color='black',bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(fontsize=15)

        # Give ourselves some more room at the bottom of the plot
        plt.subplots_adjust(bottom=0.15)
        plt.show(f_plot)

    #calculating and plotting distance between features
    if _distance_plot == True:

        if dimentions_entered == True:
            d = _feature_pitch
        else:
            d = calculated_distance

        temp = d
        d = []

        for i in temp:
            if i < average_distance + 3 * stdev_distance:
                d.append(i)

        average_distance = np.average(d)
        stdev_distance = np.std(d)

        _mean = []
        _mean.append("Mean Distance: ")
        _mean.append(str(average_distance))
        _mean.append(" Stdev: ")
        _mean.append(str(stdev_distance))
        _mean.append(" ")
        _mean.append(str(units))
        mean_label = ''.join(_mean)
        fig, ax = plt.subplots()
        f_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=15)
        x_label = "Distance, " + str(units)
        plt.xlabel(x_label,fontsize=15)
        plt.ylabel('Count, n',fontsize=15)
        plt.title('Distribution of distance between features',fontsize=15)

        plt.grid(True)
        # Set the ticks to be at the edges of the bins.
        ax.set_xticks(bins)
        # Set the xaxis's tick labels to be formatted with 1 decimal place...
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))

        # Change the colors of bars at the edges...
        fiftyfifth, _fiftyfifth = np.percentile(d, [50, 50])
        for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
            if rightside < fiftyfifth:
                patch.set_facecolor('grey')
            elif leftside > _fiftyfifth:
                patch.set_facecolor('grey')
        max_y_bin = np.max(bins)
        # Label the raw counts and the percentages below the x-axis...
        bin_centers = 0.5 * np.diff(bins) + bins[:-1]
        for count, x in zip(counts, bin_centers):
            # Label the raw counts
            ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                        xytext=(0, 65), textcoords='offset points', va='top', ha='center',rotation=90)

            # Label the percentages
            # percent = '%1.0f%%' % (100 * float(count) / counts.sum())
            # ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
            #           xytext=(0, 45), textcoords='offset points', va='top', ha='center')
        plt.axvline(x=average_distance, color="red", linestyle='dashed', linewidth=2)
        #plt.text(0, 0, mean_label, color='black',bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(fontsize=15)

        # Give ourselves some more room at the bottom of the plot
        plt.subplots_adjust(bottom=0.15)
        plt.show(f_plot)
        #endregion

    # calculating and plotting distance between features
    if _height_plot == True:
        _countours = countours

        d = []

        for i in _countours:
            _elev = i[3]
            d.append(_elev)

        stdev_height = round(np.std(d), 2)
        average_height = round(np.average(d), 2)

        _mean = []
        _mean.append("Mean Height: ")
        _mean.append(str(average_height))
        _mean.append(" Stdev: ")
        _mean.append(str(stdev_height))
        _mean.append(" ")
        _mean.append(str(units))
        mean_label = ''.join(_mean)
        fig, ax = plt.subplots()
        f_plot = counts, bins, patches = ax.hist(d, facecolor='g', edgecolor='gray', bins=15)
        x_label = "Height, " + str(units)
        plt.xlabel(x_label,fontsize=15)
        plt.ylabel('Count, n',fontsize=15)
        plt.title('Distribution of heights', fontsize= 15)

        plt.grid(True)
        # Set the ticks to be at the edges of the bins.
        ax.set_xticks(bins)
        # Set the xaxis's tick labels to be formatted with 1 decimal place...
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0f'))

        # Change the colors of bars at the edges...
        fiftyfifth, _fiftyfifth = np.percentile(d, [50, 50])
        for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
            if rightside < fiftyfifth:
                patch.set_facecolor('grey')
            elif leftside > _fiftyfifth:
                patch.set_facecolor('grey')
        max_y_bin = np.max(bins)
        # Label the raw counts and the percentages below the x-axis...
        bin_centers = 0.5 * np.diff(bins) + bins[:-1]
        for count, x in zip(counts, bin_centers):
            # Label the raw counts
            ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
                        xytext=(0, 65), textcoords='offset points', va='top', ha='center',rotation=90)

            # Label the percentages
            # percent = '%1.0f%%' % (100 * float(count) / counts.sum())
            # ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
            #           xytext=(0, 45), textcoords='offset points', va='top', ha='center')
        plt.axvline(x=average_height, color="red", linestyle='dashed', linewidth=2)
        #plt.text(0, 0, mean_label, color='black',bbox=dict(facecolor='white', edgecolor='red', boxstyle='round'))
        plt.xticks(rotation=70, fontsize= 15)
        plt.yticks(fontsize= 15)

        # Give ourselves some more room at the bottom of the plot
        plt.subplots_adjust(bottom=0.15)
        plt.show(f_plot)



        # result terminal print-out
        # region
    #messagebox

    #message box string builder
    try:
        message_box1 = "Average Pitch: "+str(round(average_pitch,0))+" "+_units+" StDev: "+str(round(stdev_pitch,0))+" "+_units
        print message_box1
    except: print ""
    try:
        message_box2 ="Average Distance between Features: "+str(round(average_distance,0))+" "+_units+" StDev: "+str(round(stdev_distance,0))+" "+_units
        print message_box2
    except: print ""
    try:
        message_box3 ="Average diameter of the features: "+str(round(average_diameter,0))+" "+_units+" StDev: "+str(round(stdev_diameter,0))+" "+_units
        print message_box3
    except: print ""
    try:
        message_box4 ="Average height of the features: "+str(round(average_height,0))+" "+_units+" StDev: "+str(round(stdev_height,0))+" "+_units
        print message_box4
    except: print ""

    #pyperclip.copy("Pitch,"+str(average_pitch)+","+str(stdev_pitch)+",Distance,"+str(average_feature_real_distane)+","+str(stdev_feature_real_distance)+",Diameter,"+str(average_diameter)+","+str(stdev_diameter)+",Units:"+_units)
    print "Complete"
        #endregion





