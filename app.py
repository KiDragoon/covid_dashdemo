import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# 데이터 파일 경로
file_path = './data/covid.csv'

# 데이터 불러오기
covid_data = pd.read_csv(file_path)

# 날짜 형식 변환 및 필요한 열 추출
covid_data['date'] = pd.to_datetime(covid_data['date'])
covid_data['month'] = covid_data['date'].dt.to_period('M').astype(str)
# 월별 데이터 계산
monthly_data = covid_data.groupby(['month', 'location'], as_index=False).agg({
    'new_deaths': 'sum',
    'people_vaccinated': 'last'
})

# Plotly 그래프 설정
fig = go.Figure()

# 각 location별 데이터 추가
locations = monthly_data['location'].unique()
for location in locations:
    loc_data = monthly_data[monthly_data['location'] == location]
    # 월별 사망자 수 추가 (막대 그래프, yaxis1)
    fig.add_trace(go.Bar(
        x=loc_data['month'],
        y=loc_data['new_deaths'],
        name=f'월별 사망자 수 - {location}',
        marker_color='red',
        yaxis='y1',
        visible=False
    ))
    # 누적 백신 접종자 수 추가 (선 그래프, yaxis2)
    fig.add_trace(go.Scatter(
        x=loc_data['month'],
        y=loc_data['people_vaccinated'],
        name=f'누적 백신 접종자 수 - {location}',
        mode='lines+markers',
        line=dict(color='blue'),
        yaxis='y2',
        visible=False
    ))

# 첫 번째 location만 표시 
fig.data[0].visible = True
fig.data[1].visible = True

# 드롭다운 버튼 생성
dropdown_buttons = []
for i, location in enumerate(locations):
    dropdown_buttons.append(
        dict(
            label=location,
            method='update',
            args=[
                {'visible': [False] * len(fig.data)},  # 모든 trace 비활성화
                {'title': f'{location}의 누적 백신 접종자 수와 월별 사망자 수'}
            ]
        )
    )
    dropdown_buttons[-1]['args'][0]['visible'][2 * i] = True  # 막대 그래프 활성화
    dropdown_buttons[-1]['args'][0]['visible'][2 * i + 1] = True  # 선 그래프 활성화

# 레이아웃 설정
fig.update_layout(
    title='지역별 누적 백신 접종자 수와 월별 사망자 수',
    xaxis=dict(title='월'),
    yaxis=dict(
        title='월별 사망자 수',
        titlefont=dict(color='red'),
        tickfont=dict(color='red')
    ),
    yaxis2=dict(
        title='누적 백신 접종자 수',
        titlefont=dict(color='blue'),
        tickfont=dict(color='blue'),
        overlaying='y',
        side='right'
    ),
    updatemenus=[
        dict(
            active=0,
            buttons=dropdown_buttons,
            direction='down',
            showactive=True
        )
    ],
    legend=dict(x=0.01, y=0.99),
    barmode='group'
)

# === 버블 차트

# 2020년 12월 이후의 데이터 필터링
covid_data = covid_data[covid_data['month'] >= '2020-12']

# 월별 데이터 계산
monthly_data = covid_data.groupby(['month', 'location'], as_index=False).agg({
    'new_deaths': 'sum',
    'people_vaccinated': 'last'
})

# Plotly 애니메이션 산점도 생성
fig_bubble = px.scatter(
    monthly_data,
    x='people_vaccinated',
    y='new_deaths',
    color='location',
    animation_frame='month',
    title='지역별 월별 사망자 수와 누적 백신 접종자 수',
    labels={'new_deaths': '월별 사망자 수', 'people_vaccinated': '누적 백신 접종자 수'},
    size='new_deaths',
    size_max=50
)

# y축의 최대값 설정
fig_bubble.update_xaxes(range=[monthly_data['people_vaccinated'].min() * -10**4, monthly_data['people_vaccinated'].max() * 1.1])
# fig_bubble.update_layoyt(page_bgcolor= "white", plot_bgcolor="white")

# Streamlit 앱 설정
st.title('COVID-19 대시보드')

# 위쪽 절반: 막대 + 선 그래프
st.plotly_chart(fig, use_container_width=True)

# 아래쪽 절반: 버블 차트
st.plotly_chart(fig_bubble, use_container_width=True)
