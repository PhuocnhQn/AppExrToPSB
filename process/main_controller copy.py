# main_controller.py
import sys, os, time, configparser, shutil, pythoncom
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt
from threading import Thread
import photoshop.api as ps
import pygetwindow as gw
import pyautogui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QComboBox, QFileDialog, QLabel, QDesktopWidget, QCheckBox, QDialog, QVBoxLayout,QHBoxLayout
from datetime import datetime
import sys, os, io, configparser
from log.ui.log_window import LogWindow
from ui.ui_main_layout import Ui_MainWindow
from log.process.gui_logger import QTextEditLogger

class MainController(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        self.running_open_exr = True
        self.process_new_files_move = None
        # --- Connect buttons ---
        self.start_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)
        self.close_button.clicked.connect(self.close_application)
        self.log_button.clicked.connect(self.toggle_log_window)
        self.select_folder_button_in.clicked.connect(self.select_folder_in)
        self.setup_logic()  # phần logic của app

    def setup_logic(self):

        # ======================================================
        # ⚙️ Đọc config.ini
        # ======================================================
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        self.create_folders(data_folder)

        self.config_file_path = os.path.join(data_folder, "config.ini")
        self.config = configparser.ConfigParser()

        if os.path.exists(self.config_file_path):
            try:
                self.config.read(self.config_file_path)
                self.checkbox_processes.setChecked(int(self.config.get("Paths", "chk_processes", fallback="0")))
                self.checkbox_prepost.setChecked(int(self.config.get("Paths", "chk_preposr", fallback="0")))
                self.txt_delay.setText(self.config.get("Paths", "delay_min", fallback=""))
                self.txt_computer_name.setText(self.config.get("Paths", "conputer_name", fallback=""))
            except FileNotFoundError:
                print("The config.ini file does not exist.")
        else:
            print("⚠️ config.ini not found, using default settings.")

        # ======================================================
        # 🔹 Tạo Log window (giữ tham chiếu vĩnh viễn)
        # ======================================================
        self.log_window = LogWindow(self)
        self.log_window.hide()

        sys.stdout = QTextEditLogger(self.log_window)
        sys.stderr = QTextEditLogger(self.log_window)




    # ===================== các hàm cũ (rút gọn mẫu) =====================
    def toggle_log_window(self):
        """Bật/tắt log panel mà không đóng chương trình."""
        if self.log_window.isVisible():
            self.log_window.hide()
            self.log_button.setText("Show Log")
        else:
            print("🪶 Opening Processing Log window...")
            # self.log_window.setWindowFlags(self.log_window.windowFlags() | Qt.WindowStaysOnTopHint) # luôn hiển thị trên cùng
            self.log_window.show()
            self.log_window.raise_()
            self.log_window.activateWindow()
            self.log_button.setText("Hide Log")

    def on_processes_state_changed(self, state):
        if state == 2:
            print("Checkbox 'Processes' is checked")
            return True
        else:
            print("Checkbox 'Processes' is unchecked")
            return False
    
    def get_exr_files_in_directory(self,directory):
            return [f for f in os.listdir(directory) if f.lower().endswith(".exr") and os.path.isfile(os.path.join(directory, f))]
    
    def process_new_files(self,source_folder, target_folder):
        # lấy danh sách file hiện tại trong thư mục
        # previous_files = self.get_exr_files_in_directory(source_folder)
        previous_files = []
        while True:
            # dừng chương trình
            status = self.config.get("Processing", "status")
            if status == "false":
                self.info_label.setText("Processing stopped process_new_files.")
                print("Processing stopped process_new_files.")
                return

            current_files = self.get_exr_files_in_directory(source_folder)

            new_files = [file for file in current_files if file not in previous_files]
            if new_files:
                self.info_label_process.setText("New files:" + str(new_files))
                print("New files:", new_files)

                for file in new_files:
                    source_path = os.path.join(source_folder, file)
                    target_path = os.path.join(target_folder, file)
                    while os.path.exists(target_path):
                        file_name, file_extension = os.path.splitext(file)
                        file = f"{file_name}_new{file_extension}"
                        target_path = os.path.join(target_folder, file)
                    try:
                        shutil.move(source_path, target_path)
                        self.info_label_process.setText(f"Moved {file} to {target_folder}") 
                        print(f"Moved {file} to {target_folder}")
                    except Exception as e:
                        print(f"Cannot move files. Maybe another program is using this file: {e}")
                    break
                    # previous_files.extend(new_files)
            time.sleep(5)

    def count_files_in_target(self, target_folder):
        while True:
            # dừng chương trình
            status = self.config.get("Processing", "status")
            if status == "false":
                self.info_label.setText("Processing stopped count_files_in_target.")
                print("Processing stopped count_files_in_target.")
                return
            
            exr_files = self.get_exr_files_in_directory(target_folder)
            self.info_label_process.setText(f"Number of EXR files in target folder: {len(exr_files)}")
            print(f"Number of EXR files in target folder: {len(exr_files)}")
            time.sleep(5)

    def create_folders(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def move1_files(self, source_folder, target_folder):
        exr_files = self.get_exr_files_in_directory(source_folder)
        # exr_files = []
        string_dict = str(source_folder)
        if exr_files:
            first_file = exr_files[0]
            source_path = os.path.join(string_dict, first_file)
            target_path = os.path.join(target_folder, first_file)
            while os.path.exists(target_path):
                file_name, file_extension = os.path.splitext(first_file)
                first_file = f"{file_name}_new{file_extension}"
                target_path = os.path.join(target_folder, first_file)
            try:
                shutil.move(source_path, target_path)
                self.info_label_process.setText(f"Moved 1 File {first_file} from {source_folder} to {target_folder}")
                print(f"Moved 1 File {first_file} from {source_folder} to {target_folder}")
                return True
            except Exception as e:
                print(f"Cannot move files. Maybe another program is using this file: {e}")
        else:
            self.info_label_process.setText("No files to move in the source folder")
            print("No files to move in the source folder")
            return False

    # Lặp vô hạn để kiểm tra thay đổi
    def has_file_changed(self,file_path):
        try:
            # Lấy kích thước tệp hiện tại
            current_size = os.path.getsize(file_path)
            if current_size == 0:
                return True  # Tệp có kích thước bằng 0 (trống)
            else:
                # Chờ một khoảng thời gian trước khi kiểm tra lại
                time.sleep(5)  # Chờ 5 giây (có thể thay đổi theo nhu cầu của bạn)
                new_size = os.path.getsize(file_path)
                if current_size == new_size:
                    return False  # Tệp không thay đổi
                else:
                    return True  # Tệp đã thay đổi
        except FileNotFoundError:
            print(" File does not exist.")
            time.sleep(5) 
            return True  # Tệp không tồn tại (có thể xem như đã thay đổi)
        except Exception as e:
            print(f"An error occurred.: {e}")
            time.sleep(5) 
            return True  # Có lỗi xảy ra (có thể xem như đã thay đổi)
    def check_png_files_in_directory(self,directory):
        png_files = [file for file in os.listdir(directory) if file.endswith('.png')]
        return len(png_files) > 0
    def check_exr_files_in_directory(self,directory):
        png_files = [file for file in os.listdir(directory) if file.endswith('.exr')]
        return len(png_files) > 0

    #quy trình làm việc với Processed
    def working_process_1(self, working_folder, complete_folder,working1_folder, complete1_folder, minutes):
        self.create_folders(working_folder)
        self.create_folders(complete_folder)
        while True:
            # dừng chương trình
            status = self.config.get("Processing", "status")
            if status == "false":
                self.info_label.setText("Processing stopped working_process_1.")
                print("Processing stopped working_process_1.")
                return
            #kiểm tra thưu mục working cso 1 file exr thì làm việc
            print("Check exr in folder Processed")
            exr_files = [file for file in os.listdir(complete_folder) if file.lower().endswith(".exr")]

            if len(exr_files) > 1:
                self.info_label_process.setText(f"There are {len(exr_files)} .exr files in the folder")
                print(f"There are {len(exr_files)} .exr files in the folder") 
                return
            elif len(exr_files) == 1:
                self.info_label_process.setText("There is 1 .exr file in the folder.")
                print("There is 1 .exr file in the folder.")
            else:
                print("No .exr files found in the folder.")
                #kiểm tra file đã được render xong chưa?
                exr_files_get = self.get_exr_files_in_directory(working_folder)
                string_dict = str(working_folder)
                if exr_files_get:
                    first_file = exr_files_get[0]
                    source_path = os.path.join(string_dict, first_file)
                    print("source_path: ",source_path)
                    min = int(minutes)
                    print(f"Delay in Munites {min}")
                    for i in range(min * 60 , 0, -1):
                        time.sleep(1)
                        print(f"Delay in Munites {i}")
                        self.info_label_process.setText(f"Delay in Munites {i}")
                        # dừng chương trình
                        status = self.config.get("Processing", "status")
                        if status == "false":
                            return
                    self.move1_files(working_folder, complete_folder)
                    self.info_label_process.setText("Moving files 1 from 'ouput' to 'working'...")
                    print("Moving files 1 from 'ouput' to 'working'...")
            # kiểm tra có file nào đc di chuyển không?
            has_exr_files = self.check_exr_files_in_directory(complete_folder)
            if has_exr_files:
                self.info_label_process.setText("handle psb Processed...")
                print("handle psb Processed...")
                try: 
                    print("Star Script Processed")
                    # mở EXR
                    exr_file = self.get_exr_file_paths_in_directory(complete_folder)
                    file_name = os.path.basename(str(exr_file[0]))
                    self.start_processing_open_exr(self.config_file_path,complete_folder)
                    while self.running_open_exr:
                        time.sleep(5)
                        current_document_name = self.get_current_document_name()
                        self.bring_photoshop_to_front(current_document_name)
                        print("currently in the process of opening the exr file")
                    print("opened exr file")
                    # Xác định thư mục chứa script, đồng thời hỗ trợ khi được đóng gói thành tệp exe
                    jsx_file_name = "Processed.jsx"
                    self.run_jsx(jsx_file_name)
                except FileNotFoundError:
                    self.info_label_process.setText("JSX file not found Processed")
                    print("JSX file not found Processed")
                except Exception as e:
                    self.info_label_process.setText("An error occurred Processed:")
                    print("An error occurred Processed:",e)
                self.info_label_process.setText("complete psb Processed...")
                print("complete psb Processed...")
                self.move1_files(working1_folder, complete1_folder)
                self.info_label_process.setText("working...")
                print("Moving files 1 from 'working' to 'complete' Processed...")
                self.running_open_exr = True
                time.sleep(5)
            else:
                print("The .exr file does not exist in the User folder of Processed")
                time.sleep(5)
    # Quy trình làm việc với prepost
    def working_process_2(self, working_folder, complete_folder):
        self.create_folders(working_folder)
        self.create_folders(complete_folder)
        
        while True:
            # Dừng chương trình nếu status là "false"
            status = self.config.get("Processing", "status")
            if status == "false":
                self.info_label.setText("Processing stopped working_process_2.")
                print("Processing stopped working_process_2.")
                return
            # Lấy danh sách tất cả các file .png trong 'complete' và lọc tên file (loại bỏ phần mở rộng)
            png_files = [os.path.splitext(file)[0] for file in os.listdir(working_folder) if file.lower().endswith(".png")]
            # Lấy danh sách tất cả các file .psb trong 'complete' và lọc tên file (loại bỏ phần mở rộng)
            psb_files = [os.path.splitext(file)[0] for file in os.listdir(working_folder) if file.lower().endswith(".psb")]
            # Tìm các tên .png có tên khác với tên .psb
            different_names = [png for png in png_files if png not in psb_files]
            name_file = ""
            check_time = False
            if different_names:
                print("List of .png files with different names from .psb files in folder:")
                for file in different_names:
                    print(file)
                    name_file = file
            else:
                print("There are no .png files with names different from the .psb filename. in folder")
                time.sleep(5)
                continue
            script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
            data_folder = os.path.join(script_folder, "data")
            self.create_folders( data_folder)
            txt_file_pngFile = os.path.join(data_folder, "pngFile.txt")
            pathfile1 = ''
            pathfile2 = ''
            with open(txt_file_pngFile, "w", encoding="utf-8") as file:
                for png in different_names:
                    png_path = os.path.join(complete_folder, png) 
                    parent_folder = os.path.dirname(png_path)
                    parent_folder_prepost = os.path.dirname(parent_folder)
                    # Thay thế phần 'prepost' bằng 'processed'
                    processed_folder = os.path.join(parent_folder_prepost, 'processed')
                    name_filePNG_prepost = png_path + ".png"
                    name_filePNG_processed = processed_folder +"/"+ name_file + ".png"
                    name_filePSD_processed = processed_folder +"/"+ name_file + ".psb"
                    check_time = self.compare_file_modification_time(name_filePNG_prepost, name_filePNG_processed)
                    
                    # Luôn cho phép xử lý PNG, bất kể thời gian
                    print("Process PNG (ignore time check).")
                   # ================== Kiểm tra sự tồn tại của cả 2 file ==================
                    if os.path.exists(name_filePNG_processed) and os.path.exists(name_filePSD_processed):
                        print(f"Both files exist in processed:\n   - {name_filePNG_processed}\n   - {name_filePSD_processed}")
                        check_time = True
                    else:
                        if not os.path.exists(name_filePNG_processed):
                            print(f"Missing PNG file in processed: {name_filePNG_processed}")
                        if not os.path.exists(name_filePSD_processed):
                            print(f"Missing PNG file in processed: {name_filePSD_processed}")
                        check_time = False
                        continue
                    # if check_time:
                    #     print("PNG has changed time")
                    # else:
                    #     print("PNG does not change time")
                    #      # kiểm tra thời gian hợp không lệ thì bỏ qua
                    #     continue
                    time.sleep(5)
                    png_path_user = os.path.join(complete_folder +'/Temp/'+ str(self.txt_computer_name.text()), png)
                    self.create_folders(complete_folder +'/Temp/'+ str(self.txt_computer_name.text()))
                    pathfile1 = png_path + ".png"
                    pathfile2 = png_path_user + ".png"
                    try:
                        shutil.move(png_path + ".png", png_path_user + ".png")
                    except Exception as e:
                        print('No file PNG');
                        continue
                    file.write(png_path_user + ".png" + "\n")
                    break
            # kiểm tra thời gian hợp không lệ thì bỏ qua
            if check_time == False:
                time.sleep(5)
                continue
            # kiểm tra file có tồn tại không trước khi vào photohsop .
            # Sử dụng hàm để kiểm tra thư mục
            png_path_user_prepost = complete_folder +'/Temp/'+ str(self.txt_computer_name.text())
            has_png_files = self.check_png_files_in_directory(png_path_user_prepost)
            if has_png_files:
                print("Folder prepost 1 PNG.")
                self.info_label_process.setText("handle psb prepost ...")
                print("handle psb prepost ...")
                # xử lý trong photoshop 
                try:
                    jsx_file_name = "prepost.jsx"
                    self.run_jsx(jsx_file_name)
                    try:
                        shutil.move(pathfile2, pathfile1)
                    except Exception as e:
                        print(f"Cannot move files. Maybe another program is using this file: {e}")
                except FileNotFoundError:
                    self.info_label_process.setText("JSX file not found prepost")
                    print("JSX file not found prepost")
                except Exception as e:
                    self.info_label_process.setText("An error occurred prepost:", e)
                    print("An error occurred prepost:", e)
                self.info_label_process.setText("complete psb prepost...")
                print("complete psb prepost...")
                time.sleep(5)
            else:
                print("Thư mục không chứa tệp PNG.")
    def run_jsx(self,filename):
        # Lấy thư mục ứng dụng thật
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        jsx_path = os.path.join(base_dir, "jsx", filename)

        if os.path.exists(jsx_path):
            print(f"▶ Running JSX: {filename}")
            pythoncom.CoInitialize()  
            try:
                app = ps.Application() 
                app.DoJavaScriptFile(jsx_path)
            except Exception as e:
                print("❌ Error running JSX:", e)
            finally:
                pythoncom.CoUninitialize()  
            print("✅ JSX executed successfully")
        else:
            print(f"❌ JSX not found: {jsx_path}")

    def get_file_modified_time(self,file_path):
        try:
            # Lấy thời gian sửa đổi của tệp
            modified_time = os.path.getmtime(file_path)
            # Chuyển đổi thời gian sửa đổi thành đối tượng datetime
            modified_time_dt = datetime.fromtimestamp(modified_time)
            return modified_time_dt
        except FileNotFoundError:
            return None

    def compare_file_modification_time(self,file_path1, file_path2):
        # Lấy thời gian sửa đổi của hai tệp
        modified_time1 = self.get_file_modified_time(file_path1)
        modified_time2 = self.get_file_modified_time(file_path2)

        if modified_time1 is not None and modified_time2 is not None:
            # Tính khoảng thời gian giữa hai thời điểm
            time_difference = (modified_time1 - modified_time2).total_seconds()
            # Kiểm tra nếu khoảng thời gian lớn hơn hoặc bằng 30 giây
            if time_difference >= 30:
                return True
            else:       
                return False
        else:
            return False
    # đặt chướng trình giữa màn hình
    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def start_processing(self):
        if self.folder_path_in.text() =='':
            self.info_label_process.setText("Select input folder")
            print("Error: Please select input folder")
            return
        delay_text = self.txt_delay.text()
        if not delay_text.isdigit():
            print("Error: Please enter Delay in Minutes as a positive integer.")
            self.info_label_process.setText("Error: Please enter Delay in Minutes as a positive integer.")
            return
        print("Start processing...")
        print("Folder Input:", self.folder_path_in.text())
        print("Selected Option:", self.selected_option.currentText())
        self.info_label_process.setText("Folder Input:" + self.folder_path_in.text())
        self.info_label_process.setText("Selected Option:" + self.selected_option.currentText())
        # lưu thông tin chọn thư mục
        source_folder = self.folder_path_in.text()
        chk_processes = str(int(self.checkbox_processes.isChecked()))
        chk_preposr = str(int(self.checkbox_prepost.isChecked()))
        delay_min = self.txt_delay.text()
        conputer_name = self.txt_computer_name.text()
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        self.create_folders( data_folder)
        config_file_path = os.path.join(data_folder, "config.ini")
        self.config["Paths"] = {
            "source_folder": source_folder,
            "chk_processes": chk_processes, 
            "chk_preposr": chk_preposr,
            "delay_min": delay_min,
            "conputer_name": conputer_name,
        }

        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        # Ghi nội dung vào file config.ini về nút star 
        self.config["Processing"] = {
            "status": "true",
        }
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        # Ghi nội dung vào file config.ini về open exr 
        self.config["Processing_exr"] = {
            "openEXR": "false",
        }
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        

        folder_processed = os.path.join(source_folder, "processed")
        folder_temp_user = os.path.join(folder_processed,"Temp")
        folder_temp = os.path.join(folder_temp_user, self.txt_computer_name.text())
        folder_prepost = os.path.join(source_folder, "prepost")
        self.create_folders( folder_processed)
        self.create_folders( folder_temp)
        self.create_folders( folder_prepost)
        # Lấy đường dẫn thư mục chứa tệp Python đang chạy Ghi nội dung vào file
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        self.create_folders( data_folder)
        txt_file_inputFolder = os.path.join(data_folder, "inputFolder.txt")
        txt_file_mode = os.path.join(data_folder, "mode.txt")
        txt_file_computer_name = os.path.join(data_folder, "computer_name.txt")
        txt_file_chk_processes = os.path.join(data_folder, "processes.txt")
        txt_file_chk_preposr = os.path.join(data_folder, "preposr.txt")
        minutes = int(self.txt_delay.text())
        with open(txt_file_inputFolder, "w") as file:
            file.write(self.folder_path_in.text())
        with open(txt_file_mode, "w") as file:
            file.write(self.selected_option.currentText())
        with open(txt_file_computer_name, "w") as file:
            file.write(conputer_name)
        with open(txt_file_chk_processes, "w") as file:
            file.write(chk_processes) 
        with open(txt_file_chk_preposr, "w") as file:
            file.write(chk_preposr)

        self.count_files_in_target_folder = Thread(target=self.count_files_in_target, args=(folder_temp,))
        self.processing_thread = Thread(target=self.check_processing_status)
        if chk_processes =="1":
            self.workflow_flow_1 = Thread(target=self.working_process_1, args=(self.folder_path_in.text(), folder_temp, folder_temp, folder_processed, minutes))
            # Bắt đầu kiểm tra trạng thái xử lý trong một luồng riêng
            self.workflow_flow_1.start()
        if chk_preposr =="1":
            self.workflow_flow_2 = Thread(target=self.working_process_2, args=(folder_prepost, folder_prepost))
            # Bắt đầu kiểm tra trạng thái xử lý trong một luồng riêng
            self.workflow_flow_2.start()
        
        # Bắt đầu kiểm tra trạng thái xử lý trong một luồng riêng
        self.count_files_in_target_folder.start()
        self.processing_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    ###########################################
    def start_processing_open_exr(self,config_file_path,file_path):
        self.tOpenEXR = Thread(target=self.open_EXR_file, args=(config_file_path,file_path))
        self.tOpenEXR.start()

        self.tAutoEnter = Thread(target=self.auto_press_enter, args=(2,file_path))
        self.tAutoEnter.start()
    def get_exr_file_paths_in_directory(self,directory):
        exr_file_paths = []
        for root, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(".exr"):
                    exr_file_paths.append(os.path.join(root, file))
        return exr_file_paths

    def get_current_document_name(self):
        pythoncom.CoInitialize()  
        try:
            app = ps.Application()  
            active_doc = app.ActiveDocument
            if active_doc:
                return active_doc.Name
            else:
                return "Adobe Photoshop"
        except Exception:
            return "Adobe Photoshop"
        finally:
            pythoncom.CoUninitialize()
    def bring_photoshop_to_front(self,current_document_name):
        photoshop_windows = gw.getWindowsWithTitle(current_document_name)
        if len(photoshop_windows) > 0:
            photoshop_windows[0].activate()
        else:
            print("Photoshop is not running.")
    def check_photoshop_status(self,current_document_name):
        # Lấy danh sách các cửa sổ có tiêu đề chứa 'Adobe Photoshop'
        photoshop_windows = gw.getWindowsWithTitle(current_document_name)
        if len(photoshop_windows) > 0:
            if photoshop_windows[0].isActive:
                return True
            else:
                return False
        else:
            return False

    def open_EXR_file(self,config_file_path,file_path):
        self.running = True
        self.config["Processing_exr"] = {"openEXR": "true"}
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        # print("Star: open_file_in_photoshop")
        self.open_file_in_photoshop(file_path)
        # print("End: open_file_in_photoshop")
        print("opened exr file finished")
        self.config["Processing_exr"] = {"openEXR": "false"}
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        self.running = False

    def open_file_in_photoshop(self, file_path):
        # print("Star trong: open_file_in_photoshop")
        try:
            exr_file = self.get_exr_file_paths_in_directory(file_path)
            # print("get_exr_file_paths_in_directory")
            # print(" app = ps.Application()")
            time.sleep(2)
            path_exr = os.path.normpath(exr_file[0])
            current_document_name = os.path.basename(str(exr_file[0]))
            # print("current_document_name: ",current_document_name)
            # print("Star: bring_photoshop_to_front")
            self.bring_photoshop_to_front(current_document_name)
           
            pythoncom.CoInitialize()
            try:
                app = ps.Application() 
                time.sleep(1)
                jsx = f"""
                    app.displayDialogs = DialogModes.NO;
                """
                app.DoJavaScript(jsx)
                time.sleep(1)
                if os.path.exists(path_exr):
                    print(f"🟢 Opening file: {path_exr}")
                    app.Open(path_exr)
                    print("✅ File opened successfully in Photoshop.")
                else:
                    print(f"❌ File not found: {path_exr}")
            except Exception as e:
                print("❌ Photoshop error while opening file:", e)
            finally:
                pythoncom.CoUninitialize()
            # message = "This is an alert message!"
            # js_code = f'alert("{message}");'  # Chuỗi JavaScript để hiển thị hộp thoại cảnh báo với nội dung được chỉ định
            # app.DoJavaScript(js_code)  # Thực thi mã JavaScript trong Photoshop
        except Exception as e:
            print("Error:", e)
        
        # time.sleep(1)
        # print("End trong: open_file_in_photoshop")

    def auto_press_enter(self, delay, folder_exr):
        print("[START] Thread auto_press_enter, running =", self.running)
        try:
            while self.running:
                try:
                    # Đọc trạng thái từ config
                    status = self.config.get("Processing_exr", "openEXR", fallback="false")
                    print("[AUTO] openEXR status:", status)

                    # Lấy document hiện tại
                    current_document_name = self.get_current_document_name()
                    print("[AUTO] Current document:", current_document_name)

                    # Cố gắng đưa Photoshop ra trước
                    try:
                        self.bring_photoshop_to_front(current_document_name)
                    except Exception as e:
                        print("[WARN] bring_photoshop_to_front error:", e)

                    # Nếu đang mở file EXR → nhấn Enter
                    if status == "true":
                        time.sleep(delay)
                        pyautogui.press('enter')
                        print("[AUTO] Pressed ENTER (Photoshop active).")

                    time.sleep(1)

                except Exception as inner_e:
                    print("[ERROR] Loop auto_press_enter:", inner_e)
                    time.sleep(1)
                    continue

        except Exception as outer_e:
            print("[FATAL] auto_press_enter crashed:", outer_e)

        finally:
            # Dọn dẹp khi dừng
            time.sleep(delay)
            print("[EXIT] Exiting auto_press_enter thread.")
            self.running_open_exr = False
            print("[END] Thread auto_press_enter ended cleanly.")


    ########################################################
    def stop_processing(self):
        self.info_label.setText("Stop processing...")
        print("Stop processing...")
        # Ghi nội dung vào file config.ini
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        self.create_folders( data_folder)        
        config_file_path = os.path.join(data_folder, "config.ini")
        self.config["Processing"] = {
            "status": "false"
        }
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        #Stop OpenEXR
        self.running = False
        self.config["Processing_exr"] = {"openEXR": "false"}
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def check_processing_status(self):
        a = 0
        while True:
            # dừng chương trình
            a += 1
            status = self.config.get("Processing", "status")
            if status == "false":
                self.info_label.setText("Processing stopped check_processing_status.")
                print("Processing stopped check_processing_status.")
                return
            
            self.info_label.setText(f"Processing started...  {str(a)} second")  # Update info label
            print("Star processing..." + str(a))
            time.sleep(1)  # Đợi 5 giây trước khi kiểm tra lại

    def select_folder_in(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.folder_path_in.setText(folder)

    def select_folder_out(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.folder_path_out.setText(folder)

    def close_application(self):
        script_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        data_folder = os.path.join(script_folder, "data")
        self.create_folders( data_folder)
        config_file_path = os.path.join(data_folder, "config.ini")
        self.config["Processing"] = {
            "status": "false"
        }
        with open(config_file_path, "w") as configfile:
            self.config.write(configfile)
            
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainController()
    win.show()
    sys.exit(app.exec_())
