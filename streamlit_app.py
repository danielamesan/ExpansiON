
import pandas as pd
from shapely import wkt
from shapely.geometry import Point
import geopandas as gpd
import math
import streamlit as st

# Función para calcular la distancia entre dos puntos geográficos
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c * 1000  # Devuelve la distancia en metros

# Cargar los datos de los CSV
df_locales = pd.read_csv('fincaraiz_final.csv')
df_puntos_interes = pd.read_csv('bogota_filtered_pois.csv')

# Invertir coordenadas de los locales y separar latitud y longitud
df_locales[['latitud', 'longitud']] = df_locales['location_point'].str.split(', ', expand=True)
df_locales['latitud'] = df_locales['latitud'].astype(float)
df_locales['longitud'] = df_locales['longitud'].astype(float)

# Convertir la columna 'geometry' a objetos geométricos usando WKT
df_puntos_interes['geometry'] = df_puntos_interes['geometry'].apply(wkt.loads)

# Filtrar solo los objetos que son de tipo Point
df_puntos_interes = df_puntos_interes[df_puntos_interes['geometry'].apply(lambda x: isinstance(x, Point))]

# Extraer latitud y longitud de los puntos de interés
df_puntos_interes['latitud'] = df_puntos_interes['geometry'].apply(lambda point: point.y)
df_puntos_interes['longitud'] = df_puntos_interes['geometry'].apply(lambda point: point.x)

# Función para buscar locales cerca de un tipo de punto de interés
def buscar_locales_cerca(tipo_punto, rango):
    # Filtrar puntos de interés por tipo
    puntos_interes_filtrados = df_puntos_interes[df_puntos_interes['amenity'].str.lower() == tipo_punto.lower()]
    
    resultados = []

    # Calcular distancias
    for index_local, local in df_locales.iterrows():
        local_lat = local['latitud']
        local_lon = local['longitud']
        
        for index_punto, punto in puntos_interes_filtrados.iterrows():
            punto_lat = punto['latitud']
            punto_lon = punto['longitud']
            
            distancia = haversine(local_lat, local_lon, punto_lat, punto_lon)
            
            if distancia <= rango:
                resultados.append({
                    'Título': local['title'],  # Columna de df_locales
                    'Precio': local['price'],  # Columna de df_locales
                    'Área': local['area'],  # Columna de df_locales
                    'Tipo de propiedad': local['property_type'],  # Columna de df_locales
                    'Estrato': local['estrato'],  # Columna de df_locales
                    'Baños': local['bathrooms'],  # Columna de df_locales
                    'Habitaciones': local['bedrooms'],  # Columna de df_locales
                    'Garaje': local['garage'],  # Columna de df_locales
                    'Punto de Interés Nombre': punto['name'],  # Columna de df_puntos_interes
                    'Distancia (metros)': distancia  # Distancia en metros
                })

    # Convertir resultados a DataFrame
    df_resultados = pd.DataFrame(resultados)
    return df_resultados

# Streamlit App
st.title("Búsqueda de Locales Cercanos a Puntos de Interés")

# Selector para tipo de punto de interés
tipos_puntos_interes = df_puntos_interes['name'].unique()
tipo_punto_interes = st.selectbox("Selecciona un tipo de punto de interés:", tipos_puntos_interes)

# Slider para rango de búsqueda
rango_busqueda = st.slider("Selecciona el rango de búsqueda (en metros):", min_value=0, max_value=3000, value=500)

# Botón para buscar
if st.button("Buscar Locales"):
    resultados_encontrados = buscar_locales_cerca(tipo_punto_interes, rango_busqueda)

    # Mostrar resultados
    if not resultados_encontrados.empty:
        st.write(f"Locales encontrados cerca de {tipo_punto_interes} en un rango de {rango_busqueda} metros:")
        st.dataframe(resultados_encontrados)
    else:
        st.write(f"No se encontraron locales cerca de {tipo_punto_interes} en un rango de {rango_busqueda} metros.")






















import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
