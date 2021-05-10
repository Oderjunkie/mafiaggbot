# mafiaggbot
mafia.gg bot
## plans
- add tkinter ui on a different thread than the api fetch bot thing \[async threading sucks btw\]
## reverse engineering
### api
|url|post data|get data|usage|
|---|---------|--------|-----|
|https://mafia.gg/api/user-session|{login, password}|{id: USERID, username: USERNAME, email: EMAIL, hostBannedUsernames: [???], isPatreonLinked: true/false, activePatreon: true/false, needsVerification: true/false, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}|used to login to an account, use the cookies|
|https://mafia.gg/api/rooms||[{id: ROOMID, name: ROOMNAME, hasStarted: true/false, playerCount: int, setupSize: 12, hostUser: {id: USERID, username: USERNAME, activepatreon: true/false, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}, createdAt: 'yyyy-mm-ddThh:mm:ss:pppZ'}]|get list of all rooms|
|https://mafia.gg/api/rooms/ROOMID||{engineUrl: URL, auth: AUTH}|get data about specific room, URL is the engine url, AUTH is the authentication token|
||
|https://mafia.gg/api/users/USERID|||get data about specific user, specifically id, username, activePatreon, createdAt|
|https://mafia.gg/api/decks?filter&page=PAGENUM|||get data about all decks on specific page|
### websocket packets
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
#### explanation of some types
|type|format|usage|
|----|------|-----|
|USERID|str|use with the users api to find name|
|PLAYERID|str|???|
|ROOMID|str|use with the rooms api|
|UNIXTIMESTAMP|int|the unix time stamp|
|MESSAGE|str|a message|
|ROOMNAME|str|the name of a room|
|TOPIC|str|the topic of a room|
|PACKET|object|see above table|
|ROLES|object|{ROLEID: ROLEAMO, ROLEID: ROLEAMO, ....}|
|ROLEID|str|the id of a role, found in a setup code|
|ROLEAMO|str|amount of times a role appears, capped to 99 by the mafia.gg GUI, if it goes over, shows as the last number below 99|
