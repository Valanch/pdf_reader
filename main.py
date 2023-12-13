from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QFileDialog, QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import QPointF, QRect, QPoint
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
import sys
from pathlib import Path


FREE_STATE = 1
BUILDING_SQUARE = 2
BEGIN_SIDE_EDIT = 3
END_SIDE_EDIT = 4


class customQPdfView(QPdfView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setGeometry(0, 28, 1000, 750)
        self.begin = QPoint()
        self.end = QPoint()

        self.state = FREE_STATE

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(QColor(255, 0, 0, 255))
        painter.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        if not self.begin.isNull() and not self.end.isNull():
            p = event.pos()
            y1, y2 = sorted([self.begin.y(), self.end.y()])
            if y1 <= p.y() <= y2:
                if abs(self.begin.x() - p.x()) <= 3:
                    self.state = BEGIN_SIDE_EDIT
                    return
                elif abs(self.end.x() - p.x()) <= 3:
                    self.state = END_SIDE_EDIT
                    return
        self.state = BUILDING_SQUARE
        self.begin = event.pos()
        self.end = event.pos()

    def apply_event(self, event):

        if self.state == BUILDING_SQUARE:
            self.end = event.pos()
        elif self.state == BEGIN_SIDE_EDIT:
            self.begin.setX(event.x())
        elif self.state == END_SIDE_EDIT:
            self.end.setX(event.x())

    def mouseMoveEvent(self, event):
        self.apply_event(event)
        self.viewport().repaint()

    def mouseReleaseEvent(self, event):
        self.apply_event(event)
        self.state = FREE_STATE


class PdfWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PDF viewer'
        self.pdf_view = customQPdfView(self)
        self.pdf_document = QPdfDocument(None)
        self.m_fileDialog = None
        self.pdf_view.setDocument(self.pdf_document)

    def open_pdf(self):
        home_dir = str(Path.home())
        doc_location = QFileDialog.getOpenFileName(
            self,
            'Open File',
            home_dir,
            "PDF files (*.pdf)"
        )

        self.pdf_document.load(doc_location[0])

        self.pdf_view.setDocument(self.pdf_document)
        self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)

        self.update()
        self.pdf_view.showMaximized()

    def next_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() < self.pdf_document.pageCount() - 1:
            nav.jump(nav.currentPage() + 1, QPointF(), nav.currentZoom())

    def previous_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() > 0:
            nav.jump(nav.currentPage() - 1, QPointF(), nav.currentZoom())


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.setWindowTitle("PDF Viewer")
        self.setGeometry(0, 28, 1000, 750)
        widget = QWidget()
        layout = QVBoxLayout()
        layout2 = QHBoxLayout()

        self.fileOpenButton = QPushButton("Open file")
        layout2.addWidget(self.fileOpenButton)
        layout2.addWidget(self.fileOpenButton)
        layout2.addWidget(self.fileOpenButton)
        self.goLeftButton = QPushButton("<")
        self.goRightButton = QPushButton(">")
        layout2.addWidget(self.goLeftButton)
        layout2.addWidget(self.goRightButton)

        layout.addLayout(layout2)

        self.pdf = PdfWindow()
        layout.addWidget(self.pdf)
        self.fileOpenButton.clicked.connect(self.pdf.open_pdf)
        self.goLeftButton.clicked.connect(self.pdf.previous_page)
        self.goRightButton.clicked.connect(self.pdf.next_page)

        widget.setLayout(layout)
        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
