import websockets
import asyncio
from ConsolePlus import execute_input, output_history
from json import dumps


async def handler(websocket, path):
    print(f"Connected with path={path}!")
    messages2send = []
    len_outputs = 0
    last_output_json_obj = {}
    async for message in websocket:
        messages2send.clear()
        # execute
        execute_input(message)
        # handle output using json
        if len_outputs < len(output_history):
            # traverse newer outputs
            for i in range(len_outputs, len(output_history)):
                # data: (interface_name, output_type, content)
                # format: {"interface_name": XXX, "output_type": XXX, "content": XXX}
                (last_output_json_obj['interface_name'],
                 last_output_json_obj['output_type'],
                 last_output_json_obj['content']) = output_history[i]
                # send
                messages2send.append(dumps(last_output_json_obj))
        # send result if have
        for message2send in messages2send:
            print(f"send: {message} -> {message2send}")
            await websocket.send(message2send)
        # refresh output length
        len_outputs = len(output_history)


if __name__ == '__main__':
    # Config
    d_host = '127.0.0.1'
    host = input(f'Please input host (default {d_host}): ')
    host = host if len(host) > 0 else d_host

    d_port = 8765
    port = input(f'Please input port (default {d_port}): ')
    port = int(port) if port else d_port

    # Launch
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(handler, host, port)
    )
    print(f'WS server launched on {host}:{port}.')
    asyncio.get_event_loop().run_forever()
