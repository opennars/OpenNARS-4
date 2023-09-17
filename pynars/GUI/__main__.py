import sys
from PySide6 import QtWidgets
from .MainWindow import apply_stylesheet, NARSWindow
from .Console import run_nars
from multiprocessing import Process
from qasync import QEventLoop
import asyncio
from time import sleep, time
from as_rpc import AioRpcClient, rpc

app = QtWidgets.QApplication(sys.argv)
# loop = asyncio.new_event_loop()
# async def foo():
#     print('foo')
# loop.create_task(foo())
# loop._ready
loop = QEventLoop(app)

asyncio.set_event_loop(loop)
# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')



window = NARSWindow()
p_nars = Process(target=run_nars, args=(1000, 1000))
p_nars.start()
# p_nars.join()


client = AioRpcClient(buff=6553500, mark='GUI')
timeout = 10
t_begin = time()
while True:
    try:
        client.init()
        break
    except ConnectionRefusedError as e:
        t_now = time()
        if t_now - t_begin <= timeout:
            sleep(1)
        else:
            raise TimeoutError("Cannot initialize NARS reasoner properly.")

window.set_client(client)

@rpc(client, "print_out")
def print_out(content):
    window.print_out(content)

# run
window.show()
with loop:
    loop.run_forever()