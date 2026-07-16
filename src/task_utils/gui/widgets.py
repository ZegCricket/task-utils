import serial.tools.list_ports
from harp.protocol.exceptions import HarpException, HarpTimeoutException
from harp.serial import Device
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)
from serial.serialutil import SerialException


class FileExplorer(QWidget):
    def __init__(self):
        layout = QHBoxLayout()

        self.line = QLineEdit(self)
        layout.addWidget(self.line)

        self.button = QPushButton("Browse", self)
        self.button.clicked.connect(self.browse_files)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def browse_files(self):
        file = QFileDialog.getExistingDirectory(self, caption="Pick Directory")
        self.line.setText(file)


class SerialComboBox(QComboBox):
    def __init__(
        self, parent, id: int, device_name: str, placeholder_text: str = "COMx"
    ):
        super().__init__(parent)

        self.id = id
        self.device = device_name
        self.setPlaceholderText(placeholder_text)
        self.addItems(self.get_ports())
        self.setCurrentText(placeholder_text)
        self.currentTextChanged.connect(self.connect_device)

    def get_ports(self):
        ports = serial.tools.list_ports.comports()

        port_strings = []
        for port in ports:
            port_strings.append(port.device)

        port_strings.append("Refresh")

        return port_strings

    def connect_device(self, text):
        if text == "Refresh" or text == "":
            self.setCurrentIndex(-1)
            self.clear()
            self.addItems(self.get_ports())
            return

        try:
            device = Device(text)
            device_id = device.WHO_AM_I
            device.disconnect()
        except HarpException:
            self.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp device.")
            return
        except HarpTimeoutException:
            self.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp device.")
            return
        except SerialException:
            self.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", "This is not a Harp device.")
            return

        if device_id != self.id:
            self.setCurrentIndex(-1)
            QMessageBox.warning(self, "Warning", f"This is not a {self.device}.")
