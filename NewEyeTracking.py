import mediapipe as mp
import cv2
import math

### Varibles
Hand_Tracking = False
IrisCenter = False
Extremes = False
WholeRightEyes = False
WholeFace = False
mouseMove = False

### Functions associated with Varibles
def Hand_Tracking_Change(State):
    global Hand_Tracking
    if State == "Off":
        Hand_Tracking = False
    if State == "On":
        Hand_Tracking = True

def IrisCenter_Change(State):
    global IrisCenter
    if State == "Off":
        IrisCenter = False
    if State == "On":
        IrisCenter = True

def Extremes_Change(State):
    global Extremes
    if State == "Off":
        Extremes = False
    if State == "On":
        Extremes = True

def WholeRightEyes_Change(State):
    global WholeRightEyes
    if State == "Off":
        WholeRightEyes = False
    if State == "On":
        WholeRightEyes = True

def WholeFace_Change(State):
    global WholeFace
    if State == "Off":
        WholeFace = False
    if State == "On":
        WholeFace = True

def Change_mouseMove(State):
    global mouseMove
    if State == "Off":
        mouseMove = False
    if State == "On":
        mouseMove = True

# Calls on mediapipe to create a face mesh solution to make a face mesh (refine_landmarks allows landmarks to be numerated)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

hand_detector = mp.solutions.hands.Hands()
def _main_(image):

    HorizonalSafe = 7
    VerticalSafe = 3

    

    

    def get_x_y_av(landmarks):
        y1 = int(landmarks[443].y * frame_height)
        y2 = int(landmarks[450].y * frame_height)
        y_av = float((y1+y2)/2)
    
        x1 = int(landmarks[362].x * frame_width)
        x2 = int(landmarks[263].x * frame_width)
        x_av = float((x1+x2)/2)
    
        return y_av, x_av
    
    def getScale(landmarks):
        y1 = int(landmarks[443].y * frame_height)
        y2 = int(landmarks[450].y * frame_height)
        scale = (y1-y2)*0.01
        actualscale = 1 - (1-scale)
    
    def getDirection(right_iris_x, x_av, right_iris_y, y_av):
        if (int(right_iris_x) > int(x_av) + HorizonalSafe):
            print('Looking Right')
            if mouseMove == True:
                #pyautogui.move(20,0)
                pass
            return('Looking Right') 
          
        elif (int(right_iris_x) < int(x_av) - HorizonalSafe):
            print('Looking Left')
            if mouseMove == True:
                #pyautogui.move(-20,0)
                pass
            return('Looking Left')
        
        elif (int(right_iris_y) > int(y_av) + VerticalSafe):
            print('looking Down')
            if mouseMove == True:
                #pyautogui.move(0,20)
                pass
            return('Looking Down')

        elif (int(right_iris_y) < int(y_av) - VerticalSafe):
            print('Looking Up')
            if mouseMove == True:
                #pyautogui.move(0,-20)
                pass
            return('Looking Up')
    
        else:
            print("############")
            return("Looking Center")
    
    def getExtremes(landmarks):
        # Find the vertical extremes and find the center
        bottom_right_eye = int(landmarks[477].y * frame_height)
        top_right_eye = int(landmarks[475].y * frame_height)
        right_iris_y = float((bottom_right_eye+top_right_eye)/2)

        # Find the horizontal extremes and find the center
        left_right_eye = int(landmarks[476].x * frame_width)
        right_right_eye = int(landmarks[474].x * frame_width)
        right_iris_x = float((right_right_eye+left_right_eye)/2)
    
        return right_iris_x, right_iris_y
    
    def drawExtremes(landmarks):
        # 474 is the right most point
        # 475 is top most point
        # 476 is left most point
        # 477 is the bottom most point
        for id, point in enumerate(landmarks[474:478]):
        
            # Points plotted with regular mediapip gives coordinates/points from 0 to 1, which does not translate well to the frame
            # To fix this, we multiple the coordinates to the respective integers coorpsonding to the frame's height and width
            x = int(point.x * frame_width) 
            y = int(point.y * frame_height)

            # Draws a circle on the OpenCV frame (frame, coordinates, size, color)
            cv2.circle(frame, (x, y), 3, (255, 255, 0))
    
    # Draw all the points around the right eye
    def draw_eyes(righteye):
        # For every landmark in righteye (around the iris/eye), plot the point on the frame
        for id, point in enumerate(righteye):   
            # Points plotted with regular mediapip gives coordinates/points from 0 to 1, which does not translate well to the frame
            # To fix this, we multiple the coordinates to the respective integers coorpsonding to the frame's height and width
            x = int(point.x * frame_width) 
            y = int(point.y * frame_height)
            # Draws a circle on the OpenCV frame (frame, coordinates, size, color)
            cv2.circle(frame, (x, y), 3, (0, 0, 255))
    
    # Euclaidean distance
    def euclaideanDistance(point, point1):
        x, y = point
        x1, y1 = point1
        distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
        return distance
    
    # Find the blinking ratio for the left
    def blinkingRatio(landmarks):
        # Left Eye
        # Horizontal Lines
        rh_left = (landmarks[33].x * frame_width, landmarks[33].y * frame_height)
        rh_right = (landmarks[133].x * frame_width, landmarks[133].y * frame_height)
    
        # Verticle Lines
        rv_top = (landmarks[159].x * frame_width, landmarks[159].y * frame_height)
        rv_bottom = (landmarks[145].x * frame_width, landmarks[145].y * frame_height)
    
        # Find the distance between points for the left eye
        rhDistance = euclaideanDistance(rh_left, rh_right)
        rvDistance = euclaideanDistance(rv_top, rv_bottom)
    
        rightRatio = rhDistance/rvDistance
    
        #print(rightRatio)
        if int(rightRatio) > 20:
            print("Blink")
            if mouseMove == True:
                #pyautogui.click(button='left')
                pass

    def trackHead():
        global lefteye
        global righteye
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Gets the converted rgb_frame and inputs it to mediapipe's face_mesh
        output = face_mesh.process(rgb_frame)

        # Puts landmark points over the face mesh
        landmark_points = output.multi_face_landmarks

        # If mediapipe detects a face in the frame (if has landmark_points)
        if landmark_points:

            # Gets the first face mediapipe sees (index 0) and gets its landmark points
            landmarks = landmark_points[0].landmark
        
            # Extremes for the eyes
            # landmark[362] is left, landmark[263] is right landmark 386 (top) and 374 (bottom)
            lefteye = [landmarks[33], landmarks[159], landmarks[133], landmarks[145]] # The extremes for the left eye
            righteye = [landmarks[362],landmarks[386], landmarks[263],landmarks[374]] # The extremes for the right eye

            wholerighteye = [landmarks[384], landmarks[385], landmarks[386], landmarks[387], landmarks[388], landmarks[390], landmarks[373], landmarks[374], landmarks[380], landmarks[381],  landmarks[362], landmarks[382], landmarks[398]]
        
            # Get the x and y averages
            y_av, x_av = get_x_y_av(landmarks)
        
            # Get the distance scale
            actual_scale = getScale(landmarks)
        
            # Center of the averages
            average_center = (int(x_av), int(y_av))

            #cv2.circle(frame, (average_center), 1, (0,0,255), 2)
        
            # Find the extremes of the right eye
            right_iris_x, right_iris_y = getExtremes(landmarks)

            # The center of both extremes 
            center = (int(right_iris_x), int(right_iris_y))
            #cv2.circle(frame, (center), 1, (0,255,0), 2)
        
            # Find where the eye is looking and move the mouse
            Direction = getDirection(right_iris_x, x_av, right_iris_y, y_av)
        
            # Detect if the eye is blinking
            blinkingRatio(landmarks)
        
        
            # Draw the eyes if debug is true

            if WholeFace == True:
                for point in landmarks:   
                    # Points plotted with regular mediapip gives coordinates/points from 0 to 1, which does not translate well to the frame
                    # # To fix this, we multiple the coordinates to the respective integers coorpsonding to the frame's height and width
                    x = int(point.x * frame_width) 
                    y = int(point.y * frame_height)
                    # Draws a circle on the OpenCV frame (frame, coordinates, size, color)
                    cv2.circle(frame, (x, y), 3, (0, 0, 255))
            


            if IrisCenter == True:
                cv2.circle(frame, (average_center), 1, (0,0,255), 2)
                cv2.circle(frame, (center), 1, (0,255,0), 2)
            
            if WholeRightEyes == True:
                draw_eyes(wholerighteye)


            if Extremes == True:
                draw_eyes(righteye)
            
            return Direction
        # Shows a window with the frame on it ("Title Name", frame)
        # cv2.imshow('Eye controlled Mouse', frame)
        # Calls OpenCV to wait for 1 second for any key inputs from the user
        cv2.waitKey(1)
    
    def trackHand():
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks
        if hands:
            for hand in hands:
                landmarks = hand.landmark
                for point in landmarks:
                    x = int(point.x*frame_width)
                    y = int(point.y*frame_height)

                    cv2.circle(img=frame, center=(x,y), radius=3, color=(0, 0, 255))
        cv2.waitKey(1)
    





    
    frame = image

    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    frame = cv2.flip(frame, 1)
    if Hand_Tracking == False:
        Direction = trackHead()
    else:
        Direction = trackHand()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return rgb_frame, Direction