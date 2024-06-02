import threading, socket
import os, sys, time, pickle
SIZE = 2048
FORMAT = 'utf-8'
port = 9998
c = socket.socket()
parpath = os.path.dirname(os.path.abspath(__file__))
rootpath = parpath + "\\clientroot\\"
normpath = os.path.normpath(rootpath)


def filedata(filepath: str) -> int:
    if os.path.exists(filepath):
        with open(filepath, 'rb') as handle:
            payload_data = pickle.dumps(handle.read())
            data = len(payload_data)
    return data

def listening(socket: socket.socket):
    global dataIn
    dataIn = False
    while dataIn == False:
        msg = socket.recv(2048).decode(FORMAT)
        msg_split = msg.split(' ')
        command = msg_split[0]
        if command == "UP_REQ":
            upload(socket, msg_split[1])
        elif not command:
            pass
        elif command == "FILESIZE":
            print('Filesize is', msg_split[1])
            global filesize
            filesize = int(msg_split[1])
            dataIn = True
        else:
            print('[SERVER]:', msg)


def talking(socket: socket.socket) -> None:
    while True:
        time.sleep(1)
        message = input(">> ")
        args = message.split()
        if len(args) == 0:
            args = [None]
        if args[0] == "DOWNLOAD":
            before = time.perf_counter()
            print("download function")
            #Audio/Video Download
            downloadAV(c, args[1])
            after = time.perf_counter()
            print(f"Downloaded in {after - before:0.4f} seconds")
        elif args[0] == "DOWNLOAD21":
            before = time.perf_counter()
            print("download function")
            # STRAT 2-1 Download
            download(c, args[1])
            if len(args) == 3:
                download(c, args[2])
            after = time.perf_counter()
            print(f"Downloaded in {after - before:0.4f} seconds")
            threadlisten = threading.Thread(target=listening, args=(c,))
            threadtalk = threading.Thread(target=talking, args=(c,))
            threadlisten.start()
            threadtalk.start()
            threadlisten.join()
            threadtalk.join()
        elif args[0] == "DOWNLOAD22":
            before = time.perf_counter()
            print("download function")
            # STRAT 2-2 Download
            download22(c, args[1], args[2])
        elif args[0] == "DOWNLOAD23":
            before = time.perf_counter()
            print("download function")
            # STRAT 2-3 Download
            download23(c, args[1], args[2])
            after = time.perf_counter()
            print(f"Downloaded in {after - before:0.4f} seconds")
        elif args[0] == "UPLOAD":
            before = time.perf_counter()
            print("upload function")
            upload(c, args[1])
            after = time.perf_counter()
            print(f"Uploaded in {after - before:0.4f} seconds")
        elif args[0] == "DELETE":
            print("delete function")
            delete(c, args[1])
        elif args[0] == "DIR":
            print("directory function")
            dir(c)
        elif args[0] == "DISCONNECT":
            socket.close()
            return
        else:
            pass


def connect(HOSTNAME: str, PORTNO: int):
    c.connect((HOSTNAME, PORTNO))
    print("Connection Successful")
    threadlisten = threading.Thread(target = listening, args = (c,))
    threadtalk = threading.Thread(target = talking, args = (c,))
    threadlisten.start()
    threadtalk.start()
    threadlisten.join()
    threadtalk.join()
    return threadtalk, threadlisten


#DOWNLOAD COMMANDS ---------- SCENARIO 1/STRATEGY 2-1 ----------------
def download(c: socket.socket, filename: str):
    print("Download request for", filename, "received")
    down_req = "DOWNLOAD21 "+filename
    c.send(down_req.encode(FORMAT))
    data = c.recv(SIZE).decode(FORMAT)
    c.send("ACK".encode(FORMAT))
    filepath = rootpath + filename
    file = open(filepath, "w")
    file.write(data)
    file.close()


#DOWNLOAD COMMANDS ---------- STRATEGY 2-2 ----------------
def download22(c: socket.socket, filename: str, filename2: str):
    print("Download request for", filename, "and", filename2, "received")
    down_req = "DOWNLOAD22 " + filename + " " + filename2
    c.send(down_req.encode(FORMAT))
    data = c.recv(SIZE).decode(FORMAT)
    filepath = rootpath + filename
    filepath2 = rootpath + filename2
    tempfilepath = rootpath + "temp"
    file = open(filepath, "w")
    file2 = open(filepath2, "w")
    tempfile = open(tempfilepath, "w")
    tempfile.write(data)
    tempfile.close()
    time.sleep(.25)
    filesize3 = filedata(tempfilepath)
    filesize2 = filesize3 - filesize
    i = 0
    while i < filesize2 - 8:
        file.write(data[i])
        i += 1
    while i < filesize3 - 20:
        file2.write(data[i])
        i += 1
    os.remove(tempfilepath)
    print(filesize)
    print(filesize2)


#DOWNLOAD COMMANDS ---------- STRATEGY 2-3 ----------------
def download23(c: socket.socket, filename: str, filename2: str):
    print("Download request for", filename, "and", filename2, "received")
    down_req = "DOWNLOAD23 " + filename + " " + filename2
    c.send(down_req.encode(FORMAT))
    data1 = c.recv(SIZE).decode(FORMAT)
    data2 = c.recv(SIZE).decode(FORMAT)
    filepath = rootpath + filename
    filepath2 = rootpath + filename2
    file = open(filepath, "w")
    file2 = open(filepath2, "w")
    time.sleep(.25)
    file.write(data1)
    file2.write(data2)


#DOWNLOAD COMMANDS ---------- AUDIO/VIDEO ----------------
def downloadAV(c: socket.socket, filename: str):
    print("Download request for", filename, "received")
    down_req = "DOWNLOAD "+filename
    c.send(down_req.encode(FORMAT))
    filepath = rootpath+filename
    i = 0
    data = []
    time.sleep(1.5)
    while i < filesize:
        packet = c.recv(SIZE)
        print(packet)
        data.append(packet)
        i += SIZE
    print("done")
    c.send("ACK".encode(FORMAT))
    data_arr = pickle.loads(b"".join(data))
    print(data_arr)
    with open(filepath, 'wb') as handle:
        handle.write(data_arr)
    dataIn = False


def upload(c: socket.socket, filename: str):
    print("Upload request for", filename, "received")
    up_req = "UPLOAD "+filename
    c.send(up_req.encode(FORMAT))
    filepath = rootpath + filename
    file = open(filepath, "r")
    data = file.read()
    file.close()
    c.send(data.encode(FORMAT))


def delete(c: socket.socket, filename: str):
    print("Delete request for", filename, "received")
    del_req = "DELETE "+filename
    c.send(del_req.encode(FORMAT))


def dir(c: socket.socket):
    print("The following files are on the server folder.")
    c.send("DIR".encode(FORMAT))


def main():
    if not os.path.exists(rootpath):
        os.makedirs(rootpath)
    os.chdir(rootpath)
    while True:
        command = input(">> ")
        argv = command.split()
        if argv[0] == "CONNECT":
            HOSTNAME = argv[1]
            if HOSTNAME == "localhost":
                HOSTNAME = socket.gethostname()
            PORTNO = int(argv[2])
            connect(HOSTNAME, PORTNO)

        elif argv[0] == "EXIT":
            sys.exit()
        else:
            print("Invalid Command")


if __name__ == "__main__":
    main()