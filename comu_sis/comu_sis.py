class ComuSis:
    def __init__():
        self.INPUT = ''
        self.OUTPUT = ''
        self.EX_OUTPUT = ''
        self.path_log = '' 
        self.OLD_FILES = '' 

    def validate_type(self, temp_file):
        if temp_file.endswith('.bmp') or temp_file.endswith('.jpg') or temp_file.endswith('.png') or temp_file.endswith('.tif'):
            return True
        return False

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

        self.path_log = ''
        if os.path.isfile('logconfig.ini'):
            with open('logconfig.ini', 'r') as arq:
                self.path_log = self.remove_next(arq.readline()) 
                if os.path.isdir(self.path_log):
                    if os.path.isfile(os.path.join(self.path_log, 'log_tif.ini')):    
                        with open(os.path.join(self.path_log, 'log_tif.ini'), 'r') as arq_aux:
                            self.log_tif = [self.remove_next(name) for name in arq_aux]
                    else:
                        with open(os.path.join(self.path_log, 'log_tif.ini'), 'w') as arq_aux:
                            self.log_tif = []
                else:
                    self.path_log = ''
                    if os.path.isfile('log_tif.ini'):
                        with open('log_tif.ini', 'r') as arq_aux:
                            self.log_tif = [self.remove_next(name) for name in arq_aux]
                    else:    
                        with open('log_tif.ini', 'w') as arq_aux:
                            self.log_tif = []  
        else:
            with open('logconfig.ini', 'w') as arq:
                if os.path.isfile('log_tif.ini'):
                    with open('log_tif.ini', 'r') as arq_aux:
                        self.log_tif = [self.remove_next(name) for name in arq_aux]
                else:    
                    with open('log_tif.ini', 'w') as arq_aux:
                        self.log_tif = []
                arq.write(os.path.abspath('')+'\\')

        
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
