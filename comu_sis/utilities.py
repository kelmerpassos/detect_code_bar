from os import path

class Utils:
    
    @staticmethod
    def remove_next(text):
        if text[-1:] == '\n':
            if text[-2:] == '\\\n':
                return text[:-2] 
            return text[:-1]
        else:
            return text

    @staticmethod
    def add_next(text):
        return f'{text}\n'

    @staticmethod
    def redirect_and_save(dict_img, restrict, new_path, arq_log):
        for code, old_path in dict_img.items():
            if code not in restrict: 
                self.redirect_img(old_path, path.join(self.new_path, f'{code}.tif'))
                arq.write(f'{code}\n') 
        arq_log.close()

    @staticmethod
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