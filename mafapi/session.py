from asyncinit import asyncinit
from mafapi.deckpointer import DeckPointer
from mafapi.deck import Deck
from mafapi.selfuser import SelfUser
from mafapi.user import User
from mafapi.room import Room
from mafapi.roompointer import RoomPointer
from mafapi.connection import Connection
import aiohttp
import asyncio

@asyncinit
class Session:
    """Session
    hi
    """
    def __init__(self, *args, **kwargs):
        self.username = ''
        self.password = ''
        self.user = None
        self.session = aiohttp.ClientSession()
    async def login(self, *args, **kwargs):
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            if len(args)>number:
                return args[number]
            return fallback
        self.username = await helper(0, 'username')
        self.password = await helper(1, 'password')
        post = {'login': self.username, 'password': self.password}
        url = 'https://mafia.gg/api/user-session'
        async with self.session.post(url, json=post) as resp:
            try:
                self.user = await SelfUser(**await resp.json())
                return self.user
            except Exception:
                return await resp.text()
    async def logout(self):
        await self.session.close()
        self.session = aiohttp.ClientSession()
    async def getAllRooms(self):
        async with self.session.get('https://mafia.gg/api/rooms') as resp:
            json = await resp.json()
            return [await Room(**desc) for desc in json['rooms']]
    async def getUnlistedCount(self):
        async with self.session.get('https://mafia.gg/api/rooms') as resp:
            json = await resp.json()
            return json['unlistedCount']
    async def getDeck(self, name):
        url = 'https://mafia.gg/api/decks?filter={}&page=1'.format(name)
        async with self.session.get(url) as resp:
            key = (await DeckPointer(**await resp.json())).decks[0].id
            url = 'https://mafia.gg/api/decks/{}'.format(key)
            async with self.session.get(url) as resp:
                return await Deck(**await resp.json())
    async def getDeckSamples(self, name):
        url = 'https://mafia.gg/api/decks?filter={}&page=1'.format(name)
        async with self.session.get(url) as resp:
            return await DeckPointer(**await resp.json())
    async def dereferenceRoomById(self, roomid):
        url = 'https://mafia.gg/api/rooms/{}'.format(roomid)
        async with self.session.get(url) as resp:
            return await RoomPointer(**await resp.json())
    async def dereferenceRoom(self, room: Room):
        return await self.dereferenceRoomById(room.id)
    async def joinRoom(self, room: Room):
        pointer = await self.dereferenceRoom(room)
        ws = await Connection(pointer, room.id, self)
        await ws.send({'type':'clientHandshake', 'userId':self.user.id, 'roomId':room.id, 'auth': pointer.auth})
        return ws
    async def joinRoomById(self, roomid):
        pointer = await self.dereferenceRoomById(roomid)
        ws = await Connection(pointer, roomid, self)
        await ws.send({'type':'clientHandshake', 'userId':self.user.id, 'roomId':roomid, 'auth': pointer.auth})
        return ws
    async def createRoom(self, roomname, unlisted):
        url = 'https://mafia.gg/api/rooms'
        post = {'name': roomname, 'unlisted': unlisted}
        async with self.session.post(url, json=post) as resp:
            return (await resp.json())['id']
    async def createRoomAndJoin(self, roomname, unlisted):
        return await self.joinRoomById(await self.createRoom(roomname, unlisted))
    async def blacklist(self, user):
        this = self.user
        return await self.session.patch('https://mafia.gg/api/user', json=
            {'email': this.email, 'hostBannedUsernames': [*this.hostBannedUsernames, user.username],
             'password': '', 'passwordConfirmation': '', 'patreonCode': None, 'timeFormat': this.timeFormat})
    async def getUser(self, userid):
        url = 'https://mafia.gg/api/users/{}'.format(userid)
        async with self.session.get(url) as resp:
            return await asyncio.gather(*(User(**part) for part in await resp.json()))
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return await self.close()
    async def close(self):
        return await self.session.close()
