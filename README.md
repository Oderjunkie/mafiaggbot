# mafiaggbot
mafia.gg bot
## plans
- [COMPLETED] add tkinter ui on a different thread than the api fetch bot thing \[async threading sucks btw\]
## reverse engineering
scroll to the bottom.
### api documentation
|url|post data|get data|usage|
|---|---------|--------|-----|
|https://mafia.gg/api/user-session|{login, password}|{id: USERID, username: USERNAME, email: EMAIL, hostBannedUsernames: [???], isPatreonLinked: true/false, activePatreon: true/false, needsVerification: true/false, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}|used to login to an account, use the cookies|
|https://mafia.gg/api/rooms||[{id: ROOMID, name: ROOMNAME, hasStarted: true/false, playerCount: int, setupSize: 12, hostUser: {id: USERID, username: USERNAME, activepatreon: true/false, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}]|get list of all rooms|
|https://mafia.gg/api/rooms/ROOMID||{engineUrl: URL, auth: AUTH}|get data about specific room, URL is the engine url, AUTH is the authentication token|
||
|https://mafia.gg/api/users/USERID||{id: USERID, username: USERNAME, activepatreon: true/false, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}|get data about specific user, specifically id, username, activePatreon, createdAt|
|https://mafia.gg/api/decks?filter&page=PAGENUM||{pagination: {page: PAGENUM, numPages: 12, total: 290}, decks: [{name: DECKNAME, version: VERSION, key: DECKID, builtin: true/false, deckSize: int, uploadTimestamp: UNIXTIMESTAMP, sampleCharacters: [{playerId: int, name: str, avatarUrl: str, backgroundColor: '#rrggbb'}]}]}|get data about all decks on specific page|
|https://mafia.gg/api/decks/DECKID||{name: DECKNAME, version: VERSION,key: DECKID, builtin: true/false, deckSize: int, uploadTimestamp: UNIXTIMESTAMP, characters: [{playerId: PLAYERID, name: str, avatarUrl: str, backgroundColor: '#rrggbb'}]}|get data about a specific deck|

### websocket packets documentation
???s are the parts i haven't figured out yet.
|type|data (from server)|data (to server)|usage|
|----|------------------|----------------|-----|
|clientHandshake|{events: [PACKET], possibleUserIds: [???], sid: ?, timestamp: UNIXTIMESTAMP, users: [{userId: USERID, isHost: ISHOST, isPlayer: ISPLAYER}]}|{userId: USERID, roomId: ROOMID, auth: AUTHTOKEN}|FIRST PACKET TO SEND, starts communication between client and server|
|ping|||client -> server|
|pong|{timestamp: UNIXTIMESTAMP, sid: ?}||server -> client|
|chat|{message: MESSAGE, from: {model: 'user'/'player', userid: USERID/0, playerid: PLAYERID}}|{message: MESSAGE}|send message through the chatroom|
|newgame|{roomId: ROOMID}|SAME AS FROM SERVER|create a new room|
|options|{dayLength: 1-9, dayStart: 'off'/'dawnStart'/'dayStart', deadlockPreventionLimit: '-1'/???, deck: '-1'/DECKID, disableVoteLock: true/false, hideSetup: true/false, hostRoleSelection: true/false, majorityRule: '-1'/'51'/???, mustVote: true/false, nightLength: 1-9, noNightTalk: true/false, revealSetting: 'allReveal'/???, roles: ROLES, roomName: ROOMNAME, scaleTimer: true/false, twoKp: '0'/???, unlisted: true/false|SAME AS FROM SERVER|set the options of the room|
|startgame|||starts the game|
|decision|{details: {text: 'votes'/???, playerId: PLAYERID, targetPlayerId: PLAYERID, }, groupId: ???, id: ???, qid: ???, sid: ?, timestamp: UNIXTIMESTAMP}||voting AFAIK, prob more|
|decisionGroup|{id: ???, kind: 'vote'/???, label: 'Condemn'/???, timestamp: UNIXTIMESTAMP}||the packet to make the tiny box appear on the screen|
|alert|{timestamp: UNIXTIMESTAMP}||||
|system|{timestamp: UNIXTIMESTAMP, message: MESSAGE}||a message from the mafia game system to the client|
|time|{phase: 'day'/'night', ordinal: number, timestamp: UNIXTIMESTAMP||when a phase begins: DAY 2, NIGHT 1, etc...|
|timer|{end: UNIXTIMESTAMP, timestamp: UNIXTIMESTAMP, topic: TOPIC}||the topic is stuff like "Free period", "End-of-night buffer" and such|
|quote|{qid: ???, timestamp: UNIXTIMESTAMP, from: {model: 'user'/'player', userId: USERID/0, playerId: PLAYERID}}||quotes in the chat|
|death|{playerId: PLAYERID, timestamp: UNIXTIMESTAMP}||death|
|userJoin|{userId: USERID, timestamp: UNIXTIMESTAMP}||a user joining|
|userQuit|{userId: USERID, timestamp: UNIXTIMESTAMP}||a user exiting|
#### explanation of some types
|type|format|usage|
|----|------|-----|
|USERID|str|use with the users api to find name|
|PLAYERID|str|use the decks api, and find the card with the playerid|
|ROOMID|str|use with the rooms api|
|UNIXTIMESTAMP|int|the unix time stamp|
|MESSAGE|str|a message|
|ROOMNAME|str|the name of a room|
|TOPIC|str|the topic of a room|
|PACKET|object|see above table|
|ROLES|object|{ROLEID: ROLEAMO, ROLEID: ROLEAMO, ....}|
|ROLEID|str|the id of a role, found in a setup code|
|ROLEAMO|str|amount of times a role appears, capped to 99 by the mafia.gg GUI, if it goes over, shows as the last number below 99|
## reverse engineering
### process
#### api
open up chrome devtools using F12, use Ctrl+F5 to refresh the page and cache, go into the devtools and click on network, you should see something like this:
![image](https://user-images.githubusercontent.com/58880677/118372522-b7f89c00-b5ba-11eb-99d3-68421c12be0f.png)
right now, the only thing that you should be looking at is that "rooms" request, click on it and you'll see
![image](https://user-images.githubusercontent.com/58880677/118372556-f4c49300-b5ba-11eb-83d0-b98ade32d263.png)
you can ignore the general and response headers sections, look at the request headers (in this case you can ignore it, but thats the exception to the rule,) another thing you should look at is the response, click preview
![image](https://user-images.githubusercontent.com/58880677/118372624-55ec6680-b5bb-11eb-9432-609304fbd944.png)
as you can see, those are all the rooms you can see on the page, in json format! this is how i figured out all the ordinary api requests.
#### websocket packets
same as with api, but you must enter a game first, and you'll see this:
![image](https://user-images.githubusercontent.com/58880677/118372703-9c41c580-b5bb-11eb-8368-dc5a2dfeff37.png)
the "engine" request is the only important thing here. click on it.

you can ignore the headers for all websocket packets, just click on messages and you'll see this:
![image](https://user-images.githubusercontent.com/58880677/118372763-d14e1800-b5bb-11eb-96d5-7cfdda611b4e.png)
each of these rows is a different packet: red arrows pointing down are the packets from the server, to the client; green arrows pointing up are the packets from the client, to the server.
