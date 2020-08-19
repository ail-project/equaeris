import ftplib


def ftp_access_test(aggressive, ip, port):
    ftp = ftplib.FTP()
    try:
        ftp.connect(ip, int(port))
    except ConnectionRefusedError:
        raise
    try:
        ftp.login("anonymous", "anonymous")
        return True, ("anonymous", "anonymous")
    except ftplib.error_perm:
        if aggressive:
            try:
                ftp.login("admin", "admin")
                return True, ("admin", "admin")
            except ftplib.error_perm:
                return False, None
        else:
            return False, None


def extract_ftp(ip, port, credentials, max_elements=500):
    global count
    count = 0
    ftp = ftplib.FTP()
    try:
        ftp.connect(ip, int(port))
    except ConnectionRefusedError:
        raise
    try:
        ftp.login(credentials[0], credentials[1])
    except ftplib.error_perm:
        raise
    extract_dir(ftp, max_elements)


def get_file(ftp, filename):
    try:
        ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)
    except:
        raise


def extract_dir(ftp, max_elements, dir=None, old_dir=None):
    global count
    if dir is not None:
        ftp.cwd(dir)
    data = []
    ftp.dir(data.append)
    for element in data:
        if element[0] == 'd':
            directory = element.split(" ")[-1]
            if dir is not None and count <= max_elements:
                extract_dir(ftp, max_elements, dir + "/" + directory, dir)
            elif count <= max_elements:
                extract_dir(ftp, max_elements, "/" + directory)
        else:
            filename = element.split(" ")[-1]
            get_file(ftp, filename)
            count += 1
        if count >= max_elements:
            return
    if old_dir is not None:
        ftp.cwd(old_dir)


print(ftp_access_test(True, "127.0.0.1", "21"))
extract_ftp("127.0.0.1", "21", ("anonymous", "anonymous"), 2)
