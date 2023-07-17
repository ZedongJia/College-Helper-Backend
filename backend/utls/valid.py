MALICE_SYMBOLS = ['\"', '\'', ';', '--', '#']

def filter_malice(pattern: str):
    r'''
    Filter str by removing ['\"', '\'', ';', '--', '#']
    '''
    for _s in MALICE_SYMBOLS:
        pattern = pattern.replace(_s, '')
    
    return pattern