from websockets import connect, WebSocketClientProtocol
from bs4 import BeautifulSoup as bs4
from json import loads, dumps
from datetime import datetime
from random import choice
import requests as rq
from sys import exit
import threading
import asyncio
import time

username = 'hackfate'
password = 'REDACTED' # no no no
roomnumb = 'dc7ac66f-5515-4a17-94ca-8cdad4065d17' # outdated room number

def convert(unix):
    time = datetime.fromtimestamp(unix)
    return '{0}:{1:2}:{2:2}'.format(time.hour, time.minute, time.second).replace(' ', '0')
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
        return loads(await self.ws.recv())
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
print('Preparing...')
make = mafiaConnectionold(roomnumb, userresponse['id'], currentcookie)
print('Starting...')
from functools import lru_cache
@lru_cache(maxsize=128)
def finddude(i):
    return loads(rq.get('https://mafia.gg/api/users/{}'.format(i)).content)[0]['username']
class Cache:
    data = None
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
class Interact:
    options = {'dayLength': 3, 'dayStart': 'off',
               'deadlockPreventionLimit': '-1', 'deck': '-1',
               'disableVoteLock': False, 'hideSetup': False,
               'hostRoleSelection': False, 'majorityRule': '51',
               'mustVote': False, 'nightLength': 1, 'noNightTalk': False,
               'revealSetting': 'allReveal', 'roles': {},
               'roomName': 'The Self-hosting server.', 'scaleTimer': True, 'twoKp': '0',
               'type': 'options', 'unlisted': False}
    def talk(msg):
        make.sendchat('[BOT] '+msg)
    def setup(settings={}):
        #keys = settings.keys()
        #for key in Interact.options.keys():
        #    if key not in keys:
        #        continue
        #    Interact.options[key] = settings[key]
        #global Interact
        #print(Interact.options, settings)
        Interact.options = {**Interact.options, **settings}
        #print(Interact.options)
        make.sendpacket({'type': 'options', **Interact.options})
    def set(key, val):
        if type(Interact.options[key])==bool:
            val = True if val.lower()=='true' else False
        Interact.options[key] = type(Interact.options[key])(val)
        make.sendpacket({'type': 'options', **Interact.options})
    def convertSetup(setup):
        return dict(map(lambda x:str.split(x, 'a'), str.split(setup, 'b')))
    def startGame():
        return make.sendpacket({'type': 'startGame'})
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
        sleep(1)
        Interact.talk('Hello, World!')
        sleep(1)
        try:
            Interact.becomespec()
        except Exception:
            pass
        try:
            Bot.onCommand('Otesunkie', '!help', [])
        except Exception:
            pass
    def forcespec():
        make.sendpacket({'type': 'forceSpectate'})
    def becomeplayer():
        make.sendpacket({'type': 'presence', 'isPlayer': True})
    def becomespec():
        make.sendpacket({'type': 'presence', 'isPlayer': False})
class Bot:
    """In order for me to recognise what you want me to do, you must type the command, followed by the arguments seperated by spaces.
!help [command WITHOUT exclamation point] - I will explain the command..
Commands: !say, !setup, !random, !unlist, !relist, !start, !new, !afk, !hello, !help.
Otesunkie/Host Commands: !becomeplayer, !becomespec, !refresh.
!say [message] - I shall say what you want! no offensive stuff please. NOTE: The message CAN have spaces.
!setup [code]? - I will change the setup to the code you provide. If you provide no code, I will choose a random setup
!random [players]? - I shall choose a random setup that everyone can play! Alternatively, you can tell me how many players you want to play.
!unlist - I shall unlist the server.
!relist - I shall relist the server.
!start - The game will start, provided it can.
!new - I will host a new room, only works after the game ends.
!afk - AFK check, I will force everyone to be a spectator, meaning everyone needs to player up.
!becomeplayer - ONLY FOR HOST, will force bot to be a player.
!becomespec - ONLY FOR HOST, will force bot to be a spectator.
!refresh - ONLY FOR HOST, will refresh server.
!hello - Greetings!
!deck [name]? - I shall change the current deck to the deck you specify, if you don't specify a deck, i will pick one randomly.
!help - You did it!"""
    def filterCommand(text):
        if text.startswith('!'):
            return text.split(' ')
        elif text.lower().lstrip() in ['hello', 'hey', 'hi', 'good morning', 'good evening', 'sup', 'yo', 'heya']:
            return ['!hello']
        elif text.lower().lstrip() in ['woof', 'bark']:
            return ['!dog']
        return None
    def onCommand(name, command, args):
        command = str.lower(command)
        if command=='!dog':
            word = choice('Woof!|Bark!'.split('|'))
            emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
            Interact.talk('{} {}'.format(word, emoticon))
        elif command=='!hello':
            word = choice('Hi!|Hello!|Hey!|Yo!|Sup!|Good morning!|Good evening!'.split('|'))
            emoticon = choice('=3 <3 =D =) :3 :D :) \'-\' ^_^ ^__^'.split(' '))
            Interact.talk('{} {}'.format(word, emoticon))
        elif command=='!help':
            if len(args)>0 and args[0].strip()!='':
                try:
                    Interact.talk(next(filter(lambda x:str.startswith(x, '!'+args[0].lower()), Bot.__doc__.split('\n'))))
                except Exception:
                    Interact.talk('That command does not exist!')
            else:
                from time import sleep
                for line in Bot.__doc__.split('\n')[:4]:
                    Interact.talk(line)
                    sleep(1.5)
        elif command=='!option':
            if len(args)!=2:
                Interact.talk('uhh no')
                return
            Interact.set(args[0], args[1])
        elif command=='!say':
            msg = ' '.join(args)
            if len(msg)>50 and name not in ['Otesunkie', 'Oderjunkie', 'hackfate']:
                Interact.talk('Too long!')
            else:
                Interact.talk(msg)
        elif command=='!setup':
            if len(args)==0:
                Bot.onCommand(name, '!random', args)
            else:
                Interact.setup({'roles': Interact.convertSetup(args[0])})
                Interact.talk('Changed setup, Thank you {}!'.format(name))
        elif command=='!unlist':
            if Interact.options['unlisted']:
                Interact.talk('Server is already unlisted, {}!'.format(name))
            else:
                Interact.setup({'unlisted': True})
                Interact.talk('Unlisted server.')
        elif command=='!relist':
            if not Interact.options['unlisted']:
                Interact.talk('Server is already listed, {}!'.format(name))
            else:
                Interact.setup({'unlisted': False})
                Interact.talk('Relisted server.')
        elif command=='!celebrate':
            if len(args)>0:
                name = args[0]
            Bot.onCommand('hackfate', '!say', ['Congratulations {}!'.format(name)])
        #elif command=='!rename':
        #    if len(args)>0:
        #        pass
        elif command=='!deck':
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
                    Interact.talk('Changed to the {} deck, Thank you {}!'.format(deckname, name))
                else:
                    Interact.talk('Changed to the {} deck.'.format(deckname))
            else:
                Interact.talk('{}, {} Deck doesn\'t exist.'.format(name, ' '.join(args)))
            #Interact.talk('DEBUG')
            #Interact.talk(deck)
        elif command=='!random':
            amo = None
            if len(args)>0:
                amo = int(args[0])
            else:
                amo = len(make.info['users'])
            table = Cache.getlist()
            amos = list(map(lambda x:x[0], Cache.getlist()))
            if amo>max(amos):
                Interact.talk('Too many players! Max known: {}'.format(max(amos)))
                return
            while amo not in amos:
                amo += 1
            print(amo)
            link = choice([x[1] for x in Cache.getlist() if x[0]==amo])
            page = bs4(rq.get(link).content, features='lxml')
            name = str(page.find(class_='portable-infobox').contents[1].contents[0])
            code = str(page.find(class_='portable-infobox').contents[3].contents[3].contents[0])
            Interact.talk('Changed setup to {}.'.format(name))
            Interact.setup({'roles': Interact.convertSetup(code)})
        elif command=='!start':
            Interact.talk('Starting...')
            Interact.startGame()
        elif command=='!new':
            #Interact.talk('Creating new room...')
            #if len(args)>0:
            #    Interact.newroom(args[0])
            #else:
            #    Interact.newroom()
            #if len(args)>0:
            #    Interact.newroom({'name': args[0], 'unlisted': Interact.options['unlisted']})
            #else:
            Interact.newroom({'name': Interact.options['roomName'], 'unlisted': Interact.options['unlisted']})
            Bot.onCommand(name, '!becomespec', [])
        elif command=='!afk':
            Interact.talk('AFK CHECK!')
            Interact.forcespec()
        elif command=='!becomeplayer':
            if name in ['Otesunkie', 'Oderjunkie', 'hackfate']:
                Interact.becomeplayer()
            else:
                Interact.talk('Sorry {}, You\'re not Otesunkie!'.format(name))
        elif command=='!becomespec':
            if name in ['Otesunkie', 'Oderjunkie', 'hackfate']:
                Interact.becomespec()
            else:
                Interact.talk('Sorry {}, You\'re not Otesunkie!'.format(name))
        elif command=='!refresh':
            if name in ['Otesunkie', 'Oderjunkie', 'hackfate']:
                from time import sleep
                Bot.onCommand(name, '!afk', [])
                Bot.onCommand(name, '!becomeplayer', [])
                Bot.onCommand(name, '!setup', ['77a1'])
                Bot.onCommand(name, '!start', [])
                sleep(0.2)
                Bot.onCommand(name, '!new', [])
            else:
                Interact.talk('Sorry {}, You\'re not Otesunkie!'.format(name))
        else:
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
        print(packet)
        pass
def debug(cli, cookies):
    Interact.talk('Hello, World!')
    Bot.onCommand('Otesunkie', '!help', [])
    import time
    while True:
        try:
            time.sleep(0.1)
            got = make.get()
            parsepacket(got, cookies, Bot)
        #except NameError as e:
        #    Interact.talk('ERROR: Bot found a box labeled {} empty?!?!?'.format(e.args[0][5:-15]))
        #    continue
        except Exception as e:
            Interact.talk('ERROR: Bot is VERY CONFUSED?!?!? {} {}'.format(type(e), e.args[0]))
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
