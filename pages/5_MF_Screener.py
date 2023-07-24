import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.optimize import minimize
from scipy import optimize
import random
import math
from shared_functions import *

st.set_page_config(
    page_title="GroWealth Investments       ",
    page_icon="nirvana.ico",
    layout="wide",
)


np.set_printoptions(precision=3)

tday = dt.datetime.today()

st.markdown(
    """
    <style>
    .css-k1vhr4 {
        margin-top: -60px;
    }


    </style>
    """,
    unsafe_allow_html=True
)
c_1, c_2 = st.columns((8,4))


st.markdown(
    """
    <style>
    .css-k1vhr4 {
        margin-top: -60px;
    }


    .css-vk3wp9.e1akgbir11 {
        display: none !important;
    }

    .css-vk3wp9.eczjsme11 {
        display: none !important;
    }

    .css-vk3wp9 {
        display: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data()
def get_perf_data():


    df_mf_perf = pd.read_csv('revised_mf_perf.csv')
    df_mf_perf.set_index('Scheme_Code', inplace=True)

    df_mf_perf['Expense'] = df_mf_perf['Expense'].apply(lambda x: float(x.replace('%','')))
    df_mf_perf['Pos_Year%']=df_mf_perf['Pos_Year%'].apply(lambda x: float(x))
    df_mf_perf['NumStocks']=df_mf_perf['NumStocks'].apply(lambda x: float(x))
    df_mf_perf['Top5_Pct']=df_mf_perf['Top5_Pct'].apply(lambda x: float(x.replace('%','')) if isinstance(x, str) else np.nan)
    df_mf_perf['Top10_Pct']=df_mf_perf['Top10_Pct'].apply(lambda x: float(x.replace('%','')) if isinstance(x, str) else np.nan )
    df_mf_perf['Top3_Sector']=df_mf_perf['Top3_Sector'].apply(lambda x: float(x.replace('%','')) if isinstance(x, str) else np.nan )
    df_mf_perf['Equity_Holding']=df_mf_perf['Equity_Holding'].apply(lambda x: float(x))
    df_mf_perf['F&O_Holding']=df_mf_perf['F&O_Holding'].apply(lambda x: float(x))
    df_mf_perf['Foreign_Holding']=df_mf_perf['Foreign_Holding'].apply(lambda x: float(x))

    df_filter = pd.read_csv('filter.csv')
    df_filter.set_index('Filter_Label', inplace=True)

    return df_mf_perf, df_filter


def get_html_table_scroll(data, header='Y'):
    if header == 'Y':

        cols = data.columns
        ncols = len(cols)

        html_script = "<style> .tableFixHead {overflow-y: auto; height: 500px;}"
        html_script = html_script + ".tableFixHead thead th {position: sticky; top: 0px;}"
        html_script = html_script + "table {border-collapse: collapse; width: 100%;}"
        html_script = html_script + "th, td {padding: 8px 16px; border: 1px solid #cc} th {background: #eee;}"
        html_script = html_script + "tr:nth-child(even) {background-color: #f2f2f2;}</style>"
        html_script = html_script + '<div class="tableFixHead"><table><thead>'
        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Red; font-size:12px;'>"

        for i in cols:
            if i in ['Scheme_Name','Scheme_Category','Fund_House']:
                html_script = html_script + "<th style='text-align:left;background-color: #ffebcc;'>{}</th>".format(i)
            else:
                html_script = html_script + "<th style='text-align:center;background-color: #ffebcc;'>{}</th>".format(i)

    html_script = html_script + "</tr></thead><tbody>"
    for j in data.index:
        #url_link = "http://localhost:8501/MutualFund_Ready_Reckoner?id={}".format(j)
        url_link = "http://gro-wealth.streamlit.app/MutualFund_Ready_Reckoner?id={}".format(j)


        html_script = html_script + "<tr style='border:none;font-family:Courier; color:Blue; font-size:10px;'>"
        a = data.loc[j]
        for k in cols:
            if k in ['Rel_MaxDD','Prob_10Pct','NIFTY_CORR']:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(round(a[k],2))
            elif k in ['Scheme_Category','Fund_House']:
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'>{}</td>".format(a[k])
            elif k == 'Scheme_Name':
                html_script = html_script + "<td style='padding:2px;text-align:left' rowspan='1'><a href={} target='_self'>{}</a></td>".format(url_link,a[k])
            else:
                html_script = html_script + "<td style='padding:2px;text-align:center' rowspan='1'>{}</td>".format(a[k])




    html_script = html_script + '</tbody></table>'

    return html_script

def plot_chart(df_chart,chart_x_axis,chart_y_axis,chart_color,chart_size):
    if len(df_chart) > 0:
        fig = px.scatter(df_chart, x=df_chart[chart_x_axis], y=df_chart[chart_y_axis], color=df_chart[chart_color],
                         size=df_chart[chart_size], size_max=25, hover_name=df_chart['Scheme_Name'], color_continuous_scale='plasma')

        y_spread = df_chart[chart_y_axis].max() - df_chart[chart_y_axis].min()
        yrange = [df_chart[chart_y_axis].min() - 0.1 * y_spread, df_chart[chart_y_axis].max() + 0.1 * y_spread]
        # fig.update_xaxes(type=[])
        fig.update_yaxes(range=yrange)
        fig.update_layout(title_text="Fund Performance Snapshot",
                      title_x=0.3,
                      title_font_size=30,
                      titlefont=dict(size=20, color='blue', family='Arial, sans-serif'),
                      xaxis_title=dict(text=chart_x_axis, font=dict(size=16, color='#C7004E')),
                      yaxis_title=dict(text=chart_y_axis, font=dict(size=16, color='#C7004E'))
                      )

        fig.update_layout(margin=dict(l=1,r=1,b=1,t=45))
        fig.update_layout(height=500)
        fig.update_layout(width=650)
        fig.update_layout(legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01)
                        )


        return fig
    else:
        return False



def get_filtered_df(df_chart, df_filter, filter_attr, filter_condition, filter_value):

    filter_df_col_name = df_filter[df_filter.index == filter_attr]['Column_Name'].iloc[0]

    if filter_attr == 'Crisil Rating':
        if filter_condition == 'IN':
            df_filtered = df_chart[df_chart[filter_df_col_name].isin(filter_value)]
        else:
            df_filtered = df_chart[~df_chart[filter_df_col_name].isin(filter_value)]
    else:

        if filter_condition == 'Less Than':
            df_filtered = df_chart[df_chart[filter_df_col_name] < filter_value]
        elif filter_condition == 'Less or Equals':
            df_filtered = df_chart[df_chart[filter_df_col_name] <= filter_value]
        elif filter_condition == 'Equals':
            df_filtered = df_chart[df_chart[filter_df_col_name] == filter_value]
        elif filter_condition == 'Not Equals':
            df_filtered = df_chart[df_chart[filter_df_col_name] != filter_value]
        elif filter_condition == 'Greater or Equals':
            df_filtered = df_chart[df_chart[filter_df_col_name] >= filter_value]
        elif filter_condition == 'Greater Than':
            df_filtered = df_chart[df_chart[filter_df_col_name] > filter_value]

    return df_filtered


df, df_filter = get_perf_data()
#st.write(df.columns)

st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px">MF Screener</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:36px;font-weight: bold;text-align:center;vertical-align:middle;color:blue;margin:0px;padding:0px"></p>', unsafe_allow_html=True)

st.markdown('<BR>',unsafe_allow_html=True)
st.markdown('<BR>',unsafe_allow_html=True)

left,right = st.columns((13,16))

fh_list = [x for x in df['Fund_House'].unique()]

left.markdown("**:blue[Fund House]**")
fh_option = left.multiselect("Select Fund House", fh_list, label_visibility="collapsed")

screen_layout = st.columns((6,2,6))
if len(fh_option) == 0:
    df_1 = df
else:
    df_1 = df[df['Fund_House'].isin(fh_option)]





sch_cat_list = [x for x in df_1['Scheme_Category'].unique()]
right.markdown("**:blue[Scheme Category]**")
sch_cat_option = right.multiselect("Select Fund Category", sch_cat_list, label_visibility="collapsed")
if len(sch_cat_option) > 0:
    df_2 = df_1[df_1['Scheme_Category'].isin(sch_cat_option)]
else:
    df_2 = df_1



chart_cols = ['Scheme_Name','AUM','Age','Sharpe Ratio','Volatility','1Y Ret','3Y Ret','Expense']
display_columns = ['Scheme_Name','Scheme_Category','Fund_House','Expense', 'AUM', 'CrisilRank', 'Age', '3M Ret', \
                   '1Y Ret','3Y Ret', '5Y Ret', 'Ret Inception', 'Sharpe Ratio', 'Sortino Ratio', 'Pos_Year%',   \
                   'Volatility', 'Rel_MaxDD','Roll_Ret_1Y', 'Roll_Ret_3Y', 'Roll_Ret_Inception', 'Prob_10Pct',   \
                   'NumStocks', 'Top5_Pct', 'Top10_Pct', 'Top3_Sector','Equity_Holding', 'F&O_Holding', \
                   'Foreign_Holding', 'GT_1PCT','GT_3PCT', 'GT_5PCT', 'LT_NEG_1PCT', 'LT_NEG_3PCT', 'LT_NEG_5PCT',  \
                   'POS_PCT', 'NIFTY_CORR', 'PCT_GT_NIFTY']
basic_columns = ['Scheme_Name','Scheme_Category','Fund_House']
config_columns = ['Expense', 'AUM', 'CrisilRank', 'Age', '3M Ret', \
                   '1Y Ret','3Y Ret', '5Y Ret', 'Ret Inception', 'Sharpe Ratio', 'Sortino Ratio', 'Pos_Year%',   \
                   'Volatility', 'Rel_MaxDD','Roll_Ret_1Y', 'Roll_Ret_3Y', 'Roll_Ret_Inception', 'Prob_10Pct',   \
                   'NumStocks', 'Top5_Pct', 'Top10_Pct', 'Top3_Sector','Equity_Holding', 'F&O_Holding', \
                   'Foreign_Holding', 'GT_1PCT','GT_3PCT', 'GT_5PCT', 'LT_NEG_1PCT', 'LT_NEG_3PCT', 'LT_NEG_5PCT',  \
                   'POS_PCT', 'NIFTY_CORR', 'PCT_GT_NIFTY']

#df_chart = df_2[chart_cols]

df_chart = df_2



#df_chart['AUM'] = df_chart['AUM'].apply(lambda x: float(str(x).replace(",","")))

#st.write(df_chart)





#placeholder_chart = st.empty()
#fig = plot_chart(df_chart)
#placeholder_chart.plotly_chart(fig, use_container_width=True)

crisil_option = ['1 Star', '3 Stars', '2 Stars', '4 Stars', '5 Stars', 'Not Rated']
operator_list = ['Less Than','Less or Equals','Equals','Not Equals','Greater or Equals','Greater Than']

left,centre, right = st.columns((8,5,16))
left.markdown("**:blue[Filter Criteria]**")
centre.markdown("**:blue[Condition]**")
right.markdown("**:blue[Value]**")

filter_list1 = [x for x in df_filter.index]

filter_1 = left.selectbox("Filter 1", filter_list1, 0, label_visibility="collapsed")
filter_1_col = df_filter[df_filter.index == filter_1]['Column_Name'].iloc[0]


if filter_1 != 'Crisil Rating':
    filter_min_value_1 = df_filter[df_filter.index == filter_1]['Min_Value'].iloc[0]
    filter_max_value_1 = df_filter[df_filter.index == filter_1]['Max_Value'].iloc[0]
    filter_step_value_1 = df_filter[df_filter.index == filter_1]['Steps'].iloc[0]

    operator_1 = centre.selectbox('Operator_1',operator_list,0,label_visibility="collapsed")
    filter_1_value = right.number_input("Value_1",min_value=filter_min_value_1, max_value=filter_max_value_1, step=filter_step_value_1, value=filter_max_value_1, label_visibility="collapsed")

else:
    operator_1 = centre.selectbox('Operator_1',('IN','NOT IN'),0,label_visibility="collapsed")
    filter_1_value = right.multiselect("Value_1",crisil_option, default=crisil_option,label_visibility="collapsed")

    if len(filter_1_value) == 0:
        filter_1_value = crisil_option

df_filter_1 = get_filtered_df(df_2,df_filter,filter_1,operator_1,filter_1_value)

filter_2 = left.selectbox("Filter 2", filter_list1, 1, label_visibility="collapsed")
filter_2_col = df_filter[df_filter.index == filter_2]['Column_Name'].iloc[0]

if filter_2 != 'Crisil Rating':
    filter_min_value_2 = df_filter[df_filter.index == filter_2]['Min_Value'].iloc[0]
    filter_max_value_2 = df_filter[df_filter.index == filter_2]['Max_Value'].iloc[0]
    filter_step_value_2 = df_filter[df_filter.index == filter_2]['Steps'].iloc[0]

    operator_2 = centre.selectbox('Operator_2',operator_list,0,label_visibility="collapsed")
    filter_2_value = right.number_input("Value_2",min_value=filter_min_value_2, max_value=filter_max_value_2, step=filter_step_value_2, value=filter_max_value_2, label_visibility="collapsed")

else:
    operator_2 = centre.selectbox('Operator_2',('IN','NOT IN'),0,label_visibility="collapsed")
    filter_2_value = right.multiselect("Value_1",crisil_option, default=crisil_option,label_visibility="collapsed")

    if len(filter_2_value) == 0:
        filter_2_value = crisil_option

#st.write(df_filter_1)
if len(df_filter_1) > 0:
    df_filter_2 = get_filtered_df(df_filter_1,df_filter,filter_2,operator_2,filter_2_value)
else:
    df_filter_2 = df_filter_1

#st.write(df_filter_2)



st.markdown('<BR>',unsafe_allow_html=True)
st.markdown('<BR>',unsafe_allow_html=True)




ch_1, ch_2 = st.columns((4,16))

ch_1.markdown('<BR><BR>',unsafe_allow_html=True)
ch_1.markdown("**:blue[Configure X-Axis]**")
chart_x_axis = ch_1.selectbox('chart_x_axis',['Volatility','NumStocks'],0,label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Y-Axis]**")
chart_y_axis = ch_1.selectbox('chart_y_axis',['3M Ret','1Y Ret','3Y Ret', '5Y Ret', 'Ret Inception','Roll_Ret_1Y', 'Roll_Ret_3Y', 'Roll_Ret_Inception'],0,label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Colour]**")
chart_color = ch_1.selectbox('chart_color',['Sharpe Ratio', 'Sortino Ratio','Expense'],0,label_visibility="collapsed")
ch_1.markdown('<BR>',unsafe_allow_html=True)

ch_1.markdown("**:blue[Configure Size]**")
chart_size = ch_1.selectbox('chart_size',['AUM', 'Age'],0,label_visibility="collapsed")


ch_2.markdown('<BR>',unsafe_allow_html=True)


fig = plot_chart(df_filter_2,chart_x_axis,chart_y_axis,chart_color,chart_size)
placeholder_chart = ch_2.empty()

if fig:
    placeholder_chart.plotly_chart(fig, use_container_width=True)
else:
    placeholder_chart.empty()



df_filter_2 = df_filter_2.sort_values([filter_1_col,filter_2_col])

basic_columns = [ 'Scheme_Name','Scheme_Category','Fund_House', filter_1_col, filter_2_col,chart_x_axis,chart_y_axis,chart_color, chart_size]
#if len(report_columns) == 0:
#    report_columns = config_columns

config_columns = [x for x in config_columns if x not in basic_columns]


st.markdown("""---""")
st.markdown('<BR>',unsafe_allow_html=True)

st.markdown("**:blue[Configure Report Columns]**")
report_columns = st.multiselect("Report_Columns",config_columns, label_visibility="collapsed")




final_report_columns = basic_columns + report_columns

final_report_columns = list(dict.fromkeys(final_report_columns))

#final_report_columns = np.unique(final_report_columns)

html_text = get_html_table_scroll(df_filter_2[final_report_columns])

st.markdown(html_text, unsafe_allow_html=True)

#st.write(df_filter_1[display_columns])


notice_txt = '<p><BR><BR><span style="font-family: Verdana, Geneva, sans-serif; font-size: 10px;">'
notice_txt = notice_txt + '<span style="color: rgb(255,0,20);">Note:Market Data as on 20th July 2023</span>'
st.markdown(notice_txt,unsafe_allow_html=True)
