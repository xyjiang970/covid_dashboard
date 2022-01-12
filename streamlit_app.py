import streamlit as st
import pandas as pd
import plotly.express as px

url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
df = pd.read_csv(url, index_col=0)

df = df[['state','cases','confirmed_cases','confirmed_deaths']]
df = df.sort_values(by='confirmed_cases', ascending=False)

fig = px.bar(df.head(10).sort_values(by='confirmed_cases', ascending=True), x='confirmed_cases', y='state',
             title="10 States With the Most Confirmed Covid Cases",
             labels = {'state':'State',
                       'confirmed_cases':'Number of Confirmed Cases'},
             orientation='h')

fig.update_layout(height=800, width=800,
                  title_x=0.5, title={font={size=20}})

st.plotly_chart(fig)
