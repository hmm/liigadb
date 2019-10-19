from __future__ import unicode_literals

from django.db import models

# Create your models here.

# Create your models here.
class Season(models.Model):
    years = models.CharField(max_length=20)
    short = models.CharField(max_length=20)
    teamcount = models.IntegerField(null=True)
    playoffsteams = models.IntegerField(null=True)
    ppg = models.IntegerField(null=True)
    
    def __unicode__(self):
        return u"Season: %s" % self.years


class Team(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20)
    currentname = models.CharField(max_length=20, null=True)
    currentteam = models.ForeignKey('Team', related_name='oldnames', null=True, on_delete=models.CASCADE)
    
    def __unicode__(self):
        return u"Team: %s" % self.id


class Game(models.Model):
    number = models.IntegerField()
    identifier = models.IntegerField()

    date = models.DateField()
    starttime = models.DurationField()

    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    playoffs = models.BooleanField()
    
    hometeam = models.ForeignKey(Team, related_name='homegameshedule', on_delete=models.CASCADE)
    awayteam = models.ForeignKey(Team, related_name='awaygameshedule', on_delete=models.CASCADE)

    homescore = models.IntegerField(null=True)
    awayscore = models.IntegerField(null=True)
    homepoints = models.IntegerField(null=True)
    awaypoints = models.IntegerField(null=True)
    
    result = models.CharField(max_length=10, null=True)
    resultattr = models.CharField(max_length=20, null=True)
    otgame = models.BooleanField()

    def __unicode__(self):
        return u"Game: %s (%s - %s) %s - %s" % (self.id, self.hometeam.id, self.awayteam.id, self.date, self.starttime)


class TeamGame(models.Model):
    season = models.ForeignKey(Season, related_name='teamgames', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='teamgames', on_delete=models.CASCADE)
    playoffs = models.BooleanField()

    date = models.DateField()
    team = models.ForeignKey(Team, related_name='teamgames', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='vsteamgames', on_delete=models.CASCADE)
    
    athome = models.BooleanField()
    gameno = models.IntegerField()

    teamscore = models.IntegerField(null=True)
    vsteamscore = models.IntegerField(null=True)
    otgame = models.BooleanField()

    teamresult = models.CharField(max_length=10, null=True)
    resultattr = models.CharField(max_length=20, null=True)
    
    won = models.BooleanField()
    tied = models.BooleanField()
    points = models.IntegerField(null=True)    
    points3 = models.IntegerField(null=True)    

    rest = models.IntegerField(null=True)
    vsrest = models.IntegerField(null=True)

    seriespoints = models.IntegerField(null=True)
    teamrank = models.IntegerField(null=True)
    vsteamrank = models.IntegerField(null=True)


class TeamSeason(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    team = models.ForeignKey(Team, related_name='seasons', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, related_name='teams', on_delete=models.CASCADE)

    attendance = models.IntegerField(null=True)

    games = models.IntegerField()
    points = models.IntegerField()

    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField()
    otwins = models.IntegerField(null=True)
    
    goals = models.IntegerField()
    goalsagainst = models.IntegerField()
    goaldiff = models.IntegerField()

    ppgoals = models.IntegerField(null=True)
    minutes = models.IntegerField(null=True)
    
    homepoints = models.IntegerField()

    homegames = models.IntegerField()
    homewins = models.IntegerField()
    homelosses = models.IntegerField()
    hometies = models.IntegerField()
    homeotwins = models.IntegerField(null=True)

    homegoals = models.IntegerField()
    homegoalsagainst = models.IntegerField()

    seriesranking = models.IntegerField(null=True)
    finalranking = models.IntegerField(null=True)
    playoffs = models.BooleanField(default=False)
    

class SeriesLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    level = models.CharField(max_length=20)

    
class PlayoffsSeries(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    season = models.ForeignKey(Season, related_name='playoffs', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='playoffs', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='playoffsvs', on_delete=models.CASCADE)

    teamrank = models.IntegerField(null=True)
    vsteamrank = models.IntegerField(null=True)

    level = models.IntegerField()
    won = models.BooleanField()

    games = models.IntegerField()
    wins = models.IntegerField()

    homewins = models.IntegerField()

    otgames = models.IntegerField()
    otwins = models.IntegerField()

    serieslength = models.IntegerField(null=True)
    seriesresult = models.CharField(max_length=10, null=True)
    results = models.CharField(max_length=10, null=True)

    def __unicode__(self):
        if self.won:
            return u"TS: %s - %s vs %s level %d: won" % (self.season.id, self.team, self.vsteam, self.level) 
        else:
            return u"TS: %s - %s vs %s level %d: lost" % (self.season.id, self.team, self.vsteam, self.level) 


class PlayoffsGame(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    season = models.ForeignKey(Season, related_name='playoffsgames', on_delete=models.CASCADE)
    series = models.ForeignKey(PlayoffsSeries, related_name='playoffsgames', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='playoffsgames', on_delete=models.CASCADE)

    team = models.ForeignKey(Team, related_name='playoffsgames', on_delete=models.CASCADE)
    vsteam = models.ForeignKey(Team, related_name='playoffsgamesvs', on_delete=models.CASCADE)

    teamrank = models.IntegerField(null=True)
    vsteamrank = models.IntegerField(null=True)

    level = models.IntegerField()
    won = models.BooleanField()
    athome = models.BooleanField()
    otgame = models.BooleanField()
    gameno = models.IntegerField()

    teamscore = models.IntegerField(null=True)
    vsteamscore = models.IntegerField(null=True)
    teamresult = models.CharField(max_length=10, null=True)

    wins = models.IntegerField()
    losses = models.IntegerField()
    seriesscore = models.CharField(max_length=10)

    
    wonseries = models.BooleanField()
    seriesgames = models.IntegerField()
    serieswins = models.IntegerField()
    seriesresult = models.CharField(max_length=10)


class Player(models.Model):
    id = models.CharField(max_length=40, primary_key=True) 
    name = models.CharField(max_length=40) 
    firstname = models.CharField(max_length=40, null=True) 
    lastname = models.CharField(max_length=40, null=True)
    homecity = models.CharField(max_length=40, null=True)
    nationality = models.CharField(max_length=40, null=True)
    position = models.CharField(max_length=10, null=True)
    stick = models.CharField(max_length=10, null=True)
    born = models.DateField(null=True)

    number = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    height = models.IntegerField(null=True)


class PlayerStat(models.Model):
    playoffs = models.BooleanField()
    position = models.CharField(max_length=10, null=True)
    games = models.IntegerField()

    goals = models.IntegerField()
    assists = models.IntegerField()
    points = models.IntegerField()

    penalties = models.IntegerField()
    plus = models.IntegerField(null=True)
    minus = models.IntegerField(null=True)
    plusminus = models.IntegerField(null=True)

    ppgoals = models.IntegerField(null=True)
    shgoals = models.IntegerField(null=True)
    wingoals = models.IntegerField(null=True)

    shots = models.IntegerField(null=True)
    shotpct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    faceoffs = models.IntegerField(null=True)
    faceoffpct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    playtime = models.DurationField(null=True)
    
    class Meta:
        abstract = True

class PlayerStats(PlayerStat):
    id = models.CharField(max_length=60, primary_key=True) 
    player = models.ForeignKey(Player, related_name='teams', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='playerstats', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

class PlayerSeason(PlayerStat):
    id = models.CharField(max_length=60, primary_key=True) 
    player = models.ForeignKey(Player, related_name='seasons', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    teams = models.IntegerField()
    teamnames = models.CharField(max_length=20)

class PlayerTotal(PlayerStat):
    id = models.CharField(max_length=60, primary_key=True) 
    player = models.ForeignKey(Player, related_name='stats', on_delete=models.CASCADE)
    seasons = models.IntegerField()
    teams = models.IntegerField()
    teamnames = models.CharField(max_length=20)

