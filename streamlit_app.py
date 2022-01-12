import streamlit as st
import pandas as pd
import plotly.express as px

url = 'https://github.com/nytimes/covid-19-data/blob/master/live/us-states.csv?raw=true'
df = pd.read_csv(url, index_col=0)

df = df[['state','cases','confirmed_cases','confirmed_deaths']]
df = df.sort_values(by='confirmed_cases', ascending=True)

fig = px.bar(df.head(10), x='confirmed_cases', y='state',
             title="10 States With the Most Confirmed Covid Cases",
             labels = {'state':'State',
                       'confirmed_cases':'Number of Confirmed Cases'},
             orientation='h')

fig.update_layout(width=800)

st.plotly_chart(fig)
