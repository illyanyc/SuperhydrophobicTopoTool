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
        #region
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="AFM Image Feature Distance - College of Staten Island", size=(300, 500))
        # Panel for frame
        self.SetBackgroundColour('gray')
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        LoadFile_btn = wx.Button(panel, id=wx.ID_ANY, label="1. Load", name="load")
        #endregion

        #create buttons and other UI items
        #region
        ProcessFile1_btn = wx.Button(panel, id=wx.ID_ANY, label="2. Identify center/edge", name="process1")
        ProcessFile2_btn = wx.Button(panel, id=wx.ID_ANY, label="3. Calculate Relationshps", name="process2")
        #self.Progressbar = wx.Gauge(panel, id=wx.ID_ANY, range=100, style=wx.GA_HORIZONTAL, validator=wx.DefaultValidator, name="Progress...")
        self.enter_units = wx.CheckBox(panel, -1, 'Enter Dimentions', (15, 30))
        lbl1 = wx.StaticText(panel, -1, "Width")
        self._width = wx.TextCtrl(panel, -1, size=(175, -1))
        lbl2 = wx.StaticText(panel, -1, "Height")
        self._height = wx.TextCtrl(panel, -1, size=(175, -1))
        lbl3 = wx.StaticText(panel, -1, "Units")
        self._units = wx.TextCtrl(panel, -1,  size=(175, -1))
        #lbl4 = wx.StaticText(panel, -1, "Phone Number (+1##########)")
        #self._phone = wx.TextCtrl(panel, -1, size=(175, -1))
        #self.sms_note_chk = wx.CheckBox(panel, -1, 'Send notification SMS', (15, 30))
        self.img_overlay_chk =  wx.CheckBox(panel, -1, 'Overlay image', (15, 55))
        self.num_tri = wx.CheckBox(panel, -1, 'Number triangles', (15, 55))
        #lbl3 = wx.StaticText(panel, -1, "Units")
        #self._height = wx.TextCtrl(panel, -1, size=(175, -1))

        #endregion

        #apply sizer to align the buttons and other UI items vertically on the left of the screen
        #region
        buttons = [LoadFile_btn, ProcessFile1_btn, self.enter_units, lbl1, self._width, lbl2, self._height, lbl3, self._units, self.img_overlay_chk, self.num_tri, ProcessFile2_btn]
        for button in buttons:
            self.buildButtons(button, sizer)
        #endregion

        panel.SetSizer(sizer)
    # ----------------------------------------------------------------------
    #define and arrange buttons
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)
        sizer.Add(btn, 0, wx.ALL, 5)

    # ----------------------------------------------------------------------

    #global params for file name
    global fileToOpen
    global attributes
    global circle_coutours

    #method excecuted when any button is pressed
    def onButton(self, event):

       # Create open file dialog
       #region
       global fileToOpen
       global attributes
       global circle_coutours
       button_id = event.GetId()
       button_by_id = self.FindWindowById(button_id)
        #endregion
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
           w= w+240
           h= h+140
           self.SetSize((w, h))

           openFileDialog.Destroy()

        #if "2. Identify center/edge" is pressed
       if buttonPressed == "process1":

           #print("Process")
           file_path = fileToOpen

           attributes,circle_coutours = lafc.process_image(file_path)

           saved_image_path = file_path + "_temp.png"

           bitmap = wx.Bitmap(saved_image_path)

           w, h = bitmap.GetSize()
           control = wx.StaticBitmap(self, -1, bitmap)
           control.SetPosition((200, 10))
           w = w + 200
           h = h + 40

           #print attributes

        #if "3. Calculate Relationships" is pressed
       if buttonPressed == "process2":
           img_overlay_bool = self.img_overlay_chk.GetValue()
           print img_overlay_bool
           send_sms_bool = False
           print send_sms_bool
           enter_width = self.enter_units.GetValue()
           #self.update_pbar_live()
           attributes = attributes
           circle_coutours=circle_coutours
           width = self._width.GetValue()
           height = self._height.GetValue()
           units = self._units.GetValue()
           phone = ""
           tri = self.num_tri.GetValue()
           nfr.triangulate(attributes,fileToOpen,send_sms_bool,img_overlay_bool,enter_width,width,height,units,phone,tri,circle_coutours)

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()

