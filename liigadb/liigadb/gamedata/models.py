from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Season(models.Model):
    years = models.CharField(max_length=20)

    def __unicode__(self):
        return u"Season: %s" % self.years

class Team(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20)
    ranking = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    
    def __unicode__(self):
        return u"Team: %s" % self.id


class GameMeta(models.Model):
    number = models.IntegerField()
    identifier = models.IntegerField()
    datetime = models.DateTimeField()
    date = models.DateField()
    starttime = models.DurationField()
    endtime = models.DurationField(null=True)

    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    
    hometeam = models.ForeignKey(Team, related_name='homegameshedule', on_delete=models.CASCADE)
    awayteam = models.ForeignKey(Team, related_name='awaygameshedule', on_delete=models.CASCADE)

    homerest = models.IntegerField(null=True)
    awayrest = models.IntegerField(null=True)
    
    def __unicode__(self):
        return u"Game: %s (%s - %s) %s - %s" % (self.id, self.hometeam.id, self.awayteam.id, self.date, self.starttime)


class Game(models.Model):
    number = models.IntegerField()
    identifier = models.IntegerField()
    date = models.DateField()
    starttime = models.DurationField(null=True)
    endtime = models.DurationField(null=True)

    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    
    hometeam = models.ForeignKey(Team, related_name='homegames', on_delete=models.CASCADE)
    awayteam = models.ForeignKey(Team, related_name='awaygames', on_delete=models.CASCADE)

    time = models.DurationField()

    periodscores = models.CharField(max_length=60) 
    result = models.CharField(max_length=10) 

    homescore = models.IntegerField()
    awayscore = models.IntegerField()
    homepoints = models.IntegerField(null=True)
    awaypoints = models.IntegerField(null=True)

    attendance = models.IntegerField(null=True)

    def __unicode__(self):
        return u"Game: %s (%s - %s)" % (self.id, self.hometeam.id, self.awayteam.id)


class Period(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    period = models.CharField(max_length=5)
    
    game = models.ForeignKey(Game, related_name='periods', on_delete=models.CASCADE)
    hometeam = models.ForeignKey(Team, related_name='homeperiods', on_delete=models.CASCADE)
    awayteam = models.ForeignKey(Team, related_name='awayperiods', on_delete=models.CASCADE)
    homescore = models.IntegerField()
    awayscore = models.IntegerField()
    gamehomescore = models.IntegerField()
    gameawayscore = models.IntegerField()
    homeshots = models.IntegerField()
    awayshots = models.IntegerField()
    homefaceoffs = models.IntegerField(null=True)
    awayfaceoffs = models.IntegerField(null=True)
    homeblocked = models.IntegerField(null=True)
    awayblocked = models.IntegerField(null=True)
    homemissed = models.IntegerField()
    awaymissed = models.IntegerField()
    homesaved = models.IntegerField()
    awaysaved = models.IntegerField()


class Gamestats(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    game = models.ForeignKey(Game, related_name='stats', on_delete=models.CASCADE)
    hometeam = models.ForeignKey(Team, related_name='homestats', on_delete=models.CASCADE)
    awayteam = models.ForeignKey(Team, related_name='awaystats', on_delete=models.CASCADE)

    homescore = models.IntegerField()
    awayscore = models.IntegerField()
    homeshots = models.IntegerField()
    awayshots = models.IntegerField()
    homefaceoffs = models.IntegerField(null=True)
    awayfaceoffs = models.IntegerField(null=True)
    homeblocked = models.IntegerField(null=True)
    awayblocked = models.IntegerField(null=True)
    homemissed = models.IntegerField()
    awaymissed = models.IntegerField()
    homesaved = models.IntegerField()
    awaysaved = models.IntegerField()

    homeppgoals = models.IntegerField()
    awayppgoals = models.IntegerField()
    homeppchances = models.IntegerField()
    awayppchances = models.IntegerField()
    homepppct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    awaypppct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    homepptime = models.DurationField()
    awaypptime = models.DurationField()
    

class Teamstats(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    game = models.ForeignKey(Game, related_name='teamstats', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='teamstats', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsteamstats', on_delete=models.CASCADE)
    gameno = models.IntegerField()
    gameno_loc = models.IntegerField()
    athome = models.BooleanField()
    wongame = models.BooleanField()
    otgame = models.BooleanField()
    
    score = models.IntegerField()
    vsscore = models.IntegerField()
    shots = models.IntegerField()
    vsshots = models.IntegerField()
    saved = models.IntegerField()
    vssaved = models.IntegerField()
    penalties = models.IntegerField()
    vspenalties = models.IntegerField()
    
    ppgoals = models.IntegerField()
    ppchances = models.IntegerField()
    pptime = models.DurationField()
    vsppgoals = models.IntegerField()
    vsppchances = models.IntegerField()
    vspptime = models.DurationField()    


class Player(models.Model):
    id = models.CharField(max_length=40, primary_key=True) 
    name = models.CharField(max_length=40) 


class TeamPlayer(models.Model):
    id = models.CharField(max_length=60, primary_key=True) 
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='teams', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    number = models.IntegerField(null=True)
    
    def __unicode__(self):
        return u"%s (%s:#%d)" % (self.player.name, self.team.name, self.number)

class PlayerGameStats(models.Model):
    id = models.CharField(max_length=60, primary_key=True) 
    game = models.ForeignKey(Game, related_name='players', on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    player = models.ForeignKey(TeamPlayer, related_name='games', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='playerstats', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsplayerstats', on_delete=models.CASCADE)
    position = models.CharField(max_length=10, null=True)
    goals = models.IntegerField()
    assists = models.IntegerField()
    points = models.IntegerField()
    penalties = models.IntegerField()
    plus = models.IntegerField()
    minus = models.IntegerField()
    plusminus = models.IntegerField()
    ppgoals = models.IntegerField(null=True)
    shgoals = models.IntegerField(null=True)
    wingoal = models.IntegerField(null=True)
    shots = models.IntegerField(null=True)
    shotpct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    faceoffs = models.IntegerField(null=True)
    faceoffpct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    playtime = models.DurationField(null=True)
    athome = models.BooleanField()
    lineno = models.IntegerField(null=True)
    gh = models.NullBooleanField()
    skating = models.IntegerField(null=True)

    skatingrecord = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    shootingrecord = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    

class GoalkeeperStats(models.Model):
    id = models.CharField(max_length=60, primary_key=True) 
    game = models.ForeignKey(Game, related_name='goalkeepers', on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    player = models.ForeignKey(TeamPlayer, related_name='gkgames', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='gkstats', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsgkstats', on_delete=models.CASCADE)
    goals = models.IntegerField()
    goalsagainst = models.IntegerField()
    assists = models.IntegerField()
    points = models.IntegerField()
    penalties = models.IntegerField()
    saves = models.IntegerField()
    savepct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    playtime = models.DurationField()
    athome = models.BooleanField()
    started = models.BooleanField()

class Referee(models.Model):
    name = models.CharField(max_length=40)
    number = models.IntegerField()

class RefereeGame(models.Model):
    game = models.ForeignKey(Game, related_name='referees', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    referee = models.ForeignKey(Referee, related_name='games', on_delete=models.CASCADE)
    reftype = models.CharField(max_length=20)
    

class GameAttr(models.Model):
    attr = models.CharField(max_length=4)
    

class GameEvent(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    time = models.DurationField()
    period = models.CharField(max_length=5)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    athome = models.BooleanField()
    teamscore = models.CharField(max_length=10)
    vsteamscore = models.CharField(max_length=10)
    goaldiff = models.IntegerField()
    teamgoals = models.IntegerField()
    vsteamgoals = models.IntegerField()
    wongame = models.BooleanField()
    otgame = models.BooleanField()
    goals = models.IntegerField(null=True)
    latestpenalty = models.DurationField(null=True)
    latestpenaltyvs = models.DurationField(null=True)
    latestgoal = models.DurationField(null=True)
    latestgoalvs = models.DurationField(null=True)
    players = models.CharField(max_length=5)
    gameresult = models.CharField(max_length=10) 
    gameresultvs = models.CharField(max_length=10) 

    class Meta:
        abstract = True


class Goal(GameEvent):
    game = models.ForeignKey(Game, related_name='goals', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='goals', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsgoals', on_delete=models.CASCADE)

    scorer = models.ForeignKey(TeamPlayer, related_name='goals', on_delete=models.CASCADE)
    assist1 = models.ForeignKey(TeamPlayer, related_name='assist1s', null=True, on_delete=models.CASCADE)
    assist2 = models.ForeignKey(TeamPlayer, related_name='assist2s', null=True, on_delete=models.CASCADE)
    goalattr = models.CharField(max_length=20, null=True)
    score = models.CharField(max_length=5, null=True)
    attrs = models.ManyToManyField(GameAttr)


class Penalty(GameEvent):
    game = models.ForeignKey(Game, related_name='penalties', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='penalties', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vspenalties', on_delete=models.CASCADE)

    player = models.ForeignKey(TeamPlayer, related_name='penalties', null=True, on_delete=models.CASCADE)
    boxed = models.ForeignKey(TeamPlayer, related_name='boxed', null=True, on_delete=models.CASCADE)
    reason = models.CharField(max_length=80)
    minutes = models.IntegerField()
    boxtime = models.DurationField(null=True)
    goalsfor = models.IntegerField(default=0)
    goalsvs = models.IntegerField(default=0)
    endtime = models.DurationField(null=True)


class PenaltyShot(GameEvent):
    game = models.ForeignKey(Game, related_name='penaltyshots', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='penaltyshots', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vspenaltyshots', on_delete=models.CASCADE)

    player = models.ForeignKey(TeamPlayer, related_name='penaltyshots', null=True, on_delete=models.CASCADE)
    keeper = models.ForeignKey(TeamPlayer, related_name='gkpenaltyshots', null=True, on_delete=models.CASCADE)
    scored = models.BooleanField()
    order = models.IntegerField(default=0)
    teamorder = models.IntegerField(default=0)
    goalattr = models.CharField(max_length=20, null=True)


class GoalkeeperEvent(GameEvent):
    game = models.ForeignKey(Game, related_name='gkevents', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='gkevents', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsgkevents', on_delete=models.CASCADE)

    event = models.CharField(max_length=20)
    playerin = models.ForeignKey(TeamPlayer, related_name='changein', null=True, on_delete=models.CASCADE)
    playerout = models.ForeignKey(TeamPlayer, related_name='changeout', null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return u"Goalkeeper: %s: %s %s (in: %s, out:%s)" % (self.id, self.time/60, self.event, self.playerin, self.playerout)


class Timeout(GameEvent):
    game = models.ForeignKey(Game, related_name='timeouts', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='timeouts', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vstimeouts', on_delete=models.CASCADE)


class Videocheck(GameEvent):
    game = models.ForeignKey(Game, related_name='videochecks', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='videoshecks', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsvideochecks', on_delete=models.CASCADE)

    scored = models.BooleanField()
    
class Shot(GameEvent):
    game = models.ForeignKey(Game, related_name='shots', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='shots', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsshots', on_delete=models.CASCADE)

    shooter = models.ForeignKey(TeamPlayer, related_name='shots', on_delete=models.CASCADE)
    blocker = models.ForeignKey(TeamPlayer, related_name='blocks', null=True, on_delete=models.CASCADE)
    keeper = models.ForeignKey(TeamPlayer, related_name='saves', null=True, on_delete=models.CASCADE)
    result = models.CharField(max_length=20)

    teamshots = models.IntegerField(default=0)
    vsteamshots = models.IntegerField(default=0)
    

    def __unicode__(self):
        return u"Shot: %s: %s %s -> %s" % (self.id, self.time/60, self.shooter, self.result)

class GameState(models.Model):
    game = models.ForeignKey(Game, related_name='states', on_delete=models.CASCADE)

    team = models.ForeignKey(Team, related_name='gamestates', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsgamestates', on_delete=models.CASCADE)

    athome = models.BooleanField()
    wongame = models.BooleanField()
    otgame = models.BooleanField()

    start = models.DurationField()
    end = models.DurationField()
    time = models.DurationField()

    score = models.CharField(max_length=10)
    goaldiff = models.IntegerField()
    teamgoals = models.IntegerField()
    vsteamgoals = models.IntegerField()
    gameresult = models.CharField(max_length=10) 
    
    playoffs = models.BooleanField()
