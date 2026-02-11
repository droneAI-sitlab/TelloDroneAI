from djitellopy import tello
import cv2

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()

while True:
    frame_read = me.get_frame_read()
    img = frame_read.frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow("Tello Camera", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
me.streamoff()