from peewee import *

db = SqliteDatabase('covid.db')

class Comuna(Model):
    region_name = CharField()
    region_id = IntegerField()
    comuna_name = CharField()
    comuna_id = IntegerField(unique=True)
    poblation = IntegerField()

    class Meta(Model):
        database = db


class Series(Model):
    serie_id = IntegerField(unique=True)
    description = CharField()

    class Meta(Model):
        database = db


class TimeSerie(Model):
    serie_id = ForeignKeyField(Series, backref="type")
    comuna_id = ForeignKeyField(Comuna)
    date = DateField()
    value = DoubleField()

    class Meta:
        database = db


class Quarantine(Model):
    init_day = DateField()
    end_day = DateField()
    comuna_id = ForeignKeyField(Comuna)
    details = CharField()

    class Meta:
        database = db


