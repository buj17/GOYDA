from datetime import date, time

from CinemasUi import Ui_MainWindow
from FileTools import create_schedule
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QWidget, QTreeWidgetItem, QPushButton, QLabel
from cinemas import CinemaNet, Cinema, Hall, Session, IncorrectTimeRangeError, TimeRangeIntersectionError


class Cinemas(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.date = self.date_edit.setDate(QDate.currentDate())
        self.schedule_start_date.setDate(QDate.currentDate())
        self.schedule_end_date.setDate(QDate.currentDate())
        self.warning_session_label.setStyleSheet('color: red')
        self.warning_schedule_label.setStyleSheet('color: red')

        self.cinema_net = CinemaNet('Кинотеатры')

        self.cinema_edit.textChanged.connect(self.block_unblock_hall_edit)

        self.hall_edit.textChanged.connect(self.block_unblock_session_line)

        self.session_edit.textChanged.connect(self.block_unblock_session_params)

        self.create_button.clicked.connect(self.add_items)

        self.cinema_combo_box.currentIndexChanged.connect(self.update_hall_combo_box)

        self.hall_combo_box.currentIndexChanged.connect(self.update_session_combo_box)

        self.delete_cinema_button.clicked.connect(self.delete_cinema)

        self.delete_hall_button.clicked.connect(self.delete_hall)

        self.delete_session_button.clicked.connect(self.delete_session)

        self.go_to_session_button.clicked.connect(self.show_session_config_window)

        self.create_schedule_button.clicked.connect(self.create_schedule)

    def block_unblock_hall_edit(self):
        if self.cinema_edit.text():
            self._unblock_hall_edit()
            if self.hall_edit.text():
                self._unblock_session_edit()
        else:
            self._block_hall_edit()
            self._block_session_edit()

    def block_unblock_session_line(self):
        if self.hall_edit.text():
            self._unblock_session_line()
            if self.session_edit.text():
                self._unblock_session_params()
        else:
            self._block_session_line()
            self._block_session_params()

    def block_unblock_session_params(self):
        if self.session_edit.text():
            self._unblock_session_params()
        else:
            self._block_session_params()

    def _block_hall_line(self):
        self.hall_edit.setDisabled(True)

    def _block_hall_params(self):
        self.length_spin_box.setDisabled(True)
        self.width_spin_box.setDisabled(True)

    def _block_hall_edit(self):
        self._block_hall_line()
        self._block_hall_params()

    def _unblock_hall_line(self):
        self.hall_edit.setEnabled(True)

    def _unblock_hall_params(self):
        self.length_spin_box.setEnabled(True)
        self.width_spin_box.setEnabled(True)

    def _unblock_hall_edit(self):
        self._unblock_hall_line()
        self._unblock_hall_params()

    def _block_session_line(self):
        self.session_edit.setDisabled(True)

    def _block_session_params(self):
        self.date_edit.setDisabled(True)
        self.start_time_edit.setDisabled(True)
        self.end_time_edit.setDisabled(True)

    def _block_session_edit(self):
        self._block_session_line()
        self._block_session_params()

    def _unblock_session_line(self):
        self.session_edit.setEnabled(True)

    def _unblock_session_params(self):
        self.date_edit.setEnabled(True)
        self.start_time_edit.setEnabled(True)
        self.end_time_edit.setEnabled(True)

    def _unblock_session_edit(self):
        self._unblock_session_line()
        self._unblock_session_params()

    def add_items(self):
        if self.cinema_edit.text():
            cinema_name = ' '.join(('Кинотеатр', self.cinema_edit.text()))
        else:
            cinema_name = None

        if self.hall_edit.isEnabled() and self.hall_edit.text():
            hall_name = ' '.join(('Зал', self.hall_edit.text()))
            hall_length = self.length_spin_box.value()
            hall_width = self.width_spin_box.value()
        else:
            hall_name = hall_length = hall_width = None

        if self.session_edit.isEnabled() and self.session_edit.text():
            session_name = ' '.join(('Сеанс', self.session_edit.text()))
            session_date = date(*self.date_edit.date().getDate())
            session_start_time = self.start_time_edit.time().toPyTime()
            session_end_time = self.end_time_edit.time().toPyTime()
        else:
            session_name = session_date = session_start_time = session_end_time = None

        if cinema_name:
            if cinema_name in self.cinema_net.get_cinemas():
                cinema = self.cinema_net.get_cinema(cinema_name)
            else:
                cinema = Cinema(cinema_name)
        else:
            cinema = None

        if hall_name:
            if hall_name in cinema.get_halls():
                hall = cinema.get_hall(hall_name)
            else:
                hall = Hall(hall_name, hall_length, hall_width)
        else:
            hall = None

        self.create_objects(cinema, hall, session_name, session_start_time, session_end_time, session_date)

    def create_objects(self,
                       cinema: Cinema | None,
                       hall: Hall | None,
                       session_name: str | None,
                       session_start_time: time | None,
                       session_end_time: time | None,
                       session_date: date | None):
        if session_name:
            hall: Hall

            if session_name not in hall.get_sessions():
                try:
                    hall.add_session(session_name, session_start_time, session_end_time, session_date)
                except IncorrectTimeRangeError:
                    self.show_warning_add_message('Время начала должно быть меньше времени конца')
                    return None
                except TimeRangeIntersectionError:
                    self.show_warning_add_message('Время данного сеанса пересекается с другим')
                    return None
                else:
                    self.cinema_net.add_cinema(cinema)
                    cinema.add_hall(hall)
                    self.hide_warning_add_message()
                    self.update_tree()
                    self.update_cinema_combo_box()
                    self.clear_add_form()

        elif cinema and hall:
            self.cinema_net.add_cinema(cinema)
            cinema.add_hall(hall)
            self.update_tree()
            self.update_cinema_combo_box()
            self.clear_add_form()

        elif cinema:
            self.cinema_net.add_cinema(cinema)
            self.update_tree()
            self.update_cinema_combo_box()
            self.clear_add_form()

    def clear_add_form(self):
        self.cinema_edit.clear()
        self.hall_edit.clear()
        self.session_edit.clear()
        self.width_spin_box.setValue(1)
        self.length_spin_box.setValue(1)
        self.date_edit.setDate(QDate.currentDate())
        self.start_time_edit.setTime(QTime(0, 0))
        self.end_time_edit.setTime(QTime(0, 0))

    def update_tree(self):
        self.cinemas_tree.clear()

        for cinema_name in self.cinema_net.get_cinemas():
            cinema: Cinema = self.cinema_net.get_cinema(cinema_name)
            cinema_tree_item = QTreeWidgetItem(self.cinemas_tree)
            cinema_text = cinema.get_name()
            cinema_tree_item.setText(0, cinema_text)

            for hall_name in cinema.get_halls():
                hall: Hall = cinema.get_hall(hall_name)
                hall_tree_item = QTreeWidgetItem(cinema_tree_item)
                hall_text = hall.get_name()
                hall_tree_item.setText(0, hall_text)

                for session_name in hall.get_sessions():
                    session = hall.get_session(session_name)
                    session_tree_item = QTreeWidgetItem(hall_tree_item)
                    session_text = session.get_name()
                    session_tree_item.setText(0, session_text)

    def show_warning_add_message(self, text):
        self.warning_session_label.setText(text)

    def hide_warning_add_message(self):
        self.warning_session_label.setText('')

    def update_cinema_combo_box(self):
        self.cinema_combo_box.clear()
        for cinema_name in self.cinema_net.get_cinemas():
            self.cinema_combo_box.addItem(cinema_name)

    def update_hall_combo_box(self):
        self.hall_combo_box.clear()
        try:
            cinema = self.cinema_net.get_cinema(self.cinema_combo_box.currentText())
        except KeyError:
            self.hall_combo_box.setDisabled(True)
            self.delete_hall_button.setDisabled(True)
            return None

        halls = cinema.get_halls()
        for hall_name in halls:
            self.hall_combo_box.addItem(hall_name)

        if self.hall_combo_box.currentText():
            self.hall_combo_box.setEnabled(True)
            self.delete_hall_button.setEnabled(True)
        else:
            self.hall_combo_box.setDisabled(True)
            self.delete_hall_button.setDisabled(True)

    def update_session_combo_box(self):
        self.session_combo_box.clear()
        try:
            cinema = self.cinema_net.get_cinema(self.cinema_combo_box.currentText())
            hall = cinema.get_hall(self.hall_combo_box.currentText())
        except KeyError:
            self.session_combo_box.setDisabled(True)
            self.go_to_session_button.setDisabled(True)
            self.delete_session_button.setDisabled(True)
            return None

        sessions = hall.get_sessions()
        for session_name in sessions:
            self.session_combo_box.addItem(session_name)

        if self.session_combo_box.currentText():
            self.session_combo_box.setEnabled(True)
            self.go_to_session_button.setEnabled(True)
            self.delete_session_button.setEnabled(True)
        else:
            self.session_combo_box.setDisabled(True)
            self.go_to_session_button.setDisabled(True)
            self.delete_session_button.setDefault(True)

    def update_all_combo_boxes(self):
        self.update_cinema_combo_box()
        self.update_hall_combo_box()
        self.update_session_combo_box()

    def delete_cinema(self):
        cinema_name = self.cinema_combo_box.currentText()
        if cinema_name:
            self.cinema_net.del_cinema(cinema_name)
            self.update_tree()
            self.update_all_combo_boxes()

    def delete_hall(self):
        hall_name = self.hall_combo_box.currentText()
        if hall_name:
            cinema = self.cinema_net.get_cinema(self.cinema_combo_box.currentText())
            cinema.del_hall(hall_name)
            self.update_tree()
            self.update_all_combo_boxes()

    def delete_session(self):
        session_name = self.session_combo_box.currentText()
        if session_name:
            cinema = self.cinema_net.get_cinema(self.cinema_combo_box.currentText())
            hall = cinema.get_hall(self.hall_combo_box.currentText())
            hall.del_session(session_name)
            self.update_tree()
            self.update_all_combo_boxes()

    def show_session_config_window(self):
        cinema = self.cinema_net.get_cinema(self.cinema_combo_box.currentText())
        hall = cinema.get_hall(self.hall_combo_box.currentText())
        session_to_config = hall.get_session(self.session_combo_box.currentText())

        self.session_config_window = SessionConfigWindow(self, session_to_config)
        self.session_config_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.session_config_window.show()

    def show_warning_schedule_message(self, text):
        self.warning_schedule_label.setText(text)

    def hide_warning_schedule_message(self):
        self.warning_schedule_label.setText('')

    def create_schedule(self):
        start_date = self.schedule_start_date.date().toPyDate()
        end_date = self.schedule_end_date.date().toPyDate()

        if start_date > end_date:
            self.show_warning_schedule_message("Начальная дата больше конечной")
        else:
            self.hide_warning_schedule_message()

        create_schedule(self.cinema_net, start_date, end_date)


class SessionConfigWindow(QWidget):
    def __init__(self, parent, session):
        super().__init__()
        self.parent = parent
        self.session: Session = session
        self.button_matrix = []
        self.initUI()

    def initUI(self):
        self.resize(500, 500)

        rows, cols = self.session.hall_width, self.session.hall_length

        for row in range(rows):
            self.button_matrix.append([])
            for col in range(cols):
                seat = self.session.get_seat(row, col)
                if seat.is_taken():
                    text = '*'
                else:
                    text = ''

                btn = QPushButton(text, self)
                btn.resize(30, 30)
                btn.move(10 + 30 * col, 10 + 30 * row)
                btn.clicked.connect(self.seat_config)
                self.button_matrix[-1].append(btn)

        self.info_label = QLabel('* - место занято, пустая строка - место свободно', self)
        self.info_label.move(10, 15 + 30 * rows)

        self.save_and_quit_button = QPushButton('Сохранить и выйти', self)
        self.save_and_quit_button.move(10, 45 + 30 * rows)
        self.save_and_quit_button.clicked.connect(self.save_and_quit)

    def seat_config(self):
        if self.sender().text() == '*':
            self.sender().setText('')
        else:
            self.sender().setText('*')

    def save_and_quit(self):
        rows, cols = self.session.hall_width, self.session.hall_length

        for row in range(rows):
            for col in range(cols):
                seat = self.session.get_seat(row, col)
                text = self.button_matrix[row][col].text()
                if text == '*':
                    seat.take()
                else:
                    seat.release()

        self.close()
