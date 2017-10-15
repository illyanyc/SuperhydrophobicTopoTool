import os
import numpy
import wx
from PIL import Image as im
import cv2
import imutils
import convert_to_png
import load_and_find_centers as lafc
import find_relationships as fr
import _new_find_relationships as nfr

class MyForm(wx.Frame):
    #initiate the form


    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title="AFM Image Feature Distance - College of Staten Island")
        # Panel for frame
        self.SetBackgroundColour('gray')

        panel = wx.Panel(self, wx.ID_ANY)
        #self.SetSize((600,200))

        sizer = wx.BoxSizer(wx.VERTICAL)
        LoadFile_btn = wx.Button(panel, id=wx.ID_ANY, label="Load", name="load")
        ProcessFile1_btn = wx.Button(panel, id=wx.ID_ANY, label="Identify center/edge", name="process1")
        ProcessFile2_btn = wx.Button(panel, id=wx.ID_ANY, label="Calculate Relationshps", name="process2")
        #self.Progressbar = wx.Gauge(panel, id=wx.ID_ANY, range=100, style=wx.GA_HORIZONTAL, validator=wx.DefaultValidator, name="Progress...")
        self.sms_note_chk = wx.CheckBox(panel, -1, 'Send notification SMS', (15, 30))
        self.img_overlay_chk =  wx.CheckBox(panel, -1, 'Overlay image', (15, 55))


        #LoadFile_btn.Bind(wx.EVT_BUTTON, self.onButton)
        #ProcessFile_btn.Bind(wx.EVT_BUTTON, self.onButton)

        buttons = [LoadFile_btn, ProcessFile1_btn, ProcessFile2_btn, self.sms_note_chk, self.img_overlay_chk]

        for button in buttons:
            self.buildButtons(button, sizer)

        panel.SetSizer(sizer)

    # ----------------------------------------------------------------------
    #define and arrange buttons
    def buildButtons(self, btn, sizer):
        btn.Bind(wx.EVT_BUTTON, self.onButton)
        sizer.Add(btn, 0, wx.ALL, 5)



    # ----------------------------------------------------------------------

    #global param for file name
    global fileToOpen
    global attributes

    #button methods
    def onButton(self, event):
       # Create open file dialog
       saved_image_path = ""
       global fileToOpen
       global attributes


       button_id = event.GetId()
       button_by_id = self.FindWindowById(button_id)

       buttonPressed = button_by_id.GetName()
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
           h= h+80
           self.SetSize((w, h))

           openFileDialog.Destroy()

       if buttonPressed == "process1":

           #print("Process")
           file_path = fileToOpen

           attributes = lafc.process_image(file_path)

           saved_image_path = file_path + "_temp.png"

           bitmap = wx.Bitmap(saved_image_path)
           w, h = bitmap.GetSize()
           control = wx.StaticBitmap(self, -1, bitmap)
           control.SetPosition((200, 10))
           w = w + 200
           h = h + 40
           #print attributes

       if buttonPressed == "process2":
           img_overlay_bool = self.img_overlay_chk.GetValue()
           print img_overlay_bool
           send_sms_bool = self.sms_note_chk.GetValue()
           print send_sms_bool
           #self.update_pbar_live()
           attributes = attributes
           nfr.triangulate(attributes,fileToOpen,send_sms_bool,img_overlay_bool)
           #fr.find_relationships(attributes, fileToOpen)
           #print("Identifying edges")

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()

