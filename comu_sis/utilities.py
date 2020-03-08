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