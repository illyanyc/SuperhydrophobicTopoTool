# AFM_Feature_Analysis by Illya Nayshevsky
# College of Staten Island, City University of New York
# illya.nayshevsky@csi.cuny.edu
#
# This application analyzes "slices" of AFM images to calculate the distance
# beteween the features on the surface, the pitch between the features on the
# surface, and the diameter of the features on the surface.
# ----------------------------------------------------------------------
import os
import wx
import convert_to_png
import load_and_find_centers as lafc
import image_processing as nfr

class MyForm(wx.Frame):
    #initiate the form

    def __init__(self):
        #initialize the frame (window) of the application
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="AFM Image Feature Distance - College of Staten Island", size=(300, 800))

        # Panel for frame
        self.SetBackgroundColour('gray')
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        LoadFile_btn = wx.Button(panel, id=wx.ID_ANY, label="1. Load Image", name="load")

        #Building UI items
            #buttons
        ProcessFile1_btn = wx.Button(panel, id=wx.ID_ANY, label="2. Identify center/edge", name="process1")
        ProcessFile2_btn = wx.Button(panel, id=wx.ID_ANY, label="3. Calculate Relationshps", name="process2")

            #labels
        lbl5 = wx.StaticText(panel, -1, "Max Elevation")
        lbl1 = wx.StaticText(panel, -1, "Width")
        lbl2 = wx.StaticText(panel, -1, "Height")
        lbl3 = wx.StaticText(panel, -1, "Units")
        lbl5_1 = wx.StaticText(panel, -1, "Min Elevation")
        lbl6 = wx.StaticText(panel, -1, "Units")
        lbl7 = wx.StaticText(panel, -1, "Contact Angle")
        lbl8 = wx.StaticText(panel, -1, "Plot Selection")

            #checkboxes
        self.num_tri = wx.CheckBox(panel, -1, 'Number triangles', (15, 55))
        self.img_overlay_chk =  wx.CheckBox(panel, -1, 'Overlay image', (15, 55))
        self.wet = wx.CheckBox(panel, -1, 'Calculate Wetting', (15, 55))
        self.elev = wx.CheckBox(panel, -1, 'Display Elevations', (15, 55))
        self.distance_plot = wx.CheckBox(panel, -1, 'Distance Plot', (15, 55))
        self.height_plot = wx.CheckBox(panel, -1, 'Height Plot', (15, 55))
        self.pitch_plot = wx.CheckBox(panel, -1, 'Pitch Plot', (15, 55))
        self.diameter_plot = wx.CheckBox(panel, -1, 'Diameter PLot', (15, 55))

            #textboxes
        self._units = wx.TextCtrl(panel, -1,  size=(175, -1))
        self._max = wx.TextCtrl(panel, -1, size=(175, -1))
        self._min = wx.TextCtrl(panel, -1, size=(175, -1))
        self.elev_unit = wx.TextCtrl(panel, -1, size=(175, -1))
        self.ca = wx.TextCtrl(panel, -1, size=(175, -1))
        self._width = wx.TextCtrl(panel, -1, size=(175, -1))
        self._height = wx.TextCtrl(panel, -1, size=(175, -1))

        #apply sizer to align the buttons and other UI items vertically on the left of the screen
            #add all UI items to array
        buttons = [LoadFile_btn,lbl5, self._max, lbl5_1, self._min, lbl6,
                   self.elev_unit, lbl7, self.ca, self.elev, ProcessFile1_btn, lbl1,
                   self._width, lbl2, self._height, lbl3, self._units, self.img_overlay_chk,
                   self.num_tri, self.wet,lbl8, self.diameter_plot,self.pitch_plot, self.distance_plot,
                   self.height_plot, ProcessFile2_btn]

            #apply sizer to all UI items
        for button in buttons:
            self.buildButtons(button, sizer)

        panel.SetSizer(sizer)
    # ----------------------------------------------------------------------
    #build all of the buttons in the sizer
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)
        sizer.Add(btn, 0, wx.ALL, 5)

    # ----------------------------------------------------------------------

    #global params for file name
    global fileToOpen
    global attributes
    global circle_coutours
    global area_at_half_height

    #method excecuted when any button is pressed
    def onButton(self, event):

       # Create open file dialog
       global fileToOpen
       global attributes
       global circle_coutours
       global area_at_half_height

       button_id = event.GetId()
       button_by_id = self.FindWindowById(button_id)

       #get pressed button name
       buttonPressed = button_by_id.GetName()

       #logical method for pressed button args
#if "1. Load" is pressed:
       if buttonPressed == "load":
           openFileDialog = wx.FileDialog(frame, "Open", "", "",
                                      "Bitmap files (*.*)|*.*",
                                      wx.FD_OPEN)
           openFileDialog.ShowModal()

           fileToOpen = openFileDialog.GetPath()
           ext = os.path.splitext(fileToOpen)[-1].lower()
           print(ext)
           if ext == ".jpg":
               convert_to_png.convert(fileToOpen)
               fileToOpen = fileToOpen+".png"

           print(fileToOpen)
           bitmap = wx.Bitmap(fileToOpen)
           w,h= bitmap.GetSize()
           control = wx.StaticBitmap(self, -1, bitmap)
           control.SetPosition((200, 10))
           w= w+300
           h= h+240
           self.SetSize((w, h))

           openFileDialog.Destroy()

#if "2. Identify center/edge" is pressed
       if buttonPressed == "process1":

           max_1 = self._max.GetValue()
           min_1 = self._min.GetValue()
           _elev=self.elev.GetValue()
           elev_unit_1 = self.elev_unit.GetValue()

           file_path = fileToOpen

           attributes,circle_coutours = lafc.process_image(file_path,max_1,min_1,elev_unit_1,_elev)

           saved_image_path = file_path + "_temp.png"
           bitmap = wx.Bitmap(saved_image_path)

           control = wx.StaticBitmap(self, -1, bitmap)
           control.SetPosition((200, 10))

#if "3. Calculate Relationships" is pressed
       if buttonPressed == "process2":

           img_overlay_bool = self.img_overlay_chk.GetValue()
           width = self._width.GetValue()
           height = self._height.GetValue()
           units = self._units.GetValue()
           _pitch_plot=self.pitch_plot.GetValue()
           _distance_plot=self.distance_plot.GetValue()
           _height_plot=self.height_plot.GetValue()
           _diameter_plot=self.diameter_plot.GetValue()
           _ca = self.ca.GetValue()
           _wet=self.wet.GetValue()
           tri = self.num_tri.GetValue()
           send_sms_bool = False
           enter_width = True

           attributes = attributes
           circle_coutours=circle_coutours
           phone = ""

           nfr.triangulate(attributes,fileToOpen,send_sms_bool,img_overlay_bool,
                           enter_width,width,height,units,phone,tri,circle_coutours,
                           _ca,_wet,_pitch_plot,_height_plot,_distance_plot,_diameter_plot)

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()

