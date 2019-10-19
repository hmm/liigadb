
from operator import attrgetter

from liigadb.gamedata.models import *
from liigadb.gamedata.dataloader import parsetime


def durfmt(d):
    minutes = d.seconds/60
    seconds = d.seconds%60
    return "%d:%02d" % (minutes, seconds)


def runreport(report, **kwargs):

    if report == "teamlongest":
        report_teamlongest(**kwargs)
    if report == "keepers":
        report_keepers(**kwargs)


def report_teamlongest(**kwargs):
    homeaway = kwargs.get('homeaway')
    
    for t in Team.objects.all():
        #print t

        prev = parsetime('00:00')
        prevvs = parsetime('00:00')
        mt = (prev, None)
        mtvs = (prevvs, None)

        for s in Season.objects.all().order_by('id'):

            prev = parsetime('00:00')
            prevvs = parsetime('00:00')

            if homeaway == 'both':
                gamequery = (t.homegames.filter(season=s) | t.awaygames.filter(season=s))
            elif homeaway == 'home':
                gamequery = (t.homegames.filter(season=s))
            elif homeaway == 'away':
                gamequery = (t.awaygames.filter(season=s))

            for g in gamequery.order_by('date'):
                for go in g.goals.all().order_by('time'):
                    if 'VL' in go.goalattr:
                        pass
                    elif go.team == t:
                        #print go.team, tdm2str(go.time), go.teamscore, (go.time - prev)/60, prev
                        if (go.time - prev)/60 > mt[0]:
                            mt = (go.time - prev)/60, g, go
                        prev = go.time
                    else:
                        #print go.team, tdm2str(go.time), go.teamscore, (go.time - prevvs)/60, prevvs
                        if (go.time - prevvs)/60 > mtvs[0]:
                            mtvs = (go.time - prevvs)/60, g, go
                        prevvs = go.time
                prev = prev - g.time
                prevvs = prevvs - g.time
                if (parsetime('00:00')-prev)/60 > mt[0]:
                    mt = (parsetime('00:00')-prev)/60, g, None
                if (parsetime('00:00')-prevvs)/60 > mtvs[0]:
                    mtvs = (parsetime('00:00')-prevvs)/60, g, None


        if mt[1]:
            if mt[2]:
                enddate = mt[1].date
            else:
                enddate = ''
            if mtvs[2]:
                vsenddate = mtvs[1].date
            else:
                vsenddate = ''

            print("%-10s | %10s | %10s | | %-10s | %10s | %10s" % (t.name, enddate, durfmt(mt[0]), t.name, vsenddate, durfmt(mtvs[0])))
            
class CK:
    def __init__(self, keeper, starttime, game):
        self.keeper = keeper
        self.time = parsetime('00:00')
        self.times = []
        self.starttime = starttime
        self.startgame = game

    def addtime(self, starttime, endtime, game, reason):
        self.times.append((game, starttime, endtime, reason))
        self.time += endtime-starttime
        self.endgame = game
        self.endtime = endtime

    def showtimes(self):
        for (g, s, e, r) in self.times:
            print(g, durfmt(s/60), durfmt(e/60), durfmt((e-s)/60), r)

    def __str__(self):
        return "%s: %s: (%s - %s)" % (self.keeper, durfmt(self.time/60), self.startgame.date, self.endgame.date)

def report_keepers(**kwargs):
    limit = kwargs.get('limit')
    homeaway = kwargs.get('homeaway')
    times = []
    for team in Team.objects.all():
        for s in Season.objects.all().order_by('id'):
            keepers = {}

            if homeaway == 'both':
                gamequery = (team.homegames.filter(season=s) | team.awaygames.filter(season=s))
            elif homeaway == 'home':
                gamequery = (team.homegames.filter(season=s))
            elif homeaway == 'away':
                gamequery = (team.awaygames.filter(season=s))

            for g in gamequery.order_by('date'):
                events = []
                for gke in g.gkevents.filter(team=team).order_by('time'):
                    if gke.playerin:
                        gkinid = gke.playerin.id
                    else:
                        gkinid = None
                    events.append((gke.time, 'keeper', gke.event, gkinid))

                for go in g.goals.all().order_by('time'):
                    if 'VL' in go.goalattr:
                        pass
                    elif go.team != team:
                        events.append((go.time, 'goal', None, None))

                events.sort()
                events.append((g.time, 'end', None, None))
                ck = None
                for (t, e, gke, v) in events:
                    if v:
                        if ck:
                            ck.time += t-last
                        vv = TeamPlayer.objects.get(id=v)
                        ck = keepers.get(vv)
                        if not ck:
                            ck = CK(vv, t, g)
                            keepers[vv] = ck
                    else:
                        if e == 'goal':
                            if ck:
                                ck.addtime(last, t, g, 'goal')
                                if ck.time > parsetime('60:00')*60:
                                    times.append(ck)
                                if t > parsetime('60:00')*60:
                                    keepers[ck.keeper] = None
                                    ck = None
                                else:
                                    ck = keepers[ck.keeper] = CK(ck.keeper, t, g)
                        elif e == 'end':
                            if ck:
                                ck.addtime(last, t, g, 'end')
                        elif gke == 'out':
                            ck.addtime(last, t, g, 'out')
                            ck = None
                    last = t

            for t in keepers.values():
                #print t.time, parsetime('60:00'), parsetime('60:00')*60
                if t and t.time > parsetime('60:00')*60:
                    times.append(t)


    st = sorted(times, key=attrgetter('time'), reverse=True)
    for t in st[:limit]:
        print("%-30s| %-10s | %-10s | %s | %s" % (t.keeper.player.name, t.keeper.team.name, durfmt(t.time/60), t.startgame.date, t.endgame.date))
        #print "%s|%s|%s|%s|%s" % (t.keeper.player.name, t.keeper.team.name, durfmt(t.time/60), t.startgame.date, t.endgame.date) 
        #t.showtimes()
        #print
    if 0:
        print()
        print(st[3])
        st[3].showtimes()


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


