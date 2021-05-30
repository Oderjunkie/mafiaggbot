import asyncio
from asyncinit import asyncinit

class RoomNotFound(RuntimeError):
    pass

@asyncinit
class RoomPointer:
    async def __init__(self, *args, **kwargs):
        from dateutil.parser import parse
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            if len(args)>number:
                return args[number]
            return fallback
        if await helper(0, 'error') == 'notFound':
            raise RoomNotFound()
        self.engineUrl = await helper(0, 'engineUrl')
        self.auth = await helper(1, 'auth')
    def __dict__(self):
        return {'engineUrl': self.engineUrl, 'auth': self.auth}
    def __list__(self):
        return [self.engineUrl, self.auth]
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'RoomPointer({})'.format(kwargstr)
