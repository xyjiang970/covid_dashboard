# Libraries
import streamlit as st
import pandas as pd
import json
from urllib.request import urlopen
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import datetime
from datetime import date
# import pytz
#############################################################################################################################

# General Adjustments
st.set_page_config(
     page_title="Covid Dashboard: NYC Focus",
     page_icon=":bar_chart:",
     layout="wide",
 )

pd.options.mode.chained_assignment = None

col1, col2, col3 = st.columns(3)

# Table of Contents
st.sidebar.markdown("## Table of Contents")
st.sidebar.markdown("""
- [Introduction](#introduction)
- [NYC Statistics](#nyc-statistics)
     - [City Overview](#city-overview)
     - [Borough Breakdown](#borough-breakdown)
- [NY State View](#ny-state-view)
     - [Confirmed Covid Cases in New York](#confirmed-covid-cases-in-new-york)
- [National View](#national-view)
     - [Covid Positive US States/ Territories Ranked](#covid-positive-states-and-territories-ranked)
     - [Covid Choropleth Map of the US](#covid-choropleth-map-of-the-us)
     - [Vaccine Breakdown](#vaccine-breakdown)
- [Global View](#global-view)
- [References](#references)
     - [Code](#code-repo)
     - [Data Sources](#data-sources)
- [Inspiration](#inspiration)
""")

#############################################################################################################################
# Get from source and load into dataframe
# Live Datasets that are regularly updated
url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
url2 = 'https://github.com/BloombergGraphics/covid-vaccine-tracker-data/blob/master/data/current-usa.csv?raw=true'
url3 = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv?raw=true'
url4 = 'https://github.com/nychealth/coronavirus-data/blob/master/totals/by-group.csv?raw=true'
url5 = 'https://github.com/nychealth/coronavirus-data/blob/master/trends/data-by-day.csv?raw=true'
url6 = 'https://github.com/nychealth/coronavirus-data/blob/master/totals/data-by-modzcta.csv?raw=true'
url7 = 'https://data.cityofnewyork.us/resource/pri4-ifjk.csv'
url8 = 'https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.csv?raw=true'
geojson_URL = 'https://data.cityofnewyork.us/resource/pri4-ifjk.geojson'

# Loadign dataframes using cache
@st.cache(allow_output_mutation=True, ttl=60*60*1) # ttl = refresh cache every hour
def load_df(URL, index_column=None):
     dataframe = pd.read_csv(URL, index_col=index_column)
     return dataframe

# Loading json using cache
@st.cache(allow_output_mutation=True, ttl=60*60*24*15) # ttl = refresh cache every 15 days 
def load_json(URL):
     info = json.loads(urlopen(URL).read())
     return info

# Dataframes
df1 = load_df(url, 0)
df2 = load_df(url2)
df3 = load_df(url3)
df4 = load_df(url4)
df5 = load_df(url5)
df6 = load_df(url6)
df7 = load_df(url7)
df8 = load_df(url8)

# Json: NYC geojson file
nycmap = load_json(geojson_URL)

#############################################################################################################################

# Adjustments and Merging dataframes

# Selection and adjustments of data from dataframe 1
df1 = df1[['state','confirmed_cases','cases']]

df1 = df1.sort_values(by='cases', ascending=False)

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
df['pct_Covid'] = (df['cases'] / df['population'])*100

# Percentage of population vaccinated (fully)
df['pct_Fully_Vaccinated'] = (df['completedVaccination'] / df['population'])*100

# Percentage of population that received booster
df['pct_ReceivedBooster'] = (df['boosterDosesAdministered'] / df['population'])*100


# Rearranging columns
df = df[['state','id','population','cases','confirmed_cases',
         'pct_Covid','completedVaccination','pct_Fully_Vaccinated',
         'boosterDosesAdministered','pct_ReceivedBooster']]


# Setting up Borough data in df4 (data frame 4)
df4 = df4.loc[df4.subgroup.isin(['Brooklyn','Bronx','Manhattan',
                                 'Queens','StatenIsland'])]
df4.rename(columns={'subgroup': "Borough"}, inplace=True)
df4.set_index('Borough', inplace=True)
df4 = df4[['CASE_RATE','CASE_COUNT']]

# Setting up NY State data in df3 (data frame 3)
df3 = df3.groupby('Province_State').sum().loc[['New York']]
df3 = df3.iloc[:, 5:]
df3.index.names = ['Date']
df3 = df3.T
df3.index = pd.to_datetime(df3.index)
df3.sort_index(ascending=False, inplace=True)

# Setting up Borough data in df5 (data frame 5)
df5 = df5.tail(365)
df5['date_of_interest'] = pd.to_datetime(df5['date_of_interest'])
df5 = df5[['date_of_interest','ALL_CASE_COUNT_7DAY_AVG',
           'BK_ALL_CASE_COUNT_7DAY_AVG','BX_ALL_CASE_COUNT_7DAY_AVG',
           'MN_ALL_CASE_COUNT_7DAY_AVG','QN_ALL_CASE_COUNT_7DAY_AVG',
           'SI_ALL_CASE_COUNT_7DAY_AVG']]
df5.rename(columns={df5.columns[0]:"Date",
                    df5.columns[1]:"Avg_Total_City_Case_Count",
                    df5.columns[2]:"BK_7Day_Avg",
                    df5.columns[3]:"BX_7Day_Avg",
                    df5.columns[4]:"MN_7Day_Avg",
                    df5.columns[5]:"QN_7Day_Avg",
                    df5.columns[6]:"SI_7Day_Avg"}, inplace=True)
df5.set_index('Date',inplace=True)

# Setting up data in merged data frame "df_MODZCTA_merge"
df_MODZCTA_merge = df6.merge(df7, how='inner', on='label')
df_MODZCTA_merge = df_MODZCTA_merge[['NEIGHBORHOOD_NAME','BOROUGH_GROUP',
                                     'modzcta','zcta','COVID_CASE_COUNT',
                                     'COVID_CASE_RATE','PERCENT_POSITIVE',
                                     'label','the_geom']]
              
# Setting up data/ grouping data in df8:
df8 = df8.groupby(['iso_code', 'location'], as_index=False).sum('total_cases')
df8.set_index('iso_code', inplace=True)
              
#############################################################################################################################

# Cleaning and dealing with 0 values and NaNs
cleaned = df.dropna(subset=['cases'])
cleaned = cleaned[cleaned.cases != 0]
cleaned = cleaned.sort_values(by='pct_Covid')
lowestCovid_pct = cleaned.sort_values(by='pct_Covid', ascending=False)

# Dataframe of 10 states with highest vaccination rates of population
highestVacc_pct = df.sort_values(by='pct_Fully_Vaccinated', 
                                 ascending=True)
#############################################################################################################################

# Intro/ Title Stuff
st.title("Covid Dashboard: NYC Focus")

st.header('Introduction')
  
st.markdown('This is a simple dashboard showing Covid-19 statistics and general information with a focus on New York City. The data is updated regularly, automatically.')
st.markdown("""
Important definitions:
- **Confirmed COVID-19 case:** _A person is classified as a confirmed COVID-19 case if they test positive with a molecular test._
- **Probable COVID-19 case:** _A person is classified as a probable COVID-19 case if they meet any of the following criteria with no positive molecular test on record: (a) test positive with an antigen test, (b) have symptoms and an exposure to a confirmed COVID-19 case, or (c) died and their cause of death is listed as COVID-19 or similar._
- **Fully Vaccinated (completed vaccination):** _Cumulative number of a state's residents who’ve been fully vaccinated with either a single- or two-dose vaccine._
- **Received Booster (booster doses administered):** _Additional doses administered to people who've already been fully vaccinated with either a single- or two-dose vaccine._
""")

st.markdown("""
Definition Sources:
- [NYC Health](https://github.com/nychealth/coronavirus-data#counting-covid-19-cases-hospitalizations-and-deaths)
- [NYT's Methodology and Definitions](https://github.com/nytimes/covid-19-data#methodology-and-definitions)
- Johns Hopkins University [field descriptions](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data)
- [Bloomberg Covid Data Dictionary](https://github.com/BloombergGraphics/covid-vaccine-tracker-data#data-dictionary)
- [PDF](https://int.nyt.com/data/documenthelper/6908-cste-interim-20-id-01-covid-19/85d47e89b637cd643d50/optimized/full.pdf) by the CSTE that establishes what are considered "probable" cases.
""")

st.text("")
st.text("")

# Setting Updated Date

# today = str(datetime.date.today())
# st.write('Data Updated: ',today)
# st.write('Data Updated: ', datetime.datetime.now(pytz.timezone("US/Eastern")))

today = date.today()
# Textual month, day and year	
curr_date = today.strftime("%B %d, %Y")
st.write("Data updated for: ", curr_date)

st.text("")

st.markdown('Tip: double-click on graphs to return to normal view.')
#############################################################################################################################

st.markdown("***")
# NYC
st.header('NYC Statistics')
st.subheader('City Overview')
st.markdown("""
[7-day average of count cases citywide](https://github.com/nychealth/coronavirus-data/tree/master/trends#cases-by-daycsv) - which includes both confirmed and probable.
""")
st.caption('Using the [data-by-day.csv](https://github.com/nychealth/coronavirus-data/blob/master/trends/data-by-day.csv) file.')

# User selection dropdown
timeframe = st.selectbox(
'Please select your desired time frame:',
('Past Year','90 Days','30 Days','14 Days','Past Week'), key=1)

# Dictionary for timeframe
timeframe_dict = {
    'Past Year':365,
    '90 Days':90,
    '30 Days':30,
    '14 Days':14,
    'Past Week':7
}

# Time series using plotly - Daily Cases (All of NYC)
def city_overview_graph(timeframe):
    global df5_city
    df5_city = df5.tail(timeframe_dict[timeframe])
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df5_city.index.values, y=df5_city.Avg_Total_City_Case_Count,
                        mode='lines+markers',
                        name='lines',
                        line=dict(color='firebrick', width=3, shape='spline'),
                        marker=dict(size=5)))

    fig.update_layout(title=f"7 Day Moving Average of NYC Daily Case Count: {timeframe}",
                      title_x=0.5, 
                      title_y=0.9,
                      xaxis_title='Date',
                      yaxis_title='Cases',
                      width=1000,
                      height=600,
                      xaxis=dict(
                        showgrid=True,
                        showticklabels=True,
                        showline=False
                      ),
                      yaxis=dict(
                        showgrid=True,
                        zeroline=False,
                        showline=False,
                        showticklabels=True,
                    ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(size=15))

    fig.update_xaxes(linewidth=2, linecolor='black',
                     showgrid=False)
    fig.update_yaxes(linewidth=2, linecolor='black',
                     showgrid=True, gridcolor='lightgray')

    return st.plotly_chart(fig)

city_overview_graph(timeframe)
#############################################################################################################################

st.subheader('Borough Breakdown')
st.markdown(
"""
**Confirmed and probable cases data**. For "counts", the number is cumulative and sums up all cases _since the beginning of the outbreak_. For "rates", [NYC HEALTH](https://github.com/nychealth/coronavirus-data#rates-vs-case-counts) defines case rate as out of 100,000 people.
"""
)
st.caption('Using the [by-group.csv](https://github.com/nychealth/coronavirus-data/blob/master/totals/by-group.csv) file.')

# Pie Chart subplots using plotly - Breakdown of Confirmed Data (counts & rates)
colors = ['rgb(164,162,184)','rgb(226,197,184)','rgb(243,239,216)',
          'rgb(197,210,156)','rgb(149,195,174)']

labels = df4.index.values

fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, 
                                            {'type':'domain'}]],
                   subplot_titles=['Covid Cases Count (Cumulative since outbreak - all variants)', 
                                   'Covid Positive RATE (per 100K people)'],
                   horizontal_spacing=0.15)

fig.add_trace(go.Pie(labels=labels, values=df4.CASE_COUNT, textinfo='label+value', 
                     name='Counts', marker_colors=colors),
              1, 1)
fig.add_trace(go.Pie(labels=labels, values=df4.CASE_RATE, textinfo='label+percent',
                     name='Rates', marker_colors=colors),
              1, 2)

fig.update_traces(hoverinfo='value', textfont_size=13)
fig.update_layout(height=500, width=950, 
                  font=dict(size=13)
                 )

st.plotly_chart(fig)

st.markdown("""
For reference, the populations for each respective borough can be seen in the interactive table below:
""")

boro_pop = pd.read_html('https://www.citypopulation.de/en/usa/newyorkcity/')[0]
boro_pop = boro_pop.iloc[:, [0,-2]]
boro_pop.set_index('Name', inplace=True)
boro_pop.rename(columns={boro_pop.columns[0]: "Latest Census Data" }, inplace = True)
st.dataframe(boro_pop)
st.caption('Table data is from [U.S. Census Bureau](https://www.citypopulation.de/en/usa/newyorkcity/).')

st.text("")
st.text("")
st.text("")

st.markdown("""
Click on the legend in the chart below to select/ deselect boroughs.
""")
st.caption('Using [data-by-day.csv](https://github.com/nychealth/coronavirus-data/blob/master/trends/data-by-day.csv) file.')

# Borough User selection timeframe
boro_timeframe = st.selectbox(
'Please select your desired time frame:',
('Past Year','90 Days','30 Days','14 Days','Past Week'), key=2)

# Dictionary for boroughs timeframe
boro_timeframeDict = {
    'Past Year': 365,
    '90 Days':90,
    '30 Days':30,
    '14 Days':14,
    'Past Week':7
}

# Time series using plotly - Daily Cases (By Borough)
def show_boro_breakdown(boro_timeframe):
    global df5_boro
    df5_boro = df5.tail(boro_timeframeDict[boro_timeframe])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df5_boro.index.values, y=df5_boro.BK_7Day_Avg,
                  mode='lines',
                  name='Brooklyn',
                  line=dict(width=3, shape='spline')))
    fig.add_trace(go.Scatter(x=df5_boro.index.values, y=df5_boro.BX_7Day_Avg,
                  mode='lines',
                  name='Bronx',
                  line=dict(width=3, shape='spline')))
    fig.add_trace(go.Scatter(x=df5_boro.index.values, y=df5_boro.MN_7Day_Avg,
                  mode='lines',
                  name='Manhattan',
                  line=dict(width=3, shape='spline')))
    fig.add_trace(go.Scatter(x=df5_boro.index.values, y=df5_boro.QN_7Day_Avg,
                  mode='lines',
                  name='Queens',
                  line=dict(width=3, shape='spline')))
    fig.add_trace(go.Scatter(x=df5_boro.index.values, y=df5_boro.SI_7Day_Avg,
                  mode='lines',
                  name='Staten Island',
                  line=dict(width=3, shape='spline')))
    
    fig.update_xaxes(linewidth=2, linecolor='gray',
                     showgrid=False, gridcolor='lightgray')
    fig.update_yaxes(linewidth=2, linecolor='gray',
                     showgrid=True, gridcolor='lightgray')

    fig.update_layout(title=f'7 Day Moving Average of Case Count by Borough: {boro_timeframe}',
                      title_x=0.45, 
                      title_y=0.9,
                      xaxis_title='Date',
                      yaxis_title='Cases',
                      width=1000,
                      height=600,
                      xaxis=dict(
                            showgrid=False,
                            showticklabels=True,
                            showline=False
                            ),
                      yaxis=dict(
                            showgrid=True,
                            zeroline=False,
                            showline=False,
                            showticklabels=True,
                            ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(size=15))
    return st.plotly_chart(fig)

show_boro_breakdown(boro_timeframe)

st.text("")
st.markdown("""
The map below shows the [percentage of people ever tested for COVID-19 (positive molecular test)](https://github.com/nychealth/coronavirus-data/tree/master/totals#data-by-modzctacsv) - cumulative since the start of outbreak.
""")
st.caption("Using [data-by-modzcta.csv](https://github.com/nychealth/coronavirus-data/blob/master/totals/data-by-modzcta.csv) file and geojson data from [NYC OpenData](https://data.cityofnewyork.us/Health/Modified-Zip-Code-Tabulation-Areas-MODZCTA-/pri4-ifjk/data).")
# NYC Map
fig = px.choropleth_mapbox(df_MODZCTA_merge,
                           geojson=nycmap,
                           locations="modzcta",
                           featureidkey="properties.modzcta",
                           color="PERCENT_POSITIVE",
                           color_continuous_scale="thermal",
                           mapbox_style="carto-positron",
                           zoom=9.3, center={"lat": 40.7, "lon": -73.99},
                           opacity=0.9,
                           hover_name="NEIGHBORHOOD_NAME",
                           labels={'PERCENT_POSITIVE':'% Positive'}
                           )

fig.update_layout(
    title_text = 'Covid Breakdown by Zip Codes',
    title_x=0.5,
    title_y=0.95,
    width=1000,
    height=600
)

st.plotly_chart(fig)
#############################################################################################################################
st.markdown("***")
# NY State View
st.header('NY State View')
st.subheader('Confirmed Covid Cases in New York')
st.caption('Using the [time_series_covid19_confirmed_US.csv](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) file.')

ny_timeframe = st.selectbox(
'Please select your desired time frame:',
('Past Year','90 Days','30 Days','14 Days','Past Week'), key=3)

ny_timeframeDict = dict({
    'Past Year':365,
    '90 Days':90,
    '30 Days':30,
    '14 Days':14,
    'Past Week':7
})

def ny_overview_graph(ny_timeframe):
    global df3_ny_overview
    df3_ny_overview = df3.head(ny_timeframeDict[ny_timeframe])
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df3_ny_overview.index.values, 
                             y=df3_ny_overview['New York'],
                        mode='lines+markers',
                        name='lines',
                        line=dict(color='firebrick', width=3),
                        line_shape='spline',
                        marker=dict(size=5)
                            )
                 )

    fig.update_layout(title=f"Confirmed New York Covid Cases: {ny_timeframe} (CUMULATIVE SINCE OUTBREAK)",
                      title_x=0.5, 
                      title_y=0.9,
                      xaxis_title='Date',
                      yaxis_title='Count',
                      width=1000,
                      height=600,
                      xaxis=dict(
                          showgrid=True,
                          showticklabels=True,
                          showline=False
                          ),
                      yaxis=dict(
                          showgrid=True,
                          zeroline=False,
                          showline=False,
                          showticklabels=True,
                          ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(size=15))

    fig.update_xaxes(linewidth=2, linecolor='black',
                     showgrid=False)
    fig.update_yaxes(linewidth=2, linecolor='black',
                     showgrid=True, gridcolor='lightgray')

    return st.plotly_chart(fig)

ny_overview_graph(ny_timeframe)
#############################################################################################################################
st.markdown("***")
# National View Stats. Section
st.header('National View')

################### % Covid Positive ###########################
with col1:
     st.subheader('Covid Positive States and Territories Ranked')

     st.markdown("""
     Cases used include both confirmed and probable.
     """)

     st.caption('Using the [us-states.csv](https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv) file.')

     # Bar Chart using plotly - By percentage of state population
     fig = px.bar(cleaned, x='pct_Covid', y='state',
                  title="% of US State/ Territory Population That Is Covid Positive",
                  labels = {'state':'State',
                            'pct_Covid':'Percentage'},
                  orientation='h',
                  color='pct_Covid')

     # Adjustments
     fig.update_layout(height=1700, width=1000,
                       title_x=0.5, 
                       title_y=0.97,
                       title=dict(font=dict(size=20)),
                       font=dict(size=15)
                       )

     st.plotly_chart(fig)

with col2:
     st.subheader('Covid Choropleth Map of the US')
     # US MAP 
     fig = go.Figure(data=go.Choropleth(
         locations=cleaned.id,
         z = cleaned.pct_Covid, # Data to be color-coded
         locationmode = 'USA-states', # set of locations match entries in `locations`,
         colorbar_title = "% of population that's covid positive",
     ))

     fig.update_layout(
         title_text = 'Covid Choropleth Map: U.S.',
         title_x=0.5,
         title_y=0.95,
         width=1000,
         height=800,
         geo=dict(scope='usa', bgcolor='rgba(0,0,0,0)',
                  showlakes=False),
         title=dict(font=dict(size=20))
     )

     st.plotly_chart(fig)

################### % Fully Vaccinated ###########################
st.subheader('Vaccine Breakdown')

st.caption('Using the [current-usa.csv](https://github.com/BloombergGraphics/covid-vaccine-tracker-data/blob/master/data/current-usa.csv) file.')

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
                  title='% of US State/ Territory Population That Is Fully Vaccinated',
                  title_x=0.5,
                  title_y=0.97,
                  xaxis_title="Percent",
                  yaxis_title="State",
                  font=dict(size=15)
                 )

# Show
st.plotly_chart(fig)
#############################################################################################################################
st.markdown("***")
# Global View Stats. Section
st.header('Global View')

st.caption('Using the [owid-covid-data.csv](https://github.com/owid/covid-19-data/blob/master/public/data/owid-covid-data.csv) file.')

fig = go.Figure(data=go.Choropleth(
    locations = df8.index,
    z = df8['total_cases_per_million'],
    text = df8['location'],
    colorscale = 'YlOrRd',
    autocolorscale=False,
    reversescale=False,
    #marker_line_color='darkgray',
    marker_line_color='black',
    marker_line_width=0.8,
    colorbar_title = 'Total Cases'
))

fig.update_layout(
    title_text='Total Covid-19 Cases per Million (to Date) by Country',
    title_x=0.5,
    title_y=0.88,
    height=800,
    width=1000,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        showocean=True,
        oceancolor='#7fcdff',
        showlakes=False,
        projection_type='natural earth'
    )
)
              
# Show
st.plotly_chart(fig)              
#############################################################################################################################
st.markdown("***")
# References Section
st.header('References')
st.subheader('Code Repo')
st.markdown("""
You can check out the [code on my github here](https://github.com/xyjiang970/covid_dashboard).
""")

st.subheader('Data Sources')
st.markdown("""
- [NYT Covid Github Repo.](https://github.com/nytimes/covid-19-data)
- [Bloomberg Covid Vaccines Github Repo.](https://github.com/BloombergGraphics/covid-vaccine-tracker-data)
- [NYC Health Github Repo.](https://github.com/nychealth/coronavirus-data)
- [Johns Hopkins University Covid-19 Github Repo.](https://github.com/CSSEGISandData/COVID-19)
- [Our World in Data (OWID)](https://github.com/owid/covid-19-data/tree/master/public/data)
- [NYC OpenData](https://opendata.cityofnewyork.us/)
""")

st.markdown("***")

st.header('Inspiration')
st.markdown("""
- [NYT Live Covid Maps & Graphs](https://www.nytimes.com/interactive/2021/us/covid-cases.html)
- [Bloomberg Live Vaccine Tracker Maps & Data](https://www.bloomberg.com/graphics/covid-vaccine-tracker-global-distribution/)
- [Johns Hopkins University Live Covid-19 Dashboard](https://coronavirus.jhu.edu/map.html)
""")
