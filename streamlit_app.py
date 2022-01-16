# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
#############################################################################################################################

# General Streamlit Adjustments
st.set_page_config(
     page_title="Covid Dashboard: NYC Focus",
     page_icon=":bar_chart:",
     layout="wide",
 )

st.sidebar.markdown("## Table of Contents")
st.sidebar.markdown("""
- [NYC Statistics](#nyc-statistics)
     - [Borough Breakdown](#nyc-statistics)
     
     
- [National View](#national-view)
     - [Covid Positive States Ranked](#covid-positive-states-ranked)
     - [Vaccine Breakdown](#vaccine-breakdown)
    
    
- [References](#references)
     - [Code](#code-repo)
     - [Data Sources](#data-sources)
""")
#############################################################################################################################

# Get from source and load into dataframe
# Live Datasets that are regularly updated
url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
url2 = 'https://github.com/BloombergGraphics/covid-vaccine-tracker-data/blob/master/data/current-usa.csv?raw=true'
url3 = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv?raw=true'
url4 = 'https://github.com/nychealth/coronavirus-data/blob/master/totals/by-group.csv?raw=true'

# Load into separate dataframes
df1 = pd.read_csv(url, index_col=0)
df2 = pd.read_csv(url2)
df3 = pd.read_csv(url3)
df4 = pd.read_csv(url4)
#############################################################################################################################

# Adjustments and Merging dataframes

# Selection and adjustments of data from dataframe 1
df1 = df1[['state','confirmed_cases','confirmed_deaths']]

df1 = df1.sort_values(by='confirmed_cases', ascending=False)

df1 = df1[-df1["state"].isin(["Northern Mariana Islands",
                              "American Samoa"])]

# Selection and adjustments of data from dataframe 2
df2 = df2.drop([i for i in range(59,66)])

df2 = df2[-df2["name"].isin(["Micronesia",
                             "Marshall Islands",
                             "Palau",
                             "Northern Marianas",
                             "American Samoa"])]

df2.replace('U.S. Virgin Islands', 'Virgin Islands', inplace=True)

df2 = df2[['id','name','peopleVaccinated','completedVaccination',
           'boosterDosesAdministered','population']]

df2.rename(columns={"name": "state"}, inplace=True)

# Merging into one main dataframe
df = df1.merge(df2, how='inner', on='state')

# Percentage of population confirmed with covid
df['pct_Covid'] = (df['confirmed_cases'] / df['population'])*100

# Percentage of population vaccinated (fully)
df['pct_Fully_Vaccinated'] = (df['completedVaccination'] / df['population'])*100

# Percentage of population that received booster
df['pct_ReceivedBooster'] = (df['boosterDosesAdministered'] / df['population'])*100


# Rearranging columns
df = df[['state','id','population','confirmed_cases',
         'pct_Covid','completedVaccination','pct_Fully_Vaccinated',
         'boosterDosesAdministered','pct_ReceivedBooster']]

# Setting up Borough data in df4 (data frame 4)
df4 = df4.loc[df4.subgroup.isin(['Brooklyn','Bronx','Manhattan',
                                 'Queens','StatenIsland'])]
df4.rename(columns={'subgroup': "Borough"}, inplace=True)
df4.set_index('Borough', inplace=True)
df4 = df4[['CONFIRMED_CASE_RATE','CONFIRMED_CASE_COUNT']]
#############################################################################################################################

# Cleaning and dealing with 0 values and NaNs
cleaned = df.dropna(subset=['confirmed_cases'])
cleaned = cleaned[cleaned.confirmed_cases != 0]
cleaned = cleaned.sort_values(by='pct_Covid')
lowestCovid_pct = cleaned.sort_values(by='pct_Covid', ascending=False)

# Dataframe of 10 states with highest vaccination rates of population
highestVacc_pct = df.sort_values(by='pct_Fully_Vaccinated', 
                                 ascending=True)
#############################################################################################################################

# Intro/ Title Stuff
st.title("Covid Dashboard: NYC Focus")

st.header('Introduction')
  
st.markdown('This is a simple dashboard showing Covid-19 statistics and general information with a focus on New York City. The data is updated daily automatically. Three main databases where the data is sourced are from: New York Times (NYT), Bloomberg, and NYC Health - all of which are linked at the end.')

today = str(datetime.date.today())
st.write('Updated: ',today)
#############################################################################################################################
st.markdown("***")
# NYC
st.header('NYC Statistics')
st.subheader('Borough Breakdown')
st.markdown(
"""
Confirmed data only. For rates, [NYC HEALTH](https://github.com/nychealth/coronavirus-data/tree/master/totals#by-groupcsv) defines confirmed case rate as out of 100,000 people.
"""
)
# Pie Chart subplots using plotly - Breakdown of Confirmed Data (counts & rates)
colors = ['rgb(164,162,184)','rgb(226,197,184)','rgb(243,239,216)',
          'rgb(197,210,156)','rgb(149,195,174)']

labels = df4.index.values

fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, 
                                            {'type':'domain'}]],
                   subplot_titles=['Covid Cases (Cumulative - all variants)', 
                                   'Covid Positive RATE (per 100K people)'],
                   horizontal_spacing = 0.25)

fig.add_trace(go.Pie(labels=labels, values=df4.CONFIRMED_CASE_COUNT, textinfo='label+value', 
                     name='Counts', marker_colors=colors),
              1, 1)
fig.add_trace(go.Pie(labels=labels, values=df4.CONFIRMED_CASE_RATE, textinfo='label+percent',
                     name='Rates', marker_colors=colors),
              1, 2)

fig.update_traces(hoverinfo='value', textfont_size=17)
fig.update_layout(height=900, width=1500)

st.plotly_chart(fig)

#############################################################################################################################
st.markdown("***")
# National View Stats. Section
st.header('National View')

################### % Covid Positive ###########################
st.subheader('Covid Positive States Ranked')
# Bar Chart using plotly - By percentage of state population
fig = px.bar(cleaned, x='pct_Covid', y='state',
             title="% of State Population That Are Covid Positive (Confirmed cases only)",
             labels = {'state':'State',
                       'pct_Covid':'Percentage'},
             orientation='h',
             color='pct_Covid')

# Adjustments
fig.update_layout(height=1200, width=1000,
                  title_x=0.5, 
                  title_y=0.95,
                  title=dict(font=dict(size=20)),
                  font=dict(size=15)
                  )

st.plotly_chart(fig)
st.caption('It\'s important to note here some states are not shown in the chart directly above because of the amount of missing data from the NYT database [here](https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv).')

st.markdown('\n')
################### % Fully Vaccinated ###########################
st.subheader('Vaccine Breakdown')
# Bar Chart using plotly - By vaccination %
fig = go.Figure()

fig.add_trace(go.Bar(
    y=highestVacc_pct.state,
    x=highestVacc_pct.pct_Fully_Vaccinated,
    name='Fully Vaccinated',
    orientation='h',
    marker=dict(
        color='rgba(102, 255, 102, 0.6)',
        line=dict(color='rgba(102, 255, 102, 0.85)', width=1)
    )
))

fig.add_trace(go.Bar(
    y=highestVacc_pct.state,
    x=highestVacc_pct.pct_ReceivedBooster,
    name='Received Booster',
    orientation='h',
    marker=dict(
        color='rgba(153, 255, 153, 0.6)',
        line=dict(color='rgba(153, 255, 153, 0.9)', width=1)
    )
))

fig.update_layout(barmode='stack', height=1600, width=1000,
                  title='% of State Population That Are Fully Vaccinated',
                  title_x=0.5,
                  title_y=0.97,
                  xaxis_title="Percentage",
                  yaxis_title="State",
                  font=dict(size=15)
                 )

# Show
st.plotly_chart(fig)
#############################################################################################################################
st.markdown("***")
# References Section
st.header('References')
st.subheader('Code Repo')
"""
You can check out the [code on my github here](https://github.com/xyjiang970/covid_dashboard).
"""

st.text("")

st.subheader('Data Sources')
"""
- [NYT](https://github.com/nytimes/covid-19-data)
- [Bloomberg](https://github.com/BloombergGraphics/covid-vaccine-tracker-data)
- [NYC Health](https://github.com/nychealth/coronavirus-data)
"""
