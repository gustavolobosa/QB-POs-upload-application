import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from logger import log_message
from reader import createPO

class NumberInputWindow(QMainWindow):
    def __init__(self, access_token, *args, **kwargs):
        super(NumberInputWindow, self).__init__(*args, **kwargs)
        self.access_token = access_token
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        if not self.layout():
            layout = QVBoxLayout()
            central_widget.setLayout(layout)
            
        self.setWindowTitle("Number Input with Drag and Drop")
        self.setGeometry(100, 100, 1000, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Layouts for number input and drag and drop
        self.input_layout = QVBoxLayout()
        self.drag_drop_layout = QVBoxLayout()
        
        # Label and text edit for number input
        self.label = QLabel("Enter a list of numbers of the IDs (comma-separated):")
        self.number_input = QTextEdit()
        self.number_input.setPlaceholderText("Type numbers here...")
        self.number_input.setFixedHeight(100)
        
        self.input_layout.addWidget(self.label)
        self.input_layout.addWidget(self.number_input)
        
        # Label and text edit for drag and drop
        self.drop_label = QLabel("Drag and drop a file here:")
        self.drop_text_edit = QTextEdit()
        self.drop_text_edit.setPlaceholderText("Drag and drop a file here...")
        self.drop_text_edit.setAcceptDrops(True)
        self.drop_text_edit.setFixedHeight(100)
        
        self.drag_drop_layout.addWidget(self.drop_label)
        self.drag_drop_layout.addWidget(self.drop_text_edit)
        
        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit)
        
        # Log window
        self.log_window = QTextEdit()
        self.log_window.setPlaceholderText("Log messages will appear here...")
        self.log_window.setReadOnly(True)
        self.log_window.setFixedHeight(600)
        
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.drag_drop_layout)
        self.main_layout.addWidget(self.submit_button)
        self.main_layout.addWidget(self.log_window)
        
        self.setLayout(self.main_layout)
        
        # Set up drag and drop functionality
        self.drop_text_edit.installEventFilter(self)
        
    def on_submit(self):
        numbers_text = self.number_input.toPlainText()
        numbers = [n.strip() for n in numbers_text.split(',') if n.strip()]
        file_content = self.drop_text_edit.toPlainText()
        
        if not numbers:
            log_message(self.log_window, "No numbers entered. Please enter at least one number.", 'default')
        else:
            log_message(self.log_window, f"Values entered: {', '.join(numbers)}", 'numbers')
        
        if file_content:
            log_message(self.log_window, f"File content: {file_content}", 'file_path')
            
        createPO(self.access_token, numbers, file_content, self.log_window)
        
        
        # Here you can use self.access_token for further actions if needed
    
    def eventFilter(self, obj, event):
        if obj == self.drop_text_edit and event.type() == event.DragEnter:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            else:
                event.ignore()
        elif obj == self.drop_text_edit and event.type() == event.Drop:
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    with open(file_path, 'r') as file:
                        content = file.read()
                    self.drop_text_edit.setPlainText(content)
                    event.acceptProposedAction()
                else:
                    event.ignore()
        return super().eventFilter(obj, event)
