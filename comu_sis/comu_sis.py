from utilities import Utils
from os import path, mkdir, name as os_name

class ComuSis:
    def __init__(self):
        self.INPUT = ''
        self.OUTPUT = ''
        self.EX_OUTPUT = ''
        self.path_log = '' 
        self.old_files = '' 

    def validate_type(self, temp_file):
        if temp_file.endswith('.bmp') or temp_file.endswith('.jpg') or temp_file.endswith('.png') or temp_file.endswith('.tif'):
            return True
        return False

    def validate_paths(self):        
        if not path.isdir(self.OUTPUT):
            mkdir(self.OUTPUT)
        if path.isfile(path.join(self.OUTPUT, 'dir.txt')):
            arq = open(path.join(self.OUTPUT, 'dir.txt'), 'r')
            for dir_ex in arq:
                self.EX_OUTPUT = Utils.remove_next(dir_ex)
                if self.EX_OUTPUT.strip(' ') == '':
                    self.EX_OUTPUT = self.create_dir_default('ordem')
                break
            arq.close()
        else:
            self.EX_OUTPUT = self.create_dir_default('ordem')
        if path.isfile(path.join(self.OUTPUT, 'input.txt')):
            arq = open(path.join(self.OUTPUT, 'input.txt'), 'r')
            for inp_ex in arq: 
                self.INPUT = Utils.remove_next(inp_ex)
                if self.INPUT.strip(' ') == '':
                    self.INPUT = self.create_dir_default('input_img')
                break
            arq.close()
        else:
            self.INPUT = self.create_dir_default('input_img')

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
        if path.isfile(path.join(self.OUTPUT, 'old_files.txt')):
            arq = open(path.join(self.OUTPUT, 'old_files.txt'), 'r')
            self.old_files = [Utils.remove_next(name.lower()) for name in arq]
            arq.close()
        else:
            self.old_files = ''
        return self.old_files


    def create_dir_default(self, name):
        if not path.isdir(name):
            mkdir(name)
        return path.join(path.dirname(path.realpath(__file__)),name)
