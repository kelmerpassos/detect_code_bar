import os
import shutil
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
            sys.exit()
        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)

    def extract_barcode(self):
        log_error = []
        begin_txt = open(os.path.join(self.OUTPUT, 'begin.txt'), 'w')
        begin_txt.write(str(len(self.input_files))) 
        begin_txt.close()     
        for data in self.input_files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4] 
            detectedBarcodes = decode(image)
            code = 'None'
            code_type = 'None'     
            for barcode in detectedBarcodes:    
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5) 
                code_type = barcode.type
                if code_type == 'CODE39':               
                    code = barcode.data.decode('utf-8')
                else:
                    break
                try:
                    int(code)
                    shutil.copy(data['path'], os.path.join(self.OUTPUT, f'{code}.tif'))
                    break
                except ValueError:
                    log_error.append(data['path'])
            self.prompt_barcode(name, code, code_type)
        end_txt = open(os.path.join(self.OUTPUT, 'end.txt'), 'w') 
        for txt in log_error:
            end_txt.write(txt)
        end_txt.close()        

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
