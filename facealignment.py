def getFacialLandmarks(img, face):
    baseImg = img.copy()

    dlib_box = dlib.rectangle(int(face[0]), int(face[1]), int(face[2]), int(face[3]))
    
    landmarkDetector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    landmarks=landmarkDetector(img,dlib_box)
    landmarksTuples = []
    for i in range(0,68):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        landmarksTuples.append((x,y))
        cv2.circle(baseImg,(x,y),2,(255,255,255),-1)
    
    routes = [i for i in range(16,-1,-1)] + [i for i in range(17,26+1)] +[16]
    routesCrd = []

    for i in range(0, len(routes)-1):
        sourcePoint = routes[i]
        targetPoint = routes[i+1]

        sourceCrd = landmarksTuples[sourcePoint]
        targetCrd = landmarksTuples[targetPoint]

        routesCrd.append(sourceCrd)

        cv2.line(baseImg, sourceCrd, targetCrd, (255,255,255),2)

    routesCrd = routesCrd + [routesCrd[0]]
    mask = np.zeros((img.shape[0],img.shape[1]))
    mask = cv2.fillConvexPoly(mask, np.array(routesCrd),1)
    mask = mask.astype(np.bool_)
    out = np.zeros_like(img)
    out[mask] = img[mask]

    # 회전 각도 계산
    delta_y = abs(landmarksTuples[44][1] - landmarksTuples[38][1])
    delta_x = abs(landmarksTuples[44][0] - landmarksTuples[38][0])
    angle = np.arctan2(delta_y, delta_x)
    angle_degrees = np.degrees(angle)

    # 이미지 회전
    (h, w) = out.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle_degrees, 1.0)
    rotated = cv2.warpAffine(out, M, (w, h), flags=cv2.INTER_CUBIC)

    # 결과 저장 또는 표시
    cv2.imwrite('aligned_face_image.jpg', rotated)
    cv2.imshow('Aligned Face', rotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()