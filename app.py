# https://dashboard-covid19-rl.herokuapp.com/
# Pour l'instant, erreur lors du lancement

# Ressources dashboard déployé : 
# https://dash.plotly.com/deployment
# https://stackoverflow.com/questions/18406721/heroku-does-not-appear-to-be-a-git-repository 
# https://devcenter.heroku.com/articles/git
# https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true











# import os

# import dash
# import dash_core_components as dcc
# import dash_html_components as html

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# server = app.server

# app.layout = html.Div([
#     html.H2('Hello World'),
#     dcc.Dropdown(
#         id='dropdown',
#         options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
#         value='LA'
#     ),
#     html.Div(id='display-value')
# ])

# @app.callback(dash.dependencies.Output('display-value', 'children'),
#               [dash.dependencies.Input('dropdown', 'value')])
# def display_value(value):
#     return 'You have selected "{}"'.format(value)

# if __name__ == '__main__':
#     app.run_server(debug=True)









# RESSOURCES : 
# Données France : 
# https://www.santepubliquefrance.fr/maladies-et-traumatismes/maladies-et-infections-respiratoires/infection-a-coronavirus/articles/infection-au-nouveau-coronavirus-sars-cov-2-covid-19-france-et-monde
# https://www.data.gouv.fr/fr/organizations/sante-publique-france/#datasets
# https://www.santepubliquefrance.fr/
# https://dashboard.covid19.data.gouv.fr/vue-d-ensemble
# https://perso.esiee.fr/~courivad/PythonViz/03-dash.html
# GO REGARDER LE JUPYTER NOTEBOOK 04 POUR CONTINUER (DONNEES PAR CONTINENT)

# Imports
import plotly.express as px
import plotly
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import json
import plotly.graph_objs as go
import urllib.request
import flask
import os


# Data
# Monde
covid_csv = pd.read_csv('https://raw.githubusercontent.com/gibello/whocovid19/master/global_who_data.csv')
pop_csv  = pd.read_csv("https://raw.githubusercontent.com/datasets/population/master/data/population.csv")
country_csv = pd.read_csv("https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv")
pop = pop_csv[pop_csv["Year"] == np.max(pop_csv["Year"])]
df = pd.merge(covid_csv, pop, how="left", left_on="ISO-3166 code", right_on="Country Code")
df = pd.merge(df, country_csv, how="left", left_on="ISO-3166 code", right_on="alpha-3")
# France
url_arr = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/arrondissements-version-simplifiee.geojson"
url_dep = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
url_reg = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions-version-simplifiee.geojson"
with urllib.request.urlopen(url_arr) as url:
    jdata_arr = json.loads(url.read().decode())
import urllib.request
with urllib.request.urlopen(url_dep) as url:
    jdata_dep = json.loads(url.read().decode())
import urllib.request
with urllib.request.urlopen(url_reg) as url:
    jdata_reg = json.loads(url.read().decode())
L_arr = len(jdata_arr['features'])
L_dep = len(jdata_dep['features'])
L_reg = len(jdata_reg['features'])
for k in range(L_arr):
    jdata_arr['features'][k]['id'] = f'{k}'
for k in range(L_dep):
    jdata_dep['features'][k]['id'] = f'{k}'
for k in range(L_reg):
    jdata_reg['features'][k]['id'] = f'{k}'
arrondissements = []
for feat   in jdata_arr['features']:
    arrondissements.append(feat['properties']['nom'])
departements = []
for feat   in jdata_dep['features']:
    departements.append(feat['properties']['nom'])
regions = []
for feat   in jdata_reg['features']:
    regions.append(feat['properties']['nom'])
pl_deep=[[0.0, 'rgb(253, 253, 204)'],
         [0.1, 'rgb(201, 235, 177)'],
         [0.2, 'rgb(145, 216, 163)'],
         [0.3, 'rgb(102, 194, 163)'],
         [0.4, 'rgb(81, 168, 162)'],
         [0.5, 'rgb(72, 141, 157)'],
         [0.6, 'rgb(64, 117, 152)'],
         [0.7, 'rgb(61, 90, 146)'],
         [0.8, 'rgb(65, 64, 123)'],
         [0.9, 'rgb(55, 44, 80)'],
         [1.0, 'rgb(39, 26, 44)']]
df_jdd = pd.read_csv("https://www.data.gouv.fr/fr/organizations/sante-publique-france/datasets-resources.csv", sep=";")
dfs = {}
urls = df_jdd["url"].drop(8, axis=0).to_list()
for i, url in enumerate(urls):
    if "metadonnee" not in url: 
        try:
            dfs[url.split("/")[-1]] = pd.read_excel(url)
        except:
            try:
                dfs[url.split("/")[-1]] = pd.read_csv(url, sep=";")
            except:
                try:
                    dfs[url.split("/")[-1]] = pd.read_csv(url)
                except:
                    print(i, " : ", url)
hosp = [url for url in dfs.keys() if "donnees-hospitalieres-covid19" in url][0]
news = [url for url in dfs.keys() if "donnees-hospitalieres-nouveaux-covid19" in url][0]
age = [url for url in dfs.keys() if "donnees-hospitalieres-classe-age-covid19" in url][0]
lastday = np.max(dfs[hosp]["jour"])
df_fr_hosp = dfs[hosp][dfs[hosp]["jour"] == lastday].groupby("dep").agg(sum).reset_index()
df_fr_news = dfs[news]
df_fr_news = df_fr_news[pd.to_datetime(df_fr_news["jour"]) > pd.to_datetime(lastday) + pd.DateOffset(days=-7)]
df_fr_news = df_fr_news.sort_values(["dep", "jour"])
df_fr_news = df_fr_news.groupby("dep").agg('mean').reset_index()
df_fr_age = dfs[age]
df_fr_age = df_fr_age[pd.to_datetime(df_fr_age["jour"]) == pd.to_datetime(lastday)]
df_fr_age = df_fr_age.groupby("cl_age90").agg("sum").drop("reg", axis=1).drop(0, axis=0).reset_index()
df_fr_age["Death rate"] = df_fr_age["dc"] / (df_fr_age["rad"] + df_fr_age["dc"])*100
df_fr_age2 = df_fr_age[["cl_age90", "hosp"]]
df_fr_age2["category"] = ["Hospitalized" for i in range(df_fr_age2.shape[0])]
df_fr_age2.columns = ["Age", "value", "Status"]
df_fr_age3 = df_fr_age[["cl_age90", "rea"]]
df_fr_age3["category"] = ["In reanimation" for i in range(df_fr_age3.shape[0])]
df_fr_age3.columns = ["Age", "value", "Status"]
df_fr_age2 = df_fr_age2.append(df_fr_age3)
df_fr_age3 = df_fr_age[["cl_age90", "rad"]]
df_fr_age3["category"] = ["Recovered" for i in range(df_fr_age3.shape[0])]
df_fr_age3.columns = ["Age", "value", "Status"]
df_fr_age2 = df_fr_age2.append(df_fr_age3)
df_fr_age3 = df_fr_age[["cl_age90", "dc"]]
df_fr_age3["category"] = ["Died" for i in range(df_fr_age3.shape[0])]
df_fr_age3.columns = ["Age", "value", "Status"]
df_fr_age2 = df_fr_age2.append(df_fr_age3)
df_fr_age3 = df_fr_age[["cl_age90", "Death rate"]]
df_fr_age3["category"] = ["Death rate" for i in range(df_fr_age3.shape[0])]
df_fr_age3.columns = ["Age", "value", "Status"]
df_fr_age2 = df_fr_age2.append(df_fr_age3)

# Data preprocessing
# Monde
def Td(serie):
    low = np.min(serie.astype(int))
    high = np.max(serie.astype(int))
    ratio = high/low
#     dt1 = 14*(2/ratio)
    dt2 = 14*np.exp((2/ratio)-1)
    return dt2
df["Date"] = pd.to_datetime(df['Date'])
last_day = np.max(df["Date"])
df["date"] = df["Date"].dt.date.astype(str)
df["Logarithm of confirmed cases"] = np.log(df["Confirmed cases"])
df["Logarithm of deaths"] = np.log(df["Deaths"])
df["Population"] = df["Value"]
df.drop("Value", axis=1)
df["Proportion of deaths * 10k"] = df["Deaths"] / df["Population"] * 10000
df["Proportion of confirmed cases * 10k"] = df["Confirmed cases"] / df["Population"] * 10000
df["Logarithm of proportion of deaths * 10k"] = np.log(df["Deaths"] / df["Population"] * 10000)
df["Logarithm of proportion of confirmed cases * 10k"] = np.log(df["Confirmed cases"] / df["Population"] * 10000)
ld = df[df["Date"] > last_day + pd.DateOffset(days=-14)]
# gb_cases = ld.groupby("Country")["Confirmed cases"].agg(Td)
# mask = np.column_stack([ld[col].str.contains("Timor Leste", na=False) for col in ld])
# print(ld.loc[mask.any(axis=1)])
# print(ld[ld.apply(lambda row: row.astype(str).str.contains('Timor Leste').any(), axis=1)])
# print("Timor Leste" in gb_cases.reset_index()["Country"])
# print("Timor Leste" in df["Country"])
# df["Time to double the amount of cases"]  = df["Country"].apply(lambda x : gb_cases[x])
# max_tdc = sorted(df.groupby("Country")["Time to double the amount of cases" ].agg("max"), reverse=True)[0]
# gb_deaths = ld.groupby("Country")["Deaths"].agg(Td)
# df["Time to double the amount of deaths"] = df["Country"].apply(lambda x : gb_deaths[x])
# max_tdd = sorted(df.groupby("Country")["Time to double the amount of deaths"].agg("max"), reverse=True)[0]
max_conf_cases = sorted(df.groupby("Country")["Confirmed cases"].agg("max"), reverse=True)[1]
max_log_conf_cases = sorted(df.groupby("Country")["Logarithm of confirmed cases"].agg("max"), reverse=True)[0]
max_prop_conf_cases = sorted(df.groupby("Country")["Proportion of confirmed cases * 10k"].agg("max"), reverse=True)[0]
max_log_prop_conf_cases = sorted(df.groupby("Country")["Logarithm of proportion of confirmed cases * 10k"].agg("max"), reverse=True)[0]
max_deaths = sorted(df.groupby("Country")["Deaths"].agg("max"), reverse=True)[1]
max_log_deaths = sorted(df.groupby("Country")["Logarithm of deaths"].agg("max"), reverse=True)[0]
max_prop_deaths = sorted(df.groupby("Country")["Proportion of deaths * 10k"].agg("max"), reverse=True)[2] # ????????????????????????????
max_log_prop_deaths = sorted(df.groupby("Country")["Logarithm of proportion of deaths * 10k"].agg("max"), reverse=True)[2] # ???????????
# min_tdc = sorted(df.groupby("Country")["Time to double the amount of cases" ].agg("min"), reverse=False)[0]
min_conf_cases = sorted(df.groupby("Country")["Confirmed cases"].agg("min"), reverse=False)[0]
min_log_conf_cases = sorted(df.groupby("Country")["Logarithm of confirmed cases"].agg("min"), reverse=False)[0]
min_prop_conf_cases = sorted(df.groupby("Country")["Proportion of confirmed cases * 10k"].agg("min"), reverse=False)[0]
min_log_prop_conf_cases = sorted(df.groupby("Country")["Logarithm of proportion of confirmed cases * 10k"].agg("min"), reverse=False)[0]
min_deaths = 0 # sorted(df.groupby("Country")["Deaths"].agg("min"), reverse=False)
min_log_deaths = 0 # sorted(df.groupby("Country")["Logarithm of deaths"].agg("min"), reverse=False)
min_prop_deaths = 0 # sorted(df.groupby("Country")["Proportion of deaths * 10k"].agg("min"), reverse=False)
min_log_prop_deaths = 0 # sorted(df.groupby("Country")["Logarithm of proportion of deaths * 10k"].agg("min"), reverse=False)
df_20_new_deaths = df[df["Country"].isin(df[df["Date"] > last_day + pd.DateOffset(days=-14)].groupby("Country")["New deaths"].agg("median").sort_values(ascending=False).head(20).reset_index()["Country"].to_list())]
df_20_new_cases  = df[df["Country"].isin(df[df["Date"] > last_day + pd.DateOffset(days=-14)].groupby("Country")["New cases" ].agg("median").sort_values(ascending=False).head(20).reset_index()["Country"].to_list())]
df_8_new_deaths = df[df["Country"].isin(df[df["Date"] > last_day + pd.DateOffset(days=-14)].groupby("Country")["New deaths"].agg("median").sort_values(ascending=False).head(10).reset_index()["Country"].to_list())]
df_8_new_cases  = df[df["Country"].isin(df[df["Date"] > last_day + pd.DateOffset(days=-14)].groupby("Country")["New cases" ].agg("median").sort_values(ascending=False).head(10).reset_index()["Country"].to_list())]
df_region = df.groupby(["date", "region"]).agg("sum").reset_index()
df2 = pd.merge(pop, country_csv, how="right", left_on="Country Code", right_on="alpha-3")
df3 = df2.groupby("region").agg("sum")["Value"].reset_index()
df3["Population"] = df3["Value"]
df3.drop("Value", axis=1, inplace=True)
df_region = pd.merge(df_region, df3, how="left", left_on="region", right_on="region")
df_region.drop("Value", axis=1, inplace=True)
df_subregion = df.groupby(["date", "sub-region"]).agg("sum").reset_index()
df2 = pd.merge(pop, country_csv, how="right", left_on="Country Code", right_on="alpha-3")
df3 = df2.groupby("sub-region").agg("sum")["Value"].reset_index()
df3["Population"] = df3["Value"]
df3.drop("Value", axis=1, inplace=True)
df_subregion = pd.merge(df_subregion, df3, how="left", left_on="sub-region", right_on="sub-region")
df_subregion.drop("Value", axis=1, inplace=True)
# France
# min_hosp = np.min(df_fr_hosp["hosp"])
# min_hosp = np.max(df_fr_hosp["hosp"])


# Main
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

# app = dash.Dash(__name__)
# server = app.server

# Confirmed cases
fig1 = px.choropleth(df, locations="ISO-3166 code", 
                    color="Confirmed cases", 
                    hover_name="Country", 
                    hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
                    animation_frame="date", # retirer et utiliser Dash pour les animations ?
                    height=800,
                    range_color=[min_conf_cases,max_conf_cases])

fig2 = px.choropleth(df, locations="ISO-3166 code", 
                    color="Logarithm of confirmed cases", 
                    hover_name="Country", 
                    hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of deaths", "Proportion of deaths * 10k", "Logarithm of proportion of deaths * 10k"], 
                    animation_frame="date", # retirer et utiliser Dash pour les animations ?
                    height=800,
                    range_color=[min_log_conf_cases,max_log_conf_cases])

# fig6 = px.choropleth(df, locations="ISO-3166 code", 
#                     color="Time to double the amount of cases", 
#                     hover_name="Country", 
#                     hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
#                     "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
#                     # animation_frame="date", # retirer et utiliser Dash pour les animations ?
#                     height=800,
#                     range_color=[min_tdc,max_tdc])

fig3 = px.line(df_20_new_deaths, 
              x="date", y="New deaths", 
              color="Country", 
              hover_name="Country",
              height=800,
              log_y = True,
              render_mode="auto")

fig4 = px.line(df_region, 
              x="date", y="New deaths", 
              color="region", 
              hover_name="region",
              height=800,
              log_y = True,
              render_mode="auto")

fig5 = px.line(df_subregion, 
              x="date", y="New deaths", 
              color="sub-region", 
              hover_name="sub-region",
              height=800,
              log_y = True,
              render_mode="auto")

fig7 = px.choropleth_mapbox(df_fr_hosp, geojson = jdata_dep, color='hosp', locations='dep',
                       color_continuous_scale="Viridis",
                       mapbox_style="carto-positron",
                       # range_color=[min_hosp, max_hosp]
                       zoom=5, center = {"lat": 46.864716, "lon": 2.349014},
                       opacity=0.5,
                       width=1600, height=900,
                      )

fig8 = px.choropleth_mapbox(df_fr_news, geojson = jdata_dep, color='incid_hosp', locations='dep',
                       color_continuous_scale="Viridis",
                       mapbox_style="carto-positron",
                       # range_color=[min_hosp, max_hosp]
                       zoom=5, center = {"lat": 46.864716, "lon": 2.349014},
                       opacity=0.5,
                       width=1600, height=900,
                      )
# fig7.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig9 = px.line(df_fr_age2, x="Age", y="value", color='Status', facet_col='Status', log_y=True)


# Layout
app.layout = html.Div(children=[

                        html.H1(children=f'World statistics',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.H2(children=f'Confirmed cases',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Scale'),
                        dcc.Dropdown(
                            id="confcases-dropdown",
                            options=[
                                {'label': 'Linear', 'value':"Linear"},
                                {'label': 'Logarithmic', 'value':"Logarithmic"},
                                {'label': 'Proportional (linear)', 'value':"Proportional (linear)"},
                                {'label': 'Proportional (logarithmic)', 'value':"Proportional (logarithmic)"},
                            ],
                            value="Proportional (logarithmic)",
                        ),

                        dcc.Graph(
                            id='confcases',
                            figure=fig1
                        ),

                        # dcc.Slider(
                        #     id='confcases-slider',
                        #     min=0,
                        #     max=df["date"].unique().shape[0],
                        #     step=1,
                        #     value=df["date"].unique().shape[0],
                        #     marks={
                        #         0: {'label': 'March 01'},
                        #         31: {'label': 'April 01'},
                        #         61: {'label': 'May 01'}
                        #     }
                        # ),
                        # dcc.Interval(
                        #     id="confcases-int", 
                        #     interval=1*250,
                        #     n_intervals=0)

                        html.Div(children=f'''
                            The graph above shows the evolution of the amount of confirmed cases
                            of COVID-19 per country from 2020-03-01 00:00:00 to {last_day}.
                        '''), 

                        ################################################


                        html.H2(children=f'Deaths',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Scale'),
                        dcc.Dropdown(
                            id="deaths-dropdown",
                            options=[
                                {'label': 'Linear', 'value':"Linear"},
                                {'label': 'Logarithmic', 'value':"Logarithmic"},
                                {'label': 'Proportional (linear)', 'value':"Proportional (linear)"},
                                {'label': 'Proportional (logarithmic)', 'value':"Proportional (logarithmic)"},
                            ],
                            value="Proportional (logarithmic)",
                        ),

                        dcc.Graph(
                            id='deaths',
                            figure=fig2
                        ),

                        html.Div(children=f'''
                            The graph above shows the evolution of the amount of deaths
                             of COVID-19 per country from 2020-03-01 00:00:00 to {last_day}.
                        '''), 

                        ################################################


                        # html.H2(children=f'Time to double the amount of cases',
                        #             style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        # # html.Label('Scale'),
                        # # dcc.Dropdown(
                        # #     id="tdc-dropdown",
                        # #     options=[
                        # #         {'label': 'Linear', 'value':"Linear"},
                        # #         {'label': 'Logarithmic', 'value':"Logarithmic"},
                        # #         {'label': 'Proportional (linear)', 'value':"Proportional (linear)"},
                        # #         {'label': 'Proportional (logarithmic)', 'value':"Proportional (logarithmic)"},
                        # #     ],
                        # #     value="Proportional (logarithmic)",
                        # # ),

                        # dcc.Graph(
                        #     id='tdc',
                        #     figure=fig6
                        # ),

                        # html.Div(children=f'''
                        #     The graph above shows the time in days taken for each country to double
                        #     the amount of cases detected the last 14 days. The higher, the brighter, the better.
                        # '''),

                        ################################################


                        html.H2(children=f'New cases / deaths per day and country',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Metric'),
                        dcc.Dropdown(
                            id="new-dropdown",
                            options=[
                                {'label': 'New confirmed cases (8 most impacted)', 'value':"New cases 8"},
                                {'label': 'New deaths (8 most impacted)', 'value':"New deaths 8"},
                                {'label': 'New confirmed cases (20 most impacted)', 'value':"New cases 20"},
                                {'label': 'New deaths (20 most impacted)', 'value':"New deaths 20"},
                                {'label': 'New confirmed cases (all)', 'value':"New cases all"},
                                {'label': 'New deaths (all)', 'value':"New deaths all"},
                            ],
                            value="New deaths 8",
                        ),

                        dcc.Graph(
                            id='new',
                            figure=fig3
                        ),

                        html.Div(children=f'''
                            The graph above shows the evolution of the amount of deaths or new cases
                             of COVID-19 per country from 2020-03-01 00:00:00 to {last_day}.
                        '''), 

                        ################################################

                        html.H2(children=f'New cases / deaths per day and subregion',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Metric'),
                        dcc.Dropdown(
                            id="new-subregion-dropdown",
                            options=[
                                {'label': 'New confirmed cases', 'value':"New cases"},
                                {'label': 'New confirmed deaths', 'value':"New deaths"},
                            ],
                            value="New deaths",
                        ),

                        dcc.Graph(
                            id='new-subregion',
                            figure=fig5
                        ),

                        html.Div(children=f'''
                            The graph above shows the evolution of the amount of deaths or new cases
                             of COVID-19 per subregion from 2020-03-01 00:00:00 to {last_day}.
                        '''), 

                        ################################################

                        html.H2(children=f'New cases / deaths per day and region',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Metric'),
                        dcc.Dropdown(
                            id="new-region-dropdown",
                            options=[
                                {'label': 'New confirmed cases', 'value':"New cases"},
                                {'label': 'New confirmed deaths', 'value':"New deaths"},
                            ],
                            value="New deaths",
                        ),

                        dcc.Graph(
                            id='new-region',
                            figure=fig4
                        ),

                        html.Div(children=f'''
                            The graph above shows the evolution of the amount of deaths or new cases
                             of COVID-19 per region from 2020-03-01 00:00:00 to {last_day}.
                        '''), 

                        ################################################

                        html.Div(children=f'''
                            Unofficial data taken from : https://github.com/gibello/whocovid19, https://github.com/datasets/population/tree/master/data and https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv.
                        '''),

                        ################################################


                        html.H1(children=f'France statistics',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.H2(children=f'Hospital data ({lastday})',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Show : '),
                        dcc.Dropdown(
                            id="fr-hosp-dropdown",
                            options=[
                                {'label': 'Hospitalized people', 'value':"hosp"},
                                {'label': 'People in reanimation', 'value':"rea"},
                                {'label': 'Recovered people', 'value':"rad"},
                                {'label': 'Dead people', 'value':"dc"},
                            ],
                            value="hosp",
                        ),

                        dcc.Graph(
                            id='fr-hosp',
                            figure=fig7
                        ),

                        html.Div(children=f'''
                            The graph above shows the amount of hospitalized people, people in reanimation, recovered people and dead people ({lastday}).
                        '''), 

                        ################################################

                        html.H2(children=f'Daily hospital data ({lastday})',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        html.Label('Show : '),
                        dcc.Dropdown(
                            id="fr-news-dropdown",
                            options=[
                                {'label': 'New hospitalized people', 'value':"incid_hosp"},
                                {'label': 'New people in reanimation', 'value':"incid_rea"},
                                {'label': 'New recovered people', 'value':"incid_rad"},
                                {'label': 'New dead people', 'value':"incid_dc"},
                            ],
                            value="incid_hosp",
                        ),

                        dcc.Graph(
                            id='fr-news',
                            figure=fig8
                        ),

                        html.Div(children=f'''
                            The graph above shows the mean (within the last seven days) of the amount of new hospitalized people, people in reanimation, recovered people and dead people ({lastday}).
                        '''), 

                        ################################################

                        html.H2(children=f'Statistics per age ({lastday})',
                                    style={'textAlign': 'center', 'color': '#7FDBFF'}),

                        dcc.Graph(
                            id='fr-age',
                            figure=fig9
                        ),

                        html.Div(children=f'''
                            The graph above shows the amount of hospitalized people, people in reanimation, recovered people, dead people and the death rate grouped by age ({lastday}).
                        '''), 

                        ################################################

                        ################################################

                        html.Div(children=f'''
                            Official french data taken from https://www.data.gouv.fr/fr/organizations/sante-publique-france/#datasets, 
                            unofficial GeoJSON data taken from https://github.com/gregoiredavid/france-geojson,

                        '''),
                        
]
)

# Updating graphs
@app.callback(
    Output(component_id='confcases', component_property='figure'),
    [Input(component_id='confcases-dropdown', component_property='value')]
)
def update_figure(input_value):
    if input_value == "Linear":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Confirmed cases", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_conf_cases,max_conf_cases])
    elif input_value == "Logarithmic" : 
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Logarithm of confirmed cases", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_log_conf_cases,max_log_conf_cases])
    elif input_value == "Proportional (linear)":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Proportion of confirmed cases * 10k", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_prop_conf_cases,max_prop_conf_cases])
    elif input_value == "Proportional (logarithmic)":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Logarithm of proportion of confirmed cases * 10k", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of confirmed cases", "Proportion of confirmed cases * 10k", "Logarithm of proportion of confirmed cases * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_log_prop_conf_cases,max_log_prop_conf_cases])

    

@app.callback(
    Output(component_id='deaths', component_property='figure'),
    [Input(component_id='deaths-dropdown', component_property='value')]
)
def update_figure(input_value):
    if input_value == "Linear":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Deaths", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of deaths", "Proportion of deaths * 10k", "Logarithm of proportion of deaths * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_deaths,max_deaths])
    elif input_value == "Logarithmic" : 
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Logarithm of deaths", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of deaths", "Proportion of deaths * 10k", "Logarithm of proportion of deaths * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_log_deaths,max_log_deaths])
    elif input_value == "Proportional (linear)":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Proportion of deaths * 10k", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of deaths", "Proportion of deaths * 10k", "Logarithm of proportion of deaths * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_prop_deaths,max_prop_deaths])
    elif input_value == "Proportional (logarithmic)":
        return px.choropleth(df, locations="ISO-3166 code", 
                        color="Logarithm of proportion of deaths * 10k", 
                        hover_name="Country", 
                        hover_data=["Confirmed cases", "New cases", "Deaths", "New deaths", 
                    "Logarithm of deaths", "Proportion of deaths * 10k", "Logarithm of proportion of deaths * 10k"], 
                        animation_frame="date", # retirer et utiliser Dash pour les animations ?
                        height=800,
                        range_color=[min_log_prop_deaths,max_log_prop_deaths])

@app.callback(
    Output(component_id='new', component_property='figure'),
    [Input(component_id='new-dropdown', component_property='value')]
)
def update_figure(input_value):
    if input_value == "New cases 8":
        return px.line(df_8_new_cases, 
                  x="date", y="New cases", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New deaths 8":
        return px.line(df_8_new_deaths, 
                  x="date", y="New deaths", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New cases 20":
        return px.line(df_20_new_deaths, 
                  x="date", y="New cases", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New deaths 20":
        return px.line(df_20_new_deaths, 
                  x="date", y="New deaths", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New cases all":
        return px.line(df, 
                  x="date", y="New cases", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New deaths all":
        return px.line(df, 
                  x="date", y="New deaths", 
                  color="Country", 
                  hover_name="Country",
                  height=800,
                  log_y = True,
                  render_mode="auto")

@app.callback(
    Output(component_id='new-subregion', component_property='figure'),
    [Input(component_id='new-subregion-dropdown', component_property='value')]
)
def update_figure(input_value):
    if input_value == "New cases":
        return px.line(df_subregion, 
                  x="date", y="New cases", 
                  color="sub-region", 
                  hover_name="sub-region",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New deaths":
        return px.line(df_subregion, 
                  x="date", y="New deaths", 
                  color="sub-region", 
                  hover_name="sub-region",
                  height=800,
                  log_y = True,
                  render_mode="auto")

@app.callback(
    Output(component_id='new-region', component_property='figure'),
    [Input(component_id='new-region-dropdown', component_property='value')]
)
def update_figure(input_value):
    if input_value == "New cases":
        return px.line(df_region, 
                  x="date", y="New cases", 
                  color="region", 
                  hover_name="region",
                  height=800,
                  log_y = True,
                  render_mode="auto")
    elif input_value == "New deaths":
        return px.line(df_region, 
                  x="date", y="New deaths", 
                  color="region", 
                  hover_name="region",
                  height=800,
                  log_y = True,
                  render_mode="auto")

@app.callback(
    Output(component_id='fr-hosp', component_property='figure'),
    [Input(component_id='fr-hosp-dropdown', component_property='value')]
)
def update_figure(input_value):
    return px.choropleth_mapbox(df_fr_hosp, geojson = jdata_dep, color=input_value, locations='dep',
                       color_continuous_scale="Viridis",
                       mapbox_style="carto-positron",
                       # range_color=[min_hosp, max_hosp]
                       zoom=5, center = {"lat": 46.864716, "lon": 2.349014},
                       opacity=0.5,
                       width=1600, height=900,
                      )

@app.callback(
    Output(component_id='fr-news', component_property='figure'),
    [Input(component_id='fr-news-dropdown', component_property='value')]
)
def update_figure(input_value):
    return px.choropleth_mapbox(df_fr_news, geojson = jdata_dep, color=input_value, locations='dep',
                       color_continuous_scale="Viridis",
                       mapbox_style="carto-positron",
                       # range_color=[min_hosp, max_hosp]
                       zoom=5, center = {"lat": 46.864716, "lon": 2.349014},
                       opacity=0.5,
                       width=1600, height=900,
                      )

# @app.callback(
#     dash.dependencies.Output('slider-output-container', 'children'),
#     [dash.dependencies.Input('my-slider', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

# Run app
if __name__ == "__main__":
    # app.run_server(debug=True)
    # port = int(os.environ.get("PORT", 5000))
    # app.run(debug=True, host='0.0.0.0', port=port)
    app.run(debug=True)