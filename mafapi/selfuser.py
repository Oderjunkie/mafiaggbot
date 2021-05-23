import asyncio
from asyncinit import asyncinit

@asyncinit
class SelfUser:
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
        self.email = await helper(2, 'email')
        self.timeFormat = await helper(3, 'timeFormat')
        self.hostBannedUsernames = await helper(4, 'hostBannedUsernames')
        self.isPatreonLinked = await helper(5, 'isPatreonLinked')
        self.activePatreon = await helper(6, 'activePatreon')
        self.needsVerification = await helper(7, 'needsVerification')
        self.createdAt = parse(await helper(8, 'createdAt'))
    def __iter__(self):
        tmp = self.__dict__()
        return iter(zip(tmp.keys(), tmp.values()))
    def __dict__(self):
        return {'id': self.id, 'username': self.username,
                'email': self.email, 'timeFormat': self.timeFormat,
                'hostBannedUsernames': self.hostBannedUsernames,
                'isPatreonLinked': self.isPatreonLinked,
                'activePatreon': self.activePatreon,
                'needsVerification': self.needsVerification,
                'createdAt': self.createdAt}
    def __list__(self):
        return [self.id, self.username, self.email, self.timeFormat,
                self.hostBannedUsernames, self.isPatreonLinked,
                self.activePatreon, self.needsVerification, self.createdAt]
    def __repr__(self):
        kwargs = dict(self)
        kwargstr = ', '.join(list(map('='.join, zip(kwargs.keys(),
                                  map(repr, kwargs.values())))))
        return 'SelfUser({})'.format(kwargstr)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
