from PyQt6 import QtGui, QtCore, QtWidgets

class ChatBubble(QtWidgets.QLabel):
    def __init__(self, text, is_left=True, parent=None):
        super().__init__(text, parent)
        self.is_left = is_left
        self.setWordWrap(True)
        self.setMargin(10)
        self.setStyleSheet("background-color: white; border-radius: 15px; padding: 10px;")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        brush = QtGui.QBrush(QtCore.Qt.GlobalColor.white)
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.gray, 1.5)
        painter.setBrush(brush)
        painter.setPen(pen)

        if self.is_left:
            rect = QtCore.QRect(5, 5, self.width() - 10, self.height() - 10)
            painter.drawRoundedRect(rect, 15, 15)
        else:
            rect = QtCore.QRect(10, 5, self.width() - 15, self.height() - 10)
            painter.drawRoundedRect(rect.adjusted(0, 0, -10, 0), 15, 15)

        super().paintEvent(event)
