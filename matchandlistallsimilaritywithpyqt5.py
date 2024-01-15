import sys
import spacy
import pymssql
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QComboBox, QSplitter, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt

# 定義一個選擇對話框類，用於讓用戶從數據庫中選擇意圖
class SelectionDialog(QDialog):
    def __init__(self, db_connection, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.db_connection = db_connection  # 保存數據庫連接
        self.initUI()  # 初始化用戶界面

    def initUI(self):
        # 設置對話框標題和佈局
        self.setWindowTitle('選擇正確的系統')
        self.comboBox = QComboBox(self)  # 創建一個下拉列表
        self.populateComboBox()  # 填充下拉列表

        # 創建確定和取消按鈕
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)  # 綁定按鈕事件
        self.buttonBox.rejected.connect(self.reject)

        # 設置對話框佈局
        layout = QVBoxLayout(self)
        layout.addWidget(self.comboBox)
        layout.addWidget(self.buttonBox)

    def populateComboBox(self):
        # 從數據庫填充下拉列表
        self.comboBox.clear()
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT Distinct IntentID, IntentName FROM Intents")
        for intent in cursor.fetchall():
            self.comboBox.addItem(f"{intent[1]}", intent[0])  # 添加數據庫中的意圖

    def getSelectedIntent(self):
        # 獲取用戶選擇的意圖
        return self.comboBox.currentData(), self.comboBox.currentText()

# 定義主窗口類
class IntentFinderApp(QMainWindow):
    def __init__(self, nlp_model, db_connection):
        super().__init__()
        self.nlp_model = nlp_model  # NLP模型
        self.db_connection = db_connection  # 數據庫連接
        self.initUI()  # 初始化用戶界面

    def initUI(self):
        # 設置窗口標題和大小
        self.setWindowTitle('Intent Finder')
        self.setGeometry(100, 100, 1000, 400)

        # 創建上半部分用戶輸入區域
        topWidget = QWidget()
        topLayout = QVBoxLayout(topWidget)
        self.textEdit = QTextEdit()  # 文本輸入框
        self.textEdit.setPlaceholderText("請輸入一句話，例如：我想去日本玩、我肚子餓了")
        self.textEdit.setStyleSheet("color: white; background-color: #0057b7; font-size: 14pt;")
        self.analyzeBtn = QPushButton('分析')  # 分析按鈕
        self.analyzeBtn.setStyleSheet("font-size: 14pt; background-color: pink;")  
        self.analyzeBtn.clicked.connect(self.analyzeText)  # 綁定按鈕事件
        topLayout.addWidget(self.textEdit)
        topLayout.addWidget(self.analyzeBtn)
        

        # 創建下半部分用於顯示系統回應
        bottomWidget = QWidget()
        bottomLayout = QVBoxLayout(bottomWidget)
        self.resultText = QTextEdit()  # 用於顯示結果的文本框
        self.resultText.setReadOnly(True)
        self.resultText.setStyleSheet("color: black; background-color: #ffd700; font-size: 14pt;")
        bottomLayout.addWidget(self.resultText)

        # 使用分割器分割上下兩部分
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(topWidget)
        splitter.addWidget(bottomWidget)
        splitter.setSizes([50, 250])

        self.setCentralWidget(splitter)

    def analyzeText(self):
        # 處理文本分析按鈕點擊
        user_input = self.textEdit.toPlainText()
        if user_input:
            self.user_input = user_input
            response = self.processInput(user_input)
            self.resultText.setText(response)
            self.confirmIntent()  # 自動調用確認方法

    def confirmIntent(self):
        # 確認意圖
        if self.top_five:
            best_match = self.top_five[0][0]
            reply = QMessageBox.question(self, '確認', f'相似度最高的系統是 {best_match}。是否是您想要的系統？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.resultText.append(f"\n沒問題，帶您去 {best_match}！")
                self.textEdit.clear()  # 清空輸入區域
            else:
                self.showSelectionDialog()  # 展示選擇對話框

    def showSelectionDialog(self):
        # 顯示選擇對話框
        dialog = SelectionDialog(self.db_connection, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_id, selected_name = dialog.getSelectedIntent()
            self.submitChoice(selected_id, selected_name)

    def submitChoice(self, selected_id, selected_name):
        # 提交用戶的選擇
        cursor = self.db_connection.cursor()
        try:
            insert_query = "INSERT INTO Intents (IntentID, IntentName, Description) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (selected_id, selected_name, self.user_input))
            self.db_connection.commit()
            self.resultText.append("資料已更新，下次不會選錯囉！")
        except Exception as e:
            self.resultText.append(f"插入數據時發生錯誤：{e}")

    def processInput(self, user_input):
        # 處理用戶輸入
        user_doc = self.nlp_model(user_input)
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT IntentName, Description FROM Intents")

        similarities = []

        for IntentName, Description in cursor:
            description_doc = self.nlp_model(Description)
            similarity = user_doc.similarity(description_doc)
            similarities.append((IntentName, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        self.top_five = similarities[:5]

        result_str = "\n相似度排名前五的系统：\n"
        for i, (IntentName, similarity) in enumerate(self.top_five, 1):
            result_str += f"-- {IntentName}，相似度: {similarity:.2f}\n"
        return result_str

# 創建 NLP 模型和數據庫連接
nlp_model = spacy.load("zh_core_web_lg")
db_connection = pymssql.connect('CSCE1112002-03', 'momouser', 'M123456', '20231119')

# 啟動應用程序
app = QApplication(sys.argv)
ex = IntentFinderApp(nlp_model, db_connection)
ex.show()
sys.exit(app.exec_())
