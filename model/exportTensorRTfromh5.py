from tensorflow.python.keras import models

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 첫 번째 GPU 사용

model = models('facenet_keras.h5')
model.export(format='engine', device=0)

#https://docs.ultralytics.com/ko/integrations/tensorrt/#configuring-int8-export
#https://wjs7347.tistory.com/71