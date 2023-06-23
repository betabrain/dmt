import libzt
import time
import sys
import socket

nwid = 0x12ac4a1e716906cf

# Authorization required via my.zerotier.com if this is a private network).
print('Joining virtual network...')
libzt.zts_startjoin(sys.argv[-1], nwid)

fd = libzt.zts_socket(socket.AF_INET,socket.SOCK_STREAM,0)
if fd < 0:
	print('error creating socket')
print('fd = ' + str(fd))

# Display info about this node
print('I am ' + str(hex(libzt.zts_get_node_id())))
address = None
libzt.zts_get_address(nwid, address, socket.AF_INET)
print('assigned address = ' + str(address))

print('Looping forever, ping me or something')
while True:
    time.sleep(1)

