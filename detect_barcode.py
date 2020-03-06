import os
from asyncio.windows_events import NULL
import io
from sys import exit
from cv2 import cv2
from pdf2image import convert_from_path
from PIL import Image
from pyzbar.pyzbar import decode
from numpy import array as np_array 


class BarCode:
    OUTPUT = 'output_code'

    def __init__(self):
        super(BarCode, self).__init__()
        self.validate_paths()
        self.get_old_files()
        self.list = os.listdir(self.INPUT)  
        self.convert_pdfs()
        self.list = set(self.list)   
        self.input_files = [ # filtra apenas os arquivos válidos
            {'path': os.path.join(self.INPUT, name), 'name': name} 
            for name in self.list 
            if self.validate_type(name.lower()) and (os.path.join(self.INPUT, name).lower() not in self.OLD_FILES) 
        ]

    def convert_pdfs(self):
        self.pdfs = [ 
            {'path': os.path.join(self.INPUT, name), 'name': name}  
            for name in self.list
            if name.lower().endswith('.pdf') and (os.path.join(self.INPUT, name).lower() not in self.OLD_FILES)
        ]
        for pdf in self.pdfs:
            name = pdf['name']
            print(f'Convertendo: {name}')
            pages = convert_from_path(pdf['path'], 500)
            i=1
            for page in pages:
                print(f'Extraindo página {i}')
                path_without_ext = pdf['path'][:-4]  
                name_without_ext = pdf['name'][:-4]    
                page.save(f'{path_without_ext}({i}).jpg', 'JPEG')
                self.list.append(f'{name_without_ext}({i}).jpg')
                i= i+1
        

    def validate_type(self, temp_file):
        if temp_file.endswith('.bmp') or temp_file.endswith('.jpg') or temp_file.endswith('.png') or temp_file.endswith('.tif'):
            return True
        return False

    def remove_next(self, text):
        if text[-1:] == '\n':
            if text[-2:] == '\\\n':
                return text[:-2] 
            return text[:-1]
        else:
            return text

    def add_next(self, text):
        return f'{text}\n'
    
    def validate_paths(self):        
        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)
        if os.path.isfile(os.path.join(self.OUTPUT, 'dir.txt')):
            arq = open(os.path.join(self.OUTPUT, 'dir.txt'), 'r')
            for dir_ex in arq:
                self.EX_OUTPUT = self.remove_next(dir_ex)
                if self.EX_OUTPUT.strip(' ') == '':
                    self.EX_OUTPUT = self.create_dir_default('ordem')
                break
            arq.close()
        else:
            self.EX_OUTPUT = self.create_dir_default('ordem')
        if os.path.isfile(os.path.join(self.OUTPUT, 'input.txt')):
            arq = open(os.path.join(self.OUTPUT, 'input.txt'), 'r')
            for inp_ex in arq: 
                self.INPUT = self.remove_next(inp_ex)
                if self.INPUT.strip(' ') == '':
                    self.INPUT = self.create_dir_default('input_img')
                break
            arq.close()
        else:
            self.INPUT = self.create_dir_default('input_img')

        self.path_log = ''
        if os.path.isfile('logconfig.ini'):
            with open('logconfig.ini', 'r') as arq:
                self.path_log = self.remove_next(arq.readline()) 
                if os.path.isdir(self.path_log):
                    if os.path.isfile(os.path.join(self.path_log, 'log_tif.ini')):    
                        with open(os.path.join(self.path_log, 'log_tif.ini'), 'r') as arq_aux:
                            self.log_tif = [self.remove_next(name) for name in arq_aux]
                    else:
                        with open(os.path.join(self.path_log, 'log_tif.ini'), 'w') as arq_aux:
                            self.log_tif = []
                else:
                    self.path_log = ''
                    if os.path.isfile('log_tif.ini'):
                        with open('log_tif.ini', 'r') as arq_aux:
                            self.log_tif = [self.remove_next(name) for name in arq_aux]
                    else:    
                        with open('log_tif.ini', 'w') as arq_aux:
                            self.log_tif = []  
        else:
            with open('logconfig.ini', 'w') as arq:
                if os.path.isfile('log_tif.ini'):
                    with open('log_tif.ini', 'r') as arq_aux:
                        self.log_tif = [self.remove_next(name) for name in arq_aux]
                else:    
                    with open('log_tif.ini', 'w') as arq_aux:
                        self.log_tif = []
                arq.write(os.path.abspath('')+'\\')
            
           
    def get_old_files(self):
        if os.path.isfile(os.path.join(self.OUTPUT, 'old_files.txt')):
            arq = open(os.path.join(self.OUTPUT, 'old_files.txt'), 'r')
            self.OLD_FILES = [self.remove_next(name.lower()) for name in arq]
            arq.close()
        else:
            self.OLD_FILES = ''


    def create_dir_default(self, name):
        if not os.path.isdir(name):
            os.mkdir(name)
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),name)

    def redirect_img(self, temp_file, code_file):
        if os.path.isfile(code_file):
            file1 = open(code_file, 'rb')
            b1 = io.BytesIO(file1.read())
            img1 = Image.open(b1)
            file2 = open(temp_file, 'rb') 
            b2 = io.BytesIO(file2.read())
            img2 = Image.open(b2).convert('RGB')
            img1.save(code_file,format='TIFF', compression='tiff_lzw', save_all=True,append_images=[img2])
            file1.close()
            file2.close()
         
        else:
            img = Image.open(temp_file).convert('RGB')
            img.save(code_file, format='TIFF', compression='tiff_lzw')

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
               detectedBarcodes = NULL
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
        self.log = {'error':[], 'success': [], 'invalid': []}
        begin_txt = open(os.path.join(self.OUTPUT, 'begin.txt'), 'w')
        begin_txt.write(str(len(self.input_files))) 
        begin_txt.close()     
        for data in self.input_files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4] 
            detectedBarcodes = self.detect_bar(image)
            code = 'None'
            code_type = 'None'
            file_error = NULL 
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
                        if code not in self.log['success']:
                            self.log['success'].append(code)
                            if code not in self.log_tif: 
                                self.redirect_img(data['path'], os.path.join(self.EX_OUTPUT, f'{code}.tif'))
                                arq = NULL
                                if self.path_log == '':
                                    arq = open('log_tif.ini', 'a')
                                else:
                                    arq = open(os.path.join(self.path_log, 'log_tif.ini'), 'a')
                                arq.write(f'{code}\n') 
                                arq.close()  
                    else:
                        if data['path'] not in self.log['error']:
                            file_error = data['path']
                except ValueError:
                    if data['path'] not in self.log['error']:
                        file_error = data['path']
                if file_error is not NULL:
                    self.log['error'].append(file_error) 
            else:
                if data['path'] not in self.log['invalid']:
                    self.log['invalid'].append(data['path'])
            self.prompt_barcode(name, code, code_type)
        self.finish()
         
    def finish(self):
        log_txt = open(os.path.join(self.OUTPUT, 'error.txt'), 'w') 
        log_txt.writelines([self.add_next(txt) if txt  != self.log['error'][-1] else txt for txt in self.log['error']])
        log_txt.close() 
        log_txt = open(os.path.join(self.OUTPUT, 'success.txt'), 'w') 
        log_txt.writelines([self.add_next(txt) if txt != self.log['success'][-1] else txt for txt in self.log['success']])
        log_txt.close()  
        log_txt = open(os.path.join(self.OUTPUT, 'invalid.txt'), 'w') 
        log_txt.writelines([self.add_next(txt) if txt != self.log['invalid'][-1] else txt for txt in self.log['invalid']])
        log_txt.close()
        if len(self.pdfs) > 0:
            self.input_files.extend(self.pdfs)
        log_txt = open(os.path.join(self.OUTPUT, 'end.txt'), 'w') 
        log_txt.writelines([self.add_next(txt['path']) if txt['path'] != self.input_files[-1]['path'] else txt['path'] for txt in self.input_files])
        log_txt.close() 
        
    def prompt_barcode(self, name, code, type_bar):
        print(f'Arquivo: {name}')
        print(f'Tipo-bar: {type_bar}')
        print(f'Code: {code}')
        print('________________________________')

if __name__ == "__main__":       
    bar_code = BarCode()
    bar_code.extract_barcode()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
