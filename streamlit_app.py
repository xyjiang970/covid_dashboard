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
url5 = 'https://github.com/nychealth/coronavirus-data/blob/master/trends/data-by-day.csv?raw=true'


# Load into separate dataframes
df1 = pd.read_csv(url, index_col=0)
df2 = pd.read_csv(url2)
df3 = pd.read_csv(url3)
df4 = pd.read_csv(url4)
df5 = pd.read_csv(url5)
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
df4 = df4[['CONFIRMED_CASE_RATE','CONFIRMED_CASE_COUNT']]

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
  
st.markdown('This is a simple dashboard showing Covid-19 statistics and general information with a focus on New York City. The data is updated regularly, automatically. Three main databases where the data is sourced are from: New York Times (NYT), Bloomberg, and NYC Health - all of which are linked at the end.')

today = str(datetime.date.today())
st.write('Updated: ',today)
#############################################################################################################################
st.markdown("***")
# NYC
st.header('NYC Statistics')
st.subheader('City Overview')

# # User selection dropdown
# option = st.selectbox(
# 'Please select your desired timeframe:',
# ('Past Year','90 Days','30 Days','14 Days','Past Week'))

# # Time series using plotly - Daily Cases (All of NYC)

# if option=='Past Year':
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(365).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)
    
# elif option=='90 Days':
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(90).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)
    
# elif option=='30 Days':
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(30).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)

# elif option=='14 Days':
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(14).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)
    
# elif option=='Past Week':
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(7).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)
    
# else:
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df5.tail(90).index.values, y=df5.Avg_Total_City_Case_Count,
#                         mode='lines+markers',
#                         name='lines',
#                         line=dict(color='firebrick', width=3)))

#     fig.update_layout(title='Average NYC Daily Case Count',
#                       title_x=0.5, 
#                       title_y=0.9,
#                       xaxis_title='Day',
#                       yaxis_title='Count (Thousands)',
#                       width=1000,
#                       height=600,
#                       xaxis=dict(
#                         showgrid=True,
#                         showticklabels=True
#                       ),
#                       yaxis=dict(
#                         showgrid=True,
#                         zeroline=False,
#                         showline=True,
#                         showticklabels=True,
#                     ),
#                       paper_bgcolor='rgba(0,0,0,0)',
#                       plot_bgcolor='rgba(0,0,0,0)')

#     fig.update_xaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=False)
#     fig.update_yaxes(showline=False, linewidth=2, linecolor='black',
#                      showgrid=True, gridcolor='lightgray')

#     st.plotly_chart(fig)



#############################################################################################################################
st.subheader('Borough Breakdown')
st.markdown(
"""
Confirmed data only. For "counts", the number is cumulative and sums up all confirmed cases _since the beginning of the outbreak_. For "rates", [NYC HEALTH](https://github.com/nychealth/coronavirus-data/tree/master/totals#by-groupcsv) defines confirmed case rate as out of 100,000 people.
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

fig.add_trace(go.Pie(labels=labels, values=df4.CONFIRMED_CASE_COUNT, textinfo='label+value', 
                     name='Counts', marker_colors=colors),
              1, 1)
fig.add_trace(go.Pie(labels=labels, values=df4.CONFIRMED_CASE_RATE, textinfo='label+percent',
                     name='Rates', marker_colors=colors),
              1, 2)

fig.update_traces(hoverinfo='value', textfont_size=16)
fig.update_layout(height=600, width=1100, 
                  font=dict(size=16)
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

#############################################################################################################################
st.markdown("***")
# National View Stats. Section
st.header('National View')

################### % Covid Positive ###########################
st.subheader('Covid Positive States Ranked')

st.markdown("""
Cases data is from [NYT](https://github.com/nytimes/covid-19-data#live-data) and is defined as, "The total number of cases of Covid-19, including both confirmed and **probable**".
""")
st.markdown("""
More info can be found in a [note here](https://github.com/nytimes/covid-19-data/blob/master/PROBABLE-CASES-NOTE.md) on "probable" cases by NYT. Additionally, here is a [PDF](https://int.nyt.com/data/documenthelper/6908-cste-interim-20-id-01-covid-19/85d47e89b637cd643d50/optimized/full.pdf) by the CSTE that establishes what are considered "probable" cases.
""")

st.caption('Using the [us-states.csv](https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv) file.')

# Bar Chart using plotly - By percentage of state population
fig = px.bar(cleaned, x='pct_Covid', y='state',
             title="% of State Population That Are Covid Positive",
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

st.markdown('\n')
################### % Fully Vaccinated ###########################
st.subheader('Vaccine Breakdown')

st.markdown("""
According to the Bloomberg repo's [data dictionary](https://github.com/BloombergGraphics/covid-vaccine-tracker-data#data-dictionary), fully vaccinated (or "completedVaccination") is defined as the "cumulative number of additional doses administered to people who've already been fully vaccinated with either a single-, two- or three-dose vaccine".
""")

st.markdown("""
Received booster (or "boosterDosesAdministered") is defined as the "Cumulative number of additional doses administered to people who've already been fully vaccinated with either a single- or two-dose vaccine".
""")

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
