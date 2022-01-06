# Anonymous FTP login
from ftplib import FTP, error_perm
from io import BytesIO

ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('user', '12345')

print(ftp.getwelcome())


def get_files():
    try:
        files = ftp.nlst()
    except error_perm as resp:
        if str(resp) == "550 No files found":
            print("No files in this directory")
        else:
            raise

    return files


def download_file(filename):
    handle = open(f'data/{filename}', 'wb')
    ftp.retrbinary('RETR %s' % filename, handle.write)
    print('file downloaded')


def handle_binary(more_data, bio):
    bio.write(more_data)

def read_file(filename):
    bio = BytesIO()
    ftp.retrbinary('RETR %s' % filename, lambda x: handle_binary(x, bio))

    return bio.getvalue()