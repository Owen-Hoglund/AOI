import cv2
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
while True:
    ret, frame = cap.read()
    if ret == False:
        print("bad frame")
        continue
    else:
        print(ret)
    cv2.imshow('frame', frame)
    if cv2.waitKey(33) == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
