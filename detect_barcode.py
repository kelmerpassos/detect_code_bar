from cv2 import cv2
from pyzbar.pyzbar import decode

# construct the argument parse and parse the arguments
image = cv2.imread("C:\siscart\/temp\/tmpBarCodeTD.bmp")
if image is not None:
    detectedBarcodes = decode(image)
else:
    exit()

for barcode in detectedBarcodes:
     
    (x, y, w, h) = barcode.rect
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
  
    print(barcode.data)
    print(barcode.type)
    bar_file = open(f'bar-teste.txt', 'w')
    bar_file.write(barcode.data.decode('utf-8'))
    bar_file.close()

# Visualizar a imagem 
# cv2.imshow("Image", image)
  
cv2.waitKey(0)
cv2.destroyAllWindows()
