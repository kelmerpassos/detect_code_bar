import os
import shutil
from asyncio.windows_events import NULL
from os.path import isdir
from sys import exit

from cv2 import cv2
from pyzbar.pyzbar import decode


class BarCode:
    INPUT = 'input_img'
    OUTPUT = 'output_code'

    def __init__(self):
        super(BarCode, self).__init__()
        self.validade_paths()    
        input_path = [ # carrega todos os arquivos do input
            {'path': os.path.join(self.INPUT, name), 'name': name} 
            for name in os.listdir(self.INPUT)
        ]  
        output_path = [ # carrega todos os arquivos do output
            {'path': os.path.join(self.OUTPUT, name), 'name': name}
            for name in os.listdir(self.OUTPUT)
        ]  
        self.input_files = [ # filtra apenas os arquivos .bmp
            input_arq for input_arq in input_path 
            if os.path.isfile(input_arq['path']) and (input_arq['path'].lower().endswith('.bmp'))
        ]
        self.output_files = [ # filtra apenas os arquivos .ini
            output_arq for output_arq in output_path 
            if os.path.isfile(output_arq['path']) and (output_arq['path'].lower().endswith('.tif'))
        ] 

    def validade_paths(self):
        if not os.path.isdir(self.INPUT):
            os.mkdir(self.INPUT)
            if not os.path.isdir(self.OUTPUT):
                os.mkdir(self.OUTPUT)
            exit()
        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)
        if os.path.isfile(os.path.join(self.INPUT, 'dir.txt')):
            for dir_ex in open(os.path.join(self.INPUT, 'dir.txt'), 'r'):
                self.EX_OUTPUT = dir_ex[:-2]
                if self.EX_OUTPUT.strip(' ') == '':
                    self.create_dir_default()
                break
        else:
            self.create_dir_default()

    def create_dir_default(self):
        if not os.path.isdir('ordem'):
            os.mkdir('ordem')
            self.EX_OUTPUT = 'ordem'


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
        log_txt.writelines([f'{txt}\n' if txt  != self.log['error'][-1] else txt for txt in self.log['error']])
        log_txt.close() 
        log_txt = open(os.path.join(self.OUTPUT, 'success.txt'), 'w') 
        log_txt.writelines([f'{txt}\n' if txt != self.log['success'][-1] else txt for txt in self.log['success']])
        log_txt.close()  
        log_txt = open(os.path.join(self.OUTPUT, 'invalid.txt'), 'w') 
        log_txt.writelines([f'{txt}\n' if txt != self.log['invalid'][-1] else txt for txt in self.log['invalid']])
        log_txt.close()
        log_txt = open(os.path.join(self.OUTPUT, 'end.txt'), 'w') 
        log_txt.write(str(len(self.log['success'])))
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
