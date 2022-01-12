import streamlit as st
import pandas as pd
import plotly.express as px

url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
df = pd.read_csv(url, index_col=0)

df = df[['state','cases','confirmed_cases','confirmed_deaths']]
df = df.sort_values(by='confirmed_cases', ascending=False)

st.title('Daily Covid Cases Dashboard')

fig = px.bar(df.head(10).sort_values(by='confirmed_cases', ascending=True), x='confirmed_cases', y='state',
             title="10 States With the Highest Confirmed Covid Cases",
             labels = {'state':'State',
                       'confirmed_cases':'Number of Confirmed Cases'},
             orientation='h',
             color='confirmed_cases')

fig.update_layout(height=800, width=800,
                  title_x=0.48, 
                  title_y=0.93,
                  title=dict(font=dict(size=20)),
                  font=dict(size=15)
                  )

st.plotly_chart(fig)

st.write('While it\'s helpful to see the breakdown of general confirmed daily covid cases, it would be more helpful to see what percentage of confirmed cases make up of the total state population as some states hold more people than others.')
