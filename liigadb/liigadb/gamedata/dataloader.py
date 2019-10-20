
import json, sys, datetime

from django.utils.text import slugify
from django.utils.dateparse import parse_duration
from liigadb.gamedata.models import *


class Data(object):
    def __init__(self, data):
        self._data = data
        for attr in data:
            value = data[attr]
            if type(value) is dict:
                value = Data(value)
            setattr(self, attr, value)

    def tojson(self):
        return json.dumps(self._data, indent=4, sort_keys=True)


class EventList(object):

    def __init__(self):
        self.events = []

    def append(self, type, event):
        self.events.append((type, event))

    def get(self, type):
        return [e for (t,e) in self.events if t == type]

    def __iter__(self):
        for (t,e) in self.events:
            yield e



class TeamEvents(object):
    def __init__(self):
        self.timeout = None
        self.penalties = []

def parsetime(t):
    if type(t) is datetime.timedelta:
        return t
    return parse_duration(t)

def timediff(t1, t2):
    if t1:
        return (t2-t1)

def td2str(td):
    if td is not None:
        return "%02d:%02d" % (td.seconds/60, td.seconds%60)

def tdm2str(tdm):
    if tdm is not None:
        td = tdm/60
        return "%02d:%02d" % (td.seconds/60, td.seconds%60)

class GameStatus(object):
    def __init__(self, game, hometeam_id, awayteam_id):
        self.game = game
        self.hometeam_id = hometeam_id
        self.awayteam_id = awayteam_id
        self.score = '0-0'
        self.home = TeamEvents()
        self.away = TeamEvents()
        self.latesteventtime = None
        self.latestevents = EventList()
        self.penalties = []
        self.latesthomepenalty = None
        self.latestawaypenalty = None
        self.latesthomegoal = None
        self.latestawaygoal = None
        self.latestpenalty = None

    def setscore(self, score, team_id):
        self.score = score

    def ishometeam(self, team_id):
        if team_id not in [self.hometeam_id, self.awayteam_id]:
            raise Exception('Unknown team id %s, game %s, home: %s, away: %s' % (team_id, self.game.id, self.hometeam_id, self.awayteam_id))
        return (team_id == self.hometeam_id)

    def getscore(self, team_id):
        if self.ishometeam(team_id):
            return self.score
        else:
            return self.score[::-1]

    def getgoals(self, team_id):
        score = self.getscore(team_id)
        return int(score.split('-')[0])

    def getlatestpenalty(self):
        return self.latestpenalty

    def getlatestpenaltytime(self, team_id, time):
        if self.ishometeam(team_id):
            return td2str(timediff(self.latesthomepenalty, time))
        else:
            return td2str(timediff(self.latestawaypenalty, time))

    def getlatestgoaltime(self, team_id, time):
        if self.ishometeam(team_id):
            return td2str(timediff(self.latesthomegoal, time))
        else:
            return td2str(timediff(self.latestawaygoal, time))

    def getgoaldiff(self, team_id):
        return eval(self.getscore(team_id))

    def wongame(self, team_id):
        if self.ishometeam(team_id):
            return (self.game.homescore > self.game.awayscore)
        else:
            return (self.game.awayscore > self.game.homescore)

    def getteamresult(self, team_id):
        if self.ishometeam(team_id):
            return DataLoader.getresult(self.game.homescore, self.game.awayscore, self.game.time, self.game.playoffs)
        else:
            return DataLoader.getresult(self.game.awayscore, self.game.homescore, self.game.time, self.game.playoffs)
        

    def newevent(self, type, event):
        if event.time != self.latesteventtime:
            self.simultaneousevents(self.latestevents)
            self.latesteventtime = event.time
            self.latestevents = EventList()
        self.latestevents.append(type, event)
        if event.athome:
            return self.home, self.away
        else:
            return self.away, self.home

    def simultaneousevents(self, events):
        for g in events.get('goal'):
            for t in events.get('timeout'):
                if t.team == g.team:
                    t.goals = 1
                else:
                    t.goals = -1
            
        for e in events:
            e.save()


    def event_goal(self, goal):
        teamdatas = self.newevent('goal', goal)
        for td in teamdatas:
            if td.timeout and td.timeout.time == goal.time:
                td.timeout.score = goal.score
                td.timeout.teamscore = self.getscore(td.timeout.team.id)
                td.timeout.goaldiff = self.getgoaldiff(td.timeout.team.id)
                td.timeout.teamgoals = self.getgoals(td.timeout.team.id)
                td.timeout.vsteamgoals = self.getgoals(td.timeout.vsteam.id)
                td.timeout.save()
        if goal.athome:
            self.latesthomegoal = parsetime(goal.time)
        else:
            self.latestawaygoal = parsetime(goal.time)


        released = ('SR' in goal.goalattr)
        for p in self.penalties:
            if p.team == goal.vsteam and p.minutes == 2 and not released:
                released = True
                self.penalties.remove(p)
                p.boxtime = g.time - p.time
            if p.team == goal.team:
                p.goalfor += 1
            elif p.team == goal.vsteam:
                p.goalagainst += 1
            p.save()

    def event_penalty(self, penalty):
        (tdata, vstdata) = self.newevent('penalty', penalty)
        tdata.penalties.append(penalty)
        if penalty.minutes > 0 and penalty.minutes < 10:
            self.latestpenalty = penalty
            if penalty.athome:
                self.latesthomepenalty = parsetime(penalty.time)
            else:
                self.latestawaypenalty = parsetime(penalty.time)

        
    def event_penaltyshot(self, penaltyshot):
        teamdatas = self.newevent('penaltyshot', penaltyshot)
        
    def event_timeout(self, timeout):
        (td, vstd) = self.newevent('timeout', timeout)
        td.timeout = timeout
        
    def event_videocheck(self, videocheck):
        pass
        
    def event_gkevent(self, gkevent):
        pass
        
    def event_shot(self, shot):
        pass
        
class DataLoader(object):

    @classmethod
    def loaddata(cls, path):
        with open(path) as fp:
            for l in fp:
                if not l.strip(): continue
                data = Data(json.loads(l))

                loadmethod = getattr(cls, "load_%s" % data.type, None)
                if not loadmethod:
                    print(data.tojson())
                    raise Exception("No loader for type %s" % data.type)
                try:
                    loadmethod(data)
                except:
                    print(data.tojson())
                    raise

        
    @classmethod
    def load_season(cls, data):
        Season.objects.update_or_create(
            id = data.id,
            defaults = dict(
                years = data.years
            )
        )

    @classmethod
    def load_team(cls, data):
        Team.objects.update_or_create(
            id = data.id,
            defaults = dict(
                name = data.name
            )
        )

    @classmethod
    def getresult(cls, score1, score2, t, playoffs):
        s1 = int(score1)
        s2 = int(score2)
        if t == '60:00':
            return "%d-%d" % (s1, s2)
        elif playoffs:
            return "%d-%d JE" % (s1, s2)
        elif t < '65:00':
            return "%d-%d JA" % (s1, s2)
        elif t == '65:00':
            return "%d-%d VL" % (s1, s2)
        else:
            raise Exception("Unknown game time %s" % t)

    @classmethod
    def load_game(cls, data):
        hometeam = Team.objects.get(id=data.home.team)
        awayteam = Team.objects.get(id=data.away.team)
        season = Season.objects.get(years=data.season)
        if data.playoffs:
            homepoints = None
            awaypoints = None
        else:
            homepoints = data.home.points
            awaypoints = data.away.points

        (game, _) = Game.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = data.playoffs,
                identifier = data.identifier,
                number = data.number,
                date = data.date,
                attendance = data.attendance,
                periodscores = data.periods,
                homescore = data.home.score,
                awayscore = data.away.score,
                homepoints = homepoints,
                awaypoints = awaypoints,
                hometeam = hometeam,
                awayteam = awayteam,
                time = data.time,
                result = cls.getresult(data.home.score, data.away.score, data.time, data.playoffs),
            )
        )
        print("%s\r" % data.id, end='')
        sys.stdout.flush()
        cls.gamestatus = GameStatus(game, hometeam.id, awayteam.id)

    @classmethod
    def get_player(cls, data, season, team=None):
        if data:
            team = Team.objects.get(id=data.team)
            teamplayer = TeamPlayer.objects.get(
                id = data.id + str(season.id) + team.id + str(data.number)
            )
            return teamplayer


    @classmethod
    def check_gamestatus(cls, gameid):
        if cls.gamestatus.game.id != gameid:
            raise Exception("gamestatus gameid mismatch %s/%s" % (cls.gamestatus.gameid, gameid))

    @classmethod
    def load_gameevent(cls, data):
        team = Team.objects.get(id=data.team)
        vsteam = Team.objects.get(id=data.vsteam)
        season = Season.objects.get(years=data.season)
        cls.check_gamestatus(data.gameid)
        game = cls.gamestatus.game
        wongame = cls.gamestatus.wongame(data.team)
        otgame = (game.time > '60:00')

        td = parsetime(data.time)

        genericvalues = dict(
            time = data.time,
            period = data.period,
            season = season,
            playoffs = data.playoffs,
            game = game,
            team = team,
            vsteam = vsteam,
            athome = (team == game.hometeam),
            teamscore = cls.gamestatus.getscore(team.id),
            vsteamscore = cls.gamestatus.getscore(vsteam.id),
            goaldiff = cls.gamestatus.getgoaldiff(team.id),
            teamgoals = cls.gamestatus.getgoals(team.id),
            vsteamgoals = cls.gamestatus.getgoals(vsteam.id),
            latestpenalty = cls.gamestatus.getlatestpenaltytime(team.id, td),
            latestpenaltyvs = cls.gamestatus.getlatestpenaltytime(vsteam.id, td),
            latestgoal = cls.gamestatus.getlatestgoaltime(team.id, td),
            latestgoalvs = cls.gamestatus.getlatestgoaltime(vsteam.id, td),
            wongame = wongame,
            otgame = otgame,
            gameresult = cls.gamestatus.getteamresult(team.id),
            gameresultvs = cls.gamestatus.getteamresult(vsteam.id),
        )

        if data.eventtype == 'goal':
            scorer = cls.get_player(data.scorer, season)
            assist1 = cls.get_player(data.assist1, season)
            assist2 = cls.get_player(data.assist2, season)
            cls.gamestatus.setscore(data.score, team.id)
            values = dict(
                scorer = scorer,
                assist1 = assist1,
                assist2 = assist2,
                goalattr = data.goalattr,
                score = data.score,
            )
            values.update(genericvalues)
            values.update(dict(
                teamscore = cls.gamestatus.getscore(team.id),
                vsteamscore = cls.gamestatus.getscore(vsteam.id),
                goaldiff = cls.gamestatus.getgoaldiff(team.id),
                teamgoals = cls.gamestatus.getgoals(team.id),
                vsteamgoals = cls.gamestatus.getgoals(vsteam.id),
                )
            )

            (goal, _) = Goal.objects.update_or_create(
                id = data.id,
                defaults = values
            )
            cls.gamestatus.event_goal(goal)
            if 'RL' in data.goalattr or 'VL' in data.goalattr:
                values = dict(
                    player = scorer,
                    scored = True,
                    goalattr = data.goalattr,
                )
                if 'VL' in data.goalattr:
                    values['order'] = data.psorder
                    values['teamorder'] = data.psteamorder
                    try:
                        values['keeper'] = cls.get_player(data.pskeeper, season)
                    except:
                        values['keeper'] = None
                values.update(genericvalues)

                (penaltyshot, _) = PenaltyShot.objects.update_or_create(
                    id = data.id,
                    defaults = values,
                )
                cls.gamestatus.event_penaltyshot(penaltyshot)
            if 'VT' in data.goalattr:
                values = dict(
                    scored = True
                )
                values.update(genericvalues)
                (videocheck, _) = Videocheck.objects.update_or_create(
                    id = data.id,
                    defaults = values
                )
                cls.gamestatus.event_videocheck(videocheck)
                
        elif data.eventtype == 'penalty':
            player = cls.get_player(data.player, season)
            boxed = cls.get_player(data.boxed, season)
            values = dict(
                player = player,
                boxed = boxed,
                reason = data.reason,
                minutes = data.minutes,
            )
            lastpenalty = cls.gamestatus.getlatestpenalty()
            if 0 and lastpenalty and player and lastpenalty.player:
                print(lastpenalty.player.id == player.id, lastpenalty.reason == data.reason, lastpenalty.time == values, lastpenalty.minutes == data.minutes, player.id, data.reason, data.time, data.minutes)
                print(lastpenalty.time, type(lastpenalty.time), type(data.time))

            if (lastpenalty and player and lastpenalty.player and
                lastpenalty.player.id == player.id and
                lastpenalty.reason == data.reason and
                lastpenalty.time == data.time and
                lastpenalty.minutes == data.minutes):

                lastpenalty.minutes = lastpenalty.minutes+data.minutes
                lastpenalty.save()
                #print "HEREEEEE!"
            else:
                values.update(genericvalues)
                (penalty, _) = Penalty.objects.update_or_create(
                    id = data.id,
                    defaults = values
                )
                cls.gamestatus.event_penalty(penalty)
        elif data.eventtype == 'timeout':
            (timeout, _) = Timeout.objects.update_or_create(
                id = data.id,
                defaults = genericvalues
            )
            cls.gamestatus.event_timeout(timeout)
        elif data.eventtype == 'videocheck':
            values = dict(
                scored = False
            )
            values.update(genericvalues)
            (videocheck, _) = Videocheck.objects.update_or_create(
                id = data.id,
                defaults = values
            )
            cls.gamestatus.event_videocheck(videocheck)

        elif data.eventtype == 'goalkeeper':
            playerin = cls.get_player(data.playerin, season)
            playerout = cls.get_player(data.playerout, season)
            values = dict(
                event = data.event,
                playerin = playerin,
                playerout = playerout,
            )
            values.update(genericvalues)
            (gkevent, _) = GoalkeeperEvent.objects.update_or_create(
                id = data.id,
                defaults = values
            )
            cls.gamestatus.event_gkevent(gkevent)

        elif data.eventtype == 'penaltyshot':
            player = cls.get_player(data.player, season)
            if data.keeper:
                try:
                    keeper = cls.get_player(data.keeper, season)
                except:
                    keeper = None
            else:
                keeper = None
            values = dict(
                player = player,
                scored = data.scored,
                keeper = keeper,
            )
            if data.period == 'VL':
                values['order'] = data.psorder
                values['teamorder'] = data.psteamorder
            values.update(genericvalues)
            (penaltyshot, _) = PenaltyShot.objects.update_or_create(
                id = data.id,
                defaults = values
            )
            cls.gamestatus.event_penaltyshot(penaltyshot)

        elif data.eventtype == 'shot':
            values = dict(
                shooter = cls.get_player(data.shooter, season, data.team),
                blocker = cls.get_player(data.blocker, season, data.vsteam),
                result = data.result,
            )
            values.update(genericvalues)
            values['latestpenalty'] = None
            values['latestpenaltyvs'] = None
            values['latestgoal'] = None
            values['latestgoalvs'] = None
            (shot, _) = Shot.objects.update_or_create(
                id = data.id,
                defaults = values
            )
            cls.gamestatus.event_shot(shot)


        else:
            raise Exception("Unknown game event: %s" % data.eventtype)


    @classmethod
    def get_playerdata(cls, data):
        team = Team.objects.get(id=data.team)
        season = Season.objects.get(years=data.season)
        cls.check_gamestatus(data.gameid)
        game = cls.gamestatus.game
        player, _ = Player.objects.update_or_create(
            id = data.id,
            defaults = dict(
                name = data.name,
            )
        )
        teamplayer, _ = TeamPlayer.objects.update_or_create(
            id = player.id + str(season.id) + team.id + str(data.number),
            defaults = dict(
                team = team,
                player = player,
                season = season,
                number = data.number,
            )
        )
        athome = (teamplayer.team == game.hometeam)
        if athome:
            vsteam = game.awayteam
        else:
            vsteam = game.hometeam

        return (team, vsteam, season, game, player, teamplayer, athome)

    @classmethod
    def load_player(cls, data):
        (team, vsteam, season, game, player, teamplayer, athome) = cls.get_playerdata(data)
        
        playtime = parsetime(data.playtime)
        playerstats, _ = PlayerGameStats.objects.update_or_create(
            id = player.id + str(game.id),
            defaults = dict(
                game = game,
                playoffs = data.playoffs,
                player = teamplayer,
                team = team,
                vsteam = vsteam,
                position = data.position,
                goals = data.goals,
                assists = data.assists,
                points = data.points,
                penalties = data.penalties,
                plus = data.plus,
                minus = data.minus,
                plusminus = data.plusminus,
                ppgoals = data.ppgoals,
                shgoals = data.shgoals,
                wingoal = data.wingoal,
                shots = data.shots,
                shotpct = data.shotpct,
                faceoffs = data.faceoffs,
                faceoffpct = data.faceoffpct,
                playtime = playtime,
                athome = athome,
                lineno = data.lineno,
                gh = data.gh,
                skating = getattr(data, 'skating', None)
            )
        )

    @classmethod
    def load_goalkeeper(cls, data):
        (team, vsteam, season, game, player, teamplayer, athome) = cls.get_playerdata(data)
        
        playtime = parsetime(data.playtime)
        playerstats, _ = GoalkeeperStats.objects.update_or_create(
            id = player.id + str(game.id),
            defaults = dict(
                game = game,
                playoffs = data.playoffs,
                player = teamplayer,
                team = team,
                vsteam = vsteam,
                goals = data.goals,
                goalsagainst = data.goalsagainst,
                assists = data.assists,
                points = data.points,
                penalties = data.penalties,
                saves = data.saves,
                savepct = data.savepct,
                playtime = playtime,
                athome = athome,
                started = data.starting,
            )
        )

    @classmethod
    def load_referee(cls, data):
        if data.number == 0:
            refs = Referee.objects.filter(number=0)
            data.id = data.gameid*1000+len(refs)+1
        
        referee, _ = Referee.objects.update_or_create(
            name=data.name,
            number=data.number
        )
        
        season = Season.objects.get(years=data.season)
        game = cls.gamestatus.game
        regame, _ = RefereeGame.objects.update_or_create(
            id = data.id,
            season = season,
            game = game,
            playoffs = data.playoffs,
            referee = referee,
            reftype = data.reftype
        )
        


    @classmethod
    def load_period(cls, data):
        season = Season.objects.get(years=data.season)
        game = cls.gamestatus.game
        hometeam = Team.objects.get(id=data.home.team)
        awayteam = Team.objects.get(id=data.away.team)
        (period, _) = Period.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = data.playoffs,
                period = data.period,
                game = game,
                hometeam = hometeam,
                awayteam = awayteam,
                homescore = data.home.score,
                awayscore = data.away.score,
                gamehomescore = data.home.gamescore,
                gameawayscore = data.away.gamescore,
                homeshots = data.home.shots,
                awayshots = data.away.shots,
                homefaceoffs = data.home.faceoffs,
                awayfaceoffs = data.away.faceoffs,
                homeblocked = data.home.blocked,
                awayblocked = data.away.blocked,
                homemissed = data.home.missed,
                awaymissed = data.away.missed,
                homesaved = data.home.saved,
                awaysaved = data.away.saved,
            )
        )

    @classmethod
    def load_gamestats(cls, data):
        season = Season.objects.get(years=data.season)
        game = cls.gamestatus.game
        hometeam = Team.objects.get(id=data.home.team)
        awayteam = Team.objects.get(id=data.away.team)
        (period, _) = Gamestats.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = data.playoffs,
                game = game,
                hometeam = hometeam,
                awayteam = awayteam,
                homescore = data.home.score,
                awayscore = data.away.score,
                homeshots = data.home.shots,
                awayshots = data.away.shots,
                homefaceoffs = data.home.faceoffs,
                awayfaceoffs = data.away.faceoffs,
                homeblocked = data.home.blocked,
                awayblocked = data.away.blocked,
                homemissed = data.home.missed,
                awaymissed = data.away.missed,
                homesaved = data.home.saved,
                awaysaved = data.away.saved,
                homeppgoals = data.home.ppgoals,
                awayppgoals = data.away.ppgoals,
                homeppchances = data.home.ppchances,
                awayppchances = data.away.ppchances,
                homepppct = data.home.pppct,
                awaypppct = data.away.pppct,
                homepptime = data.home.pptime,
                awaypptime = data.away.pptime,
            )
        )

        for (locdata, team, playerattr, attribute, recordattr) in [
                (data.home, hometeam, 'fastestshooter', 'fastestshot', 'shootingrecord'),
                (data.away, awayteam, 'fastestshooter', 'fastestshot', 'shootingrecord'),
                (data.home, hometeam, 'fastestskater', 'fastestskating', 'skatingrecord'),
                (data.away, awayteam, 'fastestskater', 'fastestskating', 'skatingrecord'),
                ]:

            if not hasattr(locdata, attribute):
                continue
            playerdata = getattr(locdata, playerattr)
            value = getattr(locdata, attribute)

            if playerdata and value:
                pgs = PlayerGameStats.objects.get(
                    id = playerdata.id + str(game.id)
                )
                if pgs:
                    setattr(pgs, recordattr, value)
                    pgs.save()


def loaddata(path):
    DataLoader.loaddata(path)


class Penalties(object):

    class PenaltyList(object):
        def __init__(self, parent):
            self.penalties = []
            self.stacked = []
            self.pending = []
            self.equal = []

        def add(self, penalty):
            self.pending.append(penalty)

        def addpending(self):
            for penalty in self.pending:
                secondpenalty = False
                for p in self.penalties:
                    if p.player and penalty.player and p.player.id == penalty.player.id:
                        penalty.secondpenalty = p.minutes
                        secondpenalty = True
                        break
                if len(self.penalties) > 1 or secondpenalty:
                    self.stacked.append(penalty)
                else:
                    penalty.starttime = penalty.time
                    self.penalties.append(penalty)
            return self.pending
            

        def endpenalty(self, time, goal):
            penaltyends = None
            stacked = None
            for p in self.penalties:
                if p.minutes == 2:
                    self.penalties.remove(p)
                    penaltyends = p
                    if self.stacked:
                        stacked = self.stacked.pop(0)
                        stacked.starttime = time
                        self.penalties.append(stacked)
                    break
            return (penaltyends, stacked)

        def length(self):
            return len(self.penalties)

        def expire(self, time):
            expired = []
            started = []
            for p in self.penalties:
                pt = parsetime(p.starttime) + datetime.timedelta(minutes=p.minutes) 
                if pt < parsetime(time):
                    self.penalties.remove(p)
                    if self.stacked:
                        stacked = self.stacked.pop(0)
                        stacked.starttime = td2str(pt)
                        started.append(stacked)
                        if pt + datetime.timedelta(minutes=stacked.minutes) < parsetime(time):
                            stacked.endtime = td2str(pt+datetime.timedelta(minutes=stacked.minutes))
                            expired.append(stacked)
                        else:
                            self.penalties.append(stacked)
                    p.endtime = td2str(pt)
                    expired.append(p)
            return (expired, started)
        

    def __init__(self):
        self.home = self.PenaltyList(self)
        self.away = self.PenaltyList(self)

    def length(self):
        return self.home.length()+self.away.length()
            

    def findequal(self):
        equals = []
        found = False
        
        for h in self.home.pending:
            for a in self.away.pending:
                if h.minutes == a.minutes and h.reason == a.reason:
                    if h in self.home.pending and a in self.away.pending and (len(self.home.pending) != 1 or len(self.away.pending) != 1):
                        print("EQ",  a.time, a.player.id, a.minutes, a.reason, h.time, h.player.id, h.minutes, h.reason)
                        
                        self.home.equal.append(h)
                        self.away.equal.append(a)
                        self.home.pending.remove(h)
                        self.away.pending.remove(a)
                        equals.append(h)
                        equals.append(a)

        return equals
        

    def tick(self, time):
        startingpenalties = self.findequal() + self.home.addpending() + self.away.addpending()
        self.home.pending = []
        self.away.pending = []

        return startingpenalties 

    def expire(self, time):
        (hexpired, hstarted) = self.home.expire(time)
        (aexpired, astarted) = self.away.expire(time)
        return (hexpired + aexpired, hstarted + astarted)


class Analyzer(object):
    def __init__(self, game):
        self.hometeam = game.home.team
        self.awayteam = game.away.team
        self.gameid = game.id
        self.penalties = Penalties()
        self.homegoalieaway = 0
        self.awaygoalieaway = 0
        self.baseplayers = 5
        self.lasttick = None

    def getplayers(self):
        home = self.baseplayers + self.homegoalieaway - self.penalties.home.length()
        away = self.baseplayers + self.awaygoalieaway - self.penalties.away.length()
        return "[%d-%d]" % (home, away)

    def penalty(self, athome, penalty):
        if penalty.minutes and penalty.minutes < 10:
            if athome:
                self.penalties.home.add(penalty)
            else:
                self.penalties.away.add(penalty)
        #print "%s %s %-10s %2d min %-30s (%s)" % (self.getplayers(), penalty.time, penalty.team, penalty.minutes, penalty.reason, playerid) 

    def goal(self, athome, goal):
        penaltyends = None
        print("%s %s %-10s %-5s %s (%s) %s" % (self.getplayers(), goal.time, goal.team, goal.score, goal.goalattr, goal.scorer.id, athome))
        if self.penalties.home.length() == self.penalties.away.length():
            return
        if athome:
            (penaltyends, starts) = self.penalties.away.endpenalty(goal.time, goal)
        else:
            (penaltyends, starts) = self.penalties.home.endpenalty(goal.time, goal)

        if penaltyends:
            print("%s %s %-10s %2d min ends %s (goal)" % (self.getplayers(), goal.time, penaltyends.team, penaltyends.minutes, penaltyends.id))
        if starts:
            print("%s %s %-10s %2d min starts %s (goal)" % (self.getplayers(), goal.time, starts.team, starts.minutes, starts.id))



    def eventtick(self, time):
        if self.lasttick != time:
            penalties = self.penalties.tick(time)
            for p in penalties:
                if p.player:
                    playerid = p.player.id
                else:
                    playerid = None
                print("%s %s %-10s %2d min %-30s (%s) %s" % (self.getplayers(), p.time, p.team, p.minutes, p.reason, playerid, p.id))

            (expired, started) = self.penalties.expire(time)

            for p in expired:
                #print "%s %s %-10s %2d min ends %s (%s)" % (self.getplayers(), "", p.team, p.minutes, p.id, time)
                print("%s %s %-10s %2d min ends %s (%s)" % (self.getplayers(), p.endtime, p.team, p.minutes, p.id, time))

            for p in started:
                print("%s %s %-10s %2d min starts %s (%s)" % (self.getplayers(), p.starttime, p.team, p.minutes, p.id, time))
            self.lasttick = time


class DataAnalyze(DataLoader):
    game = None

    @classmethod
    def load_season(cls, data):
        pass

    @classmethod
    def load_team(cls, data):
        pass

    @classmethod
    def load_game(cls, data):
        cls.game = Analyzer(data)
        print()
        print(data.id, data.home.team, data.away.team)

    @classmethod
    def load_period(cls, data):
        pass

    @classmethod
    def load_gamestats(cls, data):
        pass

    @classmethod
    def load_player(cls, data):
        pass

    @classmethod
    def load_goalkeeper(cls, data):
        pass

    @classmethod
    def load_gameevent(cls, data):
        cls.game.eventtick(data.time)
        athome = (data.team == cls.game.hometeam)
        if data.eventtype == 'goal':
            cls.game.goal(athome, data)
        elif data.eventtype == 'penalty':
            cls.game.penalty(athome, data)
        else:
            pass

            
class Calendar(DataLoader):

    @classmethod
    def load_game(cls, data):
        hometeam = Team.objects.get(id=data.hometeam)
        awayteam = Team.objects.get(id=data.awayteam)
        season = Season.objects.get(years=data.season)


        (game, _) = GameMeta.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = False,
                identifier = data.identifier,
                number = data.number,
                date = data.date,
                hometeam = hometeam,
                awayteam = awayteam,
                starttime = data.time,
                datetime = "%s %s+03" % (data.date, data.time)
            )
        )
        print("%s\r" % data.id, end='')
        sys.stdout.flush()

class OldLiiga(DataLoader):
    nullnumbers = {}
    gamestatus = None

    @classmethod
    def load_game(cls, data):
        hometeam = Team.objects.get(id=data.home_team)
        awayteam = Team.objects.get(id=data.away_team)
        season = Season.objects.get(years=data.season)
        if data.playoffs:
            homepoints = None
            awaypoints = None
        else:
            homepoints = data.home_points
            awaypoints = data.away_points
        gametime = data.time
        if gametime is None:
            gametime = '00:00'

        (game, _) = Game.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = data.playoffs,
                identifier = data.identifier,
                number = data.number,
                date = data.date,
                attendance = data.attendance,
                homescore = data.home_goals,
                awayscore = data.away_goals,
                homepoints = homepoints,
                awaypoints = awaypoints,
                hometeam = hometeam,
                awayteam = awayteam,
                time = gametime,
                result = data.score,
            )
        )
        print("%s\r" % data.id, end='')
        sys.stdout.flush()
        cls.gamestatus = GameStatus(game, hometeam.id, awayteam.id)

    @classmethod
    def check_gamestatus(cls, gameid, gametime = None):
        
        if not cls.gamestatus or cls.gamestatus.game.id != gameid:
            game = Game.objects.get(id=gameid)
            cls.gamestatus = GameStatus(game, game.hometeam.id, game.awayteam.id)
            if gametime:
                cls.gamestatus.goals = game.goals.all().order_by('id')
        if gametime:
            prevg = None
            for g in cls.gamestatus.goals:
                if g.time > gametime:
                    break
                prevg = g
                cls.gamestatus.setscore(g.score, g.team.id)
                cls.gamestatus.event_goal(g)
            

    @classmethod
    def get_playerdata(cls, data):
        team = Team.objects.get(id=data.team)
        season = Season.objects.get(years=data.season)
        cls.check_gamestatus(data.gameid)
        game = cls.gamestatus.game
        player, _ = Player.objects.update_or_create(
            id = data.player,
            defaults = dict(
                name = data.name,
            )
        )
        athome = (team == game.hometeam)
        if athome:
            vsteam = game.awayteam
        else:
            vsteam = game.hometeam

        if data.number is None:
            try:
                teamplayer = TeamPlayer.objects.get(player=player, season=season, team=team)
                return (team, vsteam, season, game, player, teamplayer, athome)
            except TeamPlayer.DoesNotExist:
                pass
            except TeamPlayer.MultipleObjectsReturned:
                for teamplayer in TeamPlayer.objects.filter(player=player, season=season, team=team):
                    return (team, vsteam, season, game, player, teamplayer, athome)

        teamplayer, _ = TeamPlayer.objects.update_or_create(
            id = player.id + str(season.id) + team.id + str(data.number),
            defaults = dict(
                team = team,
                player = player,
                season = season,
                number = data.number,
            )
        )
        if data.number is None:
            cls.nullnumbers[(team.id, player.id, season.id)] = teamplayer
        else:
            nullplayer = cls.nullnumbers.get((team.id, player.id, season.id))
            if nullplayer:
                PlayerGameStats.objects.filter(player_id=nullplayer.id).update(player_id=teamplayer.id)
                Goal.objects.filter(scorer_id=nullplayer.id).update(scorer_id=teamplayer.id)
                Goal.objects.filter(assist1_id=nullplayer.id).update(assist1_id=teamplayer.id)
                Goal.objects.filter(assist2_id=nullplayer.id).update(assist2_id=teamplayer.id)
                Penalty.objects.filter(player_id=nullplayer.id).update(player_id=teamplayer.id)
                nullplayer.delete()
                del cls.nullnumbers[(team.id, player.id, season.id)]

        return (team, vsteam, season, game, player, teamplayer, athome)

    @classmethod
    def load_player(cls, data):
        (team, vsteam, season, game, player, teamplayer, athome) = cls.get_playerdata(data)
        
        if data.playtime is not None:
            playtime = parsetime(data.playtime)
        else:
            playtime = None
        if data.penalties is not None:
            penalties = data.penalties
        else:
            penalties = 0
        
        playerstats, _ = PlayerGameStats.objects.update_or_create(
            id = player.id + str(game.id),
            defaults = dict(
                game = game,
                playoffs = data.playoffs,
                player = teamplayer,
                team = team,
                vsteam = vsteam,
                position = data.position,
                goals = data.goals,
                assists = data.assists,
                points = data.points,
                penalties = penalties,
                plus = data.plus,
                minus = data.minus,
                plusminus = data.plusminus,
                playtime = playtime,
                athome = athome,
                lineno = data.lineno,
            )
        )

        
    @classmethod
    def getPlayer(cls, playerid, game, team=None):
        if not playerid: return None
        player = Player.objects.get(id=playerid)
        for tp in player.teams.filter(season=game.season):
            try:
                pgs = tp.games.get(game=game)
                return pgs.player
            except PlayerGameStats.DoesNotExist:
                pass

        #print("HERE", playerid, game, team, game.hometeam)
        if team:
            tp = TeamPlayer.objects.get(player=player, season=game.season, team=team)
            #print("TP:", tp)
            return tp
                    
        raise Exception("TeamPlayer %s for game %s not found" % (playerid, game))
            
    @classmethod
    def load_goal(cls, data):
        cls.check_gamestatus(data.gameid)

        game = cls.gamestatus.game
        athome = (data.team == game.hometeam.id)
        homegoals = cls.gamestatus.getgoals(game.hometeam.id)
        awaygoals = cls.gamestatus.getgoals(game.awayteam.id)
        if athome:
            homegoals += 1
            team = game.hometeam
            vsteam = game.awayteam
        else:
            awaygoals += 1
            team = game.awayteam
            vsteam = game.hometeam
        cls.gamestatus.setscore("%d-%d" % (homegoals, awaygoals), data.team)

        gtimetxt = data.time
        eventnum = 0
        goalid = data.gameid * 1000000 + int(gtimetxt.replace(':',''))*100 + eventnum
        td = parsetime(data.time)

        scorer = cls.getPlayer(data.scorer, game)
        assist1 = cls.getPlayer(data.assist1, game)
        assist2 = cls.getPlayer(data.assist2, game)

        (goal, _) = Goal.objects.update_or_create(
            id = goalid,
            defaults = dict(
                scorer = scorer,
                assist1 = assist1,
                assist2 = assist2,
                time = data.time,
                game = game,
                team = team,
                vsteam = vsteam,
                season = game.season,
                goalattr = data.goalattr,
                score = cls.gamestatus.score,
                teamscore = cls.gamestatus.getscore(team.id),
                vsteamscore = cls.gamestatus.getscore(vsteam.id),
                goaldiff = cls.gamestatus.getgoaldiff(team.id),
                teamgoals = cls.gamestatus.getgoals(team.id),
                vsteamgoals = cls.gamestatus.getgoals(vsteam.id),
                latestgoal = cls.gamestatus.getlatestgoaltime(team.id, td),
                latestgoalvs = cls.gamestatus.getlatestgoaltime(vsteam.id, td),
                playoffs = game.playoffs,
                wongame = cls.gamestatus.wongame(data.team),
                athome = athome,
                otgame = (game.time > parsetime('60:00'))
            )
        )
        cls.gamestatus.event_goal(goal)

    @classmethod
    def load_xpenalty(cls, data):
        pass
    
    @classmethod
    def load_penalty(cls, data):
        gtimetxt = data.time
        td = parsetime(data.time)
        cls.check_gamestatus(data.gameid, td)

        game = cls.gamestatus.game
        athome = (data.team == game.hometeam.id)
        if athome:
            team = game.hometeam
            vsteam = game.awayteam
        else:
            team = game.awayteam
            vsteam = game.hometeam

        eventnum = 0
        penaltyid = data.gameid * 1000000 + int(gtimetxt.replace(':',''))*100 + eventnum
        player = cls.getPlayer(data.player, game, team)
        (penalty, _) = Penalty.objects.update_or_create(
            id = penaltyid,
            defaults = dict(
                player = player,
                time = data.time,
                game = game,
                team = team,
                vsteam = vsteam,
                season = game.season,
                minutes = data.minutes,
                reason = data.reason,
                playoffs = game.playoffs,
                teamscore = cls.gamestatus.getscore(team.id),
                vsteamscore = cls.gamestatus.getscore(vsteam.id),
                goaldiff = cls.gamestatus.getgoaldiff(team.id),
                teamgoals = cls.gamestatus.getgoals(team.id),
                vsteamgoals = cls.gamestatus.getgoals(vsteam.id),
                latestgoal = cls.gamestatus.getlatestgoaltime(team.id, td),
                latestgoalvs = cls.gamestatus.getlatestgoaltime(vsteam.id, td),
                wongame = cls.gamestatus.wongame(data.team),
                athome = athome,
                otgame = (game.time > parsetime('60:00'))
            )
        )
        cls.gamestatus.event_penalty(penalty)
        


def oldliiga(path):
    OldLiiga.loaddata(path)

def analyze(path):
    DataAnalyze.loaddata(path)

def calendar(path):
    Calendar.loaddata(path)

class StatePerTime(object):

    def __init__(self, values, initial):
        self.values = values
        self.latestvalue = initial
        if values:
            self.nextlimit = values[0][0]
        else:
            self.nextlimit = None

    def get(self, time):
        if self.nextlimit is not None and time >= self.nextlimit:
            self.nextlimit = None
            for (t, v) in self.values:
                if time > t:
                    self.latestvalue = v
                else:
                    self.nextlimit = t
                    break

        return self.latestvalue

def calendarcalc():

    lastgame = {}
    
    for g in GameMeta.objects.all().order_by('id'):
        hlast = lastgame.get(g.hometeam.id)
        if hlast:
            g.homerest = (g.date - hlast).days-1

        alast = lastgame.get(g.awayteam.id)
        if alast:
            g.awayrest = (g.date - alast).days-1

        lastgame[g.hometeam.id] = g.date
        lastgame[g.awayteam.id] = g.date
        g.save()
        

def calculate(season):

    if season:
        seasonquery = Season.objects.filter(id=season)
    else:
        seasonquery = Season.objects.all()
    
    for s in seasonquery.order_by('id'):
        teamgames = {}
        teampos = {}

        gameend = parsetime('0:60:00')*60
        for g in Game.objects.filter(season=s).order_by('id'):
            homegks = []
            awaygks = []
            homegoalsl = []
            awaygoalsl = []

            if not g.playoffs:
                (p, w, gdiff,tid) = teampos.get(g.hometeam.id, (0,0,0, g.hometeam.id))
                teampos[g.hometeam.id] = (p+g.homepoints, w+(g.homepoints==3), gdiff+g.homescore-g.awayscore, tid)
                (p, w, gdiff,tid) = teampos.get(g.awayteam.id, (0,0,0, g.awayteam.id))
                teampos[g.awayteam.id] = (p+g.awaypoints, w+(g.awaypoints==3), gdiff+g.awayscore-g.homescore, tid)

            for gke in g.gkevents.all().order_by('time'):
                if gke.athome:
                    homegks.append((gke.time, gke.playerin))
                else:
                    awaygks.append((gke.time, gke.playerin))

            awaypenalties = homepenalties = 0
            for p in g.penalties.all():
                if p.athome:
                    homepenalties += p.minutes
                else:
                    awaypenalties += p.minutes

            for (team, vsteam, loc, n) in [(g.hometeam, g.awayteam, 'home',1), (g.awayteam, g.hometeam, 'away', 2)]:
                gameno = teamgames[team] = teamgames.setdefault(team, 0)+1
                gameno_loc = teamgames[loc+team.id] = teamgames.setdefault(loc+team.id, 0)+1
                print(g.id, team.name, loc, gameno, gameno_loc, end="                     \r")
                stats = Gamestats.objects.get(id=g.id)

                if team == g.hometeam:
                    Teamstats.objects.update_or_create(
                        id = g.id*10+n,
                        defaults = dict(
                            season=g.season,
                            playoffs=g.playoffs,
                            game=g,
                            team=team,
                            vsteam=vsteam,
                            gameno=gameno,
                            gameno_loc=gameno_loc,
                            athome=True,
                            otgame=(g.time > gameend),
                            wongame=g.homescore>g.awayscore,
                            score=g.homescore,
                            vsscore=g.awayscore,
                            shots=stats.homeshots,
                            vsshots=stats.awayshots,
                            saved=stats.homesaved,
                            vssaved=stats.awaysaved,
                            penalties=homepenalties,
                            vspenalties=awaypenalties,
                            ppgoals=stats.homeppgoals,
                            ppchances=stats.homeppchances,
                            pptime=stats.homepptime,
                            vsppgoals=stats.awayppgoals,
                            vsppchances=stats.awayppchances,
                            vspptime=stats.awaypptime,
                        )
                    )
                else:
                    Teamstats.objects.update_or_create(
                        id = g.id*10+n,
                        defaults = dict(
                            season=g.season,
                            playoffs=g.playoffs,
                            game=g,
                            team=team,
                            vsteam=vsteam,
                            gameno=gameno,
                            gameno_loc=gameno_loc,
                            athome=False,
                            otgame=(g.time > gameend),
                            wongame=g.homescore<g.awayscore,
                            score=g.awayscore,
                            vsscore=g.homescore,
                            shots=stats.awayshots,
                            vsshots=stats.homeshots,
                            saved=stats.awaysaved,
                            vssaved=stats.homesaved,
                            penalties=awaypenalties,
                            vspenalties=homepenalties,
                            ppgoals=stats.awayppgoals,
                            ppchances=stats.awayppchances,
                            pptime=stats.awaypptime,
                            vsppgoals=stats.homeppgoals,
                            vsppchances=stats.homeppchances,
                            vspptime=stats.homepptime,
                        )
                    )

            prevtime = parsetime('00:00')
            i = 1

            for go in g.goals.all().order_by('time'):
                if go.athome:
                    homegoalsl.append((go.time, go.teamgoals))
                else:
                    awaygoalsl.append((go.time, go.teamgoals))

                GameState.objects.update_or_create(
                    id=int(g.id)*100+i,
                    defaults = dict(
                        game = g,
                        team = go.team,
                        vsteam = go.vsteam,
                        athome = go.athome,
                        wongame = go.wongame,
                        otgame = go.otgame,
                        start = tdm2str(prevtime),
                        end = tdm2str(go.time),
                        time = tdm2str(go.time - prevtime),
                        score = "%d-%d" % (go.teamgoals-1, go.vsteamgoals),
                        goaldiff = go.goaldiff-1,
                        teamgoals = go.teamgoals-1,
                        vsteamgoals = go.vsteamgoals,
                        gameresult = go.gameresult,
                        playoffs = g.playoffs,
                    )
                )
                i+=1
                GameState.objects.update_or_create(
                    id=int(g.id)*100+i,
                    defaults = dict(
                        game = g,
                        team = go.vsteam,
                        vsteam = go.team,
                        athome = not go.athome,
                        wongame = not go.wongame,
                        otgame = go.otgame,
                        start = tdm2str(prevtime),
                        end = tdm2str(go.time),
                        time = tdm2str(go.time - prevtime),
                        score = "%d-%d" % (go.vsteamgoals, go.teamgoals-1),
                        goaldiff = 1-go.goaldiff,
                        teamgoals = go.vsteamgoals,
                        vsteamgoals = go.teamgoals-1,
                        gameresult = go.gameresultvs,
                        playoffs = g.playoffs,
                    )
                )
                i+=1
                prevtime = go.time

            if not go.otgame:
                GameState.objects.update_or_create(
                    id=int(g.id)*100+i,
                    defaults = dict(
                        game = g,
                        team = go.team,
                        vsteam = go.vsteam,
                        athome = go.athome,
                        wongame = go.wongame,
                        otgame = go.otgame,
                        start = tdm2str(go.time),
                        end = tdm2str(gameend),
                        time = tdm2str(gameend-go.time),
                        score = "%d-%d" % (go.teamgoals, go.vsteamgoals),
                        goaldiff = go.goaldiff,
                        teamgoals = go.teamgoals,
                        vsteamgoals = go.vsteamgoals,
                        gameresult = go.gameresult,
                        playoffs = g.playoffs,
                    )
                )
                i+=1
                GameState.objects.update_or_create(
                    id=int(g.id)*100+i,
                    defaults = dict(
                        game = g,
                        team = go.vsteam,
                        vsteam = go.team,
                        athome = not go.athome,
                        wongame = not go.wongame,
                        otgame = go.otgame,
                        start = tdm2str(go.time),
                        end = tdm2str(gameend),
                        time = tdm2str(gameend-go.time),
                        score = "%d-%d" % (go.vsteamgoals, go.teamgoals),
                        goaldiff = -go.goaldiff,
                        teamgoals = go.vsteamgoals,
                        vsteamgoals = go.teamgoals,
                        gameresult = go.gameresultvs,
                        playoffs = g.playoffs,
                    )
                )


            homeshots = 0
            awayshots = 0
            homegk = StatePerTime(homegks, None)
            awaygk = StatePerTime(awaygks, None)
            homegoals = StatePerTime(homegoalsl, 0)
            awaygoals = StatePerTime(awaygoalsl, 0)

            for s in g.shots.order_by('time'):
                if s.athome:
                    homeshots += 1
                    s.teamshots = homeshots
                    s.vsteamshots = awayshots
                    s.keeper = awaygk.get(s.time)
                    s.teamgoals = homegoals.get(s.time)
                    s.vsteamgoals = awaygoals.get(s.time)
                    s.teamscore = "%d-%d" % (s.teamgoals, s.vsteamgoals)
                    s.vsteamscore = "%d-%d" % (s.vsteamgoals, s.teamgoals)
                else:
                    awayshots += 1
                    s.teamshots = awayshots
                    s.vsteamshots = homeshots
                    s.keeper = homegk.get(s.time)
                    s.teamgoals = awaygoals.get(s.time)
                    s.vsteamgoals = homegoals.get(s.time)
                    s.teamscore = "%d-%d" % (s.teamgoals, s.vsteamgoals)
                    s.vsteamscore = "%d-%d" % (s.vsteamgoals, s.teamgoals)
                s.time = tdm2str(s.time)

                s.save()

            homegk = StatePerTime(homegks, None)
            awaygk = StatePerTime(awaygks, None)
            for ps in g.penaltyshots.order_by('time'):
                if not ps.keeper:
                    if ps.athome:
                        ps.keeper = awaygk.get(ps.time)
                    else:
                        ps.keeper = homegk.get(ps.time)
                ps.time = tdm2str(ps.time)
                ps.latestpenalty = tdm2str(ps.latestpenalty)
                ps.latestpenaltyvs = tdm2str(ps.latestpenaltyvs)
                ps.latestgoal = tdm2str(ps.latestgoal)
                ps.latestgoalvs = tdm2str(ps.latestgoalvs)
                ps.save()

        poslist = list(teampos.values())
        poslist.sort()
        poslist.reverse()
        i = 1
        for (p,w,gdiff,teamid) in poslist:

            t = Team.objects.get(id=teamid)
            t.ranking = i
            t.points = p
            t.save()
            i+=1



from django.db.models import Sum 

class Calculator(object):

    @classmethod
    def teamdata(cls):
        hp = Team.objects.annotate(home_points=Sum('homegames__homepoints'))
        values = dict()
        for p in hp:
            values[p.id] = p.home_points
        ap = Team.objects.annotate(away_points=Sum('awaygames__awaypoints'))
        ordered = []
        for p in ap:
            values[p.id] += p.away_points
            ordered.append((values[p.id], p.id))
        ordered.sort()
        ranking = 0
        for (p, tid) in ordered[::-1]:
            t = Team.objects.get(id=tid)
            print(t.name, p)
            ranking += 1
            t.ranking = ranking
            t.points = p
            t.save()

    @classmethod
    def calendar(cls):
        games = {}
        abbgames = {}
        bbgames = {}
        bbogames = {}
        bbmgames = {}
        bbagames = {}
        for g in  GameMeta.objects.all():
            hg = games.setdefault(g.hometeam.id, [])
            ag = games.setdefault(g.awayteam.id, [])
            adays = hdays = datetime.timedelta(days=100)
            if hg:
                hdays = g.date - hg[-1].date
            if ag:
                adays = g.date - ag[-1].date

            if hdays.days <= 1 and adays.days <= 1:
                abbgames.setdefault(g.hometeam.id, []).append(hg[-1])
                abbgames.setdefault(g.awayteam.id, []).append(ag[-1])
                abbgames.setdefault(g.hometeam.id, []).append(g)
                abbgames.setdefault(g.awayteam.id, []).append(g)
                bbgames.setdefault(g.hometeam.id, []).append(g)
                bbgames.setdefault(g.awayteam.id, []).append(g)
            elif hdays.days <= 1:
                abbgames.setdefault(g.hometeam.id, []).append(hg[-1])
                abbgames.setdefault(g.hometeam.id, []).append(g)
                bbmgames.setdefault(g.hometeam.id, []).append(g)
                bbogames.setdefault(g.awayteam.id, []).append(g)
            elif adays.days <= 1:
                abbgames.setdefault(g.awayteam.id, []).append(ag[-1])
                abbgames.setdefault(g.awayteam.id, []).append(g)
                bbmgames.setdefault(g.awayteam.id, []).append(g)
                bbogames.setdefault(g.hometeam.id, []).append(g)

            if adays.days <= 1 and ag[-1].awayteam.id == g.awayteam.id:
                bbagames.setdefault(g.awayteam.id, []).append(ag[-1])
                bbagames.setdefault(g.awayteam.id, []).append(g)
            g.hdays = hdays.days
            g.adays = adays.days
            ag.append(g)
            hg.append(g)

        for t in bbgames.keys():
            te = Team.objects.get(id=t)
            print(te.name, len(bbmgames.get(t, [])), len(bbgames[t]), len(bbogames.get(t, [])), len(bbagames.get(t, [])))
            for g in abbgames.get(t, []):
                print(g.date, g.starttime, g.hometeam.name, g.awayteam.name, g.hdays, g.adays)
            print()
            if 0:
                for g in bbmgames.get(t, []):
                    print(g)
                print()
                for g in bbgames[t]:
                    print(g)
                print()
                for g in bbogames.get(t, []):
                    print(g)
                print()
                print()
                


def loadgametimes(path):
    with open(path) as fp:
        for l in fp:
            (gameid, starttime, endtime) = l.split()
            print(gameid, starttime, endtime, "2018%03d" % int(gameid))
            
            game = Game.objects.get(id="2018%03d" % int(gameid))
            game.starttime = starttime
            game.endtime = endtime
            game.save()
