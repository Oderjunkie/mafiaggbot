#  >>> from datetime import datetime
#  >>> datetime.fromtimestamp(1246126)
#  datetime.datetime(1970, 1, 15, 13, 8, 46)
#  >>> datetime.timestamp(datetime.fromtimestamp(1246126))
#  1246126.0

import asyncio
from asyncinit import asyncinit
from mafapi.deckcharacter import DeckCharacter

@asyncinit
class Deck:
    async def __init__(self, *args, **kwargs):
        from datetime import datetime
        #print(args, kwargs)
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            elif len(args)>=number:
                return args[number]
            return fallback
        async def callfunc(func):
            async def inner(args=[], kwargs={}):
                if type(kwargs) == list != type(args):
                    tmp = kwargs
                    kwargs = {**args}
                    args = [*tmp]
                if type(kwargs) == type(args) == dict:
                    kwargs = {**args, **kwargs}
                    args = []
                if type(kwargs) == type(args) == list:
                    args = [*args, *kwargs]
                    kwargs = {}
                return await func(*args, **kwargs)
            return inner
        self.name = await helper(0, 'name')
        self.version = await helper(1, 'version')
        self.id = await helper(2, 'key')
        self.builtin = await helper(3, 'builtin')
        self.size = await helper(4, 'deckSize')
        upload = await helper(5, 'uploadTimestamp')
        self.upload = datetime.fromtimestamp(upload/1000)
        self.characters = None
        self.chartype = 'characters'
        if await helper(6, 'sampleCharacters'):
            self.chartype = 'sampleCharacters'
            self.characters = [await (await callfunc(DeckCharacter))(x) for x in await helper(6, 'sampleCharacters')]
        else:
            self.characters = [await (await callfunc(DeckCharacter))(x) for x in await helper(6, 'characters')]
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __dict__(self):
        from datetime import datetime
        return {'name': self.name, 'version': self.version, 'key': self.id,
                'builtin': self.builtin, 'deckSize': self.size,
                'uploadTimestamp': datetime.timestamp(self.upload),
                self.chartype: self.characters}
    def __list__(self):
        from datetime import datetime
        return [self.name, self.version, self.id, self.builtin,
                self.size, datetime.timestamp(self.upload), self.characters]
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'Deck({})'.format(kwargstr)
