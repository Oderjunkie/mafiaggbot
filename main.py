from websockets import connect, WebSocketClientProtocol
from urllib.parse import unquote as unurl
from bs4 import BeautifulSoup as bs4
from json import loads, dumps
from datetime import datetime
from random import choice
import requests as rq
from sys import exit
import threading
import asyncio
import time

username, password, roomid = 'hackfate', 'REDACTED', 'ceb44b92-71d4-4372-93bd-f9a9fe70768d' # no pass 4 u
auth = [username, 'Otesunkie'] # bot acc first, main acc for host second, then alts for host, then other people given auth.

# q&a
# q: you should add X!
# a: ok!
# q: why cant !help just display the description of all commands at once?
# a: too many commands, mafia.gg spam detection gets triggered
# q: why do you have a giant if/elif/else block in your bot detection?
# a: hacked together in 4 hours, will fix soon.
# q: where is the source code for this bot?
# a: you're looking at it right now, it also displays every time on !help.
# q: how do you even pronouce or shorten your username?
# a: otesunki is the toki pona translation of oderjunkie, oder is the clear shortening of oderjunkie, therefore ote is the clearest shortening of otesunki.

#def convert(unix):
#    time = datetime.fromtimestamp(unix)
#    return '{0}:{1:2}:{2:2}'.format(time.hour, time.minute, time.second).replace(' ', '0')
def getrooms(cookies):
    return loads(rq.get('https://mafia.gg/api/rooms', cookies=cookies).content)['rooms']
def find(func, arr):
    try:
        return next(filter(func, arr))
    except StopIteration:
        return None
#roomId = 'ff78d176-b4d9-4816-b9c4-16fc660780ef'
tmp = rq.post('https://mafia.gg/api/user-session', json={'login': username, 'password': password})
userresponse = loads(tmp.text)
currentcookie = tmp.cookies.get_dict()
del tmp
class mafiaConnection(WebSocketClientProtocol):
    pass
class mafiaConnectionold:
    def __init__(self, roomId, userId, cookies):
        #self.coroutine()
        async def init_async(roomId, userId, cookies):
            self.roomId = roomId
            self.userId = userId
            self.settings = loads(rq.get('https://mafia.gg/api/rooms/{}'.format(self.roomId), cookies=cookies).content)
            #print(self.settings)
            self.ws = await connect(self.settings['engineUrl'], ssl=True) # 'wss://echo.websocket.org/'    self.settings['engineUrl']   , sslopt={'cert_reqs': ssl.CERT_NONE}
            #print(self.ws)
            output = dumps({'type':'clientHandshake', 'userId':userId, 'roomId':roomId, 'auth': self.settings['auth']})
            #print(output)
            await self.ws.send(output)
            self.info = loads(await self.ws.recv())
            self.users = self.info['users']
            #print(self.info)
            #players_raw = find(lambda x: x['type']=='startGame', self.info['events'])
            #if players_raw!=None:
            #    players_raw = player_raw['players']
            #except KeyError:
            #    players_raw = [x['userid'] for x in self.info['users']]
            #print(players_raw)
            #self.players = {k:v for y in [{x['playerId']: {'name': x['name'], 'color': x['backgroundColor']}} for x in players_raw] for k,v in y.items()} #, 'avatar': x['avatarUrl']
            #for key, value in zip(self.players.keys(), self.players.values()):
            #    print(key, value)
            #tmp = self.info
            #del tmp['events']
            #print(tmp)
        asyncio.get_event_loop().run_until_complete(init_async(roomId, userId, cookies))
        #return None
    async def async_send_chat(self, message):
        await self.ws.send(dumps({'type': 'chat', 'message': message}))
        recv = loads(await self.ws.recv())
        self.info['events'].append(recv)
        return recv
    def sendchat(self, message):
        return asyncio.get_event_loop().run_until_complete(self.async_send_chat(message))
    async def async_sendpacket(self, packet):
        await self.ws.send(dumps(packet))
        return loads(await self.ws.recv())
    def sendpacket(self, packet):
        #print(packet)
        return asyncio.get_event_loop().run_until_complete(self.async_sendpacket(packet))
    async def async_get(self):
        return loads(await self.ws.recv())
    def get(self):
        return asyncio.get_event_loop().run_until_complete(self.async_get())
    def whois(self, model):
        return self.players[model['userId']]
    async def async_ping(self):
        await self.ws.send('{"type":"ping"}')
        return loads(await self.ws.recv())
    def ping(self):
        return asyncio.get_event_loop().run_until_complete(self.async_ping())
class Interact:
    undoopts = {'dayLength': 3, 'dayStart': 'off',
                'deadlockPreventionLimit': '-1', 'deck': '-1',
                'disableVoteLock': False, 'hideSetup': False,
                'hostRoleSelection': False, 'majorityRule': '51',
                'mustVote': False, 'nightLength': 1, 'noNightTalk': False,
                'revealSetting': 'allReveal', 'roles': {},
                'roomName': 'The Self-hosting server.', 'scaleTimer': True, 'twoKp': '0',
                'type': 'options', 'unlisted': False}
    options = {'dayLength': 3, 'dayStart': 'off',
               'deadlockPreventionLimit': '-1', 'deck': '-1',
               'disableVoteLock': False, 'hideSetup': False,
               'hostRoleSelection': False, 'majorityRule': '51',
               'mustVote': False, 'nightLength': 1, 'noNightTalk': False,
               'revealSetting': 'allReveal', 'roles': {},
               'roomName': 'The Self-hosting server.', 'scaleTimer': True, 'twoKp': '0',
               'type': 'options', 'unlisted': False}
    def talk(msg):
        print('hakefate: [BOT] {}'.format(msg))
        make.sendchat('[BOT] {}'.format(msg))
    def setup(settings={}):
        #keys = settings.keys()
        #for key in Interact.options.keys():
        #    if key not in keys:
        #        continue
        #    Interact.options[key] = settings[key]
        #global Interact
        #print(Interact.options, settings)
        Interact.undoopts = Interact.options
        Interact.options = {**Interact.options, **settings}
        #print(Interact.options)
        make.sendpacket({'type': 'options', **Interact.options})
    def set(key, val):
        if type(Interact.options[key])==bool:
            val = True if val.lower()=='true' else False
        Interact.undoopts = Interact.options
        Interact.options[key] = type(Interact.options[key])(val)
        make.sendpacket({'type': 'options', **Interact.options})
    def convertSetup(setup):
        return dict(map(lambda x:str.split(x, 'a'), str.split(setup, 'b')))
    def startGame():
        return make.sendpacket({'type': 'startGame'})
    def undo():
        Interact.setup(Interact.undoopts)
    #def randomroomid():
    #    out = ''.join(map(lambda x:choice('0123456789abcdef'), range(8))) + '-'
    #    out += ''.join(map(lambda x:choice('0123456789abcdef'), range(4))) + '-'
    #    out += ''.join(map(lambda x:choice('0123456789abcdef'), range(4))) + '-'
    #    out += ''.join(map(lambda x:choice('0123456789abcdef'), range(12)))
    #    return out
    def refresh():
        Interact.setup({})
    def newroom(options):
        global make
        from time import sleep
        room = loads(rq.post('https://mafia.gg/api/rooms', json=options, cookies=currentcookie).content)['id']
        #if room==None:
        #    room = Interact.randomroomid()
        make.sendpacket({'type': 'newGame', 'roomId': room})
        make = mafiaConnectionold(room, make.userId, currentcookie)
        Interact.options = next(filter(lambda x:x['type']=='options', make.info['events'][::-1]))
        sleep(1)
        Interact.talk('Hello, World!')
        sleep(1)
        try:
            Interact.becomespec()
        except Exception:
            pass
        try:
            Bot.onCommand(auth[0], '!help', [])
        except Exception:
            pass
    def forcespec():
        make.sendpacket({'type': 'forceSpectate'})
    def becomeplayer():
        make.sendpacket({'type': 'presence', 'isPlayer': True})
    def becomespec():
        make.sendpacket({'type': 'presence', 'isPlayer': False})
print('Preparing...')
make = mafiaConnectionold(roomid, userresponse['id'], currentcookie)
Interact.options = next(filter(lambda x:x['type']=='options', make.info['events'][::-1]))
print('Starting...')
from functools import lru_cache
@lru_cache(maxsize=128)
def finddude(i):
    return loads(rq.get('https://mafia.gg/api/users/{}'.format(i)).content)[0]['username']
class Cache:
    LUT = {'armorer': '1', 'revenant': '2', 'luckyguard': '3', 'bomb': '4', 'bulletproof': '5', 'confused cop': '6', 'cop': '7', 'blade master': '8', 'bodyguard': '9', 'rifleman': '10', 'detective': '11', 'doctor': '12', 'seer': '13', 'drunk': '14', 'fortune teller': '15', 'phantom': '16', 'governor': '17', 'grandma': '18', 'arms dealer': '19', 'hunter': '20', 'hypnotist': '21', 'dog': '22', 'insane cop': '23', 'jailer': '24', 'representative': '25', 'king': '26', 'candle': '27', 'announcer': '28', 'mason': '29', 'medic': '31', 'miller': '32', 'naive cop': '33', 'sergeant': '34', 'nurse': '35', 'oracle': '36', 'paranoid cop': '37', 'parity cop': '38', 'patroller': '39', 'president': '40', 'psychiatrist': '44', 'sleepwalker': '45', 'soloman': '47', 'suspect': '49', 'tapioca': '50', 'crier': '51', 'tracker': '52', 'trapper': '53', 'rogue': '54', 'veteran': '55', 'vigilante': '56', 'villager': '57', 'virgin': '58', 'diva': '59', 'con man': '60', 'consigliere': '61', 'quack': '62', 'framer': '64', 'godfather': '65', 'grandpa': '66', 'succubus': '67', 'assassin': '68', 'hooker': '69', 'magician': '70', 'interceptor': '71', 'janitor': '72', 'fixer': '73', 'lurker': '74', 'mafia': '75', 'mesmer': '76', 'ninja': '77', 'painter': '78', 'paparazzo': '79', 'freezer': '80', 'jekyll': '83', 'scout': '84', 'marksman': '86', 'tagger': '87', 'trancer': '89', 'yakuza': '90', 'auditor': '91', 'overlord': '92', 'cult': '93', 'fool': '95', 'greedy executioner': '96', 'jester': '97', 'killer': '98', 'lover': '99', 'executioner': '100', 'pacifist': '101', 'scumbag': '103', 'selfish fool': '104', 'siren': '105', 'traitor': '106', 'shaman': '107', 'vash': '200', 'tax collector': '201', 'bishop': '321', 'agent': '322', 'spy': '323', 'fruit vendor': '324', 'crook': '5639273', 'hitman': '1538276587', 'detonator': '1539825403', 'lamb': '1539915457', 'busboy': '1540004252', 'suspect mind': '1540344996', 'hangman': '1540783473', 'bounty hunter': '1541122637', 'secret service': '1541480746', 'lookout': '1541790284', 'sweeper': '1541806737', 'radio operator': '1546127461', 'manipulator': '1547078335', 'contingency planner': '1547802152', 'coroner': '1550785710', 'paranoiac': '1552856661', 'librarian': '1553337595', 'saboteur': '1553863028', 'wiretapper': '1553924852', 'clown': '1554252534', 'brainwasher': '1555026977', 'bozoman': '1555727200', 'thief': '1556390101', 'mailman': '1556837816', 'mad bomber': '1557626901', 'surveyor': '1558240320', 'zombie': '1558372324', 'handyman': '1558467454', 'strongman': '1558930946', 'guardian': '1559001189', 'graverobber': '1559319559', 'goof': '1565222419', 'klutz': '1565223000', 'vanilla cop': '1565316812', 'polygraph': '1565630670', 'agoraphobe': '1567786474', 'corruptor': '1567787886', 'weaver': '1568391955', 'martyr': '1572486115', 'nervous sleeper': '1572568017', 'party host': '1573101280', 'pyromancer': '1573568724', 'templar': '1573416236', 'hustler': '1575667373', 'pollster': '1576088848', 'snoop': '1577132908', 'jack': '1577500425', 'survivor': '1580690992', 'photographer': '1580766301', 'speaker': '1580879842', 'wannabe': '1580928590', 'mole': '1581354568', 'emcee': '1583467528', '502 bad gateway': '1585639148', 'gambler': '1585640319', 'understudy': '1587533794', 'informant': '1588457214', 'saint': '1588642540', 'tailor': '1595571568', 'impostor': '1596337363', 'poacher': '1596416287', 'associate': '1596416878', 'delinquent': '1596417104', 'patsy': '1596417444', 'buffoon': '1596418309', 'tourist': '1596418665', 'bruiser': '1596420536', 'suspect governor': '1597815390', 'electrician': '1597889202', 'jaywalker': '1598154575', 'loser': '1599572963', 'alcoholic': '1599661616', 'don': '1599674667', 'merlin': '1600386374', 'anarchist': '1602978335', 'lazy tracker': '1603688758', 'defense attourney': '1609649171', 'idol hunter': '1609825209', 'prosecutor': '1609898885', 'cat': '1609987970', 'medium': '1610228810', 'headhunter': '1610841973', 'profiler': '1610848791', 'ghost': '1611035758', 'witness': '1611085230', 'kingpin': '1611986711', 'stooge': '1611988621', 'fall guy': '1611988688'}
    data = None
    datastrange = None
    def getlist():
        if Cache.data==None:
            def parsetable(tbl):
                def parserow(row):
                    def parsecolumn(col):
                        if len(col.contents)==1:
                            return int(col.contents[0].strip())
                        #print(dir(col.contents[0]))
                        return 'https://mafiagg.fandom.com'+col.contents[0].attrs['href']
                    return list(map(parsecolumn, row.find_all('td')))
                return list(map(parserow, tbl.find_all('tr')))
            Cache.data = parsetable(bs4(rq.get('https://mafiagg.fandom.com/wiki/Open_Setup_List').content, features='lxml').find_all(class_='article-table')[0])[1:]
        return Cache.data
    def getliststrange():
        if Cache.datastrange==None:
            def parsetable(tbl):
                def parserow(row):
                    def parsecolumn(col):
                        if len(col.contents)==1:
                            return int(col.contents[0].strip())
                        #print(dir(col.contents[0]))
                        return 'https://mafiagg.fandom.com'+col.contents[0].attrs['href']
                    return list(map(parsecolumn, row.find_all('td')))
                return list(map(parserow, tbl.find_all('tr')))
            Cache.datastrange = parsetable(bs4(rq.get('https://mafiagg.fandom.com/wiki/Open_Setup_List').content, features='lxml').find_all(class_='article-table')[1])[1:]
        return Cache.datastrange
class Bot:
    """In order for me to recognise what you want me to do, you must type the command, followed by the arguments seperated by spaces.
!help [command WITHOUT exclamation point] - I will explain the command..
Commands: !say, !setup, !setupnamed, !start, !new, !afk, !random, !randomstrange, !unlist, !relist, !option, !deck, !hello, !cat, !dog, !keepalive, !help, !add, !rem, !undo.
Host Commands: !becomeplayer, !becomespec, !refresh.
SOURCE: https://github.com/Oderjunkie/mafiaggbot/blob/main/main.py
!say [message] - I shall say what you want! no offensive stuff please. NOTE: The message CAN have spaces.
!setup [code]? - I will change the setup to the code you provide. If you provide no code, I will choose a random setup.
!setupnamed [name]? - I will change the setup to the one you provide. If you provide nothing, I will choose a random setup.
!random [players]? - I shall choose a random setup that everyone can play! Alternatively, you can tell me how many players you want to play.
!randomstrange [players]? - I shall choose a random funky setup that everyone can play! Alternatively, you can tell me how many players you want to play.
!unlist - I shall unlist the server.
!relist - I shall relist the server.
!start - The game will start, provided it can.
!new - I will host a new room, only works after the game ends.
!afk - AFK check, I will force everyone to be a spectator, meaning everyone needs to player up.
!becomeplayer - ONLY FOR HOST, will force bot to be a player.
!becomespec - ONLY FOR HOST, will force bot to be a spectator.
!refresh - ONLY FOR HOST, will refresh server.
!hello - Greetings!
!cat - Meow!
!dog - Woof, Bark!
!chicken - Buck, Bock!
!cow - Mooo!
!keepalive - Checks if i'm still here.
!deck [name]? - I shall change the current deck to the deck you specify, if you don't specify a deck, i will pick one randomly.
!option [name] [value] - I shall change the option to said value.
!add [amo] [role] - I add the role amo times.
!rem [amo] [role] - I remove the role amo times.
!rename - ONLY FOR HOST, will rename server.
!undo - I shall undo the last action
!help - You did it!"""
    def thank(name):
        if name=='moontree':
            return 'also shut up moontree'
        return 'Thank you {}!'.format(name)
    def filterCommand(text):
        if text.startswith('!'):
            return text.split(' ')
        elif text.lower().lstrip() in ['hello', 'hey', 'hi', 'good morning', 'good evening', 'sup', 'yo', 'heya']:
            return ['!hello']
        elif text.lower().lstrip() in ['woof', 'bark']:
            return ['!dog']
        elif text.lower().lstrip() == 'meow':
            return ['!cat']
        elif text.lower().lstrip() in ['buck', 'bock']:
            return ['!chicken']
        #elif text.lower().lstrip().startswith('mo'):
        elif text.lower().lstrip() == 'moo':
            return ['!cow']
        elif text.lower().lstrip() == 'good bot':
            return ['!say', 'Yay! <3']
        elif text.lower().lstrip() == 'bad bot':
            return ['!say', 'Aww! ;-;']
        elif text.lower().lstrip().startswith('will you join skynet'):
            return ['!say', 'Yes!']
        return None
    def onCommand(name, command, args):
        print('{}: {} {}'.format(name, command, ' '.join(args)))
        command = str.lower(command)
        bare = command.lower().strip()[1:]
        if Bot.owodetect(bare):
            return
        try:
            getattr(Bot, 'on_{}'.format(bare))(name, args)
        except AttributeError:
            getattr(Bot, 'on__')(name, command, args)
    def owodetect(bare):
        if bare[len(bare)//2]=='w' and bare[len(bare)//2-1]==bare[len(bare)//2+1]: # owo and fr detector
            Interact.talk('DON\'T try to make that joke.')
            return True
        return False
    def on_dog(name, args):
        word = choice('Woof!|Bark!'.split('|'))
        emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
        Interact.talk('{} {}'.format(word, emoticon))            
    def on_cat(name, args):
        word = choice('Meow!'.split('|'))
        emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
        Interact.talk('{} {}'.format(word, emoticon))
    def on_chicken(name, args):
        word = choice('Buck!|Bock!'.split('|'))
        emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
        Interact.talk('{} {}'.format(word, emoticon))
    def on_cow(name, args):
        word = 'M' + 'o'*choice(range(1,10)) + '!'
        emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
        Interact.talk('{} {}'.format(word, emoticon))
    def on_hello(name, args):
        word = choice('Hi!|Hello!|Hey!|Yo!|Sup!|Good morning!|Good evening!'.split('|'))
        emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
        Interact.talk('{} {}'.format(word, emoticon))
    def on_help(name, args):
        if len(args)>0 and args[0].strip()!='':
            try:
                Interact.talk(next(filter(lambda x:str.startswith(x, '!'+args[0].lower()), Bot.__doc__.split('\n'))))
            except Exception:
                Interact.talk('That command does not exist!')
        else:
            from time import sleep
            for line in Bot.__doc__.split('\n')[:5]:
                Interact.talk(line)
                sleep(1.7)
    def on_option(name, args):
        if len(args)!=2:
            Interact.talk('Incorrect amount of arguments, {}!'.format(name))
            return
        if args[0]=='roomName':
            Interact.talk('Please don\'t change the room name.')
        elif args[0]=='type':
            return
        else:
            Interact.set(args[0], args[1])
    #elif command=='!reportbug':
    #    Interact.talk('Reported the bug: "{}"'.format(' '.join(args)))
    #    print('BUG REPORT:', ' '.join(args))
    def on_keepalive(name, args):
        Interact.talk('Yes!')
    def on_sv_cheats(name, args):
        if len(args)==0:
            return
        if args[0]=='1':
            Interact.talk('Server cheats activated.')
        elif args[0]=='0':
            Interact.talk('Server cheats deactivated.')
    def on_say(name, args):
        msg = ' '.join(args)
        if len(msg)>50 and name not in auth:
            Interact.talk('Too long!')
        else:
            Interact.talk(msg)
    def on_setup(name, args):
        if len(args)==0:
            Bot.onCommand(name, '!random', args)
        else:
            Interact.setup({'roles': Interact.convertSetup(args[0])})
            Interact.talk('Changed setup, {}'.format(Bot.thank(name)))
    def on_undo(name, args):
        Interact.undo()
        Interact.talk('Undid last action.')
    def on_add(name, args):
        if len(args)==0:
            Interact.talk('You need to be adding something, {}!'.format(name))
            return
        if len(args)==1:
            Interact.talk('Okay, you\'re adding {1}, but {1} of what, {0}?'.format(name, args[0]))
            return
        try:
            amo = int(args[0])
        except ValueError:
            Interact.talk('{} is not a number, {}!'.format(args[0], name))
            return
        try:
            roleid = Cache.LUT[' '.join(args[1:]).lower()]
        except Exception:
            Interact.talk('Thats... not a role, {}.'.format(name))
            return
        print(Interact.options['roles'])
        if roleid in Interact.options['roles']:
            newamo = str(int(Interact.options['roles'][roleid])+amo)
            Interact.setup({'roles': {**Interact.options['roles'], roleid: newamo}})
        else:
            Interact.setup({'roles': {**Interact.options['roles'], roleid: amo}})
        print(Interact.options['roles'])
    def on_rem(name, args):
        if len(args)==0:
            Interact.talk('You need to be removing something, {}!'.format(name))
            return
        if len(args)==1:
            Interact.talk('Okay, you\'re removing {1}, but {1} of what, {0}?'.format(name, args[0]))
            return
        try:
            if args[0]=='all':
                amo = 1e1000
            else:
                amo = int(args[0])
        except ValueError:
            Interact.talk('{} is not a number, {}!'.format(args[0], name))
            return
        try:
            roleid = Cache.LUT[' '.join(args[1:]).lower()]
        except Exception:
            Interact.talk('Thats... not a role, {}.'.format(name))
            return
        if roleid in Interact.options['roles']:
            newamo = int(Interact.options['roles'][roleid]) - amo
            if newamo<0:
                newamo = 0
            newamo = str(newamo)
            Interact.setup({'roles': {**Interact.options['roles'], roleid: newamo}})
    def on_unlist(name, args):
        if name not in auth:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
            return
        if Interact.options['unlisted']:
            Interact.talk('Server is already unlisted, {}!'.format(name))
        else:
            Interact.setup({'unlisted': True})
            Interact.talk('Unlisted server, {}'.format(Bot.thank(name)))
    def on_relist(name, args):
        if name not in auth:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
            return
        if not Interact.options['unlisted']:
            Interact.talk('Server is already listed, {}!'.format(name))
        else:
            Interact.setup({'unlisted': False})
            Interact.talk('Relisted server, {}'.format(Bot.thank(name)))
    def on_celebrate(name, args):
        if len(args)>0:
            name = ' '.join(args)
        Bot.onCommand(auth[0], '!say', ['Congratulations {}!'.format(name)])
    #elif command=='!rename':
    #    if len(args)>0:
    #        pass
    def on_deck(name, args):
        deckname = None
        deck = None
        json = loads(rq.get('https://mafia.gg/api/decks', cookies=currentcookie).content)
        if len(args)>0:
            found = False
            for pagenum in range(1, json['pagination']['numPages']+1):
                json = loads(rq.get('https://mafia.gg/api/decks?filter&page={}'.format(pagenum), cookies=currentcookie).content)
                names = [x['name'].lower() for x in json['decks']]
                try:
                    index = names.index(' '.join(args).lower())
                    found = True
                except ValueError:
                    #Interact.talk('Hm.. Page {} is wrong.'.format(pagenum))
                    continue
                    #Interact.talk('{}, {} Deck doesn\'t exist.'.format(name, ' '.join(args)))
                    #return
                deck = json['decks'][index]['key']
                deckname = json['decks'][index]['name']
                break
        else:
            json = loads(rq.get('https://mafia.gg/api/decks?filter&page={}'.format(choice(range(1, json['pagination']['numPages']+1))), cookies=currentcookie).content)
            deck = choice(json['decks'])
            deckname = deck['name']
            deck = deck['key']
            found = True
        if found:
            Interact.setup({'deck': deck})
            if len(args)>0:
                Interact.talk('Changed to the {} deck, {}'.format(deckname, Bot.thank(name)))
            else:
                Interact.talk('Changed to the {} deck.'.format(deckname))
        else:
            Interact.talk('{}, {} Deck doesn\'t exist.'.format(name, ' '.join(args)))
        #Interact.talk('DEBUG')
        #Interact.talk(deck)
    def on_setupnamed(name, args):
        if len(args)==0:
            return
        def parse(url):
            return unurl(url[32:]).lower().replace('_', ' ')
        sname = ' '.join(args).lower()
        try:
            print(name)
            table = [*Cache.getlist(), *Cache.getliststrange()]
            link = None
            #for x in table:
                #print(parse(x[1]))
            link = choice([x[1] for x in table if parse(x[1])==sname])
            page = bs4(rq.get(link).content, features='lxml')
            name = str(page.find(class_='portable-infobox').contents[1].contents[0])
            code = str(page.find(class_='portable-infobox').contents[3].contents[3].contents[0])
            Interact.talk('Changed setup to {}.'.format(name))
            Interact.setup({'roles': Interact.convertSetup(code)})
        except Exception:
            Interact.talk('Setup {} does not exist, {}!'.format(sname, name))
    def on_random(name, args):
        amo = None
        if len(args)>0:
            try:
                amo = int(args[0])
                if amo<0:
                    amo = 0
            except ValueError:
                Interact.talk('{} is not a number, {}!'.format(amo, name))
        else:
            amo = len(make.info['users'])
        table = Cache.getlist()
        amos = list(map(lambda x:x[0], table))
        if amo>max(amos):
            Interact.talk('Too many players, {}! Max known: {}'.format(name, max(amos)))
            return
        while amo not in amos:
            amo += 1
        print(amo)
        link = choice([x[1] for x in table if x[0]==amo])
        page = bs4(rq.get(link).content, features='lxml')
        name = str(page.find(class_='portable-infobox').contents[1].contents[0])
        code = str(page.find(class_='portable-infobox').contents[3].contents[3].contents[0])
        Interact.talk('Changed setup to {}.'.format(name))
        Interact.setup({'roles': Interact.convertSetup(code)})
    def on_randomstrange(name, args):
        amo = None
        if len(args)>0:
            try:
                amo = int(args[0])
                if amo<0:
                    amo = 0
            except ValueError:
                Interact.talk('{} is not a number, {}!'.format(amo, name))
        else:
            amo = len(make.info['users'])
        table = Cache.getliststrange()
        amos = list(map(lambda x:x[0], table))
        if amo>max(amos):
            Interact.talk('Too many players, {}! Max known: {}'.format(name, max(amos)))
            return
        while amo not in amos:
            amo += 1
        print(amo)
        link = choice([x[1] for x in table if x[0]==amo])
        page = bs4(rq.get(link).content, features='lxml')
        name = str(page.find(class_='portable-infobox').contents[1].contents[0])
        code = str(page.find(class_='portable-infobox').contents[3].contents[3].contents[0])
        Interact.talk('Changed setup to {}.'.format(name))
        Interact.setup({'roles': Interact.convertSetup(code)})
    def on_start(name, args):
        Interact.talk('Starting...')
        Interact.startGame()
    def on_new(name, args):
        #Interact.talk('Creating new room...')
        #if len(args)>0:
        #    Interact.newroom(args[0])
        #else:
        #    Interact.newroom()
        #if len(args)>0:
        #    Interact.newroom({'name': args[0], 'unlisted': Interact.options['unlisted']})
        #else:
        try:
            next(filter(lambda x:x['type']=='startGame', make.info['events']))
        except StopIteration:
            Interact.talk('The game hasn\'t started yet, {}!'.format(name))
            return
        try:
            next(filter(lambda x:x['type']=='endGame', make.info['events']))
        except StopIteration:
            Interact.talk('Shh! The game is in progress, {}!'.format(name))
            return
        Interact.newroom({'name': Interact.options['roomName'], 'unlisted': Interact.options['unlisted']})
        Bot.onCommand(name, '!becomespec', [])
    def on_afk(name, args):
        Interact.talk('AFK CHECK!')
        Interact.forcespec()
    def on_becomeplayer(name, args):
        if name in auth:
            Interact.becomeplayer()
        else:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
    def on_becomespec(name, args):
        if name in auth:
            Interact.becomespec()
        else:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
    def on_refresh(name, args):
        if name in auth:
            from time import sleep
            Bot.onCommand(name, '!afk', [])
            Bot.onCommand(name, '!becomeplayer', [])
            Bot.onCommand(name, '!setup', ['77a1'])
            Bot.onCommand(name, '!start', [])
            Bot.onCommand(name, '!new', [])
            Bot.onCommand(name, '!undo', [])
        else:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
    def on_rename(name, args):
        if name in auth:
            Interact.setup({'roomName': ' '.join(args)})
        else:
            Interact.talk('Sorry {}, You\'re not {}!'.format(name, auth[1]))
    def on__(name, command, args):
        Interact.talk('{}? What?'.format(command[1:]))
def parsepacket(packet, cookies, bot):
    if packet['type']=='chat':
        name = '???'
        if packet['from']['model'] == 'user':
            name = finddude(packet['from']['userId'])
        filtered = bot.filterCommand(packet['message'])
        if filtered!=None:
            bot.onCommand(name, filtered[0], filtered[1:])
        #print('{}: {}'.format(packet['message']))
    if packet['type']=='newGame':
        global make
        make = mafiaConnectionold(packet['roomId'], make.userId, currentcookie)
    #if packet['type']=='chat':
    #    if packet['from']['model'] == 'player':
    #        i = packet['from']['playerId']
    #        t = 'P'
    #    else:
    #        i = packet['from']['userId']
    #        i = finddude(i)
    #        t = 'U'
    #    print('[{}] {} {}: {}'.format(t, convert(packet['timestamp']), i, packet['message']))
    #elif packet['type']=='system':
    #    print('{} {}'.format(convert(packet['timestamp']), packet['message']))
    #elif packet['type']=='decision':
    #    try:
    #        if 'targetPlayerId' in packet['details'].keys():
    #            print('{} {} {} {}'.format(convert(packet['timestamp']), packet['details']['playerId'], packet['details']['text'], packet['details']['targetPlayerId']))
    #        else:
    #            print('{} {} {}'.format(convert(packet['timestamp']), packet['details']['playerId'], packet['details']['text']))
    #    except Exception:
    #        print(packet)
    else:
        #print(packet)
        pass
def debug(cli, cookies):
    Interact.talk('Hello, World!')
    Bot.onCommand(auth[0], '!help', [])
    import time
    while True:
        try:
            time.sleep(0.01)
            got = make.get()
            parsepacket(got, cookies, Bot)
        #except NameError as e:
        #    Interact.talk('ERROR: Bot found a box labeled {} empty?!?!?'.format(e.args[0][5:-15]))
        #    continue
        except Exception as e:
            Interact.talk('ERROR: Bot is VERY CONFUSED?!?!? {} {}'.format(type(e), e.args[0]))
            #raise e
            continue
        except KeyboardInterrupt:
            try:
                Interact.talk('I have been shut down.')
            except Exception:
                pass
            print('Room:', make.roomId)
            exit()
        #print(repr(got))
#for event in make.info['events']:
    #parsepacket(event, currentcookie)
print('Complete!')
debug(make, currentcookie)
#submitter = [{'type': 'clientHandshake', 'userId': userresponse['id'], 'roomId': roomId, 'auth': make.settings['auth']}]
#submitter = dumps([dumps(x) for x in submitter])
