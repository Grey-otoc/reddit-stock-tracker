import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QListView
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
        font.setPointSize(25)
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
                font-size: 24px;
                outline: none;
            }
            QListView::item { padding: 15px; }
        """)
        
        self.ticker_rank_model = CenteredListModel()
        example = ["AAPL: 150", "TSLA: 120", "NVDA: 95", "BTC: 80", "ETH: 60", "AAPL: 150", "TSLA: 120", "NVDA: 95", "BTC: 80", "ETH: 60", "AAPL: 150", "TSLA: 120", "NVDA: 95", "BTC: 80", "ETH: 60"]
        self.ticker_rank_model.setStringList(example)
        
        self.ticker_rank_list.setModel(self.ticker_rank_model)
        self.layout.addWidget(self.ticker_rank_list)
        
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
