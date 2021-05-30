import asyncio
from asyncinit import asyncinit

@asyncinit
class DeckCharacter:
    async def __init__(self, *args, **kwargs):
        from datetime import datetime
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            elif len(args)>=number:
                return args[number]
            return fallback
        self.id = await helper(0, 'playerId')
        self.name = await helper(1, 'name')
        self.avatarUrl = await helper(2, 'avatarUrl')
        self.backgroundColor = await helper(3, 'backgroundColor')
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __dict__(self):
        return {'playerId': self.id, 'name': self.name,
                'avatarUrl': self.avatarUrl,
                'backgroundColor': self.backgroundColor}
    def __list__(self):
        return [self.id, self.name, self.avatarUrl,
                self.backgroundColor]
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'DeckCharacter({})'.format(kwargstr)
