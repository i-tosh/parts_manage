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


# セッション状態の初期化
if 'df1' not in st.session_state:
    st.session_state.df1 = pd.read_csv("統合テーブル(予定の納期に減算).csv")

if 'df3' not in st.session_state:
    st.session_state.df3 = pd.read_csv("統合テーブル(納品日に減算).csv")
#    st.session_state.df3['棚卸フラグ'] = 0

if 'toroshi' not in st.session_state:
    st.session_state.toroshi = pd.read_csv("棚卸管理.csv")

tab1, tab2, tab3 = st.tabs(["納期確認", "発注","棚卸"])

with tab1:
    st.header("納期確認")


#    df = pd.read_csv("統合テーブル(予定の納期に減算).csv")

    parts_no = st.session_state.df1["製品番号"].unique().tolist()

    select = st.selectbox("製品番号", parts_no, key="selectbox_tab1")

    #st.write('選択された製品は',select)

    d = st.date_input(
        "受注日を入力してください",
        datetime.date(2021, 1, 1))
    day = d.strftime('%Y-%m-%d')
    #st.write('受注日:', day)

    zaiko =st.session_state.df1[st.session_state.df1['製品番号']==select ][['日付','在庫数']]
    zaiko =zaiko.reset_index(drop=True)
    idx = zaiko[zaiko['日付']==day].index[0]
    zaiko = zaiko[idx:]
    zaiko = zaiko.reset_index()

    zai = st.session_state.df1[(st.session_state.df1['製品番号'] == select) & (st.session_state.df1['日付']==day)]['在庫数'].iat[0]
    st.write('現在の在庫数:',zai)

    number = st.number_input('注文数を入力してください',step=1)
    #st.write('注文数: ', number)

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


    # スタイル関数を定義
    def highlight(row):
        if row['在庫数'] <= row['発注点']:
            return ['color: red', 'color: red']
        else:
            return ['', '']

    parts_list = st.session_state.df1[st.session_state.df1["日付"]=='2021-01-01'].loc[:,['製品番号','発注点']]
    #st.write(parts_list)

    st.caption('本来は今日の日付を自動認識')
    d2 = st.date_input(
        "本日の日付を入力してください",
        datetime.date(2021, 1, 1),key="selectbox_tab2")
    day2 = d2.strftime('%Y-%m-%d')
    #st.write('本日は', day2)
    #在庫数一覧を取得
    zaiko2 =st.session_state.df1[st.session_state.df1['日付']==day2][['製品番号','在庫数']]
    #同じ日に複数の受注があるので、その場合は一番下の行の在庫数を採用する
    zaiko2.reset_index( inplace=True,drop=True)
    #st.write(zaiko2)
        
    grouped = zaiko2.groupby('製品番号').apply(lambda x: x.index[-1])
    indices = grouped.tolist()
    zaiko2 = zaiko2.iloc[[i  for i in indices]]
    zaiko2 = pd.merge(zaiko2, parts_list)
    zaiko2 = zaiko2.reset_index(drop=True)
    st.divider()
    st.write('発注すべき製品を赤字表示しています。また発注管理欄は1となっているので発注が必要なものを素早く確認する際には発注管理欄の並びを変えて下さい')
    st.divider()
    zaiko2['発注管理'] = 0
    #発注が必要な場合は発注管理を1にする
    zaiko2.loc[zaiko2['在庫数'] <= zaiko2['発注点'], '発注管理'] = 1
    # DataFrameにスタイルを適用
    styled_df = zaiko2.style.apply(highlight, axis=1, subset=['在庫数', '発注点'])
    # Streamlitで表示
    st.dataframe(styled_df, width=350, hide_index = True)
    

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

    st.caption('本来は今日の日付を自動認識')
    d = st.date_input(
        "本日の日付を入力してください",
        datetime.date(2021, 1, 1))
    day = d.strftime('%Y-%m-%d')
    #st.write('本日は', day)

    zaiko =st.session_state.df3[st.session_state.df3['製品番号']==select ][['日付','在庫数']]
    idx2 = zaiko[zaiko['日付']==day].index[0]   #棚卸の結果はidx2に上書きする
    zai = st.session_state.df3[(st.session_state.df3['製品番号'] == select) & (st.session_state.df3['日付']==day)]['在庫数'].iat[0]

#    number = st.number_input("修正個数", min_value=0, value=zai, format="%d")
#    number = st.number_input("修正個数(Enterで確定)",  value=zai, format="%d")
#    st.write("idx2=",idx2)
    
    num = st.text_input('個数修正しない場合も棚卸ボタンをクリックしてください(棚卸ボタンで確定)', zai)
    try:
        number_dummy = int(num)
    except:
        st.error("整数を入力してください")
        number_dummy = zai
    
    if st.button('棚卸'):
        number = number_dummy
#        st.session_state.toroshi[st.session_state.toroshi['製品番号']==select ]['棚卸']=1
        idx_tana = st.session_state.toroshi[st.session_state.toroshi['製品番号']==select ].index[0]   #棚卸の結果はidx_tanaに上書きする
        st.session_state.toroshi.iat[idx_tana,1]=1
    else:
        number = zai

        
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
        #idx3 = zaiko[zaiko['日付']==day].index[0]   #idx3は直下の再計算範囲算出のみに使用
        tmp = zaiko.reset_index(drop=True)
        idx3 = tmp[tmp['日付']==day].index[0]

        calc_area = len(zaiko[idx3:])          #再計算する範囲
        endidx = idx2+calc_area
#        st.write(zaiko)
        
        #df1内の在庫数再計算
        zaiko =st.session_state.df1[st.session_state.df1['製品番号']==select ][['日付','在庫数']]
        idx21 = zaiko[zaiko['日付']==day].index[0]   #棚卸の結果はdf1のidx21に上書きする
#       st.write("idx21=",idx21)
        zai = st.session_state.df1[(st.session_state.df1['製品番号'] == select) & (st.session_state.df1['日付']==day)]['在庫数'].iat[0]
#        st.write("DF1のzai=",zai)
        if number > zai: #調整入庫
            st.session_state.df1.at[idx21,'調整入庫'] = number-zai
        else: #調整出庫
            st.session_state.df1.at[idx21,'調整出庫'] = zai -number

        #idx31 = zaiko[zaiko['日付']==day].index[0]   #idx3は直下の再計算範囲算出のみに使用
        tmp = zaiko.reset_index(drop=True)
        idx31 = tmp[tmp['日付']==day].index[0]
#        st.write("idx31=",idx31)
#        st.write("zaiko1")
#        st.write(zaiko[idx31:])
        
        calc_area = len(zaiko[idx31:])          #再計算する範囲
        endidx1 = idx21+calc_area
        for i in range(idx21, endidx1):
            if st.session_state.df1.loc[i,'日付'] != "2021-01-01":
                st.session_state.df1.loc[i,'在庫数'] = (
                    st.session_state.df1.loc[i-1,'在庫数'] 
                    + st.session_state.df1.loc[i,'通常入庫'] 
                    + st.session_state.df1.loc[i,'調整入庫'] 
                    - st.session_state.df1.loc[i,'調整出庫'] 
                    - st.session_state.df1.loc[i,'受注本数']
                )
            else:   #2021-01-01の例外処理
                st.session_state.df1.loc[i,'在庫数'] = (
                    st.session_state.df1.loc[i,'在庫数'] 
#                    + st.session_state.df1.loc[i,'通常入庫'] 
                    + st.session_state.df1.loc[i,'調整入庫'] 
                    - st.session_state.df1.loc[i,'調整出庫'] 
#                    - st.session_state.df1.loc[i,'受注本数']
                )
                
        #st.write(st.session_state.df1[idx21-5:idx21+5])
        
        #df3内の在庫数再計算
        for i in range(idx2, endidx):
            if st.session_state.df3.loc[i,'日付'] != "2021-01-01":
                st.session_state.df3.loc[i,'在庫数'] = (
                    st.session_state.df3.loc[i-1,'在庫数'] 
                    + st.session_state.df3.loc[i,'通常入庫'] 
                    + st.session_state.df3.loc[i,'調整入庫'] 
                    - st.session_state.df3.loc[i,'調整出庫'] 
                    - st.session_state.df3.loc[i,'納品本数']
                )
            else:   #2021-01-01の例外処理
                st.session_state.df3.loc[i,'在庫数'] = (
                    st.session_state.df3.loc[i,'在庫数'] 
#                    + st.session_state.df3.loc[i,'通常入庫'] 
                    + st.session_state.df3.loc[i,'調整入庫'] 
                    - st.session_state.df3.loc[i,'調整出庫'] 
#                    - st.session_state.df3.loc[i,'納品本数']
                )

            
#        st.write(st.session_state.df1[idx21-5:idx21+5])
#        st.write("calc_area=",calc_area)
#        st.write(st.session_state.df1[endidx1-5:endidx1+5])

#        st.write(st.session_state.df3[idx2-5:idx2+5])
#        st.write("calc_area=",calc_area)
#        st.write(st.session_state.df3[endidx-5:endidx+5])


    
    with st.expander("棚卸完了状況"):
        st.write('棚卸が完了した製品は棚卸欄が１になっています。棚卸未完了の製品を素早く確認する際には棚卸欄の並びを変えて下さい')
        st.dataframe(st.session_state.toroshi, width=200, hide_index = True)


