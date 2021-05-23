import asyncio
from asyncinit import asyncinit
from mafapi.deck import Deck

@asyncinit
class DeckPointer:
    async def __init__(self, *args, **kwargs):
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
        pagination = await helper(0, 'pagination')
        self.page = pagination['page']
        self.numPages = pagination['numPages']
        self.total = pagination['total']
        self.decks = [await (await callfunc(Deck))(x) for x in await helper(1, 'decks')]
    def __dict__(self):
        return {'pagination':
                {'page': self.page, 'numPages': self.numPages,
                 'total': self.total},
                'decks': [deck.__dict__() for deck in self.decks]}
    def __list__(self):
        return [{'page': self.page, 'numPages': self.numPages,
                 'total': self.total},
                [deck.__dict__() for deck in self.decks]]
    def __repr__(self):
        kwargs = self.__dict__()
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'DeckPointer({})'.format(kwargstr)
