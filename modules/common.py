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


def turn_userinfo_to_dict(user):
    return {"id": user.id, "username": user.username, "role": user.roles[0].name, "email": user.email,
            "create_date": str(user.create_date)}

def turn_categoryinfo_to_dict(category):
    return {"id": category.id, "name": category.name, "basename":category.basename, "pub_date": str(category.pub_date)}


def turn_linkinfo_to_dict(link):
    return {"id": link.id, "name": link.name, "callback_url": link.callback_url, "pub_date": str(link.pub_date)}

def turn_taginfo_to_dict(tag):
    return {"id": tag.id, "name": tag.name, "pub_date": str(tag.pub_date)}

def turn_descinfo_to_dict(desc):
    return {"id": desc.id, "content": desc.content, "pub_date": str(desc.pub_date)}

if __name__ == '__main__':
    obj = get_datetime()
    print(obj)
