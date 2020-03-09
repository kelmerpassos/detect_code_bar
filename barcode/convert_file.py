from pdf2image import convert_from_path
from PIL import Image
import io
from os import path


class ConvertFile:
    def __init__(self):
        self.pdfs = []
    
    def convert_tiff(self, temp_file, dest_file=None):
        if dest_file == None:
            pass
        elif path.isfile(dest_file):
            with open(dest_file, 'rb') as file1:
                b1 = io.BytesIO(file1.read())
                img1 = Image.open(b1)
                with open(temp_file, 'rb') as file2: 
                    b2 = io.BytesIO(file2.read())
                    img2 = Image.open(b2).convert('RGB')
                    img1.save(dest_file,format='TIFF', compression='tiff_lzw', save_all=True,append_images=[img2])
         
        else:
            img = Image.open(temp_file).convert('RGB')
            img.save(dest_file, format='TIFF', compression='tiff_lzw')

    def convert_pdfs(self, path, list_files=[], list_restriction=[]):
        self.pdfs = ( 
            {'path': path.join(path, name), 'name': name}  
            for name in list_files
            if name.lower().endswith('.pdf') and (path.join(path, name).lower() not in list_restriction)
        )
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
                list_files.append(f'{name_without_ext}({i}).jpg')
                i= i+1
        return list_files
