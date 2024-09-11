from utils.utils import faceAlignment, faceDetection, faceRepresentation, verifyFace
import cv2
import os


image_path ='img3.jpg'
image = cv2.imread(image_path)
verifyFace_path ='img.jpg'
verifyFaceImg = cv2.imread(verifyFace_path)

# 얼굴 검출
faces = faceDetection(image)
verified = []
detectedVerifiedFace = faceDetection(verifyFaceImg)[0]
verifiedFace = faceAlignment(verifyFaceImg,detectedVerifiedFace)
verified.append(faceRepresentation(verifiedFace))

for face in faces:
    try:
        rotated = faceAlignment(image, face)
        embedding = faceRepresentation(rotated)
        if(verifyFace(embedding, verified)==False):
            print("블러처리 하지 않음")
        else:
            print("블러처리함")
        cv2.imshow('Face', rotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except ValueError as e:
        print("오류 발생:", e)
        continue