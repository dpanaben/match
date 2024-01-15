# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 20:54:18 2024

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

    best_match = None
    highest_similarity = 0

    for IntentName, Description in myCursor:
        description_doc = nlp(Description)
        similarity = user_doc.similarity(description_doc)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = IntentName

    if best_match:
        print(f"\n相似度最高的系統: {best_match}，相似度: {highest_similarity}")
        correct = input("是否是您想要的系統？(是/否)：")
        if correct.lower() == '是':
            print(f"馬上帶您往 {best_match} 前進")
            continue
        else:
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
    else:
        print("\n没有找到匹配的系統。")

myCursor.close()
myConn.close()




