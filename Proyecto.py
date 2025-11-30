import pandas as pd 
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

## 1. Cargar el DataFrame
proyecto =pd.read_csv("United_States.csv")

## 2. Transformación de datos (Si es necesario)
proyecto = proyecto.rename(columns={"Name":"Nombre","Industry":"Industria","Revenue (USD millions)":"Ganacia(USD)","Revenue growth":"Crecimiento","Employees":"#Empleados","Headquarters":"Sede"})
proyecto["Ganacia(USD)"] = proyecto["Ganacia(USD)"].str.replace(',', '.').astype(float)
def ganancia(row):
 return row ["Ganacia(USD)"] *1000
proyecto['GananciaTotal']=proyecto.apply(lambda x: ganancia(x),axis=1)
proyecto["Crecimiento"] = proyecto["Crecimiento"].str.replace('%', '').astype(float)

from ast import Return
def Resultado(row):
  if row["Crecimiento"] >0 :
    return "Crece"
  else:
    return "No crece"
proyecto["Resultados"]= proyecto.apply(lambda x: Resultado (x),axis= 1)

Empresas = proyecto['Nombre'].unique()
Industrias = proyecto['Industria'].unique()
Sedes = proyecto['Sede'].unique()
Resultados = proyecto['Resultados'].unique()
Ganancia_min = proyecto['GananciaTotal'].min()
Ganancia_max = proyecto['GananciaTotal'].max()

## 3. Crear la aplicación Dash
external_stylesheets = [dbc.themes.PULSE]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Detalle de resultados empresas americanas"

app.layout = dbc.Container([
    dbc.Row([html.H1("Reporte de ganancias industrias Americanas")]),
      dbc.Row([
          dbc.Col([
              html.Label("Selecciona la industria:"),
              dcc.Dropdown(
              id='selector_industria',
              options=[{'label': industria, 'value': industria} for industria in Industrias],
              value=proyecto['Industria'].unique()[0]  # Valor por defecto
          )]),
          dbc.Col([
              html.Label("Selecciona la empresa:"),
              dcc.Dropdown(
              id='selector_empresa',
              options=[{'label': empresa, 'value': empresa} for empresa in Empresas],
              value=proyecto['Nombre'].unique()[0]  # Valor por defecto
          )]),
          dbc.Col([
              html.Label("Selecciona la sede:"),
              dcc.RadioItems(
              id='selector_sede',
              options=[{'label': sede, 'value': sede} for sede in Sedes],
              value=proyecto['Sede'].unique()[0]  # Valor por defecto
          )])
      ]),
        dbc.Row([
          dbc.Col([
              html.Label("Selecciona el rango de ganancia:"),
              dcc.RangeSlider(
              id='selector_ganancia',
              min=Ganancia_min,
              max=Ganancia_max,
              value=[Ganancia_min,Ganancia_max],
              marks={i: str(i) for i in range(int(Ganancia_min), int(Ganancia_max) + 1)},
              step=1
          )]),
          dbc.Col([
              html.Label("Selecciona los resultados:"),
              dbc.Checklist(
                  id='selector_resultados',
                  options=[{'label': valor_resultado, 'value': valor_resultado} for valor_resultado in proyecto['Resultados'].unique()],
                  value=[proyecto['Resultados'].unique()[0]],
              )
          ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafica_barras')
        ]),
        dbc.Col([
            dcc.Graph(id='grafica_torta')
        ]),
        dbc.Col([
            dcc.Graph(id='grafica_area')
        ])
    ])
])

@app.callback(
    [Output('grafica_barras', 'figure'),
     Output('grafica_torta', 'figure'),
     Output('grafica_area', 'figure')],
    [Input('selector_industria', 'value'),
     Input('selector_empresa', 'value'),
     Input('selector_sede', 'value'),
     Input('selector_resultados', 'value'),]
)

def crear_graficas(valor_industria, valor_empresa, valor_sede, valor_ganancia):
    # Filtrar el DataFrame según el género seleccionado
    if valor_industria is None:
      df_filtrado = proyecto[(proyecto['Industria'] == valor_industria) & (proyecto['GananciaTotal'] >= valor_ganancia[0]) & (proyecto['GananciaTotal'] <= valor_ganancia[1])]
    else:
       df_filtrado = proyecto[(proyecto['Industria'] == valor_industria) & (proyecto['Nombre'] == valor_empresa) & (proyecto['GananciaTotal'] >= valor_ganancia[0]) & (proyecto['GananciaTotal'] <= valor_ganancia[1])]


    conteo_empresas_sector = df_filtrado.groupby(['Nombre','Sede'])['Ganancia'].count().reset_index().sort_values(by='Nombre', ascending=False)

    grafica_barras = px.bar(conteo_empresas_sector,
                            x='Marital Status',
                            y='Age',
                            color = 'Feedback',
                            title='Promedio del tamaño de la familia por estado civil',
                            color_discrete_sequence=['#65c78c', '#f74a50'])

    conteo_votos_feedback = df_filtrado.groupby(['Sede'])['Nombre'].count().reset_index().sort_values(by='Sede', ascending=False)
    grafica_torta = px.pie(conteo_votos_feedback,
                            names='Feedback',
                            values='Age',
                            title='Distribución del tamaño de la familia por estado civil',
                            color_discrete_sequence=['#65c78c', '#f74a50'])

    grafica_area = px.area(df_filtrado, x="Educational Qualifications", y="Family size", color="Gender",title='Gráfica de area',)


    ## Esto me sirve para que el fondo de las gráficas sea transparente
    grafica_barras.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    grafica_torta.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    grafica_area.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    return grafica_barras, grafica_torta, grafica_area