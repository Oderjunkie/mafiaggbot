import asyncio
from asyncinit import asyncinit

@asyncinit
class User:
    async def __init__(self, *args, **kwargs):
        from dateutil.parser import parse
        async def helper(number, key, fallback=None):
            if key in kwargs:
                return kwargs[key]
            elif len(args)>=number:
                return args[number]
            return fallback
        self.id = await helper(0, 'id')
        self.username = await helper(1, 'username')
        self.activePatreon = await helper(2, 'activePatreon')
        self.createdAt = parse(await helper(3, 'createdAt'))
        self.type = await helper(4, 'type', 'user')
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __dict__(self):
        return {'id': self.id, 'username': self.username,
                'activePatreon': self.activePatreon,
                'createdAt': self.createdAt, 'type': self.type}
    def __list__(self):
        return [self.id, self.username, self.activePatreon,
                self.createdAt, self.type]
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'User({})'.format(kwargstr)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
