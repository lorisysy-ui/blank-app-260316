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
# Streamlit 요소 데모 섹션
with st.expander('Streamlit 주요 UI 요소 데모', expanded=False):
    st.write('Streamlit에서 자주 사용하는 다양한 UI 요소 예시입니다.')
    st.header('텍스트/마크다운')
    st.text('이것은 일반 텍스트입니다.')
    st.markdown('**이것은 마크다운 텍스트입니다!**')
    st.code('print("Hello, Streamlit!")', language='python')
    st.header('버튼')
    if st.button('클릭해보세요!'):
        st.success('버튼이 클릭되었습니다!')
    st.header('체크박스')
    checked = st.checkbox('동의합니다')
    st.write('체크박스 상태:', checked)
    st.header('라디오 버튼')
    radio_val = st.radio('라디오 선택', ['옵션 1', '옵션 2', '옵션 3'])
    st.write('선택된 값:', radio_val)
    st.header('슬라이더')
    slider_val = st.slider('값을 선택하세요', 0, 100, 50)
    st.write('슬라이더 값:', slider_val)
    st.header('셀렉트박스')
    select_val = st.selectbox('하나를 선택하세요', ['A', 'B', 'C'])
    st.write('선택:', select_val)
    st.header('멀티셀렉트')
    multi_val = st.multiselect('여러 개 선택', ['Python', 'Java', 'C++'])
    st.write('선택:', multi_val)
    st.header('입력창')
    text_input = st.text_input('텍스트 입력')
    st.write('입력값:', text_input)
    st.header('숫자 입력')
    num_input = st.number_input('숫자 입력', min_value=0, max_value=100, value=10)
    st.write('입력값:', num_input)
    st.header('파일 업로드')
    uploaded_file = st.file_uploader('파일을 업로드하세요')
    if uploaded_file:
        st.write('업로드된 파일명:', uploaded_file.name)
    st.header('컬럼 레이아웃')
    col1, col2 = st.columns(2)
    with col1:
        st.write('왼쪽 컬럼')
    with col2:
        st.write('오른쪽 컬럼')
    st.header('진행바')
    import time
    if st.button('진행바 실행'):
        progress = st.progress(0)
        for i in range(1, 101):
            time.sleep(0.01)
            progress.progress(i)
        st.success('완료!')
    st.header('경고/성공/에러 메시지')
    st.warning('이것은 경고 메시지입니다!')
    st.success('이것은 성공 메시지입니다!')
    st.error('이것은 에러 메시지입니다!')

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
