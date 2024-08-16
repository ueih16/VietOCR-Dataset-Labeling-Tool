import sys
import cv2 as cv
import numpy as np
import os

from datetime import datetime
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication
from MainUI import Ui_Form
from LineDataUI import Ui_Form as LineDataUIForm
from PyQt5.QtCore import pyqtSlot


class RunApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.line_data_form = QtWidgets.QWidget()
        self.line_data_ui = LineDataUIForm()
        self.line_data_ui.setupUi(self.line_data_form)

        # Initial Variable
        self.x_start = None
        self.x_end = None
        self.y_start = None
        self.y_end = None
        self.x_start_real = None
        self.y_start_real = None
        self.x_end_real = None
        self.y_end_real = None
        self.is_draw = False
        self.mask_template_crop = None
        self.temp_image = None

        self.img_dir = None
        self.img_list = []
        self.current_img_index = -1  # -1 nghĩa là chưa có ảnh nào được load

        # Set up attribute and implement function
        self.set_ui_attribute()
        self.implement_function()
        self.line_data_form.hide()

    # Setup UI attribute here
    def set_ui_attribute(self):
        # Automatically adjust the window size to fit the content
        self.adjustSize()
        self.setFixedSize(self.size())

        self.line_data_form.adjustSize()
        self.line_data_form.setFixedSize(self.line_data_form.size())

        # Setup HEADER
        self.setWindowTitle("OCR DEMO")

        color = QtGui.QColor(70, 136, 224)
        color.setAlpha(130)
        effect_1 = QtWidgets.QGraphicsDropShadowEffect(offset=QtCore.QPoint(3, 3), blurRadius=4, color=color)
        self.ui.btn_save.setGraphicsEffect(effect_1)

        color = QtGui.QColor(196, 64, 51)
        color.setAlpha(130)
        effect_2 = QtWidgets.QGraphicsDropShadowEffect(offset=QtCore.QPoint(3, 3), blurRadius=4, color=color)
        self.ui.btn_exit.setGraphicsEffect(effect_2)

        widgets1 = [
            self.ui.dp_view,
        ]

        for widget in widgets1:
            effect = QtWidgets.QGraphicsDropShadowEffect(offset=QtCore.QPoint(3, 3), color=QtGui.QColor(217, 217, 217))
            widget.setGraphicsEffect(effect)

        self.ui.rad_train.setChecked(True)

    # Implement function for UI element here
    def implement_function(self):
        # Main UI
        self.ui.btn_exit.clicked.connect(self.close)
        self.ui.btn_choose_img_dir.clicked.connect(lambda: self.choose_img_dir())
        self.ui.btn_prev.clicked.connect(lambda: self.go_prev_img())
        self.ui.btn_next.clicked.connect(lambda: self.go_next_img())
        self.ui.btn_choose_dataset_dir.clicked.connect(lambda: self.choose_dataset_dir())
        self.ui.btn_save.clicked.connect(lambda: self.save())
        self.ui.dp_view.mousePressEvent = self.mouse_press_event
        self.ui.dp_view.mouseMoveEvent = self.mouse_move_event
        self.ui.dp_view.mouseReleaseEvent = self.mouse_release_event

        # Fill Data Line UI
        self.line_data_ui.btnBox.accepted.connect(lambda: self.append_annotation())
        self.line_data_ui.txb_line_data.returnPressed.connect(lambda: self.append_annotation())

        self.line_data_ui.btnBox.rejected.connect(lambda: self.cancel_annotation())
        self.line_data_form.keyPressEvent = self.keyPressEvent

    def closeEvent(self, e):
        return_value = QtWidgets.QMessageBox.warning(self, "Warning ?",
                                                     "Are you sure you want to quit ?",
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                     QtWidgets.QMessageBox.No)
        if return_value == QtWidgets.QMessageBox.Yes:
            e.accept()
        else:
            e.ignore()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel_annotation()

    def mouse_press_event(self, event):
        try:
            dp_view = self.ui.dp_view
            crop_x_ratio = self.temp_image.shape[1] / dp_view.size().width()
            crop_y_ratio = self.temp_image.shape[0] / dp_view.size().height()
            if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
                self.x_start = event.x()
                self.y_start = event.y()
                self.x_start_real = round(event.x() * crop_x_ratio)
                self.y_start_real = round(event.y() * crop_y_ratio)
                self.is_draw = True
        except Exception as e:
            print(e)

    def mouse_move_event(self, event):
        try:
            if self.is_draw:
                image = np.copy(self.temp_image)
                image = cv.resize(image, (self.ui.dp_view.size().width(), self.ui.dp_view.size().height()))
                cv.rectangle(image, (self.x_start, self.y_start), (event.x(), event.y()), (0, 0, 255), thickness=1)
                self.add_image_to_qlabel(image, self.ui.dp_view)
        except Exception as e:
            print(e)

    def mouse_release_event(self, event):
        try:
            crop_x_ratio = self.temp_image.shape[1] / self.ui.dp_view.size().width()
            crop_y_ratio = self.temp_image.shape[0] / self.ui.dp_view.size().height()
            self.is_draw = False
            self.x_end = event.x()
            self.y_end = event.y()
            self.x_end_real = round(event.x() * crop_x_ratio)
            self.y_end_real = round(event.y() * crop_y_ratio)

            # Recalculate coordinates
            if self.x_start > self.x_end:
                self.x_start, self.x_end = self.x_end, self.x_start
            if self.y_start > self.y_end:
                self.y_start, self.y_end = self.y_end, self.y_start
            if self.x_start_real > self.x_end_real:
                self.x_start_real, self.x_end_real = self.x_end_real, self.x_start_real
            if self.y_start_real > self.y_end_real:
                self.y_start_real, self.y_end_real = self.y_end_real, self.y_start_real

            self.mask_template_crop = self.temp_image[
                                      self.y_start_real:self.y_end_real,
                                      self.x_start_real:self.x_end_real]

            self.add_image_to_qlabel(self.mask_template_crop, self.ui.dp_view_crop)
            self.line_data_form.show()
            self.line_data_ui.txb_line_data.setFocus(True)
            self.line_data_form.raise_()
        except Exception as e:
            print(e)

    def choose_img_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Image Directory",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if dir_path:
            self.img_dir = dir_path
            self.img_list = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'))]
            if self.img_list:
                self.current_img_index = 0
                self.load_image()

    def go_prev_img(self):
        if self.current_img_index > 0:
            self.current_img_index -= 1
            self.load_image()

    def go_next_img(self):
        if self.current_img_index < len(self.img_list) - 1:
            self.current_img_index += 1
            self.load_image()

    def load_image(self):
        if self.img_dir and self.img_list and 0 <= self.current_img_index < len(self.img_list):
            img_path = os.path.join(self.img_dir, self.img_list[self.current_img_index])
            self.temp_image = cv.imread(img_path)
            self.add_image_to_qlabel(self.temp_image, self.ui.dp_view)

    def choose_dataset_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )
        if dir_path:
            self.ui.txb_dataset_dir.setText(dir_path)

    def append_annotation(self):
        if not os.path.exists(os.path.join(self.ui.txb_dataset_dir.text(), "images")):
            os.mkdir(os.path.join(self.ui.txb_dataset_dir.text(), "images"))

        img_name = datetime.now().strftime("%Y%m%d%H%M%S.png")
        img_file_name = os.path.join(self.ui.txb_dataset_dir.text(), "images", img_name)

        txt = f"images/{img_name} {self.line_data_ui.txb_line_data.text()}"

        if self.ui.rad_train.isChecked():
            self.ui.tab_annotation.setCurrentIndex(0)
            self.ui.txb_train_annotation.append(txt)
        elif self.ui.rad_test.isChecked():
            self.ui.tab_annotation.setCurrentIndex(1)
            self.ui.txb_test_annotation.append(txt)

        img = self.mask_template_crop
        cv.imwrite(img_file_name, img)

        print(f"Success: {txt}")
        self.line_data_form.hide()

    def cancel_annotation(self):
        self.line_data_ui.txb_line_data.clear()
        self.line_data_form.hide()
        print("Line Form Rejected")

    def save(self):
        current_dir = self.ui.txb_dataset_dir.text()
        train_anno_file_name = os.path.join(current_dir, "train_annotation.txt")
        test_anno_file_name = os.path.join(current_dir, "test_annotation.txt")

        train_anno_data = self.ui.txb_train_annotation.toPlainText()
        test_anno_data = self.ui.txb_test_annotation.toPlainText()

        with open(train_anno_file_name, "w", encoding="utf-8") as file:
            file.write(train_anno_data)

        with open(test_anno_file_name, "w", encoding="utf-8") as file:
            file.write(test_anno_data)

        print("Save Dataset Successfully !!!")

    @pyqtSlot(np.ndarray, QtWidgets.QLabel)
    def add_image_to_qlabel(self, image: np.ndarray, dp_view: QtWidgets.QLabel):
        img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        dp_view_height = dp_view.size().height()
        dp_view_width = dp_view.size().width()

        img = cv.resize(img, (dp_view_width, dp_view_height))
        h, w, chanel = img.shape
        bytes_per_line = 3 * w
        qimg = QtGui.QImage(img.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap(qimg)

        dp_view.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RunApp()
    window.show()
    sys.exit(app.exec_())
