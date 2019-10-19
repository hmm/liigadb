# Generated by Django 2.2.6 on 2019-10-17 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('identifier', models.IntegerField()),
                ('date', models.DateField()),
                ('starttime', models.DurationField(null=True)),
                ('endtime', models.DurationField(null=True)),
                ('playoffs', models.BooleanField()),
                ('time', models.DurationField()),
                ('periodscores', models.CharField(max_length=60)),
                ('result', models.CharField(max_length=10)),
                ('homescore', models.IntegerField()),
                ('awayscore', models.IntegerField()),
                ('homepoints', models.IntegerField(null=True)),
                ('awaypoints', models.IntegerField(null=True)),
                ('attendance', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Referee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('years', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('ranking', models.IntegerField(null=True)),
                ('points', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Videocheck',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('scored', models.BooleanField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videochecks', to='gamedata.Game')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videoshecks', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsvideochecks', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Timeout',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeouts', to='gamedata.Game')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeouts', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vstimeouts', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teamstats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playoffs', models.BooleanField()),
                ('gameno', models.IntegerField()),
                ('gameno_loc', models.IntegerField()),
                ('athome', models.BooleanField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('score', models.IntegerField()),
                ('vsscore', models.IntegerField()),
                ('shots', models.IntegerField()),
                ('vsshots', models.IntegerField()),
                ('saved', models.IntegerField()),
                ('vssaved', models.IntegerField()),
                ('penalties', models.IntegerField()),
                ('vspenalties', models.IntegerField()),
                ('ppgoals', models.IntegerField()),
                ('ppchances', models.IntegerField()),
                ('pptime', models.DurationField()),
                ('vsppgoals', models.IntegerField()),
                ('vsppchances', models.IntegerField()),
                ('vspptime', models.DurationField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teamstats', to='gamedata.Game')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teamstats', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsteamstats', to='gamedata.Team')),
            ],
        ),
        migrations.CreateModel(
            name='TeamPlayer',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('number', models.IntegerField(null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='gamedata.Player')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='gamedata.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Shot',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('result', models.CharField(max_length=20)),
                ('teamshots', models.IntegerField(default=0)),
                ('vsteamshots', models.IntegerField(default=0)),
                ('blocker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='gamedata.TeamPlayer')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shots', to='gamedata.Game')),
                ('keeper', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='saves', to='gamedata.TeamPlayer')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('shooter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shots', to='gamedata.TeamPlayer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shots', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsshots', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RefereeGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playoffs', models.BooleanField()),
                ('reftype', models.CharField(max_length=20)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referees', to='gamedata.Game')),
                ('referee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='gamedata.Referee')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerGameStats',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('playoffs', models.BooleanField()),
                ('position', models.CharField(max_length=10, null=True)),
                ('goals', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('points', models.IntegerField()),
                ('penalties', models.IntegerField()),
                ('plus', models.IntegerField()),
                ('minus', models.IntegerField()),
                ('plusminus', models.IntegerField()),
                ('ppgoals', models.IntegerField(null=True)),
                ('shgoals', models.IntegerField(null=True)),
                ('wingoal', models.IntegerField(null=True)),
                ('shots', models.IntegerField(null=True)),
                ('shotpct', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('faceoffs', models.IntegerField(null=True)),
                ('faceoffpct', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('playtime', models.DurationField(null=True)),
                ('athome', models.BooleanField()),
                ('lineno', models.IntegerField(null=True)),
                ('gh', models.NullBooleanField()),
                ('skating', models.IntegerField(null=True)),
                ('skatingrecord', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('shootingrecord', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='gamedata.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='gamedata.TeamPlayer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playerstats', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsplayerstats', to='gamedata.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playoffs', models.BooleanField()),
                ('period', models.CharField(max_length=5)),
                ('homescore', models.IntegerField()),
                ('awayscore', models.IntegerField()),
                ('gamehomescore', models.IntegerField()),
                ('gameawayscore', models.IntegerField()),
                ('homeshots', models.IntegerField()),
                ('awayshots', models.IntegerField()),
                ('homefaceoffs', models.IntegerField(null=True)),
                ('awayfaceoffs', models.IntegerField(null=True)),
                ('homeblocked', models.IntegerField(null=True)),
                ('awayblocked', models.IntegerField(null=True)),
                ('homemissed', models.IntegerField()),
                ('awaymissed', models.IntegerField()),
                ('homesaved', models.IntegerField()),
                ('awaysaved', models.IntegerField()),
                ('awayteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awayperiods', to='gamedata.Team')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periods', to='gamedata.Game')),
                ('hometeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeperiods', to='gamedata.Team')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
            ],
        ),
        migrations.CreateModel(
            name='PenaltyShot',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('scored', models.BooleanField()),
                ('order', models.IntegerField(default=0)),
                ('teamorder', models.IntegerField(default=0)),
                ('goalattr', models.CharField(max_length=20, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penaltyshots', to='gamedata.Game')),
                ('keeper', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gkpenaltyshots', to='gamedata.TeamPlayer')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='penaltyshots', to='gamedata.TeamPlayer')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penaltyshots', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vspenaltyshots', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('reason', models.CharField(max_length=80)),
                ('minutes', models.IntegerField()),
                ('boxtime', models.DurationField(null=True)),
                ('goalsfor', models.IntegerField(default=0)),
                ('goalsvs', models.IntegerField(default=0)),
                ('endtime', models.DurationField(null=True)),
                ('boxed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='boxed', to='gamedata.TeamPlayer')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to='gamedata.Game')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to='gamedata.TeamPlayer')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vspenalties', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperStats',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('playoffs', models.BooleanField()),
                ('goals', models.IntegerField()),
                ('goalsagainst', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('points', models.IntegerField()),
                ('penalties', models.IntegerField()),
                ('saves', models.IntegerField()),
                ('savepct', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('playtime', models.DurationField()),
                ('athome', models.BooleanField()),
                ('started', models.BooleanField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goalkeepers', to='gamedata.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gkgames', to='gamedata.TeamPlayer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gkstats', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsgkstats', to='gamedata.Team')),
            ],
        ),
        migrations.CreateModel(
            name='GoalkeeperEvent',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('event', models.CharField(max_length=20)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gkevents', to='gamedata.Game')),
                ('playerin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changein', to='gamedata.TeamPlayer')),
                ('playerout', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changeout', to='gamedata.TeamPlayer')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gkevents', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsgkevents', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('time', models.DurationField()),
                ('period', models.CharField(max_length=5)),
                ('playoffs', models.BooleanField()),
                ('athome', models.BooleanField()),
                ('teamscore', models.CharField(max_length=10)),
                ('vsteamscore', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('goals', models.IntegerField(null=True)),
                ('latestpenalty', models.DurationField(null=True)),
                ('latestpenaltyvs', models.DurationField(null=True)),
                ('latestgoal', models.DurationField(null=True)),
                ('latestgoalvs', models.DurationField(null=True)),
                ('players', models.CharField(max_length=5)),
                ('gameresult', models.CharField(max_length=10)),
                ('gameresultvs', models.CharField(max_length=10)),
                ('goalattr', models.CharField(max_length=20, null=True)),
                ('score', models.CharField(max_length=5, null=True)),
                ('assist1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assist1s', to='gamedata.TeamPlayer')),
                ('assist2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assist2s', to='gamedata.TeamPlayer')),
                ('attrs', models.ManyToManyField(to='gamedata.GameAttr')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='gamedata.Game')),
                ('scorer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='gamedata.TeamPlayer')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsgoals', to='gamedata.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gamestats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playoffs', models.BooleanField()),
                ('homescore', models.IntegerField()),
                ('awayscore', models.IntegerField()),
                ('homeshots', models.IntegerField()),
                ('awayshots', models.IntegerField()),
                ('homefaceoffs', models.IntegerField(null=True)),
                ('awayfaceoffs', models.IntegerField(null=True)),
                ('homeblocked', models.IntegerField(null=True)),
                ('awayblocked', models.IntegerField(null=True)),
                ('homemissed', models.IntegerField()),
                ('awaymissed', models.IntegerField()),
                ('homesaved', models.IntegerField()),
                ('awaysaved', models.IntegerField()),
                ('homeppgoals', models.IntegerField()),
                ('awayppgoals', models.IntegerField()),
                ('homeppchances', models.IntegerField()),
                ('awayppchances', models.IntegerField()),
                ('homepppct', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('awaypppct', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('homepptime', models.DurationField()),
                ('awaypptime', models.DurationField()),
                ('awayteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awaystats', to='gamedata.Team')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='gamedata.Game')),
                ('hometeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homestats', to='gamedata.Team')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
            ],
        ),
        migrations.CreateModel(
            name='GameState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('athome', models.BooleanField()),
                ('wongame', models.BooleanField()),
                ('otgame', models.BooleanField()),
                ('start', models.DurationField()),
                ('end', models.DurationField()),
                ('time', models.DurationField()),
                ('score', models.CharField(max_length=10)),
                ('goaldiff', models.IntegerField()),
                ('teamgoals', models.IntegerField()),
                ('vsteamgoals', models.IntegerField()),
                ('gameresult', models.CharField(max_length=10)),
                ('playoffs', models.BooleanField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='gamedata.Game')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamestates', to='gamedata.Team')),
                ('vsteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vsgamestates', to='gamedata.Team')),
            ],
        ),
        migrations.CreateModel(
            name='GameMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('identifier', models.IntegerField()),
                ('datetime', models.DateTimeField()),
                ('date', models.DateField()),
                ('starttime', models.DurationField()),
                ('endtime', models.DurationField(null=True)),
                ('playoffs', models.BooleanField()),
                ('homerest', models.IntegerField(null=True)),
                ('awayrest', models.IntegerField(null=True)),
                ('awayteam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awaygameshedule', to='gamedata.Team')),
                ('hometeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homegameshedule', to='gamedata.Team')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='awayteam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awaygames', to='gamedata.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='hometeam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homegames', to='gamedata.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamedata.Season'),
        ),
    ]
