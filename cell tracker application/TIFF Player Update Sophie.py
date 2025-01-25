import sys
import csv
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QLabel, QPushButton, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QDialog, QCheckBox, QScrollArea, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import tifffile
from random import randint


class CellTrajectoryPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tiff_stack = None
        self.cell_trajectories = {}  # Dictionary to store trajectories for all cells
        self.current_frame = 1  # Start frame at 1 instead of 0
        self.scale_factor = 1.0
        self.bounding_box_radius = 5
        self.selected_cells = set()
        self.cell_colors = {}
        self.next_cell_id = 1  # Counter to assign unique cell IDs
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Cell Trajectory Player')
        self.setGeometry(100, 100, 1000, 700)  # Set a fixed initial window size
        self.setMinimumSize(800, 600)  # Ensure a minimum size for the window
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)  # Allow the window to be maximized

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left Panel for Controls
        control_panel = QVBoxLayout()
        main_layout.addLayout(control_panel, stretch=1)

        # Create File Load Section
        file_group = QGroupBox("File Load")
        file_layout = QHBoxLayout()
        self.tiff_button = QPushButton('Load TIFF Stack')
        self.csv_button = QPushButton('Load CSV File')
        self.select_cells_button = QPushButton('Select Cells')
        self.select_cells_button.setEnabled(False)
        self.tiff_button.clicked.connect(self.load_tiff)
        self.csv_button.clicked.connect(self.load_csv)
        self.select_cells_button.clicked.connect(self.select_cells)
        file_layout.addWidget(self.tiff_button)
        file_layout.addWidget(self.csv_button)
        file_layout.addWidget(self.select_cells_button)
        file_group.setLayout(file_layout)
        control_panel.addWidget(file_group)

        # Frame Control Section
        frame_group = QGroupBox("Frame Controls")
        frame_layout = QVBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setMinimum(1)  # Start slider at 1 instead of 0
        self.slider.valueChanged.connect(self.update_frame)
        self.frame_label = QLabel('Frame: 1')  # Default frame label starts at 1
        self.frame_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.slider)
        frame_layout.addWidget(self.frame_label)
        frame_group.setLayout(frame_layout)
        control_panel.addWidget(frame_group)

        # Scale and Bounding Box Section
        control_group = QGroupBox("Image Controls")
        control_layout = QGridLayout()

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.update_scale)
        scale_label = QLabel("Scale (%):")
        self.scale_value_label = QLabel("100")
        control_layout.addWidget(scale_label, 0, 0)
        control_layout.addWidget(self.scale_slider, 0, 1)
        control_layout.addWidget(self.scale_value_label, 0, 2)

        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(1, 50)
        self.radius_slider.setValue(self.bounding_box_radius)
        self.radius_slider.valueChanged.connect(self.update_radius)
        radius_label = QLabel("Bounding Box Radius:")
        self.radius_value_label = QLabel("5")
        control_layout.addWidget(radius_label, 1, 0)
        control_layout.addWidget(self.radius_slider, 1, 1)
        control_layout.addWidget(self.radius_value_label, 1, 2)

        control_group.setLayout(control_layout)
        control_panel.addWidget(control_group)

        # Right Panel for Image Display
        self.image_label = QLabel('No image loaded')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #f5f5f5;")
        main_layout.addWidget(self.image_label, stretch=2)

        # Styling
        self.setStyleSheet(""" 
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel {
                font-size: 14px;
            }
            QSlider {
                min-height: 20px;
            }
        """)

    def load_tiff(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open TIFF Stack", "", "TIFF Files (*.tiff *.tif)")
        if file_path:
            try:
                self.tiff_stack = tifffile.imread(file_path)
                self.slider.setMinimum(1)  # Start slider at 1
                self.slider.setMaximum(len(self.tiff_stack))  # Set maximum to the number of frames
                self.slider.setEnabled(True)
                self.select_cells_button.setEnabled(True)
                self.update_frame(1)  # Start at frame 1
                QMessageBox.information(self, "Success", "TIFF stack loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load TIFF stack: {str(e)}")

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Assign a unique cell ID for this CSV file
                cell_id = f"Cell_{self.next_cell_id}"
                self.next_cell_id += 1

                # Parse the CSV file and add trajectories for this cell
                trajectories = self.parse_csv(file_path, cell_id)
                self.cell_trajectories[cell_id] = trajectories
                self.update_frame(self.current_frame)
                QMessageBox.information(self, "Success", f"CSV file loaded as {cell_id}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")

    def parse_csv(self, csv_path, cell_id):
        trajectories = []
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                frame = int(row['Slice n°'])  # Use 'Slice n°' as the frame number
                x = int(float(row['X']))  # Convert X coordinate to integer
                y = int(float(row['Y']))  # Convert Y coordinate to integer
                trajectories.append((frame, x, y))
        return trajectories

    def select_cells(self):
        if not self.cell_trajectories:
            QMessageBox.warning(self, "No Data", "Load a CSV file with cell trajectories first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Cells")
        layout = QVBoxLayout(dialog)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        checkboxes = {}
        for cell_id in self.cell_trajectories.keys():
            checkbox = QCheckBox(f"Cell {cell_id}")
            checkbox.setChecked(cell_id in self.selected_cells)
            checkboxes[cell_id] = checkbox
            scroll_layout.addWidget(checkbox)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self.update_selected_cells(checkboxes, dialog))
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def update_selected_cells(self, checkboxes, dialog):
        self.selected_cells.clear()
        for cell_id, checkbox in checkboxes.items():
            if checkbox.isChecked():
                self.selected_cells.add(cell_id)
                if cell_id not in self.cell_colors:
                    self.cell_colors[cell_id] = self.generate_random_color()
        dialog.accept()
        self.update_frame(self.current_frame)

    def generate_random_color(self):
        return QColor(randint(0, 255), randint(0, 255), randint(0, 255))

    def update_frame(self, frame):
        self.current_frame = frame
        self.frame_label.setText(f"Frame: {frame}")
        self.display_frame()

    def update_scale(self, value):
        self.scale_factor = value / 100.0
        self.scale_value_label.setText(str(value))
        self.display_frame()

    def update_radius(self, value):
        self.bounding_box_radius = value
        self.radius_value_label.setText(str(value))
        self.display_frame()

    def display_frame(self):
        if self.tiff_stack is None:
            return

        # Retrieve the current frame (adjust for zero-based indexing)
        frame_index = self.current_frame - 1  # Convert to zero-based index
        frame_image = self.tiff_stack[frame_index]

        # Ensure the image is displayed without altering intensity for scaling
        scaled_image = frame_image  # Keep intensity values unchanged
        height, width = scaled_image.shape

        # Convert the image to QImage
        q_image = QImage(scaled_image.data, width, height, width, QImage.Format_Grayscale8)

        # Scale the QPixmap based on the scale_factor
        pixmap = QPixmap.fromImage(q_image).scaled(
            int(width * self.scale_factor),
            int(height * self.scale_factor),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Draw the bounding boxes for selected cells
        painter = QPainter(pixmap)
        for cell_id in self.selected_cells:
            if cell_id in self.cell_trajectories:
                for frame, x, y in self.cell_trajectories[cell_id]:
                    if frame == self.current_frame:  # Match frame numbers directly
                        painter.setPen(QPen(self.cell_colors[cell_id], 2))
                        scaled_x = x * self.scale_factor
                        scaled_y = y * self.scale_factor
                        scaled_radius = self.bounding_box_radius * self.scale_factor

                        # Draw a rectangle around the cell (bounding box)
                        painter.drawRect(
                            scaled_x - scaled_radius,
                            scaled_y - scaled_radius,
                            2 * scaled_radius,
                            2 * scaled_radius
                        )
        painter.end()

        # Update the QLabel with the pixmap
        self.image_label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = CellTrajectoryPlayer()
    player.show()
    sys.exit(app.exec_())