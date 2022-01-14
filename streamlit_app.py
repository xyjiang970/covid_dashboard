# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Live Datasets that are regularly updated
url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
url2 = 'https://github.com/BloombergGraphics/covid-vaccine-tracker-data/blob/master/data/current-usa.csv?raw=true'

# Load into separate dataframes
df1 = pd.read_csv(url, index_col=0)
df2 = pd.read_csv(url2)

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

st.title('Covid Dashboard: NYC Focus')

########################################################################################
# Dataframe of 10 states with the highest general number of people who are covid positive
highestNumCovid = df.head(10).sort_values(by='confirmed_cases', ascending=True)

# Dataframe of 10 states with highest percentage of covid positive population
highestCovid_pct = df.head(10).sort_values(by='pct_Covid', ascending=True)

# Missing (NaN) and 0 confirmed cases states removed
cleaned = df.dropna(subset=['confirmed_cases'])
cleaned = cleaned[cleaned.confirmed_cases != 0]
cleaned = cleaned.sort_values(by='pct_Covid')
lowestCovid_pct = cleaned.head(10).sort_values(by='pct_Covid', ascending=False)

# Dataframe of 10 states with highest vaccination rates of population
highestVacc_pct = df.head(10).sort_values(by='pct_Fully_Vaccinated')
########################################################################################

# Setting Timezone
today = str(datetime.date.today())
st.write('Updated: ',today)

############# Bar Chart using plotly - General confirmed cases #############
fig = px.bar(df.head(10).sort_values(by='confirmed_cases', ascending=True), x='confirmed_cases', y='state',
             title="10 States With the Highest Confirmed Covid Cases",
             labels = {'state':'State',
                       'confirmed_cases':'Number of Confirmed Cases (Millions)'},
             orientation='h',
             color='confirmed_cases')

fig.update_layout(height=800, width=1000,
                  title_x=0.40, 
                  title_y=0.93,
                  title=dict(font=dict(size=20)),
                  font=dict(size=15)
                  )

# Show
st.plotly_chart(fig, use_container_width=True)


###########################################################################

st.markdown('While it\'s helpful to see the general number of confirmed daily covid cases by state, it would be more insightful to see **_what percentage of confirmed cases make up the total state population_** (since some states have a larger population than other states).')

# Bar Chart using plotly - By percentage of state population 
fig = px.bar(df.head(10).sort_values(by='pct_Covid', ascending=True), x='pct_Covid', y='state',
             title="10 States with the Highest Confirmed Covid Cases: By % of State Population",
             labels = {'state':'State',
                       'pct_Covid':'Percentage of Population with Covid'},
             orientation='h',
             color='pct_Covid')

# Adjustments
fig.update_layout(height=800, width=1000,
                  title_x=0.45, 
                  title_y=0.93,
                  title=dict(font=dict(size=20)),
                  font=dict(size=15)
                  )

# Show
st.plotly_chart(fig, use_container_width=True)

###########################################################################

# Bar Chart using plotly - By vaccination %

# Dataframe of 10 states with highest vaccination rates of population
highestVacc_pct = df.head(10).sort_values(by='pct_Fully_Vaccinated')

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

fig.update_layout(barmode='stack', height=800, width=1000,
                  title='10 States With the Highest % of Population Fully Vaccinated',
                  title_x=0.48,
                  title_y=0.92,
                  xaxis_title="Percentage",
                  yaxis_title="State",
                  font=dict(size=15))


# Show
st.plotly_chart(fig, use_container_width=True)

###########################################################################

st.markdown('You can check out the [code on my github here](https://github.com/xyjiang970/covid_dashboard).')


fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Top 10 Highest % States", ""),
                    horizontal_spacing = 0.3)


fig.add_trace(
    go.Bar(
        x=highestCovid_pct.pct_Covid, 
        y=highestCovid_pct.state,
        orientation='h',
        showlegend=False),
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=lowestCovid_pct.pct_Covid, 
        y=lowestCovid_pct.state,
        orientation='h',
        showlegend=False),
    row=1, col=2
)

# Update xaxis properties
fig.update_xaxes(title_text="Percentage", row=1, col=1)
fig.update_xaxes(title_text="Percentage", row=1, col=2)

# Update yaxis properties
fig.update_yaxes(title_text="State", row=1, col=1)
fig.update_yaxes(title_text="State", row=1, col=2)

fig.update_layout(height=800, width=1000, 
                  title_text="Covid Positive by % of State Population",
                  title_x=0.5)

st.plotly_chart(fig, use_container_width=True)
