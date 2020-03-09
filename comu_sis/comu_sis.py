from utilities import Utils
from os import path, mkdir, listdir, name as os_name

class ComuSis:
    def __init__(self, output):
        self.input = ''
        self.output = output
        self.img_output = ''
        self.path_log = ''
        self.log_tif = []
        self.old_files = ''
        self.validate_paths()
        self.list = []
        self.input_files = []

    def validate_type(self, temp_file):
        if temp_file.endswith('.bmp') or temp_file.endswith('.jpg') or temp_file.endswith('.png') or temp_file.endswith('.tif'):
            return True
        return False

    def validate_paths(self):        
        if not path.isdir(self.output):
            mkdir(self.output)
        if path.isfile(path.join(self.output, 'dir.txt')):
            arq = open(path.join(self.output, 'dir.txt'), 'r')
            for dir_ex in arq:
                self.img_output = Utils.remove_next(dir_ex)
                if self.img_output.strip(' ') == '':
                    self.img_output = self.create_dir_default('ordem')
                break
            arq.close()
        else:
            self.img_output = self.create_dir_default('ordem')
        if path.isfile(path.join(self.output, 'input.txt')):
            arq = open(path.join(self.output, 'input.txt'), 'r')
            for inp_ex in arq: 
                self.input = Utils.remove_next(inp_ex)
                if self.input.strip(' ') == '':
                    self.input = self.create_dir_default('input_img')
                break
            arq.close()
        else:
            self.input = self.create_dir_default('input_img')

        self.path_log = ''
        if path.isfile('logconfig.ini'):
            with open('logconfig.ini', 'r') as arq:
                self.path_log = Utils.remove_next(arq.readline()) 
                if path.isdir(self.path_log):
                    if path.isfile(path.join(self.path_log, 'log_tif.ini')):    
                        with open(path.join(self.path_log, 'log_tif.ini'), 'r') as arq_aux:
                            self.log_tif = [Utils.remove_next(name) for name in arq_aux]
                    else:
                        with open(path.join(self.path_log, 'log_tif.ini'), 'w') as arq_aux:
                            self.log_tif = []
                else:
                    self.path_log = ''
                    if path.isfile('log_tif.ini'):
                        with open('log_tif.ini', 'r') as arq_aux:
                            self.log_tif = [Utils.remove_next(name) for name in arq_aux]
                    else:    
                        with open('log_tif.ini', 'w') as arq_aux:
                            self.log_tif = []  
        else:
            with open('logconfig.ini', 'w') as arq:
                if path.isfile('log_tif.ini'):
                    with open('log_tif.ini', 'r') as arq_aux:
                        self.log_tif = [Utils.remove_next(name) for name in arq_aux]
                else:    
                    with open('log_tif.ini', 'w') as arq_aux:
                        self.log_tif = []
                if os_name != 'posix':
                    arq.write(path.abspath('')+'\\')
                else:
                    arq.write(path.abspath('')+'/')

        
    def get_old_files(self):
        if path.isfile(path.join(self.output, 'old_files.txt')):
            arq = open(path.join(self.output, 'old_files.txt'), 'r')
            self.old_files = [Utils.remove_next(name.lower()) for name in arq]
            arq.close()
        else:
            self.old_files = ''
        return self.old_files


    def create_dir_default(self, name):
        if not path.isdir(name):
            mkdir(name)
        return path.join(path.realpath(''),name)

    def map_files(self):
        self.list = listdir(self.input)
        return self.list

    def filter_valid(self):
        self.input_files = ( # filtra apenas os arquivos válidos
            {'path': os.path.join(self.input, name), 'name': name} 
            for name in self.list 
            if self.validate_type(name.lower()) and (os.path.join(self.input, name).lower() not in self.old_files) 
        )
        return self.input_files
    
    def get_file_log(self):
        arq = open(os.path.join(self.path_log, 'log_tif.ini'), 'a')
        return arq

    def finish(self, log, pdfs):
        log_txt = open(os.path.join(self.output, 'error.txt'), 'w') 
        log_txt.writelines([Utils.add_next(txt) if txt  != log['error'][-1] else txt for txt in log['error']])
        log_txt.close() 
        log_txt = open(os.path.join(self.output, 'success.txt'), 'w') 
        log_txt.writelines([Utils.add_next(txt) if txt != log['success'][-1] else txt for txt in log['success']])
        log_txt.close()  
        log_txt = open(os.path.join(self.output, 'invalid.txt'), 'w') 
        log_txt.writelines([Utils.add_next(txt) if txt != log['invalid'][-1] else txt for txt in log['invalid']])
        log_txt.close()
        if len(pdfs) > 0:
            self.input_files.extend(pdfs)
        log_txt = open(os.path.join(self.output, 'end.txt'), 'w') 
        log_txt.writelines([Utils.add_next(txt['path']) if txt['path'] != self.input_files[-1]['path'] else txt['path'] for txt in self.input_files])
        log_txt.close() 
