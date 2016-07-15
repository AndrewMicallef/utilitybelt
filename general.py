#python3

def log(x, **kwargs):
    import datetime
    today = datetime.datetime.today().strftime('%Y%m%d')
    with open('log_%s.txt' %today, 'a') as f: 
        print(x, file = f, **kwargs)