# 基本ライブラリ
import streamlit as st
import numpy as np
import pandas as pd
import datetime

st.title("製品管理システム")

tab1, tab2, tab3 = st.tabs(["受注", "発注","棚卸"])

with tab1:
    st.header("受注")


    df = pd.read_csv("data.csv")

    parts_no = df["製品番号"].unique().tolist()

    select = st.selectbox("部品番号", parts_no)

    st.write('選択された製品は',select)

    d = st.date_input(
        "受注日を入力してください",
        datetime.date(2021, 1, 1))
    day = d.strftime('%Y-%m-%d')
    st.write('受注日:', day)


    zaiko =df[df['製品番号']==select ][['日付','在庫数']]
    zaiko = zaiko.set_index('日付')

    zai = df[(df['製品番号'] == select) & (df['日付']==day)]['在庫数'].iat[0]
    st.write('現在の在庫数:',zai)


    number = st.number_input('注文数を入力してください',step=1)
    st.write('注文数: ', number)

    if(number != 0):
        if(number <= zai):
            st.success('即納可能')
        else:
            st.error('在庫不足')

    with st.expander("年間の在庫数推移(参考資料)"):
        st.line_chart(zaiko)

with tab2:
    st.header("発注")


with tab3:
    st.header("棚卸")
