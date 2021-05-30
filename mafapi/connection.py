from asyncinit import asyncinit
import aiohttp
import asyncio

@asyncinit
class Connection:
    roleLUT = {'thorne': '1596390851', 'shogun': '42', 'armorer': '1', 'revenant': '2', 'luckyguard': '3', 'bomb': '4', 'bulletproof': '5', 'confused cop': '6', 'cop': '7', 'blade master': '8', 'bodyguard': '9', 'rifleman': '10', 'detective': '11', 'doctor': '12', 'seer': '13', 'drunk': '14', 'fortune teller': '15', 'phantom': '16', 'governor': '17', 'grandma': '18', 'arms dealer': '19', 'hunter': '20', 'hypnotist': '21', 'dog': '22', 'insane cop': '23', 'jailer': '24', 'representative': '25', 'king': '26', 'candle': '27', 'announcer': '28', 'mason': '29', 'medic': '31', 'miller': '32', 'naive cop': '33', 'sergeant': '34', 'nurse': '35', 'oracle': '36', 'paranoid cop': '37', 'parity cop': '38', 'patroller': '39', 'president': '40', 'psychiatrist': '44', 'sleepwalker': '45', 'soloman': '47', 'suspect': '49', 'tapioca': '50', 'crier': '51', 'tracker': '52', 'trapper': '53', 'rogue': '54', 'veteran': '55', 'vigilante': '56', 'villager': '57', 'virgin': '58', 'diva': '59', 'con man': '60', 'consigliere': '61', 'quack': '62', 'framer': '64', 'godfather': '65', 'grandpa': '66', 'succubus': '67', 'assassin': '68', 'hooker': '69', 'magician': '70', 'interceptor': '71', 'janitor': '72', 'fixer': '73', 'lurker': '74', 'mafia': '75', 'mesmer': '76', 'ninja': '77', 'painter': '78', 'paparazzo': '79', 'freezer': '80', 'jekyll': '83', 'scout': '84', 'marksman': '86', 'tagger': '87', 'trancer': '89', 'yakuza': '90', 'auditor': '91', 'overlord': '92', 'cult': '93', 'fool': '95', 'greedy executioner': '96', 'jester': '97', 'killer': '98', 'lover': '99', 'executioner': '100', 'pacifist': '101', 'scumbag': '103', 'selfish fool': '104', 'siren': '105', 'traitor': '106', 'shaman': '107', 'vash': '200', 'tax collector': '201', 'bishop': '321', 'agent': '322', 'spy': '323', 'fruit vendor': '324', 'crook': '5639273', 'hitman': '1538276587', 'detonator': '1539825403', 'lamb': '1539915457', 'busboy': '1540004252', 'suspect mind': '1540344996', 'hangman': '1540783473', 'bounty hunter': '1541122637', 'secret service': '1541480746', 'lookout': '1541790284', 'sweeper': '1541806737', 'radio operator': '1546127461', 'manipulator': '1547078335', 'contingency planner': '1547802152', 'coroner': '1550785710', 'paranoiac': '1552856661', 'librarian': '1553337595', 'saboteur': '1553863028', 'wiretapper': '1553924852', 'clown': '1554252534', 'brainwasher': '1555026977', 'bozoman': '1555727200', 'thief': '1556390101', 'mailman': '1556837816', 'mad bomber': '1557626901', 'surveyor': '1558240320', 'zombie': '1558372324', 'handyman': '1558467454', 'strongman': '1558930946', 'guardian': '1559001189', 'graverobber': '1559319559', 'goof': '1565222419', 'klutz': '1565223000', 'vanilla cop': '1565316812', 'polygraph': '1565630670', 'agoraphobe': '1567786474', 'corruptor': '1567787886', 'weaver': '1568391955', 'martyr': '1572486115', 'nervous sleeper': '1572568017', 'party host': '1573101280', 'pyromancer': '1573568724', 'templar': '1573416236', 'hustler': '1575667373', 'pollster': '1576088848', 'snoop': '1577132908', 'jack': '1577500425', 'survivor': '1580690992', 'photographer': '1580766301', 'speaker': '1580879842', 'wannabe': '1580928590', 'mole': '1581354568', 'emcee': '1583467528', '502 bad gateway': '1585639148', 'gambler': '1585640319', 'understudy': '1587533794', 'informant': '1588457214', 'saint': '1588642540', 'tailor': '1595571568', 'impostor': '1596337363', 'poacher': '1596416287', 'associate': '1596416878', 'delinquent': '1596417104', 'patsy': '1596417444', 'buffoon': '1596418309', 'tourist': '1596418665', 'bruiser': '1596420536', 'suspect governor': '1597815390', 'electrician': '1597889202', 'jaywalker': '1598154575', 'loser': '1599572963', 'alcoholic': '1599661616', 'don': '1599674667', 'merlin': '1600386374', 'anarchist': '1602978335', 'lazy tracker': '1603688758', 'defense attourney': '1609649171', 'idol hunter': '1609825209', 'prosecutor': '1609898885', 'cat': '1609987970', 'medium': '1610228810', 'headhunter': '1610841973', 'profiler': '1610848791', 'ghost': '1611035758', 'witness': '1611085230', 'kingpin': '1611986711', 'stooge': '1611988621', 'fall guy': '1611988688'}
    async def __init__(self, pointer, roomid, session):
        self.ws = await session.session.ws_connect(pointer.engineUrl)
        await self.send({'type': 'clientHandshake', 'userId': session.user.id, 'roomId': roomid, 'auth': pointer.auth})
        self.info = await self.get()
        self.options = next(filter(lambda x:x['type']=='options', self.info['events'][::-1]))
        self.session = session
        self.roomid = roomid
        for packet in self.events:
            await self.parse(packet)
    async def get(self):
        return await self.parse(await self.ws.receive_json())
    async def send(self, data):
        return await self.ws.send_json(data)
    async def sendchat(self, msg):
        return await self.send({'type': 'chat', 'message': msg})
    async def close(self):
        return await self.ws.close()
    async def kick(self, user):
        return await self.session.session.post('https://mafia.gg/api/rooms/{}/kick'.format(self.roomid), json={'userId': user.id})
    async def shadowban(self, user):
        return await self.session.blacklist(user)
    async def ban(self, user):
        return [await shadowban(user), await kick(user)]
    async def parse(self, packet):
        return packet
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return await self.close()
    @property
    def events(self):
        return self.info['events']
    @events.setter
    def setter(self, data):
        self.info['events'] = data
        return data
