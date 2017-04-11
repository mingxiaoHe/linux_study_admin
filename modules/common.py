import os.path
import hashlib
import datetime

def get_md5_string(string):
    encrypt_obj = hashlib.md5(bytes('passwd', encoding='utf-8'))
    encrypt_obj.update(bytes(string, encoding='utf-8'))
    return encrypt_obj.hexdigest()


def turn_to_int(arg, default):
    try:
        arg = int(arg)
    except Exception as e:
        arg = default
    return arg

def turn_bytes_to_str(arg):
    return str(arg, encoding='utf-8')

def get_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    obj = get_datetime()
    print(obj)