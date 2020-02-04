import os
from cv2 import cv2
from pyzbar.pyzbar import decode


class BarCode:
    path_input = 'input_img'
    path_output = 'output_code'

    def __init__(self):
        super(BarCode, self).__init__()
        input_path = [ # carrega todos os arquivos do input
            {'path': os.path.join(self.path_input, name), 'name': name} 
            for name in os.listdir(self.path_input)
        ]  
        output_path = [ # carrega todos os arquivos do output
            {'path': os.path.join(self.path_output, name), 'name': name}
            for name in os.listdir(self.path_output)
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

    def extract_barcode(self):
        for data in self.valid_files:
            image = cv2.imread(data['path']) 
            name = data['name'][:-4]      
            if image is not None:
                detectedBarcodes = decode(image)
            else:
                exit()

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
