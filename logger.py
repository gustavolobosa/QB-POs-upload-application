# logger.py

from PyQt5.QtGui import QColor

def log_message(log_widget, message, color='black'):
    """
    Log a message with a specified color.

    :param log_widget: QTextEdit widget where the message will be logged
    :param message: Message to log
    :param color: Color of the message text (default is 'black')
    """
    color_map = {
        'red': QColor('red'),
        'green': QColor('green'),
        'blue': QColor('blue'),
        'black': QColor('black')
    }
    color = color_map.get(color, QColor('black'))
    log_widget.setTextColor(color)
    log_widget.append(message)
