from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QLineEdit, QMessageBox, QWidget
from ui.theme import MESSAGEBOX_STYLES


def ask_yes_no(parent: QWidget, title: str, text: str, info: str = "") -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    if info:
        box.setInformativeText(info)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.No)
    box.setStyleSheet(MESSAGEBOX_STYLES)
    return box.exec() == QMessageBox.StandardButton.Yes


def confirm_student_number(parent: QWidget, number: str, info: str = "") -> bool:
    """The confirmation used everywhere a student number is entered."""
    return ask_yes_no(parent, "Confirm student number",
                      f"Is this student number {number} correct?",
                      info or "You can only check out of your seat using this same number.")


def notify(parent: QWidget, title: str, text: str, warning: bool = False):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning if warning else QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStyleSheet(MESSAGEBOX_STYLES)
    box.exec()


STUDENT_NUMBER_RULE = "Student number must be exactly 7 digits (numbers only)."


def limit_to_student_number(edit: QLineEdit):
    """Only digits can be typed/pasted, and never more than 7."""
    edit.setMaxLength(7)
    edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]{0,7}"), edit))
