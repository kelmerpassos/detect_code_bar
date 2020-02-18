import os
import shutil
from asyncio.windows_events import NULL
from os.path import isdir
from sys import exit

from cv2 import cv2
from pyzbar.pyzbar import decode


class BarCode:
    OUTPUT = 'output_code'

    def __init__(self):
        super(BarCode, self).__init__()
        self.validade_paths()
        self.get_old_files()    
        input_path = [ # carrega todos os arquivos do input
            {'path': os.path.join(self.INPUT, name), 'name': name} 
            for name in os.listdir(self.INPUT)
            if os.path.join(self.INPUT, name).lower() not in self.OLD_FILES
        ]  
        self.input_files = [ # filtra apenas os arquivos .bmp
            input_arq for input_arq in input_path 
            if os.path.isfile(input_arq['path']) and (input_arq['path'].lower().endswith('.bmp'))
        ]
        
    
    def remove_next(self, text):
        if text[-1:] == '\n':
            if text[-2:] == '\\\n':
                return text[:-2] 
            return text[:-1]
        else:
            return text

    def add_next(self, text):
        return f'{text}\n'
    
    def validade_paths(self):        
        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)
        if os.path.isfile(os.path.join(self.OUTPUT, 'dir.txt')):
            for dir_ex in open(os.path.join(self.OUTPUT, 'dir.txt'), 'r'):
                self.EX_OUTPUT = self.remove_next(dir_ex)
                if self.EX_OUTPUT.strip(' ') == '':
                    self.EX_OUTPUT = self.create_dir_default('ordem')
                break
        else:
            self.EX_OUTPUT = self.create_dir_default('ordem')
        if os.path.isfile(os.path.join(self.OUTPUT, 'input.txt')):
            for inp_ex in open(os.path.join(self.OUTPUT, 'input.txt'), 'r'): 
                self.INPUT = self.remove_next(inp_ex)
                if self.INPUT.strip(' ') == '':
                    self.INPUT = self.create_dir_default('input_img')
                break
        else:
            self.INPUT = self.create_dir_default('input_img')
   
    def get_old_files(self):
        if os.path.isfile(os.path.join(self.OUTPUT, 'old_files.txt')):
            self.OLD_FILES = [self.remove_next(name.lower()) for name in open(os.path.join(self.OUTPUT, 'old_files.txt'), 'r')]
        else:
            self.OLD_FILES = ''


    def create_dir_default(self, name):
        if not os.path.isdir(name):
            os.mkdir(name)
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),name)

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
                        if len(code[1:]) == 6:        
                            if code[1:] not in self.log['success']:
                                self.log['success'].append(code[1:])

                                shutil.copy(data['path'], os.path.join(self.EX_OUTPUT, f'{code[1:]}.tif'))
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
    
'''
from PIL import Image

img1 = Image.open(open("test2.tiff", 'rb'))
img2 = Image.open(open("test.tiff", 'rb'))

img1.save('C:\/Users\/Public\/Pictures\/Sample Pictures\/teste.tif',save_all=True,append_images=[img2])

https://www.devmedia.com.br/forum/como-pegar-via-delphi-a-data-de-criacao-do-arquivo/320595
'''