import glob
import os
import shutil
from asyncio.windows_events import NULL
import io
from sys import exit
from cv2 import cv2
from pdf2image import convert_from_path
from PIL import Image
from pyzbar.pyzbar import decode


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
        if temp_file.endswith('.bmp') or temp_file.endswith('.jpg') or temp_file.endswith('.png'):
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
        if not os.path.isfile('log_tif.txt'):
            log = open('log_tif.txt', 'w')
            log.close()
            self.log_tif = []
        else:
            arq = open('log_tif.txt', 'r')
            self.log_tif = [self.remove_next(name) for name in arq]
            arq.close()
        
   
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

    def extract_barcode(self):
        print('Extraindo código de imagens ...')
        self.log = {'error':[], 'success': [], 'invalid': []}
        begin_txt = open(os.path.join(self.OUTPUT, 'begin.txt'), 'w')
        begin_txt.write(str(len(self.input_files))) 
        begin_txt.close()     
        for data in self.input_files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4] 
            detectedBarcodes = decode(image)
            code = 'None'
            code_type = 'None'
            file_error = NULL 
            if len(detectedBarcodes) != 0:    
                for barcode in detectedBarcodes:    
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5) 
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
                                    arq = open('log_tif.txt', 'a')
                                    arq.write(f'{code}\n') 
                                    arq.close()  
                            file_error = NULL
                            break
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
    
