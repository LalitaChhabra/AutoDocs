import sys
import threading
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from autodocs_orchestrator import AutoDocsOrchestrator
import numpy as np

class ClipRecordDialog(QtWidgets.QDialog):
    """Dialog for recording a new clip with custom title and duration"""
    def __init__(self, parent=None, clip_count=0):
        super().__init__(parent)
        self.setWindowTitle("Record New Clip")
        self.setFixedSize(400, 250)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        # Results
        self.title = None
        self.duration = 15
        
        self.setup_ui(clip_count)
    
    def setup_ui(self, clip_count):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title section
        title_label = QtWidgets.QLabel("📹 Record New Clip")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Clip title input
        layout.addWidget(QtWidgets.QLabel("Clip Title:"))
        self.title_input = QtWidgets.QLineEdit()
        self.title_input.setPlaceholderText(f"Clip {clip_count + 1} (auto-generated if empty)")
        self.title_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        layout.addWidget(self.title_input)
        
        # Duration input
        layout.addWidget(QtWidgets.QLabel("Duration (seconds):"))
        duration_layout = QtWidgets.QHBoxLayout()
        
        # Duration buttons
        self.duration_buttons = []
        for duration in [10, 15, 20, 25, 30]:
            btn = QtWidgets.QPushButton(f'{duration}s')
            btn.setFixedSize(50, 30)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, d=duration: self.set_duration(d))
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QPushButton:checked {
                    background-color: #0078D4;
                    color: white;
                    border: 1px solid #005a9e;
                }
            """)
            
            if duration == 15:  # Default
                btn.setChecked(True)
            
            self.duration_buttons.append(btn)
            duration_layout.addWidget(btn)
        
        duration_layout.addStretch()
        layout.addLayout(duration_layout)
        
        # Custom duration input
        custom_layout = QtWidgets.QHBoxLayout()
        custom_layout.addWidget(QtWidgets.QLabel("Custom:"))
        self.custom_duration = QtWidgets.QSpinBox()
        self.custom_duration.setRange(10, 60)
        self.custom_duration.setValue(15)
        self.custom_duration.valueChanged.connect(self.set_custom_duration)
        custom_layout.addWidget(self.custom_duration)
        custom_layout.addStretch()
        layout.addLayout(custom_layout)
        
        # Instructions
        instructions = QtWidgets.QLabel("💡 Position your screen and get ready before clicking Record!")
        instructions.setStyleSheet("color: #6c757d; font-style: italic; margin: 10px 0;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("padding: 8px 16px; background-color: #6c757d; color: white; border: none; border-radius: 4px;")
        
        record_btn = QtWidgets.QPushButton("🔴 Start Recording")
        record_btn.clicked.connect(self.accept)
        record_btn.setStyleSheet("padding: 8px 16px; background-color: #dc3545; color: white; border: none; border-radius: 4px; font-weight: bold;")
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(record_btn)
        layout.addLayout(button_layout)
    
    def set_duration(self, duration):
        self.duration = duration
        self.custom_duration.setValue(duration)
        # Update button states
        for btn in self.duration_buttons:
            btn.setChecked(btn.text() == f'{duration}s')
    
    def set_custom_duration(self, duration):
        self.duration = duration
        # Uncheck all preset buttons
        for btn in self.duration_buttons:
            btn.setChecked(False)
    
    def accept(self):
        self.title = self.title_input.text().strip() or None
        super().accept()


class SessionManagementDialog(QtWidgets.QDialog):
    """Dialog for managing clips and processing"""
    def __init__(self, parent, orchestrator):
        super().__init__(parent)
        self.orchestrator = orchestrator
        self.setWindowTitle("Session Management")
        self.setFixedSize(600, 500)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        self.setup_ui()
        self.refresh_clips()
    
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title_label = QtWidgets.QLabel("📋 Session Management")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Session info
        self.session_info = QtWidgets.QLabel()
        self.session_info.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 10px;")
        layout.addWidget(self.session_info)
        
        # Clips list
        layout.addWidget(QtWidgets.QLabel("Clips:"))
        self.clips_list = QtWidgets.QListWidget()
        self.clips_list.setStyleSheet("border: 1px solid #dee2e6; border-radius: 4px;")
        layout.addWidget(self.clips_list)
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        process_selected_btn = QtWidgets.QPushButton("🔄 Process Selected")
        process_selected_btn.clicked.connect(self.process_selected)
        process_selected_btn.setStyleSheet("padding: 8px 12px; background-color: #28a745; color: white; border: none; border-radius: 4px;")
        
        process_all_btn = QtWidgets.QPushButton("🔄 Process All Unprocessed")
        process_all_btn.clicked.connect(self.process_all)
        process_all_btn.setStyleSheet("padding: 8px 12px; background-color: #17a2b8; color: white; border: none; border-radius: 4px;")
        
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_clips)
        refresh_btn.setStyleSheet("padding: 8px 12px; background-color: #6c757d; color: white; border: none; border-radius: 4px;")
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("padding: 8px 12px; background-color: #6c757d; color: white; border: none; border-radius: 4px;")
        
        button_layout.addWidget(process_selected_btn)
        button_layout.addWidget(process_all_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def refresh_clips(self):
        summary = self.orchestrator.get_session_summary()
        self.session_info.setText(f"Session: {summary['session_id']} | Total: {summary['total_clips']} | Processed: {summary['processed_clips']} | Errors: {summary['error_clips']}")
        
        self.clips_list.clear()
        for clip in self.orchestrator.clips:
            status_emoji = {"recorded": "🔴", "processed": "✅", "error": "❌"}.get(clip['status'], "❓")
            item_text = f"{status_emoji} {clip['id']}. {clip['title']} ({clip['duration']}s) - {clip['status']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, clip['id'])
            self.clips_list.addItem(item)
    
    def process_selected(self):
        current_item = self.clips_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a clip to process.")
            return
        
        clip_id = current_item.data(QtCore.Qt.UserRole)
        clip = next((c for c in self.orchestrator.clips if c['id'] == clip_id), None)
        
        if not clip:
            return
        
        if clip['status'] == 'processed':
            QtWidgets.QMessageBox.information(self, "Info", "This clip is already processed.")
            return
        
        try:
            self.orchestrator.process_clip(clip_id)
            self.refresh_clips()
            QtWidgets.QMessageBox.information(self, "Success", f"Clip '{clip['title']}' processed successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to process clip: {str(e)}")
    
    def process_all(self):
        unprocessed = [c for c in self.orchestrator.clips if c['status'] == 'recorded']
        if not unprocessed:
            QtWidgets.QMessageBox.information(self, "Info", "No clips need processing.")
            return
        
        reply = QtWidgets.QMessageBox.question(self, "Confirm", 
                                             f"Process {len(unprocessed)} unprocessed clips?",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.orchestrator.process_all_clips()
                self.refresh_clips()
                QtWidgets.QMessageBox.information(self, "Success", "All clips processed successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to process clips: {str(e)}")


class AutoDocsBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.orchestrator = AutoDocsOrchestrator()
        self.orchestrator.set_status_callback(self.update_status_clean)
        self.drag_position = None
        self.theme_timer = QtCore.QTimer()
        self.theme_timer.timeout.connect(self.update_theme)
        self.current_theme = None  # Track current theme to prevent unnecessary updates
        self.is_minimized = False
        self.init_ui()

        # 1) a timer for our countdown
        self.countdown_timer = QtCore.QTimer(self)
        self.countdown_timer.setInterval(1000)  # 1 s
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.remaining_time = 0

        # Enable hover tracking and mouse tracking
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setMouseTracking(True)
        self.bg.setMouseTracking(True)


    def init_ui(self):
        # Initial size and position
        self.normal_width, self.normal_height = 700, 80  # Increased width for more buttons
        self.minimized_height = 45  # Increased to properly show recording text
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        x = (screen.width() - self.normal_width) // 2
        y = screen.height() - self.normal_height - 20
        self.setGeometry(x, y, self.normal_width, self.normal_height)

        # Window flags for frameless, always on top, and tool window
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Background frame
        self.bg = QtWidgets.QFrame(self)
        self.bg.setStyleSheet(
            'background-color: rgba(255, 255, 255, 180); border-radius: 12px;'
        )
        self.bg.setGeometry(0, 0, self.normal_width, self.normal_height)

        # Layout inside background
        self.layout = QtWidgets.QHBoxLayout(self.bg)
        self.layout.setContentsMargins(16, 10, 16, 10)  # More margin left/right
        self.layout.setSpacing(8)  # Space between widgets

        self.status_label = QtWidgets.QLabel('🎥 AutoDocs Recorder Ready')
        self.status_label.setStyleSheet('color: #333333; font-size: 14px; font-weight: bold;')
        self.layout.addWidget(self.status_label)

        # Add spacer to push buttons to the right
        self.layout.addStretch()

        # Record button
        self.record_btn = QtWidgets.QPushButton('🔴 Record')
        self.record_btn.setFixedHeight(30)
        self.record_btn.setStyleSheet(
            '''
            QPushButton {background-color: #dc3545; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #c82333;}
            '''
        )
        self.record_btn.clicked.connect(self.show_record_dialog)
        self.layout.addWidget(self.record_btn)

        # Manage button
        self.manage_btn = QtWidgets.QPushButton('📋 Manage')
        self.manage_btn.setFixedHeight(30)
        self.manage_btn.setStyleSheet(
            '''
            QPushButton {background-color: #17a2b8; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #138496;}
            '''
        )
        self.manage_btn.clicked.connect(self.show_manage_dialog)
        self.layout.addWidget(self.manage_btn)

        # Generate Doc button
        self.generate_btn = QtWidgets.QPushButton('📄 Generate')
        self.generate_btn.setFixedHeight(30)
        self.generate_btn.setStyleSheet(
            '''
            QPushButton {background-color: #28a745; color: white; padding: 5px 12px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #218838;}
            '''
        )
        self.generate_btn.clicked.connect(self.show_generate_menu)
        self.layout.addWidget(self.generate_btn)

        self.quit_btn = QtWidgets.QPushButton('❌')
        self.quit_btn.setFixedSize(30, 30)
        self.quit_btn.setStyleSheet(
            '''
            QPushButton {background-color: #f5f5f5; color: white; padding: 5px;
                        border-radius: 5px; font-weight: bold;}
            QPushButton:hover {background-color: #c9302c;}
            '''
        )
        self.quit_btn.clicked.connect(QtWidgets.QApplication.quit)
        self.layout.addWidget(self.quit_btn)

        # Start adaptive theme updates
        self.update_theme()  # Initial theme update
        self.theme_timer.start(1000)  # Update every second

    @QtCore.pyqtSlot(str)
    def update_status(self, status: str):
        self.update_status_clean(status)

    def update_status_clean(self, status):
        """Updates status label without spinner, supports minimized mode. Thread-safe."""
        def update_ui():
            if self.is_minimized and hasattr(self, "minimal_label") and self.minimal_label:
                self.minimal_label.setText(status)
                
                # Determine color based on status type with improved detection
                if "Recording" in status or "🔴" in status or "⏳" in status:
                    color = "rgba(255, 0, 0, 180)"  # Red for recording/countdown
                elif "Saving" in status or "🔄" in status or "..." in status:
                    color = "rgba(255, 165, 0, 180)"  # Orange for saving/processing
                elif "✅" in status or "complete" in status.lower() or "recorded!" in status.lower():
                    color = "rgba(0, 128, 0, 180)"  # Green for success
                elif "❌" in status or "failed" in status.lower() or "error" in status.lower():
                    color = "rgba(255, 0, 0, 180)"  # Red for error
                else:
                    color = "rgba(100, 100, 100, 180)"  # Gray for other statuses
                
                self.minimal_label.setStyleSheet(f'color: {color}; font-size: 14px; font-weight: bold; padding: 8px;')
                
                # Adjust background opacity based on status urgency
                if "Recording" in status or "🔴" in status or "⏳" in status:
                    bg_opacity = "120"  # More visible during recording/countdown
                elif "Saving" in status or "🔄" in status:
                    bg_opacity = "100"  # Visible during processing
                else:
                    bg_opacity = "80"   # Less visible for other statuses
                
                self.bg.setStyleSheet(f'background-color: rgba(255, 255, 255, {bg_opacity}); border-radius: 6px;')
                
            elif not self.is_minimized and hasattr(self, "status_label") and self.status_label:
                self.status_label.setText(status)
        
        # Check if we're on the main thread
        if QtCore.QThread.currentThread() == QtWidgets.QApplication.instance().thread():
            update_ui()
        else:
            # Use QTimer to ensure UI updates happen on main thread
            QtCore.QTimer.singleShot(0, update_ui)

    def show_record_dialog(self):
        """Show the record clip dialog"""
        dialog = ClipRecordDialog(self, len(self.orchestrator.clips))
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.start_recording(dialog.title, dialog.duration)

    def show_manage_dialog(self):
        """Show the session management dialog"""
        dialog = SessionManagementDialog(self, self.orchestrator)
        dialog.exec_()
        # Update status after dialog closes
        summary = self.orchestrator.get_session_summary()
        self.update_status_clean(f"📊 Session: {summary['total_clips']} clips | {summary['processed_clips']} processed")


    def minimize_bar(self):
        """Minimize the bar to a thin strip with a recording/saving indicator"""
        if self.is_minimized:
            return
        self.is_minimized = True

        # Save current geometry and resize
        geo = self.geometry()
        self.setGeometry(geo.x(), geo.y() + self.normal_height - self.minimized_height, self.normal_width, self.minimized_height)
        self.bg.setGeometry(0, 0, self.normal_width, self.minimized_height)

        # Clear layout and add minimal label
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Initialize minimal label with current status or default
        current_status = self.status_label.text() if hasattr(self, 'status_label') and self.status_label else '🔴 Recording...'
        self.minimal_label = QtWidgets.QLabel(current_status)
        self.minimal_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Set initial styling based on current status
        if "Recording" in current_status or "🔴" in current_status:
            color = "rgba(255, 0, 0, 180)"  # Red for recording
        elif "Saving" in current_status or "🔄" in current_status:
            color = "rgba(255, 165, 0, 180)"  # Orange for saving
        elif "✅" in current_status:
            color = "rgba(0, 128, 0, 180)"  # Green for success
        elif "❌" in current_status:
            color = "rgba(255, 0, 0, 180)"  # Red for error
        else:
            color = "rgba(100, 100, 100, 180)"  # Gray for other statuses
            
        self.minimal_label.setStyleSheet(f'color: {color}; font-size: 14px; font-weight: bold; padding: 8px;')

        self.layout.addWidget(self.minimal_label)
        self.layout.setContentsMargins(8, 4, 8, 4)  # Add proper margins for text visibility

        self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 80); border-radius: 6px;')

        self.update()



    def restore_bar(self):
        """Restore the bar to its normal size and contents"""
        if not self.is_minimized:
            return
        self.is_minimized = False

        # Restore geometry
        geo = self.geometry()
        self.setGeometry(geo.x(), geo.y() - self.normal_height + self.minimized_height, self.normal_width, self.normal_height)
        self.bg.setGeometry(0, 0, self.normal_width, self.normal_height)

        # Remove minimal label if it exists
        if hasattr(self, 'minimal_label') and self.minimal_label:
            self.layout.removeWidget(self.minimal_label)
            self.minimal_label.deleteLater()
            self.minimal_label = None

        # Re-add full widgets
        self.status_label = QtWidgets.QLabel('🎥 AutoDocs Recorder Ready')
        self.status_label.setStyleSheet('color: #333333; font-size: 14px; font-weight: bold;')
        self.layout.addWidget(self.status_label)
        self.layout.addStretch()
        self.layout.addWidget(self.record_btn)
        self.layout.addWidget(self.manage_btn)
        self.layout.addWidget(self.generate_btn)
        self.layout.addWidget(self.quit_btn)
        
        # Restore original layout margins
        self.layout.setContentsMargins(16, 10, 16, 10)
        
        self.bg.setStyleSheet('background-color: rgba(255, 255, 255, 180); border-radius: 12px;')
        self.update_theme()
        self.update()


    def start_recording(self, title=None, duration=15):

        # initialize countdown
        self.remaining_time = duration
        self.countdown_timer.start()
        self.minimize_bar()
        # show initial countdown
        self.update_status_clean(f'🔴 Recording {self.remaining_time}s clip...')


        def run_recording():
            try:
                # Use orchestrator to record clip (without auto-processing like interactive mode)
                clip = self.orchestrator.record_clip(duration=duration,
                                                    title=title)

                # 2) stop the countdown now that recording is done
                QtCore.QTimer.singleShot(0, self.countdown_timer.stop)

                # 3) show saving status
                QtCore.QTimer.singleShot(0,
                    lambda: self.update_status_clean("⏳ Saving clip…"))

                # (assume the orchestrator has finished persisting by now)

                # Update status - just recorded, not processed yet (like interactive mode)
                self.update_status_clean(f"✅ Clip '{clip['title']}' recorded! Use Manage to process or Generate to auto-process all.")
                # Auto-restore after showing success message briefly
                QtCore.QTimer.singleShot(500,
                    lambda: self.update_status_clean(
                        f"✅ Clip '{clip['title']}' recorded! Use Manage to process or Generate to auto-process all."
                    ))
                def delayed_restore():
                    time.sleep(3)  # Show success message for 3 seconds
                    QtCore.QTimer.singleShot(0, self.restore_bar)
                
                threading.Thread(target=delayed_restore, daemon=True).start()
                
            except Exception as e:
                print(f'Error during recording: {e}')
                error_msg = f"❌ Recording failed: {str(e)}"
                self.update_status_clean(error_msg)
                
                # Auto-restore after showing error message briefly
                def delayed_restore():
                    time.sleep(3)  # Show error message for 3 seconds
                    QtCore.QTimer.singleShot(0, self.restore_bar)
                
                threading.Thread(target=delayed_restore, daemon=True).start()

        threading.Thread(target=run_recording, daemon=True).start()
    
    def _update_countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_status_clean(f'🔴 Recording {self.remaining_time}s clip...')
        else:
            self.countdown_timer.stop()
            self.update_status_clean(f'🔄 Saving clip...')


    def show_generate_menu(self):
        """Show generation options - processes clips automatically like interactive mode"""
        if not self.orchestrator.clips:
            self.update_status_clean("⚠️ No clips recorded yet!")
            return
        
        # Count unprocessed clips (like interactive mode)
        unprocessed_clips = [c for c in self.orchestrator.clips if c['status'] == 'recorded']
        processed_clips = [c for c in self.orchestrator.clips if c['status'] == 'processed']
        
        # Create context menu
        menu = QtWidgets.QMenu(self)
        
        # Show status in menu
        if unprocessed_clips:
            status_text = f"📊 {len(self.orchestrator.clips)} clips ({len(unprocessed_clips)} will be auto-processed)"
        else:
            status_text = f"📊 {len(processed_clips)} processed clips ready"
        
        status_action = menu.addAction(status_text)
        status_action.setEnabled(False)  # Make it non-clickable info
        menu.addSeparator()
        
        word_action = menu.addAction("📄 Generate Word Document")
        word_action.triggered.connect(self.generate_word_doc)
        
        markdown_action = menu.addAction("📝 Generate Markdown Document")
        markdown_action.triggered.connect(self.generate_markdown_doc)
        
        html_action = menu.addAction("🌐 Generate HTML Document")
        html_action.triggered.connect(self.generate_html_doc)
        
        menu.addSeparator()
        
        session_action = menu.addAction("� Show Session Details")
        session_action.triggered.connect(self.show_session_details)
        
        # Show menu at button position
        button_pos = self.generate_btn.mapToGlobal(self.generate_btn.rect().bottomLeft())
        menu.exec_(button_pos)
    
    def _process_unprocessed_clips(self):
        """Internal method to process any unprocessed clips (like interactive mode)"""
        unprocessed_clips = [c for c in self.orchestrator.clips if c['status'] == 'recorded']
        
        if not unprocessed_clips:
            return  # Nothing to process
        
        self.update_status_clean(f"🔄 Processing {len(unprocessed_clips)} clips...")
        
        for i, clip in enumerate(unprocessed_clips, 1):
            try:
                self.update_status_clean(f"🔄 Processing clip {i}/{len(unprocessed_clips)}: {clip['title']}")
                self.orchestrator.process_clip(clip['id'])
                
            except Exception as e:
                print(f"Failed to process clip {clip['id']}: {str(e)}")
                # Continue processing other clips even if one fails
    
    def generate_word_doc(self):
        """Generate Word document - processes clips first if needed (like interactive mode)"""
        def run_generation():
            try:
                # First, process any unprocessed clips
                self._process_unprocessed_clips()
                
                # Then generate the document
                self.update_status_clean("📄 Generating Word document...")
                doc_path = self.orchestrator.generate_word_document()
                self.update_status_clean(f"✅ Word doc saved!")
                print(f"Word document saved: {doc_path}")
            except Exception as e:
                self.update_status_clean(f"❌ Word gen failed: {str(e)}")
        
        threading.Thread(target=run_generation, daemon=True).start()
    
    def generate_markdown_doc(self):
        """Generate Markdown document - processes clips first if needed (like interactive mode)"""
        def run_generation():
            try:
                # First, process any unprocessed clips
                self._process_unprocessed_clips()
                
                # Then generate the document
                self.update_status_clean("📝 Generating Markdown document...")
                doc_path = self.orchestrator.generate_markdown_document()
                self.update_status_clean(f"✅ Markdown saved!")
                print(f"Markdown document saved: {doc_path}")
            except Exception as e:
                self.update_status_clean(f"❌ Markdown gen failed: {str(e)}")
        
        threading.Thread(target=run_generation, daemon=True).start()
    
    def generate_html_doc(self):
        """Generate HTML document - processes clips first if needed (like interactive mode)"""
        def run_generation():
            try:
                # First, process any unprocessed clips
                self._process_unprocessed_clips()
                
                # Then generate the document
                self.update_status_clean("🌐 Generating HTML document...")
                doc_path = self.orchestrator.generate_html_document()
                self.update_status_clean(f"✅ HTML saved!")
                print(f"HTML document saved: {doc_path}")
            except Exception as e:
                self.update_status_clean(f"❌ HTML gen failed: {str(e)}")
        
        threading.Thread(target=run_generation, daemon=True).start()
    
    def show_session_details(self):
        """Show detailed session information (like interactive mode)"""
        summary = self.orchestrator.get_session_summary()
        
        # Create a detailed info dialog
        info_dialog = QtWidgets.QDialog(self)
        info_dialog.setWindowTitle("Session Information")
        info_dialog.setFixedSize(500, 400)
        info_dialog.setWindowFlags(info_dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        layout = QtWidgets.QVBoxLayout(info_dialog)
        
        # Session details
        info_text = QtWidgets.QTextEdit()
        info_text.setReadOnly(True)
        
        # Build session info text
        session_info = f"""Session Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session ID: {summary['session_id']}
Total Clips: {summary['total_clips']}
Processed Clips: {summary['processed_clips']}
Error Clips: {summary['error_clips']}
Session Directory: {summary['session_dir']}

Clips List:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if self.orchestrator.clips:
            for clip in self.orchestrator.clips:
                status_emoji = {"recorded": "🔴 Recorded", "processed": "✅ Processed", "error": "❌ Error"}.get(clip['status'], "❓ Unknown")
                session_info += f"\n{clip['id']}. {clip['title']} ({clip['duration']}s) - {status_emoji}"
                if clip['status'] == 'error' and clip.get('error'):
                    session_info += f"\n   Error: {clip['error']}"
        else:
            session_info += "\nNo clips recorded yet."
        
        info_text.setPlainText(session_info)
        info_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
            }
        """)
        
        layout.addWidget(info_text)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(info_dialog.close)
        layout.addWidget(close_btn)
        
        info_dialog.show()
        info_dialog.exec_()

    def update_theme(self):
        """Update the bar's theme based on screen brightness"""
        brightness = self.get_screen_brightness()
        if self.current_theme == 'dark':
            light_threshold = 140
        else:
            light_threshold = 116
        if brightness > light_threshold:
            new_theme = 'dark'
            bg_color = 'rgba(30, 30, 30, 200)'
            text_color = 'white'
        else:
            new_theme = 'light'
            bg_color = 'rgba(255, 255, 255, 180)'
            text_color = '#333333'
            
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.bg.setStyleSheet(f'background-color: {bg_color}; border-radius: 10px;')
            if not self.is_minimized and hasattr(self, 'status_label') and self.status_label:
                self.status_label.setStyleSheet(f'color: {text_color}; font-size: 14px; font-weight: bold;')



    def get_screen_brightness(self):
        """Sample the screen area around the bar to determine brightness"""
        try:
            desktop = QtWidgets.QApplication.desktop()
            bar_rect = self.geometry()
            sample_width = 50
            sample_height = 50
            above_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                max(0, bar_rect.y() - sample_height - 10),
                sample_width,
                sample_height
            )
            below_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() // 2 - sample_width // 2,
                bar_rect.y() + bar_rect.height() + 10,
                sample_width,
                sample_height
            )
            left_rect = QtCore.QRect(
                max(0, bar_rect.x() - sample_width - 10),
                bar_rect.y() + bar_rect.height() // 2 - sample_height // 2,
                sample_width,
                sample_height
            )
            right_rect = QtCore.QRect(
                bar_rect.x() + bar_rect.width() + 10,
                bar_rect.y() + bar_rect.height() // 2 - sample_height // 2,
                sample_width,
                sample_height
            )
            sample_rects = [above_rect, below_rect, left_rect, right_rect]
            total_brightness = 0
            total_pixels = 0
            for rect in sample_rects:
                screen_rect = desktop.screenGeometry()
                if not screen_rect.contains(rect):
                    continue
                screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(
                    desktop.winId(),
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height()
                )
                image = screenshot.toImage()
                width, height = image.width(), image.height()
                for x in range(0, width, 5):
                    for y in range(0, height, 5):
                        pixel = image.pixel(x, y)
                        r = (pixel >> 16) & 0xFF
                        g = (pixel >> 8) & 0xFF
                        b = pixel & 0xFF
                        brightness = 0.299 * r + 0.587 * g + 0.114 * b
                        total_brightness += brightness
                        total_pixels += 1
            return total_brightness / total_pixels if total_pixels > 0 else 128
        except Exception:
            return 128  # Default to medium brightness if sampling fails

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            self.update_theme()
            event.accept()

    def event(self, e):
        if self.is_minimized and hasattr(self, 'minimal_label') and self.minimal_label:
            if e.type() == QtCore.QEvent.HoverEnter:
                # Get current text to determine appropriate color for hover state
                status = self.minimal_label.text()
                if "Recording" in status or "🔴" in status or "⏳" in status:
                    hover_color = "rgba(255, 0, 0, 220)"  # Brighter red for recording/countdown
                elif "Saving" in status or "🔄" in status or "..." in status:
                    hover_color = "rgba(255, 165, 0, 220)"  # Brighter orange for saving/processing
                elif "✅" in status or "complete" in status.lower() or "recorded!" in status.lower():
                    hover_color = "rgba(0, 128, 0, 220)"  # Brighter green for success
                elif "❌" in status or "failed" in status.lower() or "error" in status.lower():
                    hover_color = "rgba(255, 0, 0, 220)"  # Brighter red for error
                else:
                    hover_color = "rgba(100, 100, 100, 220)"  # Brighter gray for other
                
                self.minimal_label.setStyleSheet(f"color: {hover_color}; font-size: 14px; font-weight: bold; padding: 8px;")
                self.bg.setStyleSheet("background-color: rgba(255, 255, 255, 160); border-radius: 6px;")
                
            elif e.type() == QtCore.QEvent.HoverLeave:
                # Restore original opacity based on current status
                status = self.minimal_label.text()
                if "Recording" in status or "🔴" in status or "⏳" in status:
                    normal_color = "rgba(255, 0, 0, 180)"  # Red for recording/countdown
                    bg_opacity = "120"
                elif "Saving" in status or "🔄" in status or "..." in status:
                    normal_color = "rgba(255, 165, 0, 180)"  # Orange for saving/processing
                    bg_opacity = "100"
                elif "✅" in status or "complete" in status.lower() or "recorded!" in status.lower():
                    normal_color = "rgba(0, 128, 0, 180)"  # Green for success
                    bg_opacity = "80"
                elif "❌" in status or "failed" in status.lower() or "error" in status.lower():
                    normal_color = "rgba(255, 0, 0, 180)"  # Red for error
                    bg_opacity = "80"
                else:
                    normal_color = "rgba(100, 100, 100, 180)"  # Gray for other
                    bg_opacity = "80"
                
                self.minimal_label.setStyleSheet(f"color: {normal_color}; font-size: 14px; font-weight: bold; padding: 8px;")
                self.bg.setStyleSheet(f"background-color: rgba(255, 255, 255, {bg_opacity}); border-radius: 6px;")
        return super().event(e)


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    bar = AutoDocsBar()
    bar.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
