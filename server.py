import socket
import threading
import os, time, pickle

parpath = os.path.dirname(os.path.abspath(__file__))
rootpath = parpath + "\\serverroot\\"
HOSTNAME = socket.gethostbyname(socket.gethostname())
PORT_NO = 9998
SIZE = 2048
FORMAT = "utf-8"
SOCKS = []


def filedata(filepath: str) -> int:
    if os.path.exists(filepath):
        with open(filepath, 'rb') as handle:
            payload_data = pickle.dumps(handle.read())
            data = len(payload_data)
    return data


def get_file_metadata(filePath: str) -> dict:
    metadata = {"FILENAME": "", "DATASIZE": 0, "TIMESTAMP": 0, "NUM_DOWNLOADS": 0,
                'FILENAME': os.path.split(filePath)[1]}
    with open(filePath, 'rb') as handle:
        handle.seek(0,2)
        metadata['DATASIZE'] = handle.tell()
    metadata['TIMESTAMP'] = os.path.getmtime(filePath)
    return metadata


# Listen for a message from the client
def listen_fn(conn: socket.socket):
    print(SOCKS)
    while True:
        msg = conn.recv(SIZE).decode(FORMAT)
        print(msg)
        msg_split = msg.split(' ')
        # Get command from Client
        command = msg_split[0]

        # If command is DIR
        if (command == "DIR"):
            for entry in os.listdir(rootpath):
                conn.send(entry.encode(FORMAT))
                time.sleep(.1)

        # If command is DELETE
        if (command == "DELETE"):
            filename = msg_split[1]
            filepath = rootpath + filename
            os.remove(filepath)
            conn.send("ACK".encode(FORMAT))

        # If command is UPLOAD
        if (command == "UPLOAD"):
            filename = msg_split[1]
            filepath = rootpath + filename
            file = open(filepath, "w")
            data = conn.recv(SIZE).decode(FORMAT)
            conn.send("ACK".encode(FORMAT))
            file.write(data)
            file.close()
            print("file made")

# DOWNLOAD COMMANDS ---------- SCENARIO 1/STRATEGY 2-1 ----------------
        # If command is DOWNLOAD
        if (command == "DOWNLOAD21"):
            for filename in msg_split[1:]:
                print('Receiving filename:', filename)
                filepath = rootpath + "\\" + filename
                files = list_root()
                # Look for the file
                if (files.count(filename) == 1):
                    # File found on server
                    conn.send("File was found on the Server".encode(FORMAT))
                    file = open(filepath, "r")
                    data = file.read()
                    conn.send(data.encode(FORMAT))
                    file.close()
                    msg = conn.recv(SIZE).decode(FORMAT)
                    print('[CLIENT]:', msg)
                else:
                    # File NOT on server
                    if len(SOCKS) == 1:
                        # Client 2 is NOT connected
                        conn.send("File NOT found on server and no other client".encode(FORMAT))
                    if len(SOCKS) == 2:
                        # Client 2 is connected ask them to upload
                        client2 = SOCKS[SOCKS.index(conn) ^ 1]
                        up_req = "UP_REQ "+filename
                        client2.send(up_req.encode(FORMAT))
                        conn.send("Requesting file from other client".encode(FORMAT))
                        time.sleep(.25)
                        file = open(filepath, "r")
                        data = file.read()
                        conn.send(data.encode(FORMAT))
                        file.close()
                        os.remove(filepath)
                        msg = conn.recv(SIZE).decode(FORMAT)
                        print('[CLIENT]:', msg)


# DOWNLOAD COMMANDS ---------- STRATEGY 2-2 ----------------
        # If command is DOWNLOAD
        if (command == "DOWNLOAD22"):
            payload = ""
            for filename in msg_split[1:]:
                print('Receiving filename:', filename)
                filepath = rootpath + "\\" + filename
                files = list_root()
                # Look for the file
                if (files.count(filename) == 1):
                    # File found on server
                    file = open(filepath, "r")
                    data = file.read()
                    filesize = filedata(filepath)
                    print(filesize)
                    strfilesize = str(filesize)
                    strfilesize = "FILESIZE "+strfilesize
                    conn.send(strfilesize.encode(FORMAT))
                    file.close()
                    payload += data

                else:
                    # File NOT on server
                    if len(SOCKS) == 1:
                        # Client 2 is NOT connected
                        conn.send("File NOT found on server and no other client".encode(FORMAT))
                    if len(SOCKS) == 2:
                        # Client 2 is connected ask them to upload
                        client2 = SOCKS[SOCKS.index(conn) ^ 1]
                        up_req = "UP_REQ "+filename
                        client2.send(up_req.encode(FORMAT))
                        time.sleep(.25)
                        file = open(filepath, "r")
                        data = file.read()
                        payload += data
                        file.close()
                        os.remove(filepath)
                payload += "\n"
            conn.send(payload.encode(FORMAT))


# DOWNLOAD COMMANDS ---------- STRATEGY 2-3 ----------------
        # If command is DOWNLOAD
        if (command == "DOWNLOAD23"):
            for filename in msg_split[1:]:
                print('Receiving filename:', filename)
                filepath = rootpath + "\\" + filename
                files = list_root()
                # Look for the file
                if (files.count(filename) == 1):
                    # File found on server
                    file = open(filepath, "r")
                    data1 = file.read()
                    filesize = filedata(filepath)
                    print(filesize)
                    strfilesize = str(filesize)
                    strfilesize = "FILESIZE "+strfilesize
                    conn.send(strfilesize.encode(FORMAT))
                    file.close()
                else:
                    # File NOT on server
                    if len(SOCKS) == 1:
                        # Client 2 is NOT connected
                        conn.send("File NOT found on server and no other client".encode(FORMAT))
                    if len(SOCKS) == 2:
                        # Client 2 is connected ask them to upload
                        client2 = SOCKS[SOCKS.index(conn) ^ 1]
                        up_req = "UP_REQ "+filename
                        client2.send(up_req.encode(FORMAT))
                        time.sleep(.25)
                        file = open(filepath, "r")
                        data2 = file.read()
                        file.close()
                        os.remove(filepath)

            conn.send(data1.encode(FORMAT))
            conn.send(data2.encode(FORMAT))


# DOWNLOAD COMMANDS ---------- AUDIO/VIDEO ----------------
        # If command is DOWNLOAD
        if (command == "DOWNLOAD"):
            for filename in msg_split[1:]:
                print('Receiving filename:', filename)
                filepath = rootpath + "\\" + filename
                files = list_root()
                # Look for the file
                if (files.count(filename) == 1):
                    # File found on server
                    filesize = filedata(filepath)
                    print(filesize)
                    strfilesize = str(filesize)
                    strfilesize = "FILESIZE "+strfilesize
                    conn.send(strfilesize.encode(FORMAT))
                    with open(filepath, 'rb') as handle:
                        payload_data = pickle.dumps(handle.read())
                    conn.send(payload_data)
                    msg = conn.recv(SIZE).decode(FORMAT)
                    print('[CLIENT]:', msg)
                else:
                    # File NOT on server
                    if len(SOCKS) == 1:
                        # Client 2 is NOT connected
                        conn.send("File NOT found on server and no other client".encode(FORMAT))
                    if len(SOCKS) == 2:
                        # Client 2 is connected ask them to upload
                        client2 = SOCKS[SOCKS.index(conn) ^ 1]
                        up_req = "UP_REQ "+filename
                        client2.send(up_req.encode(FORMAT))
                        conn.send("Requesting file from other client".encode(FORMAT))
                        time.sleep(.25)
                        filesize = filedata(filepath)
                        print(filesize)
                        strfilesize = str(filesize)
                        strfilesize = "FILESIZE " + strfilesize
                        conn.send(strfilesize.encode(FORMAT))
                        with open(filepath, 'rb') as handle:
                            payload_data = pickle.dumps(handle.read())
                        conn.send(payload_data)
                        os.remove(filepath)
                        msg = conn.recv(SIZE).decode(FORMAT)
                        print('[CLIENT]:', msg)


def new_client(sock: socket.socket, addr):
    print("Connection established with:", addr)
    listen_thread_1 = threading.Thread(target=listen_fn, args=(sock,))
    listen_thread_1.start()


def list_root():
    files = os.listdir(rootpath)
    return files


def main():
    if not os.path.exists(rootpath):
        os.makedirs(rootpath)
    os.chdir(rootpath)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOSTNAME, PORT_NO))
    print('Server hosted at', HOSTNAME, 'Port:', PORT_NO)

    server_socket.listen(2)
    print('Waiting for connections...')

    while True:
        client_socket, addr = server_socket.accept()
        SOCKS.append(client_socket)
        new_client(client_socket, addr)


if __name__ == "__main__":
    main()