# 基本ライブラリ
import streamlit as st
import numpy as np
import pandas as pd
import datetime

st.title("製品管理システム")

df = pd.read_csv("data.csv")

parts_no = df["製品番号"].unique().tolist()

select = st.selectbox("部品番号", parts_no)

st.write('選択された製品は',select)

d = st.date_input(
    "受注日を入力してください",
    datetime.date(2021, 1, 1))
day = d.strftime('%Y-%m-%d')
#st.write(type(d))
st.write('受注日:', day)

#zaiko =df[df['製品番号']==select ,"在庫数"]
zaiko =df[df['製品番号']==select ][['日付','在庫数']]
zaiko = zaiko.set_index('日付')

zai = df[(df['製品番号'] == select) & (df['日付']==day)]['在庫数'].iat[0]
#st.write('現在の在庫数:',df[(df['製品番号'] == select) & (df['日付']==day)]['在庫数'])
st.write('現在の在庫数:',zai)

#st.line_chart(zaiko,x='日付',y='在庫数')
st.line_chart(zaiko)


number = st.number_input('注文数を入力してください',step=1)
st.write('The current number is ', number)

if(number <= zai):
    st.write('即納可能')
else:
    st.write('在庫不足')