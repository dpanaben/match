# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 17:25:54 2024

@author: yeh1007
"""

import pymssql
import spacy

nlp = spacy.load("zh_core_web_lg")

server = 'CSCE1112002-03'
username = 'momouser'
password = 'M123456'
database = '20231119'
 
myConn = pymssql.connect(server, username, password, database) 
myCursor = myConn.cursor()

while True:
    user_input = input("\n請輸入一句话，例如：我想去日本玩、我肚子餓了（輸入'退出'以结束程序）：")
    if user_input == '退出':
        break

    user_doc = nlp(user_input)
    myCursor.execute("SELECT IntentName, Description FROM Intents")

    similarities = []

    for IntentName, Description in myCursor:
        description_doc = nlp(Description)
        similarity = user_doc.similarity(description_doc)
        similarities.append((IntentName, similarity))

    # 对相似度进行排序并取前五名
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_five = similarities[:5]

    # 显示相似度最高和其他四个系统的相似度
    print("\n相似度排名前五的系统：")
    for i, (IntentName, similarity) in enumerate(top_five, 1):
        print(f"-- {IntentName}，相似度: {similarity:.2f}")

    # 询问用户是否正确
    best_match = top_five[0][0] if top_five else None
    correct = input(f"\n相似度最高的系統是 {best_match}。是否是您想要的系統？(是/否)：")
    if correct.lower() == '是':
        print(f"馬上帶您往 {best_match} 前進\n")
        continue

    # 处理用户选择不同的系统
    myCursor.execute("SELECT Distinct IntentID, IntentName FROM Intents")
    intent_list = myCursor.fetchall()
    print("\n所有可用系統：")
    for intent in intent_list:
        print(f"{intent[0]}.{intent[1]}")

    selected_id = input("請選擇正確的 ID：")
    selected_id = int(selected_id)  # 确保输入为整数
    selected_name = next((intent[1] for intent in intent_list if intent[0] == selected_id), None)

    if selected_name:
        try:
            insert_query = "INSERT INTO Intents (IntentID, IntentName, Description) VALUES (%s, %s, %s)"
            myCursor.execute(insert_query, (selected_id, selected_name, user_input))
            myConn.commit()
            print("資料已更新，下次不會選錯囉！")
        except Exception as e:
            print(f"插入數據時發生錯誤：{e}")
    else:
        print("未找到選定的 IntentID.")

myCursor.close()
myConn.close()



