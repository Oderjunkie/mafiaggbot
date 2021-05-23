import asyncio
from asyncinit import asyncinit
from mafapi.roompointer import RoomPointer
from mafapi.user import User

@asyncinit
class Room:
    async def __init__(self, *args, **kwargs):
        from dateutil.parser import parse
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            elif len(args)>=number:
                return args[number]
            return fallback
        self.id = await helper(0, 'id')
        self.name = await helper(1, 'name')
        self.hasStarted = await helper(2, 'hasStarted')
        self.playerCount = await helper(3, 'playerCount')
        self.setupSize = await helper(4, 'setupSize')
        self.hostUser = await User(**await helper(5, 'hostUser'))
        self.createdAt = parse(await helper(6, 'createdAt'))
    def __dict__(self):
        return {'id': self.id, 'name': self.name, 'hasStarted': self.hasStarted,
                'playerCount': self.playerCount, 'setupSize': self.setupSize,
                'hostUser': self.hostUser, 'createdAt': self.createdAt}
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __list__(self):
        return [self.id, self.name, self.hasStarted, self.playerCount,
                self.setupSize, self.hostUser, self.createdAt]
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'Room({})'.format(kwargstr)
    async def getpointer(self, session):
        async with session.get('https://mafia.gg/api/rooms/{}'.format(self.id)) as pointer:
            json = await pointer.json()
            return await RoomPointer(**json)
