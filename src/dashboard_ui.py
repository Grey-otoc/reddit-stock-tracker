from datetime import datetime, timedelta, timezone
from db_queries import get_tickers_by_mention_count, get_mentions_by_ticker
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QListView, QComboBox, 
    QStackedWidget, QPushButton
)
from PySide6.QtCore import Qt, QAbstractListModel
import sys
import webbrowser

'''
creates a main window object with a simplistic UI, allowing for visualisation of
ticker mention trends in a range of different timeframes
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RST by grey-otoc")
        self.setup_window_geometry()
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.main_page_container = QWidget()
        self.layout = QVBoxLayout(self.main_page_container)
        self.stack.addWidget(self.main_page_container)
        
        self.init_title()
        self.init_timeframe_menu()
        self.init_ticker_ranking_list()
    
    def setup_window_geometry(self):
        screen = QApplication.primaryScreen()
        # available geometry ensures that toolbar and taskbar are accounted for
        # in width and height calculations
        usable_rect = screen.availableGeometry()
        
        width = usable_rect.width() // 2
        height = usable_rect.height()
        x = usable_rect.x() + width
        y = usable_rect.y()
        
        self.setGeometry(x, y, width, height)
    
    def init_title(self):
        self.title = QLabel("Reddit Stock Tracker")
        
        font = self.title.font()
        font.setPointSize(30)
        font.setBold(True)
        
        self.title.setFont(font)
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def init_ticker_ranking_list(self):
        self.ticker_rank_list = QListView()
        self.ticker_rank_list.setEditTriggers(QListView.NoEditTriggers)
        self.ticker_rank_list.clicked.connect(self.open_ticker_detail)
        
        self.ticker_rank_list.setStyleSheet("""
            QListView {
                background-color: #3B0D05;
                border: 3px solid #3B0D05;
                border-radius: 10px;
                font-weight: bold;
                font-size: 24px;
                outline: none;
                selection-background-color: transparent;
            }
            QListView::item { padding: 15px; }
            QListView::item:hover {
                background: #250d05; 
                border-radius: 10px;
            }
        """)
        
        self.ticker_rank_model = CenteredListModel()
        
        # set string list for ticker ranking list with default timeframe of last 24 hours
        self.new_timeframe_selected("Last Hour")
        
        self.ticker_rank_list.setModel(self.ticker_rank_model)
        
        self.layout.addWidget(self.ticker_rank_list)
        
    def init_timeframe_menu(self):
        self.timeframe_filter_menu = QComboBox()
        
        # combobox-popup gets rid of the default box around the QAbstractItemView
        # (aka the dropdown list)
        self.timeframe_filter_menu.setStyleSheet("""
            QComboBox {
                background-color: #3B0D05;
                color: white;
                border: 3px solid #3B0D05;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                font-weight: bold;
                combobox-popup: 0;
            }

            QComboBox:hover {
                background-color: #250d05;
            }
            
            QComboBox QAbstractItemView {
                background-color: #3B0D05;
                color: white;
                border-radius: 10px;
                padding: 10px;
                selection-background-color: transparent;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background: #250d05;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        
        options = ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last Month", "Last Year", "All Time"]
        self.timeframe_filter_menu.addItems(options)
        
        self.timeframe_filter_menu.currentTextChanged.connect(self.new_timeframe_selected)
        
        self.layout.addWidget(self.timeframe_filter_menu)
        
    def new_timeframe_selected(self, new_selection: str):
        if new_selection == "All Time":
            mentions_since = 0.0
        else:
            time_map = {
                "Last Hour": timedelta(hours=1),
                "Last 24 Hours": timedelta(days=1),
                "Last 7 Days": timedelta(weeks=1),
                "Last Month": timedelta(days=31),
                "Last Year": timedelta(days=365)
            }
            time_to_subtract = time_map.get(new_selection)
            target_time = (datetime.now(timezone.utc) - time_to_subtract)
            mentions_since = target_time.timestamp()
            
        ranked_tickers = get_tickers_by_mention_count(mentions_since)
        ranked_tickers_str = []
        
        for ticker in ranked_tickers:
            symbol = ticker[0]
            mentions = ticker[1]
            plural_check = "time" if mentions == 1 else "times"
            
            ranked_tickers_str.append(f"${symbol}: Mentioned {mentions} {plural_check}")
        
        if not ranked_tickers_str:
            ranked_tickers_str = ["Nothing to display in this timeframe."]
        
        self.ticker_rank_model.setStringList(ranked_tickers_str)
        
    def open_ticker_detail(self, index):
        text = index.data()
        
        if text == "Nothing to display in this timeframe.":
            return
        
        detail_page = self.create_ticker_detail_page(text)
        self.stack.addWidget(detail_page)
        self.stack.setCurrentWidget(detail_page)
    
    def create_ticker_detail_page(self, text: str) -> QWidget:
        detail_page = QWidget()
        layout = QVBoxLayout(detail_page)
        
        text = text.split(":")
        ticker_symbol = text[0]
        title = QLabel(f"All Mentions For: {ticker_symbol}")
        font = title.font()
        font.setPointSize(30)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B0D05;
                border: 3px solid #3B0D05;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 10px;
            }
            
            QPushButton::hover {
                background-color: #250d05;
            }
        """)
        
        list_of_mentions = QListView()
        list_of_mentions.setEditTriggers(QListView.NoEditTriggers)
        list_of_mentions.clicked.connect(self.open_post_url)
        list_of_mentions.setStyleSheet("""
            QListView {
                background-color: #3B0D05;
                border: 3px solid #3B0D05;
                border-radius: 10px;
                font-weight: bold;
                font-size: 22px;
                outline: none;
                selection-background-color: transparent;
            }
            QListView::item { padding: 15px; }
            QListView::item:hover {
                background: #250d05; 
                border-radius: 10px;
            }
        """)
        model = CenteredListModel()
        list_of_mentions.setModel(model)
        mentions = get_mentions_by_ticker(ticker_symbol.strip("$"))
        mentions_str = []
        for mention in mentions:
            time = datetime.fromtimestamp(mention[3], timezone.utc).replace(tzinfo=None)
            if mention[2] == None:
                mentions_str.append(
                    f"Post {mention[1]} in r/{mention[4]} at "
                   f"{time}"
                )
            else:
                mentions_str.append(
                    f"Post {mention[1]} and comment {mention[2]} in "
                    f"r/{mention[4]} at {time}"
                )
        model.setStringList(mentions_str)
        
        layout.addWidget(title)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(list_of_mentions)
        
        return detail_page
    
    def open_post_url(self, index):
        text = index.data().split(" ")
        post_id = text[1]
        subreddit = text[6] if "comment" in text else text[3]
        post_url = f"https://reddit.com/{subreddit}/comments/{post_id}"
        
        attempt = webbrowser.open_new_tab(post_url)
        if attempt == False:
            print("NON-FATAL Error: Attempt to open post for selected mention failed.")
        
# creates a custom QStringListModel of sorts so that we can have some more control
# over how items are displayed in our ticker ranking list
class CenteredListModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None
        
        # provide the text
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]
        
        # provide the alignment
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def setStringList(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
