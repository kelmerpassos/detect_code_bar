from log_bar import LogBar
from cv2 import cv2
from pyzbar.pyzbar import decode
from numpy import array as np_array 

class ExtractBarCode:
    def __init__(self, files):
        self.log = LogBar()
        self.files = files
        self.img_redirect = []

    def extract_black(self, image):
        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # define range of black color in HSV
        lower_val = np_array([0,0,0])
        upper_val = np_array([179,255,127])
        # Threshold the HSV image to get only black colors
        mask = cv2.inRange(hsv, lower_val, upper_val)
        # invert mask to get black symbols on white background
        mask_inv = cv2.bitwise_not(mask)
        return mask_inv
    
    def detect_bar(self, image):
        detectedBarcodes = decode(self.extract_black(image))
        if len(detectedBarcodes) == 0:
           detectedBarcodes = decode(image)
           if len(detectedBarcodes) == 0:
               detectedBarcodes = None
        return detectedBarcodes 
    
    def most_likely_barcode(self, list_detect):
        new_list_detect = []
        for i, barcode in  enumerate(list_detect):
            (x, y, w, h) = barcode.rect
            base = abs(x-(x+w))
            height = abs(y-(y+h))
            area = base*height
            new_list_detect.append((i, area))
        index = max(new_list_detect, key=lambda x: x[1])
        return list_detect[index[0]]

    def extract_barcode(self):
        print('Extraindo código de imagens ...')  
        for data in self.files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4] 
            detectedBarcodes = self.detect_bar(image)
            code = 'None'
            code_type = 'None'
            file_error = None 
            if detectedBarcodes:    
                barcode = self.most_likely_barcode(detectedBarcodes)    
                # (x, y, w, h) = barcode.rect
                # cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5) 
                code_type = barcode.type
                if code_type == 'CODE39':               
                    code = barcode.data.decode('utf-8')
                else:
                    code = 'Inválido'
                try:
                    int(code)
                    code = code[1:]
                    if len(code) == 6:        
                        if code not in self.log.sucess:
                            self.log.sucess.append(code)
                            self.img_redirect.append({code: data['path']}) 
                    else:
                        if data['path'] not in self.log.error:
                            file_error = data['path']
                except ValueError:
                    if data['path'] not in self.log.error:
                        file_error = data['path']
                if file_error is not None:
                    self.log.error.append(file_error) 
            else:
                if data['path'] not in self.log.invalid:
                    self.log.invalid.append(data['path'])
            self.prompt_barcode(name, code, code_type)
        return self.log, self.img_redirect

    def prompt_barcode(self, name, code, type_bar):
        print(f'Arquivo: {name}')
        print(f'Tipo-bar: {type_bar}')
        print(f'Code: {code}')
        print('________________________________')