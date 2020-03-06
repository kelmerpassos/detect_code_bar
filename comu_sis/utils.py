def remove_next(self, text):
    if text[-1:] == '\n':
        if text[-2:] == '\\\n':
            return text[:-2] 
        return text[:-1]
    else:
        return text

def add_next(self, text):
    return f'{text}\n'