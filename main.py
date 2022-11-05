from kivymd.app import MDApp
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.button import MDRectangleFlatButton
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.core.window import Window
import cv2
import NewEyeTracking
from kivymd.uix.button import MDRoundFlatIconButton

# Kivy specifc format layout
kv = '''
#:import Snackbar kivymd.uix.snackbar.Snackbar


MDFloatLayout:
    radius: [25, 0, 0, 0]

    Toggle:
        icon: "hand-front-right-outline"
        text: app.Hand
        font_size: "25sp"
        on_press: app.ToggleHand(self)
        pos_hint: {"center_x": .92, "center_y": .60}

    Toggle:
        icon: "video"
        text: app.Camera
        font_size: "25sp"
        on_press: app.ToggleCamera(self)
        on_release: app.switch_theme_style()
        pos_hint: {"center_x": .92, "center_y": .54}
    
    Toggle:
        icon: "mouse"
        text: app.Mouse
        font_size: "25sp"
        on_press: app.ToggleMouse(self)
        pos_hint: {"center_x": .92, "center_y": .48}

    MDRectangleFlatButton:
        text: "Authors"
        pos_hint: {"center_x": .92, "center_y": .4}
        duration: 50
        on_release: Snackbar(text="Made by Tyler, Kenneth, Sam, and Imanol!",font_size=50,snackbar_x="10dp",snackbar_y="10dp",size_hint_x=.5,duration=10).open()

    MDSlider:
        min: 1
        max: 5
        step: 1
        value: 1
        orientation: 'vertical'
        pos_hint: {"center_x": .06, "center_y": .5}
        size_hint: .25, .25
        on_value: app.SliderChange(*args)

    MDLabel:
        text: app.Looking
        adaptive_size: True
        font_style: "H5"
        pos_hint: {"center_x": .06, "center_y": .7}
    
    MDLabel:
        text: app.Type
        adaptive_size: True
        font_style: "H5"
        pos_hint: {"center_x": .06, "center_y": .3}


'''
# Gives CameraToggle the same attribute as MDRectangleFlatButton and makes it a toggable function
class CameraToggle(MDRectangleFlatButton, MDToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = self.theme_cls.primary_color

class Toggle(MDRoundFlatIconButton,MDToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Main function
class MainApp(MDApp):

    # Text for the button
    Camera = StringProperty('Camera On')
    Mouse = StringProperty('Mouse Off')
    Hand = StringProperty('Hand Off')

    # Text for the label
    Looking = StringProperty('Looking Center')
    Type = StringProperty('Normal')

    def build(self):
        # Theming
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Light"

        # Loads kv at the top
        layout = Builder.load_string(kv)

        # Generates and loads a canvas for the webcam
        self.image = Image(source ='A_New_Black_image.png',keep_ratio = (True), allow_stretch=(True), size = Window.size)
        layout.add_widget(self.image)

        # Sets to read webcam 1
        self.capture = cv2.VideoCapture(0)

        # Does function load_video 10 times per frame
        Clock.schedule_interval(self.load_video, 1.0/10.0)

        # Outputs everything to the window
        return layout
    
    # Function that loads frame or black image to the canvas
    def load_video(self,*args):
        # Reads the frame from capture and sets it 
        ret, frame = self.capture.read()
        #self.image_frame = EyeTracking._main_(frame)
        self.image_frame = frame
        #if camera:
        try:
            self.image_frame, Direction = NewEyeTracking._main_(self.image_frame)
            buffer = cv2.flip(self.image_frame, 0).tostring()
            texture = Texture.create(size=(self.image_frame.shape[1], self.image_frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture
            try:
                self.Looking = Direction
            except:
                pass
        except:
            img = cv2.imread('A_New_Black_image.png')
            self.image_frame = img
            buffer = cv2.flip(self.image_frame, 0).tostring()
            texture = Texture.create(size=(self.image_frame.shape[1], self.image_frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture
            self.Looking = "None"
    
    def SliderChange(self, instance, value):
        if value == 1:
            NewEyeTracking.IrisCenter_Change("Off")
            self.Type = "Normal"
        elif value == 2:
            NewEyeTracking.IrisCenter_Change("On")
            NewEyeTracking.Extremes_Change("Off")
            self.Type = "Iris"
        elif value == 3:
            NewEyeTracking.Extremes_Change("On")
            NewEyeTracking.WholeRightEyes_Change("Off")
            self.Type = "Extremes"
        elif value == 4:
            NewEyeTracking.WholeRightEyes_Change("On")
            NewEyeTracking.WholeFace_Change("Off")
            self.Type = "Entire Right Eye"
        elif value == 5:
            NewEyeTracking.WholeFace_Change("On")
            NewEyeTracking.WholeRightEyes_Change("Off")
            self.Type = "Entire Face"
    
    # Function for the togglable camera function, based on webcam statue
    def ToggleHand(self, button):
        if self.Hand == "Hand On":
            self.Hand = "Hand Off"
            NewEyeTracking.Hand_Tracking_Change("Off")
        elif self.Hand == "Hand Off":
            self.Hand = "Hand On"
            NewEyeTracking.Hand_Tracking_Change("On")

    def ToggleCamera(self, button):
        if self.Camera == "Camera On":
            self.Camera = "Camera Off"
            self.capture.release()
        elif self.Camera == "Camera Off":
            self.Camera = "Camera On"
            self.capture = cv2.VideoCapture(0)
    
    def ToggleMouse(self, button):
        if self.Mouse == "Mouse On":
            self.Mouse = "Mouse Off"
            NewEyeTracking.Change_mouseMove("Off")
        elif self.Mouse == "Mouse Off":
            self.Mouse = "Mouse On"
            NewEyeTracking.Change_mouseMove("On")

    # Switch the window themeing based on current theme
    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light")

if __name__ == '__main__':
    MainApp().run()