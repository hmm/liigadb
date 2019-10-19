import json, sys, datetime, functools

from django.utils.text import slugify
from django.utils.dateparse import parse_duration
from liigadb.seasondata.models import *
from liigadb.gamedata.dataloader import DataLoader


class SeasonData(DataLoader):

    @classmethod
    def load_season(cls, data):
        Season.objects.update_or_create(
            id = data.id,
            defaults = dict(
                years = data.years
            )
        )
        cls.seasonstats = {}

    @classmethod
    def load_team(cls, data):
        Team.objects.update_or_create(
            id = data.id,
            defaults = dict(
                name = data.name
            )
        )

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

        otgame = False
        if hasattr(data, 'resultattr'):
            starttime = data.time
            if data.resultattr:
                result = "%s %s" % (data.score, data.resultattr)
                otgame = True
            else:
                result = data.score
            resultattr = data.resultattr
        else:
            starttime = '00:00'
            if data.time == '60:00':
                result = data.score
                resultattr = ''
            else:
                result = "%s JA" % (data.score)
                resultattr = 'JA'
                otgame = True


        (game, _) = Game.objects.update_or_create(
            id = data.id,
            defaults = dict(
                season = season,
                playoffs = data.playoffs,
                identifier = data.identifier,
                number = data.number,
                date = data.date,
                hometeam = hometeam,
                awayteam = awayteam,
                starttime = starttime,
                homescore = data.home.score,
                awayscore = data.away.score,
                homepoints = homepoints,
                awaypoints = awaypoints,
                result = result,
                resultattr = resultattr,
                otgame = otgame
            )
        )
        if not game.playoffs:
            cls.updatestats(hometeam, game)
            cls.updatestats(awayteam, game)

        print("%s\r" % data.id, end='')
        sys.stdout.flush()



    @classmethod
    def updatestats(cls, team, game):
        athome = team == game.hometeam

        stats = cls.seasonstats.setdefault(team.id,
            TeamSeason(
                team = team,
                season = game.season,
                games = 0,
                points = 0,
                wins = 0,
                losses = 0,
                ties = 0,
                otwins = 0,
                goals = 0,
                goalsagainst = 0,
                goaldiff = 0,
                homepoints = 0,
                homegames = 0,
                homewins = 0,
                homelosses = 0,
                hometies = 0,
                homeotwins = 0,
                homegoals = 0,
                homegoalsagainst = 0,
                playoffs = False,
                )
        )
        stats.games += 1
        if athome:
            stats.homegames += 1
            stats.points += game.homepoints
            stats.goals += game.homescore
            stats.goalsagainst += game.awayscore
            stats.homepoints += game.homepoints
            stats.goaldiff = stats.goals - stats.goalsagainst
            stats.homegoals += game.homescore
            stats.homegoalsagainst += game.awayscore
            if game.resultattr in ['JA', 'VL'] or game.homescore == game.awayscore:
                stats.ties += 1
                stats.hometies += 1
                if game.homescore > game.awayscore:
                    stats.otwins += 1
                    stats.homeotwins += 1
            elif game.homepoints == 0:
                stats.losses += 1
                stats.homelosses += 1
            elif game.awaypoints == 0:
                stats.wins += 1
                stats.homewins += 1
        else:
            stats.points += game.awaypoints
            stats.goals += game.awayscore
            stats.goalsagainst += game.homescore
            stats.goaldiff = stats.goals - stats.goalsagainst
            if game.resultattr in ['JA', 'VL'] or game.homescore == game.awayscore:
                stats.ties += 1
                if game.awayscore > game.homescore:
                    stats.otwins += 1
            elif game.awaypoints == 0:
                stats.losses += 1
            elif game.homepoints == 0:
                stats.wins += 1

    @classmethod
    def load_teamstat(cls, data):
        stats = cls.seasonstats[data.team]
        id = data.season + data.team
        (st, _) = TeamSeason.objects.update_or_create(
            id = id,
            defaults = dict(
                team = stats.team,
                season = stats.season,
                games = stats.games,
                points = stats.points,
                wins = stats.wins,
                losses = stats.losses,
                ties = stats.ties,
                otwins = stats.otwins,
                goals = stats.goals,
                goalsagainst = stats.goalsagainst,
                goaldiff = stats.goaldiff,
                homepoints = stats.homepoints,
                homegames = stats.homegames,
                homewins = stats.homewins,
                homelosses = stats.homelosses,
                hometies = stats.hometies,
                homeotwins = stats.homeotwins,
                homegoals = stats.homegoals,
                homegoalsagainst = stats.homegoalsagainst,
                attendance = data.attendance,
                minutes = data.minutes,
                ppgoals = data.ppgoals,
            )
        )



def loadseasons(path):
    SeasonData.loaddata(path)
    
class PlayoffData(SeasonData):

    @classmethod
    def load_player(cls, data):
        pass

    @classmethod
    def load_goalkeeper(cls, data):
        pass

    @classmethod
    def load_gameevent(cls, data):
        pass

    @classmethod
    def load_period(cls, data):
        pass

    @classmethod
    def load_gamestats(cls, data):
        pass


def loadplayoffs(path):
    PlayoffData.loaddata(path)

class PlayersData(DataLoader):

    @classmethod
    def load_playerstats(cls, data):
        player = Player.objects.get(id=data.playerid)
        team = Team.objects.get(id=data.team)
        season = Season.objects.get(years=data.season)
        if data.playoffs:
            id = str(season.id) + data.team + data.playerid + 'playoffs'
        else:
            id = str(season.id) + data.team + data.playerid
        (stat, _) = PlayerStats.objects.update_or_create(
            id = id,
            player = player,
            team = team,
            season = season,
            playoffs = data.playoffs,
            defaults = dict(
                position = data.position,
                games = data.games,
                goals = data.goals,
                assists = data.assists,
                points = data.points,
                penalties = data.penalties,
                plus = data.plus,
                minus = data.minus,
                plusminus = data.plusminus,
                ppgoals = data.ppgoals,
                shgoals = data.shgoals,
                wingoals = data.wingoals,
                shots = data.shots,
                shotpct = data.shotpct,
                #faceoffs = data.faceoffs,
                #faceoffpct = data.faceoffpct,
                #playtime = data.playtime,
            )
        )

    @classmethod
    def load_playermeta(cls, data):
        (lastname, firstname) = [s.strip() for s in data.name.split(',')]
        (player, _) = Player.objects.update_or_create(
            id = data.playerid,
            defaults = dict(
                name = data.name,
                lastname = lastname,
                firstname = firstname,
                homecity = data.homecity,
                nationality = data.nationality,
                position = data.position,
                stick = data.stick,
                born = data.born,
                number = data.number,
                weight = data.weight,
                height = data.height
            )
        )
               
    @classmethod
    def load_otherseries(cls, data):
        pass

def loadplayers(path):
    PlayersData.loaddata(path)
                
def calcplayers():
    pass



class TSData(object):
    def __init__(self, team, vsteam, season, level, won):
        self.team = team
        self.vsteam = vsteam
        self.season = season
        self.level = level
        self.won = won
        self.wins = 0
        self.otwins = 0
        self.homewins = 0
        self.games = 0
        self.otgames = 0
        self.homegames = 0
    

@functools.total_ordering
class TeamSeriesStats(object):
    def __init__(self, team, season):
        self.team = team
        self.season = season
        self.points = 0
        self.games = 0
        self.wins = 0
        self.goals = 0
        self.vsgoals = 0
        self.position = None

    def update(self, won, points, goals, vsgoals):
        self.games += 1
        if won:
            self.wins += 1
        self.points += points
        self.goals += goals
        self.vsgoals += vsgoals

    def __cmp__(self, other):
        if self.points != other.points:
            return other.points - self.points

        if self.wins != other.wins:
            return other.wins - self.wins

        if self.goals-self.vsgoals != other.goals-other.vsgoals:
            return (other.goals-other.vsgoals) - (self.goals-self.vsgoals)
        
        return other.goals - self.goals

    def __lt__(self, other):
        return self.__cmp__(other) < 0
    
    def __eq__(self, other):
        return self.__cmp__(other) == 0

    @classmethod
    def calculate(cls, teams):
        tl = list(teams)
        tl.sort()
        pos = 1
        for t in tl:
            t.position = pos
            pos += 1

def calculate():
    teamseries = {}


    for s in Season.objects.all().order_by('id'):
        rank = 1
        prevts = None
        if s.id < 2013:
            search = TeamSeason.objects.filter(season=s).order_by('-points', '-goaldiff', '-wins')
            nowins = True
        else:
            search = TeamSeason.objects.filter(season=s).order_by('-points', '-wins', '-goaldiff', '-goals')
            nowins = False
            
        for ts in search:
            ts.seriesranking = rank
            rank+=1
            ts.save()
            if prevts and ts.points == prevts.points and (ts.wins == prevts.wins or nowins) and (
                    (ts.goals-ts.goalsagainst) > (prevts.goals-prevts.goalsagainst)):
                    (prevts.seriesranking, ts.seriesranking) = (ts.seriesranking, prevts.seriesranking) 
                    prevts.save()
                    ts.save()
            elif s.id == 1987 and prevts and ts.points == prevts.points and (
                    (ts.goals-ts.goalsagainst) < (prevts.goals-prevts.goalsagainst)):
                    (prevts.seriesranking, ts.seriesranking) = (ts.seriesranking, prevts.seriesranking) 
                    prevts.save()
                    ts.save()
            prevts = ts
        

    for s in Season.objects.all().order_by('id'):
        
        levels = [5, 5, 4, 4, 4, 4, 3, 3, 2, 1]
        
        for g in Game.objects.filter(playoffs=True, season=s).order_by('-id'):
            hk = (g.hometeam.id, g.awayteam.id, g.season.id)
            ak = (g.awayteam.id, g.hometeam.id, g.season.id)

            for pteam in [g.hometeam, g.awayteam]:
                pts = TeamSeason.objects.get(season=s, team=g.hometeam)
                if not pts.playoffs:
                    pts.playoffs = True
                    pts.save()
            
            if hk not in teamseries:
                level = levels.pop()
                teamseries[hk] = TSData(g.hometeam, g.awayteam, s, level, g.homescore>g.awayscore)
                teamseries[ak] = TSData(g.awayteam, g.hometeam, s, level, g.homescore<g.awayscore)
                
            teamseries[hk].games += 1
            teamseries[ak].games += 1
            if g.resultattr == "JA":
                teamseries[hk].otgames += 1
                teamseries[ak].otgames += 1
                    
            if g.homescore>g.awayscore:
                teamseries[hk].wins += 1
                teamseries[hk].homewins += 1
                if g.resultattr == "JA":
                    teamseries[hk].otwins += 1
                        
            else:
                teamseries[ak].wins += 1
                if g.resultattr == "JA":
                    teamseries[ak].otwins += 1

    k = list(teamseries.keys())
    k.sort()
    for tsk in k:
        ts = teamseries[tsk]
        #print tsk, ts.level, ts.won, ts.games
        tss = TeamSeason.objects.get(season=ts.season, team=ts.team)
        vstss = TeamSeason.objects.get(season=ts.season, team=ts.vsteam)
        if ts.won:
            serieslength = ts.wins*2-1
        else:
            serieslength = (ts.games-ts.wins)*2-1
            

        PlayoffsSeries.objects.update_or_create(
            id = "%s-%s-%s" % (ts.season.id, ts.team.id, ts.vsteam.id),
            defaults = dict(
                season = ts.season,
                team = ts.team,
                vsteam = ts.vsteam,
                teamrank = tss.seriesranking,
                vsteamrank = vstss.seriesranking,

                level = ts.level,
                won = ts.won,

                games = ts.games,
                wins = ts.wins,
                serieslength = serieslength,
                seriesresult = "%d-%d" % (ts.wins, ts.games-ts.wins),

                homewins = ts.homewins,

                otgames = ts.otgames,
                otwins = ts.otwins,
            )
                
        )
    
    for s in Season.objects.all().order_by('id'):
        rank = 1
        for ps in PlayoffsSeries.objects.filter(season=s, level__lt=3).order_by('level', '-won'):
            #print ps
            ts = TeamSeason.objects.get(season=s, team=ps.team)
            ts.finalranking = rank
            ts.save()
            rank+=1

        teams4 = []
        teams5 = []
        for ps in PlayoffsSeries.objects.filter(season=s, level__gt=3, won=False):
            if ps.level == 4:
                teams4.append(ps.team.id)
            elif ps.level == 5:
                teams5.append(ps.team.id)

        rank4 = 5
        rank5 = 9
                
        for ts in TeamSeason.objects.filter(season=s).order_by('seriesranking'):
            if ts.team.id in teams4:
                ts.finalranking=rank4
                ts.save()
                rank4+=1
            elif ts.team.id in teams5:
                ts.finalranking=rank5
                ts.save()
                rank5+=1
            elif not ts.finalranking or ts.finalranking > 4:
                ts.finalranking = ts.seriesranking
                ts.save()

        for ps in PlayoffsSeries.objects.filter(season=s):
            gameno = 1

            f1 = Game.objects.filter(playoffs=True, season=s, hometeam=ps.team, awayteam=ps.vsteam)
            f2 = Game.objects.filter(playoffs=True, season=s, awayteam=ps.team, hometeam=ps.vsteam)

            seriesresults = []

            for g in (f1 | f2).order_by('date'):
                if g.hometeam == ps.team:
                    won = g.homescore > g.awayscore
                    athome = True
                    teamscore = g.homescore
                    vsteamscore = g.awayscore
                else:
                    won = g.homescore < g.awayscore
                    athome = False
                    teamscore = g.awayscore
                    vsteamscore = g.homescore
                    
                if g.resultattr != '':
                    otgame = True
                    teamresult = "%d-%d %s" % (teamscore, vsteamscore, g.resultattr)
                else:
                    otgame = False
                    teamresult = "%d-%d" % (teamscore, vsteamscore)

                if won:
                    if otgame:
                        seriesresults.append('w')
                    else:
                        seriesresults.append('W')
                else:
                    if otgame:
                        seriesresults.append('l')
                    else:
                        seriesresults.append('L')
                    
                PlayoffsGame.objects.update_or_create(
                    id = "%s-%s-%s-%d" % (ts.season.id, ps.team.id, ps.vsteam.id, gameno),
                    defaults = dict(
                        season = s,
                        series = ps,
                        game = g,
                        
                        team = ps.team,
                        vsteam = ps.vsteam,
                        
                        teamrank = ps.teamrank,
                        vsteamrank = ps.vsteamrank,
                        
                        level = ps.level,
                        won = won,
                        athome = athome,
                        otgame = otgame,
                        gameno = gameno,
                        
                        teamscore = teamscore,
                        vsteamscore = vsteamscore,
                        teamresult = teamresult,

                        wins = 0,
                        losses= 0,
                        seriesscore = '',
                        
                        wonseries = ps.won,
                        seriesgames = ps.games,
                        serieswins = ps.wins,
                        seriesresult = "%d-%d" % (ps.wins, ps.games-ps.wins)
                    )
                )
                gameno += 1

            ps.results = ''.join(seriesresults)
            ps.save()

        lastteams = None
        for pg in PlayoffsGame.objects.filter(season=s).order_by('id'):
            if lastteams != (pg.team_id, pg.vsteam_id):
                wins = losses = 0
                lastteams = (pg.team.id, pg.vsteam.id)
                    
            if pg.won:
                wins += 1
            else:
                losses += 1
            pg.wins = wins
            pg.losses = losses
            pg.seriesscore = "%d-%d" % (wins, losses)
            pg.save()
                
                
        teamgames = {}
        lastgame = {}
        seriesteams = {}
        prevdate = None
        
        for g in Game.objects.filter(season=s).order_by('id'):
            id = g.id*10+1
            gameno = teamgames[g.hometeam.id] = teamgames.setdefault(g.hometeam.id, 0) + 1
            hlast = lastgame.get(g.hometeam.id)
            if hlast:
                homerest = (g.date - hlast).days-1
            else:
                homerest = None
                
            alast = lastgame.get(g.awayteam.id)
            if alast:
                awayrest = (g.date - alast).days-1
            else:
                awayrest = None

            lastgame[g.hometeam.id] = g.date
            lastgame[g.awayteam.id] = g.date

            if g.date != prevdate:
                TeamSeriesStats.calculate(seriesteams.values())
                prevdate = g.date

            hts = seriesteams.get(g.hometeam.id)
            if not hts:
                hts = seriesteams[g.hometeam.id] = TeamSeriesStats(g.hometeam, s)

            ats = seriesteams.get(g.awayteam.id)
            if not ats:
                ats = seriesteams[g.awayteam.id] = TeamSeriesStats(g.awayteam, s)

            
            homepoints3 = awaypoints3 = None
            if not g.playoffs:
                if g.resultattr == '':
                    if g.homescore > g.awayscore:
                        homepoints3 = 3
                        awaypoints3 = 0
                    else:
                        homepoints3 = 0
                        awaypoints3 = 3
                else:
                    if g.homescore > g.awayscore:
                        homepoints3 = 2
                        awaypoints3 = 1
                    elif g.homescore < g.awayscore:
                        homepoints3 = 1
                        awaypoints3 = 2
                    else:
                        homepoints3 = 1
                        awaypoints3 = 1

            
            (tg, created) = TeamGame.objects.update_or_create(
                id = id,
                defaults = dict(
                    season = s,
                    game = g,
                    playoffs = g.playoffs,
                    date = g.date,
                    team = g.hometeam,
                    vsteam = g.awayteam,
                    athome = True,
                    gameno = gameno,
                    teamscore = g.homescore,
                    vsteamscore = g.awayscore,
                    otgame = g.resultattr != '',
                    resultattr = g.resultattr,
                    won = g.homescore > g.awayscore,
                    tied = g.homescore == g.awayscore or g.resultattr != '',
                    points = g.homepoints,
                    points3 = homepoints3,
                    rest = homerest,
                    vsrest = awayrest,
                    seriespoints = hts.points,
                    teamrank = hts.position,
                    vsteamrank = ats.position,
                )
            )
            id = g.id*10+2
            gameno = teamgames[g.awayteam.id]= teamgames.setdefault(g.awayteam.id, 0) + 1
            (tg, created) = TeamGame.objects.update_or_create(
                id = id,
                defaults = dict(
                    season = s,
                    game = g,
                    playoffs = g.playoffs,
                    date = g.date,
                    team = g.awayteam,
                    vsteam = g.hometeam,
                    athome = False,
                    gameno = gameno,
                    teamscore = g.awayscore,
                    vsteamscore = g.homescore,
                    otgame = g.resultattr != '',
                    resultattr = g.resultattr,
                    won = g.homescore < g.awayscore,
                    tied = g.homescore == g.awayscore or g.resultattr != '',
                    points = g.awaypoints,
                    points3 = awaypoints3,
                    rest = awayrest,
                    vsrest = homerest,
                    seriespoints = ats.points,
                    teamrank = ats.position,
                    vsteamrank = hts.position,
                )
            )
            if not g.playoffs:
                hts.update(g.resultattr == '' and g.homescore > g.awayscore,
                           g.homepoints,
                           g.homescore,
                           g.awayscore)
                ats.update(g.resultattr == '' and g.homescore < g.awayscore,
                           g.awaypoints,
                           g.awayscore,
                           g.homescore)
