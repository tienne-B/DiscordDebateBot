from django.db import models

# Create your models here.

class Tournament(models.Model):
	TABSITE_TABBYCAT = 'tc'
	TABSITE_MIT = 'mit'

	TABSITE_CHOICES = (
		(TABSITE_TABBYCAT, 'Tabbycat'),
		(TABSITE_MIT, 'MIT-Tab'),
	)

	name = models.CharField(max_length=150)
	api = models.URLField()
	tabsite = models.CharField(max_length=5, choices=TABSITE_CHOICES)


class Team(models.Model):
	tab_id = models.IntegerField()
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)


class Person(models.Model):
	tab_id = models.IntegerField()
	discord_name = models.CharField(max_length=35, null=True)


class Speaker(Person):
	team = models.ForeignKey(Team, on_delete=models.CASCADE)


class Adjudicator(Person):
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
