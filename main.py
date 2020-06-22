import requests
import pandas as pd
import io
from ORM_database import db, Series, TimeSerie, Comuna, Quarantine

# Obtenemos los csv desde Github:
r_tot = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                         'master/output/producto1/Covid-19.csv')
r_totales = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                         'master/output/producto1/Covid-19_T.csv')
r_semanas = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                         'master/output/producto15/SemanasEpidemiologicas.csv')
r_sintomas = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                          'master/output/producto15/FechaInicioSintomas.csv')
r_mov = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                     'master/output/producto33/IndiceDeMovilidad-IM_T.csv')
r_cuarentenas = requests.get('https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/'
                             'master/output/producto29/Cuarentenas-Totales.csv')

# Transformamos a data frames para trabajar mas amigablemente
df_tot = pd.read_csv(io.StringIO(r_tot.text))
df_totales = pd.read_csv(io.StringIO(r_totales.text))
df_mov = pd.read_csv(io.StringIO(r_mov.text))
df_cuarentenas = pd.read_csv(io.StringIO(r_cuarentenas.text))
df_semanas = pd.read_csv(io.StringIO(r_semanas.text))
df_sintomas = pd.read_csv(io.StringIO(r_sintomas.text))


db.connect(reuse_if_open=True)
db.create_tables([Comuna, Series, TimeSerie, Quarantine])

# Almacenamos la información de las comunas en SQLite:

info_comunas = df_tot[['Region', 'Codigo region', 'Comuna', 'Codigo comuna', 'Poblacion']]
print("OK")
info_comunas.columns = ['region_name', 'region_id', 'comuna_name', 'comuna_id', 'poblation']
info_comunas = info_comunas.dropna()
Comuna.insert_many(info_comunas.to_dict(orient='records')).execute()
print("done comunas")

# Almacenamos la información de las Series de tiempo
# (Por simplicidad, solo de las comunas Las Condes, Independencia y providencia):
#query = Comuna.select(Comuna.comuna_id).where(Comuna.region_name == 'Metropolitana')
#metropolitana_ids = pd.DataFrame(list(query.dicts()))
#selected = list(metropolitana_ids['comuna_id'])
selected = [13114, 13123, 13101,
            13201, 13110, 13125]


# Tipo de Serie:
Series.create(serie_id=0, description="Serie de Casos Totales Incremental")
Series.create(serie_id=1, description="Serie de Movilidad")
Series.create(serie_id=2, description="Serie de Casos Nuevos por Fecha de inicio síntomas")
print("done Series")

# Serie de tiempo: Total Casos por comuna

time_serie = df_totales[4:-1]
time_serie.columns = df_totales.iloc[2]
aux = time_serie.to_dict(orient='list')
dates = aux['Codigo comuna']
for id in selected:
    s_id = str(id)
    ts = zip(dates, aux[s_id])
    for (date, value) in ts:
        TimeSerie.create(serie_id=0, comuna_id=id, date=date, value=value)
print("done df_totales")


# Serie de Tiempo: Indice de movilidad por comuna:

time_serie = df_mov[5::]
time_serie.columns = df_mov.iloc[2]
aux = time_serie.to_dict(orient='list')
dates = aux['Codigo comuna']
for id in selected:
    s_id = str(id)
    ts = zip(dates, aux[s_id])
    for (date, value) in ts:
        TimeSerie.create(serie_id=1, comuna_id=id, date=date, value=value)
print("done df_movilidad")

# Almacenamos la información de las Cuarentenas históricas:

df = df_cuarentenas.iloc[:, [4, 5, 6, 7]]
df.columns = ['init_day', 'end_day', 'comuna_id', 'details']
df['init_day'] = df['init_day'].str.slice(0, 10)
df['end_day'] = df['end_day'].str.slice(0, 10)
df_selected = df[df['comuna_id'].isin(selected)]
Quarantine.insert_many(df_selected.to_dict(orient='records')).execute()
print("done df_cuarentenas")


# Almacenamos información sobre casos nuevos por semana epidemiológica:

drop_cols = ['Region', 'Codigo region', 'Comuna', 'Poblacion']
df_sintomas = df_sintomas.drop(drop_cols, axis=1)
new_names = ['Codigo comuna']
for week in df_sintomas.columns[1::]:
    init_day = df_semanas[week][0]
    new_names.append(init_day)
df_sintomas.columns = new_names
df_sintomas = df_sintomas.set_index('Codigo comuna')
df_sintomas = df_sintomas.T
df_sintomas = df_sintomas.drop(0, axis=1)

aux = df_sintomas.to_dict(orient='list')
for id in selected:
    ts = zip(df_sintomas.index, aux[id])
    for (date, value) in ts:
        TimeSerie.create(serie_id=2, comuna_id=id, date=date, value=value)

print("done df_sintomas")


