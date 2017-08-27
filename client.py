from socket import *
import asyncio

@asyncio.coroutine
def create_connection(host,port, *, loop=None):
	reader, writer = yield from asyncio.open_connection(host, port, loop=loop)
	conn = RedisClient(reader, writer, loop=loop)
	return conn

class RedisClient:
	def __init__(self,reader,writer,loop=None):
		self._reader = reader
		self._writer = writer
		self._loop = loop
	def format_command(self,*tokens, **kwargs):
		cmds = []
		for t in tokens:
			cmds.append("$%s\r\n%s\r\n" % (len(t), t))
		return "*%s\r\n%s" % (len(tokens), "".join(cmds))
	def execute_command(self,cmd,*args,**kwargs):
		command = self.format_command(cmd,*args,**kwargs)
		self._writer.write(command.encode('utf-8'))
		yield from self._writer.drain()
		data = yield from self._reader.read(65536)
		return  data.decode('utf-8')  
	def set(self,key,value):
		result = self.execute_command("SET",key,value)
		return result
	def get(self,key):
		value = self.execute_command("GET",key)
		return value



def main():
    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def go():
        conn = yield from create_connection('localhost', 6379)

        ok = yield from conn.set('love', '123')

        value = yield from conn.get('love')
        print(value)

    loop.run_until_complete(go())
if __name__ == '__main__':
	main()
