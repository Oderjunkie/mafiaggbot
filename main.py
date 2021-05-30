import config
import asyncio
import mafapi
import logging

from mafapi.botbase import BotBase
from mafapi.botdecorators import badge_req, perm_req, locked_to, use_database

logging.basicConfig(level=logging.DEBUG)

class Hackfate(BotBase):
    """i bet you you've seen this bot before
!help [command] - I will explain the command, commands are: !say, !whoami, !badge, !unbadge, !nick, !kick, !ban, !unlist, !relist, !afk, !option, !start, !new.
discrod https://discord.gg/gQ2j78mYdD, gitbub https://github.com/Oderjunkie/mafiaggbot/tree/refactor
!say [text] - i say the thing
!whoami - i will tell you your stats
!badge [name] [badge] - i will gave the person a badge
!unbadge [name] [badge] - i will take away a badge from someone
!nick [nickname] - you know what this means
!relist - relist the server [need auth]
!unlist - unlist the server [need auth]
!setup [code] - i will change the setup to the code you specify
!deck [name] - i will change the deck to the one you specify
!nodeck - no deck
!option [option] [value] - i will change an option. remember: camelCase.
!afk - kfc czech
!start - start the game
!new - makes a new game
!kick [name] - kick [need auth]
!ban [name] - ban [need auth]"""
    async def _on_say(self, userobj, args):
        await self.ws.sendchat(' '.join(args))

    async def _on_afk(self, userobj, args):
        from random import choice
        await self.ws.send({'type': 'forceSpectate'})
        await self.ws.sendchat(choice(['AFK']*3+['KFC']) + ' ' + choice(['CHECK']*3+['CZECH']))

    @use_database
    async def _on_unlist(self, user, args):
        if self.ws.options['unlisted']:
            await self.ws.sendchat('Server is already unlisted, {}!'.format(user['nickname']))
        else:
            self.ws.options = {**self.ws.options, 'unlisted': True}
            await self.ws.send(self.ws.options)

    @use_database
    async def _on_relist(self, user, args):
        if self.ws.options['unlisted']:
            self.ws.options = {**self.ws.options, 'unlisted': False}
            await self.ws.send(self.ws.options)
        else:
            await self.ws.sendchat('Server is already listed, {}!'.format(user['nickname']))

    @use_database
    async def _on_relist(self, user, args):
        if self.ws.options['unlisted']:
            self.ws.options = {**self.ws.options, 'unlisted': False}
            await self.ws.send(self.ws.options)
        else:
            await self.ws.sendchat('Server is already listed, {}!'.format(user['nickname']))

    async def _on_start(self, userobj, args):
        await self.ws.sendchat('Starting the game...')
        await self.ws.send({'type': 'startGame'})

    async def _on_new(self, userobj, args):
        try:
            next(filter(lambda x:x['type']=='endGame', self.ws.events))
            await self.ws.sendchat('Creating new room...')
            roomid = await self.session.createRoom(self.ws.options['roomName'], self.ws.options['unlisted'])
            await self.ws.sendchat('NOTE: I have gone to https://mafia.gg/game/{}.'.format(roomid))
            await self.ws.send({'type': 'newGame', 'roomId': roomid})
            self.ws = await self.session.joinRoomById(roomid)
        except StopIteration:
            await self.ws.sendchat('Unable to create new room.')
    
    @use_database
    async def _on_setup(self, user, args):
        self.ws.options = {**self.ws.options, 'roles': dict(map(lambda x:str.split(x, 'a'), str.split(args[0], 'b')))}
        await self.ws.send(self.ws.options)
        await self.ws.send('Changed setup, Thank you {}!'.format(user['nickname']))

    async def _on_option(self, user, args):
        typeofkey = type(self.ws.options[args[0]])
        value = args[1].strip()
        if typeofkey==bool:
            value = value.lower()=='true'
        if args[0]=='dayStart':
            if value.lower()=='informed':
                value = 'dawnStart'
            if value.lower()=='uninformed':
                value = 'dayStart'
        if args[0]=='majorityRule':
            if value.lower()=='simple':
                value = '51'
            elif value.lower()=='2/3':
                value = '66'
            elif value.lower()=='3/4':
                value = '75'
            elif value.lower()=='off':
                value = '-1'
        self.ws.options[args[0]] = typeofkey(value) #mmm python type casting mmmmm
        await self.ws.send(self.ws.options)
        await self.ws.sendchat('Set {} to {}.'.format(args[0], args[1]))
        
    async def _on_nodeck(self, user, args):
        self.ws.options = {**self.ws.options, 'deck': '-1'}
        await self.ws.send(self.ws.options)

    async def _on_deck(self, user, args):
        self.ws.options = {**self.ws.options, 'deck': str((await self.session.getDeckSamples(' '.join(args)))[0].id)}
        await self.ws.send(self.ws.options)

    async def _on_help(self, userobj, args):
        if len(args)>0 and args[0].strip()!='':
            command = args[0].lower()
            if command.startswith('!'):
                command = command[1:]
            try:
                await self.ws.sendchat(next(filter(lambda x:str.startswith(x, '!'+command), self.__doc__.split('\n'))))
            except StopIteration:
                await self.ws.sendchat('!{} does not exist!'.format(command))
            return
        for line in self.__doc__.split('\n')[:3]:
            await self.ws.sendchat(line)

    @badge_req('Auth', True)
    async def _on_kick(self, user, args):
        newuser = await self.find_user_with_filter({'username': ' '.join(args)})
        if newuser == None:
            newuser = await self.find_user_with_filter({'nickname': ' '.join(args)})
            if newuser == None:
                await self.ws.sendchat('Sorry, {}, but {} doesn\'t exist.'.format(user['nickname'], ' '.join(args)))
        await self.ws.kick(newuser)
        await self.ws.sendchat('Bye bye {}!'.format(' '.join(args)))

    @badge_req('Auth', True)
    async def _on_ban(self, user, args):
        newuser = await self.find_user_with_filter({'username': ' '.join(args)})
        if newuser == None:
            newuser = await self.find_user_with_filter({'nickname': ' '.join(args)})
            if newuser == None:
                await self.ws.sendchat('Sorry, {}, but {} doesn\'t exist.'.format(user['nickname'], ' '.join(args)))
        await self.ws.ban(newuser)
        await self.ws.sendchat('Bye bye {}! No one will miss you! [especially not {}]'.format(' '.join(args), user['nickname']))

    @use_database
    async def _on_whoami(self, user, args):
        #await self.ws.sendchat(repr(userobj))
        generatedmsg = 'You are '
        if user['nickname']==user['username']:
            generatedmsg += '{}'.format(user['username'])
        else:
            generatedmsg += '{} ({})'.format(user['nickname'], user['username'])
        if len(user['badges'])>0:
            generatedmsg += ' ' + ' '.join(map('[{}]'.format, user['badges']))
        generatedmsg += ', you have {} wins, '.format(user['wins'])
        generatedmsg += '{} losses, '.format(user['loss'])
        generatedmsg += '{} ratings, '.format(user['rating'])
        generatedmsg += '{} antiratings, '.format(user['antirating'])
        generatedmsg += 'and a permission level of {}.'.format(user['permlevel'])
        await self.ws.sendchat(generatedmsg)

    @badge_req('Admin', True)
    async def _on_badge(self, user, args):
        newuser = await self.find_user_with_filter({'username': args[0]})
        if newuser == None:
            newuser = await self.find_user_with_filter({'nickname': args[0]})
            if newuser == None:
                await self.ws.sendchat('Sorry, {}, but {} doesn\'t exist.'.format(user['nickname'], args[0]))
        await self.edit_attribute_of_user(newuser, {'badges': [' '.join(args[1:]), *newuser['badges']]})
        await self.ws.sendchat('Congrats, {}, you have the [{}] badge!'.format(newuser['nickname'], ' '.join(args[1:])))

    @badge_req('Admin', True)
    async def _on_unbadge(self, user, args):
        newuser = await self.find_user_with_filter({'username': args[0]})
        if newuser == None:
            newuser = await self.find_user_with_filter({'nickname': args[0]})
            if newuser == None:
                await self.ws.sendchat('Sorry, {}, but {} doesn\'t exist.'.format(user['nickname'], args[0]))
        badges = list(map(lambda x:x, newuser['badges']))
        badges.remove(' '.join(args[1:]))
        await self.edit_attribute_of_user(newuser, {'badges': badges})
        await self.ws.sendchat('Fs in the chat for {}, who lost the [{}] badge. F.'.format(newuser['nickname'], ' '.join(args[1:])))

    @use_database
    async def _on_nick(self, user, args):
        await self.edit_attribute_of_user(user, {'nickname': ' '.join(args)})
        await self.ws.sendchat('Goodbye, {}. Hello, {}!'.format(user['nickname'], ' '.join(args)))

    async def _greet(self, generatedname):
        await self.ws.sendchat('Welcome to the party, {}!'.format(generatedname))

    async def _invalid_(self, userobj, command, args):
        await self.ws.sendchat('{}? What?'.format(command))

    async def _error_badge_missing(self, userobj, user, badge):
        await self.ws.sendchat('Sorry, {}, but you don\'t have the [{}] badge!'.format(user['nickname'], badge))

    async def _error_badge_present(self, userobj, user, badge):
        await self.ws.sendchat('Sorry, {}, but you have the [{}] badge!'.format(user['nickname'], badge))

    async def _error_perm_missing(self, userobj, user, perm):
        await self.ws.sendchat('Sorry, {}, but you have the permission level of {}, and you just tried to'\
                               'execute a command with a required permission level of {}!'.format(user['nickname'], user['permlevel'], perm))

    async def _error_user_mismatch(self, userobj, user, usernamereq):
        await self.ws.sendchat('Sorry, {}, but you\'re not {}!'.format(user['nickname'], usernamereq))

async def main():
    hackfate = await Hackfate(config)
    await hackfate.run()

asyncio.get_event_loop().run_until_complete(main())
