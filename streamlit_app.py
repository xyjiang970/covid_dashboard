# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
#############################################################################################################################

# Get from source and load into dataframe
# Live Datasets that are regularly updated
url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
url2 = 'https://github.com/BloombergGraphics/covid-vaccine-tracker-data/blob/master/data/current-usa.csv?raw=true'
url3 = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv?raw=true'
url4 = 'https://github.com/nychealth/coronavirus-data/blob/master/totals/group-data-by-boro.csv?raw=true'

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

# Percentage of population confirmed dead from covid
df['pct_deadFromCovid'] = (df['confirmed_deaths'] / df['population'])*100

# Rearranging columns
df = df[['state','id','population','confirmed_cases',
         'pct_Covid','completedVaccination','pct_Fully_Vaccinated',
         'boosterDosesAdministered','pct_ReceivedBooster',
         'confirmed_deaths','pct_deadFromCovid']]

# Setting up Borough data in df4 (data frame 4)
boroughConfirmedCount = ['BK_CONFIRMED_CASE_COUNT','BX_CONFIRMED_CASE_COUNT',
                         'MN_CONFIRMED_CASE_COUNT', 'QN_CONFIRMED_CASE_COUNT',
                         'SI_CONFIRMED_CASE_COUNT']
df4 = df4[boroughConfirmedCount].iloc[0].T.to_frame()
df4.rename(columns={0:'Counts'}, inplace=True)
df4.rename(index={'BK_CONFIRMED_CASE_COUNT': 'Brooklyn', 'BX_CONFIRMED_CASE_COUNT':'Bronx',
                  'MN_CONFIRMED_CASE_COUNT':'Manhattan', 'QN_CONFIRMED_CASE_COUNT':'Queens',
                  'SI_CONFIRMED_CASE_COUNT':'StatenIsland'}, inplace=True)
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
  
st.markdown('This is a simple, live dashboard showing Covid-19 statistics and general information with a focus on New York City. Three main databases where the data originated from are: New York Times (NYT), Bloomberg, and NYC Health - all of which are linked at the end.')

# Setting Timezone
today = str(datetime.date.today())
st.write('Updated: ',today)
#############################################################################################################################
st.markdown("***")
# NYC
st.header('NYC Statistics')
st.subheader('Borough Breakdown')
# Pie Chart using plotly - Breakdown of Confirmed Covid Cases by Borough
fig = px.pie(df4, values='Counts', names=df4.index.values,
             color_discrete_sequence=px.colors.sequential.RdBu,
             title='% Breakdown of Confirmed Covid Cases by Borough',
             height=600,
             width=600)

# Adjustments
fig.update_traces(textfont_size=15)
fig.update_layout(
                  title_x=0.5, 
                  title_y=0.95,
                  )

st.plotly_chart(fig)

#############################################################################################################################
st.markdown("***")
# National View Stats. Section
st.header('National View')

################### % Covid Positive ###########################
# Bar Chart using plotly - By percentage of state population
fig = px.bar(cleaned, x='pct_Covid', y='state',
             title="% of State Population That Are covid Positive",
             labels = {'state':'State',
                       'pct_Covid':'Percentage'},
             orientation='h',
             color='pct_Covid')

# Adjustments
fig.update_layout(height=1200, width=1000,
                  title_x=0.5, 
                  title_y=0.95,
                  title=dict(font=dict(size=15)),
                  font=dict(size=11)
                  )

st.plotly_chart(fig)
st.caption('It\'s important to note here some states are not shown in the chart directly above because of the amount of missing data from the NYT database [here](https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv).')

st.markdown('\n')
################### % Fully Vaccinated ###########################
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

fig.update_layout(barmode='stack', height=1700, width=1000,
                  title='% of State Population That Are Fully Vaccinated',
                  title_x=0.5,
                  title_y=0.97,
                  xaxis_title="Percentage",
                  yaxis_title="State",
                  font=dict(size=10)
                 )

# Show
st.plotly_chart(fig)
#############################################################################################################################
st.markdown("***")
# References Section
st.header('References')
"""
### Code Repo
You can check out the [code on my github here](https://github.com/xyjiang970/covid_dashboard).
"""

st.text("")

"""
### DataSources
- [NYT](https://github.com/nytimes/covid-19-data)
- [Bloomberg](https://github.com/BloombergGraphics/covid-vaccine-tracker-data)
- [NYC Health](https://github.com/nychealth/coronavirus-data)
"""
