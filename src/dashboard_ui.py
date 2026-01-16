from datetime import datetime, timedelta, timezone
from db_queries import get_tickers_by_mention_count
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QListView, QComboBox
from PySide6.QtCore import Qt, QAbstractListModel

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RST by grey-otoc")
        self.setup_window_geometry()
        
        self.container = QWidget()
        self.setCentralWidget(self.container)
        self.layout = QVBoxLayout(self.container)
        
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
        
        self.ticker_rank_list.setStyleSheet("""
            QListView {
                background-color: #3B0D05;
                border: none;
                border-radius: 10px;
                font-family: "Alte Haas Grotesk";
                font-weight: bold;
                font-size: 24px;
                outline: none;
            }
            QListView::item { padding: 15px; }
            QListView::item::hover { background: #250d05; border-radius: 10px;}
        """)
        
        self.ticker_rank_model = CenteredListModel()
        
        # set string list for ticker ranking list with default timeframe of last 24 hours
        self.new_timeframe_selected("Last 24 Hours")
        
        self.ticker_rank_list.setModel(self.ticker_rank_model)
        
        self.layout.addWidget(self.ticker_rank_list)
        
    def init_timeframe_menu(self):
        self.timeframe_filter_menu = QComboBox()
        
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
            
            ranked_tickers_str.append(f"{symbol}: Mentioned {mentions} {plural_check}")
        
        if not ranked_tickers_str:
            ranked_tickers_str = ["Nothing to display in this timeframe."]
        
        self.ticker_rank_model.setStringList(ranked_tickers_str)
        
# creates a custom QStringListModel of sorts so that we can have some more control
# over how items are displayed in our list
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

app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
