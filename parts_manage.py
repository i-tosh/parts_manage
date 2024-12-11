# 基本ライブラリ
import streamlit as st
import numpy as np
import pandas as pd
import datetime

#デプロイボタンを非表示
st.markdown("""
<style>
.stAppDeployButton {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

#右上のメニューを非表示
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
.stDeployButton {display:none;}
footer {visibility: hidden;}
#stDecoration {display:none;}
.reportview-container {margin-top: -2em;}
</style>
""", unsafe_allow_html=True)

st.title("製品管理システム")

# CSVからDataFrameを読み込む
#@st.cache_data
#def load_data(file):
#    return pd.read_csv(file)

# セッション状態の初期化
if 'df1' not in st.session_state:
    st.session_state.df1 = pd.read_csv("統合テーブル(予定の納期に減算).csv")

if 'df3' not in st.session_state:
    st.session_state.df3 = pd.read_csv("統合テーブル(納品日に減算).csv")
    st.session_state.df3['棚卸フラグ'] = 0

tab1, tab2, tab3 = st.tabs(["納期確認", "発注","棚卸"])

with tab1:
    st.header("納期確認")


#    df = pd.read_csv("統合テーブル(予定の納期に減算).csv")

    parts_no = st.session_state.df1["製品番号"].unique().tolist()

    select = st.selectbox("製品番号", parts_no, key="selectbox_tab1")

    st.write('選択された製品は',select)

    d = st.date_input(
        "受注日を入力してください",
        datetime.date(2021, 1, 1))
    day = d.strftime('%Y-%m-%d')
    st.write('受注日:', day)

    zaiko =st.session_state.df1[st.session_state.df1['製品番号']==select ][['日付','在庫数']]
    zaiko =zaiko.reset_index(drop=True)
    idx = zaiko[zaiko['日付']==day].index[0]
    zaiko = zaiko[idx:]
    zaiko = zaiko.reset_index()

    zai = st.session_state.df1[(st.session_state.df1['製品番号'] == select) & (st.session_state.df1['日付']==day)]['在庫数'].iat[0]
    st.write('現在の在庫数:',zai)

    number = st.number_input('注文数を入力してください',step=1)
    st.write('注文数: ', number)

    if(number != 0):
        if(number <= zai):
            st.success('即納可能')
        else:
            #直近で納品可能になる日を検索
            zaiko['納品可能'] = (zaiko['在庫数'] - number) >= 0
            position = zaiko['納品可能'].idxmax()
            if position > 0:
                st.write('直近の納品可能になる入庫予定日は',zaiko.iat[position, 1],'です')
            else:
                st.error('直近で納品可能になる入庫予定はありません')
            st.error('在庫不足(製品の発注処理が必要です)')

    with st.expander("今後の在庫数推移予想(参考資料)"):
        st.line_chart(zaiko, x='日付', y ='在庫数')

with tab2:
    st.header("発注")



with tab3:
    st.header("棚卸")
    
    def insrt_row(df, pos, row):
        # データフレームを分割
        df1 = df.iloc[:pos]
        df2 = df.iloc[pos:]
        # 分割したデータフレームと新しい行を結合
        df_result = pd.concat([df1, row, df2]).reset_index(drop=True)
        return df_result
        
#    def calc_zaiko(df,stidx,endidx):
        #指定されたインデックス間で入出庫データに基づき在庫数の再計算を行う
        

    parts_no3 = st.session_state.df3["製品番号"].unique().tolist()
    select = st.selectbox("製品番号", parts_no3, key="selectbox_tab3")
    st.write('選択された製品は',select)

    st.write('本来は今日の日付を自動認識')
    d = st.date_input(
        "本日の日付を入力してください",
        datetime.date(2021, 1, 1))
    day = d.strftime('%Y-%m-%d')
    st.write('本日は', day)

    zaiko =st.session_state.df3[st.session_state.df3['製品番号']==select ][['日付','在庫数']]
    idx2 = zaiko[zaiko['日付']==day].index[0]   #棚卸の結果はidx2に上書きする
    zai = st.session_state.df3[(st.session_state.df3['製品番号'] == select) & (st.session_state.df3['日付']==day)]['在庫数'].iat[0]

    number = st.number_input("修正個数", min_value=0, value=zai, format="%d")
    #st.write("idx2=",idx2)
    #st.write("tana=",st.session_state.df3.loc[idx2].to_frame().T)
    if number != zai:   #棚卸の実行
        ##tana =st.session_state.df3.loc[idx2].to_frame().T
        #tana['棚卸フラグ'] = 1
        st.session_state.df3.at[idx2,'棚卸フラグ'] = 1
        if number > zai: #調整入庫
            st.session_state.df3.at[idx2,'調整入庫'] = number-zai
        else: #調整出庫
            st.session_state.df3.at[idx2,'調整出庫'] = zai -number
        
        zaiko =zaiko.reset_index(drop=True)
        idx3 = zaiko[zaiko['日付']==day].index[0]   #idx3は直下の再計算範囲算出のみに使用
        calc_area = len(zaiko[idx3:])          #再計算する範囲
        endidx = idx2+calc_area
        
        #df1内の在庫数再計算
        zaiko =st.session_state.df1[st.session_state.df1['製品番号']==select ][['日付','在庫数']]
        idx21 = zaiko[zaiko['日付']==day].index[0]   #棚卸の結果はidx21に上書きする
        zai = st.session_state.df1[(st.session_state.df1['製品番号'] == select) & (st.session_state.df1['日付']==day)]['在庫数'].iat[0]
#        st.write("DF1のzai=",zai)
        if number > zai: #調整入庫
            st.session_state.df1.at[idx21,'調整入庫'] = number-zai
        else: #調整出庫
            st.session_state.df1.at[idx21,'調整出庫'] = zai -number

        idx31 = zaiko[zaiko['日付']==day].index[0]   #idx3は直下の再計算範囲算出のみに使用
        calc_area = len(zaiko[idx31:])          #再計算する範囲
        endidx1 = idx2+calc_area
        for i in range(idx21, endidx1):
            st.session_state.df1.loc[i,'在庫数'] = (
                st.session_state.df1.loc[i-1,'在庫数'] 
                + st.session_state.df1.loc[i,'通常入庫'] 
                + st.session_state.df1.loc[i,'調整入庫'] 
                - st.session_state.df1.loc[i,'調整出庫'] 
                - st.session_state.df1.loc[i,'受注本数']
            )

        
        #df3内の在庫数再計算
        for i in range(idx2, endidx):
            st.session_state.df3.loc[i,'在庫数'] = (
                st.session_state.df3.loc[i-1,'在庫数'] 
                + st.session_state.df3.loc[i,'通常入庫'] 
                + st.session_state.df3.loc[i,'調整入庫'] 
                - st.session_state.df3.loc[i,'調整出庫'] 
                - st.session_state.df3.loc[i,'納品本数']
            )
            
#        st.write(st.session_state.df1[idx21-5:idx21+5])
#        st.write("calc_area=",calc_area)
#        st.write(st.session_state.df1[endidx1-5:endidx1+5])

    zai = number
    st.write('現在の在庫数:',zai)


