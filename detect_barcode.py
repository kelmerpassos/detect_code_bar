import os
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
            if os.path.isfile(output_arq['path']) and (output_arq['path'].lower().endswith('.ini'))
        ]
        self.valid_files = [
            valid_arq for valid_arq in self.input_files 
            if self.validate_file(valid_arq)
        ]    

    def validate_file(self, valid_arq):
        name = valid_arq['name']
        output_file = [
            output for output in self.output_files 
            if output['name'] == f'bar-{name[:-4]}.ini'
        ]
        if len(output_file) == 0:
            return True
        return False 

    def validade_paths(self):
        if not os.path.isdir(self.INPUT):
            os.mkdir(self.INPUT)
            if not os.path.isdir(self.OUTPUT):
                os.mkdir(self.OUTPUT)
            sys.exit()
        if not os.path.isdir(self.OUTPUT):
            os.mkdir(self.OUTPUT)

    def extract_barcode(self):
        for data in self.valid_files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4] 
            detectedBarcodes = decode(image)     
            if len(detectedBarcodes) == 0:
                bar_file = open(f'output_code\/bar-{name}.ini', 'w')
                bar_file.write('None')
                bar_file.close()
                self.prompt_barcode(name, 'None', 'None')
                next

            for barcode in detectedBarcodes:    
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
                bar_file = open(f'output_code\/bar-{name}.ini', 'w')
                code = barcode.data.decode('utf-8')
                bar_file.write(code)
                bar_file.close()
                self.prompt_barcode(name, code, barcode.type)

    def prompt_barcode(self, name, code, type_bar):
        print(f'Arquivo: {name}')
        print(f'Tipo-bar: {type_bar}')
        print(f'Name: {name}')
        print('________________________________')


if __name__ == "__main__":       
    bar_code = BarCode()
    bar_code.extract_barcode()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
