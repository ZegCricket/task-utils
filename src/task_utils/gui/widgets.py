from enum import StrEnum
from typing import Optional

import serial.tools.list_ports
from harp.protocol.exceptions import HarpException, HarpTimeoutException
from harp.serial import Device
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QWidget,
)
from serial.serialutil import SerialException


class ExplorerType(StrEnum):
    DIRECTORY = "directory"
    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"


class ExplorerWidget(QWidget):
    def __init__(
        self,
        *args,
        text: str = "",
        type: ExplorerType = ExplorerType.DIRECTORY,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._type = type

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.line = QLineEdit(self, text=text)
        layout.addWidget(self.line)

        self.button = QPushButton("Browse", parent=self)
        self.button.clicked.connect(self.browse)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def browse(self) -> None:
        match self._type:
            case ExplorerType.DIRECTORY:
                entry = QFileDialog.getExistingDirectory(caption="Pick Directory")
            case ExplorerType.OPEN_FILE:
                entry = QFileDialog.getOpenFileName(caption="Pick File")
            case ExplorerType.SAVE_FILE:
                entry = QFileDialog.getSaveFileName(caption="Pick File")
        self.line.setText(entry)


class SerialComboBox(QComboBox):
    def __init__(
        self,
        parent,
        id: int,
        device_name: str,
        placeholder_text: str = "COMx",
        *,
        value: Optional[str] = None,
    ):
        super().__init__(parent)

        self.id = id
        self.device = device_name
        self.setPlaceholderText(placeholder_text)
        self.addItems(self.get_ports())
        if value is not None:
            self.setCurrentText(value)
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


class ResolutionWidget(QWidget):
    def __init__(
        self,
        *args,
        width: int = 1440,
        height: int = 1080,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._type = type

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.width = QSpinBox(self, maximum=9999, value=width)
        layout.addWidget(self.width)

        separator = QLabel("x")
        layout.addWidget(separator)

        self.height = QSpinBox(self, maximum=9999, value=height)
        layout.addWidget(self.height)

        self.setLayout(layout)

    def get_resolution(self) -> str:
        return f"{self.width.value()}x{self.height.value()}"
