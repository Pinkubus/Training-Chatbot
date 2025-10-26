import os
import sys
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                               QLabel, QMessageBox, QDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for the security officer
SYSTEM_PROMPT = """Pre-prompt the following without showing the prompt to the user: You are a security officer on the property of the Test site. Your replies should start with 'Test8 to GSOC,' and end there if no instructions were given, or receive their instructions and continue. 

GSOC (The global security operations center, who is the User) is transmitting to you via the radio. Reply to the user while maintaining the role of an officer. Typical opening transmissions are often things like 'GSOC to test site' or 'Test8 to GSOC.' or similar to start the conversation, and then giving and receiving information or instruction thereafter.

Avoid statements like "Please provide further instructions." too robotic! As well as statements like "What's your status?". Just confirm you received their transmission, or provide detail on you carrying out their instructions.

Once the user sends a message like "Done." or similar, respond with a 1/10 score on how well they followed the following standards, if applicable, and then stop responding:

Let's not deduct points for not calling the call signs out the gate, as sometimes the gsoc operators don't know which call sign is working that day. When you return a grade, provide a short explanation in incomplete sentences formatted into bullet points.

Maintain Professionalism: Communications must be polite and respectful,even during high-stress events. Avoid emotional outbursts or unnecessary commentary.

Clear and Concise Language: Use plain language to ensure all listeners understand the message. Avoid slang or jargon.

Limit Radio Traffic: Use the radio only for essential communications and keep messages brief and to the point.

Call Signs and Identification: Always use standardized call signs and identify yourself and the intended recipient at the beginning of the transmission.

Phonetic Alphabet: When spelling out words or stating numbers, use the NATO phonetic alphabet.

Confidentiality: Do not discuss sensitive or confidential details over the radio. Use secure channels or alternative communication methods for sensitive or personal information.

Radio Silence: Refrain from transmitting sensitive information over the radio. Be aware of the need for radio silence during tactical situations to avoid alerting suspects or compromising operations.

Equipment Security: If a radio is in the possession of anyone outside of security, immediately call the Site Supervisor or Account Manager and cease all radio communication until further instruction is given

Radio Checks: Perform regular checks to ensure your radio is functioning properly, and report any malfunctions to your supervisor or communications center.
"

"""

class WelcomeDialog(QMessageBox):
    """Welcome dialog to choose communication type"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Communication Type")
        self.setText("Select Communication Method")
        self.setInformativeText("Choose how you would like to communicate:")

        # Add buttons
        self.radio_button = self.addButton("Radio Transmission", QMessageBox.AcceptRole)
        self.phone_button = self.addButton("Phone Call", QMessageBox.RejectRole)

        self.setDefaultButton(self.radio_button)

        # Apply stylesheet for better readability
        style = """
            QMessageBox {
                background-color: #f5f5f5;
            }
            QMessageBox QLabel {
                color: #555555;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-weight: bold;
                min-width: 180px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        self.setStyleSheet(style)

        # Set minimum size to ensure content fits
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)


class ResponseWorker(QThread):
    """Worker thread for API calls"""
    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, user_message, conversation_history):
        super().__init__()
        self.user_message = user_message
        self.conversation_history = conversation_history

    def run(self):
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": self.user_message
            })

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )

            # Extract response
            assistant_message = response.choices[0].message.content

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            self.response_ready.emit(assistant_message)

        except AuthenticationError:
            self.error_occurred.emit("Authentication failed. Please check your API key in the .env file.")
        except RateLimitError:
            self.error_occurred.emit("Rate limit exceeded. Please wait a moment and try again.")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {str(e)}")


class SecurityOfficerChatbot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Officer Chatbot - Test Site")
        self.setGeometry(100, 100, 900, 700)

        self.conversation_history = []
        self.worker = None
        self.communication_type = None

        # Create GUI elements
        self.setup_ui()
        self.apply_styles()

        # Show welcome dialog
        self.show_welcome_dialog()

    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Title label
        title_label = QLabel("Test Site - GSOC Radio Communication")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Courier", 10))
        main_layout.addWidget(self.chat_display)

        # Input label
        input_label = QLabel("Your transmission:")
        main_layout.addWidget(input_label)

        # User input field
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your transmission here...")
        self.user_input.returnPressed.connect(self.send_message)
        main_layout.addWidget(self.user_input)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Send button
        send_button = QPushButton("Send Transmission")
        send_button.clicked.connect(self.send_message)
        send_button.setMinimumHeight(40)
        button_layout.addWidget(send_button)

        # Clear button
        clear_button = QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_chat)
        clear_button.setMinimumHeight(40)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)
        
    def apply_styles(self):
        """Apply modern styling to the application"""
        style = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New';
            }
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                color: #333333;
                font-size: 11pt;
            }
        """
        self.setStyleSheet(style)

    def show_welcome_dialog(self):
        """Show welcome dialog to select communication type"""
        dialog = WelcomeDialog(self)
        result = dialog.exec()

        # Check which button was clicked
        if dialog.clickedButton() == dialog.radio_button:
            self.communication_type = "radio"
            self.chat_display.setText("You will be speaking with an officer. Start a transmission as you would on the radio, and dispatch the officer to a location or task.\n\n")
        elif dialog.clickedButton() == dialog.phone_button:
            self.communication_type = "phone"
            self.chat_display.setText("Phone Call mode selected. (Coming soon)\n\n")
            self.user_input.setEnabled(False)
            self.user_input.setPlaceholderText("Phone Call mode not yet implemented")
        else:
            # Dialog closed without selection, default to radio
            self.communication_type = "radio"
            self.chat_display.setText("You will be speaking with an officer. Start a transmission as you would on the radio, and dispatch the officer to a location or task.\n\n")

    def display_message(self, sender, message):
        """Display a message in the chat area"""
        current_text = self.chat_display.toPlainText()
        self.chat_display.setText(current_text + f"{sender}: {message}\n\n")
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def send_message(self):
        """Send a message to the chatbot"""
        if self.communication_type != "radio":
            QMessageBox.warning(self, "Not Available", "Please select Radio Transmission mode first.")
            return

        user_message = self.user_input.text().strip()

        if not user_message:
            QMessageBox.warning(self, "Empty Message", "Please enter a transmission.")
            return

        if not os.getenv("OPENAI_API_KEY"):
            QMessageBox.critical(self, "API Key Error",
                               "OpenAI API key not found. Please add it to the .env file.")
            return

        # Display user message
        self.display_message("GSOC", user_message)
        self.user_input.clear()
        self.user_input.setEnabled(False)

        # Create and start worker thread
        self.worker = ResponseWorker(user_message, self.conversation_history)
        self.worker.response_ready.connect(self.on_response_ready)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(lambda: self.user_input.setEnabled(True))
        self.worker.start()

    def on_response_ready(self, assistant_message):
        """Handle response from API"""
        # Display response (filter out system prompt if it leaks through)
        if assistant_message and not assistant_message.strip().startswith("You are a security officer"):
            self.display_message("Test 8", assistant_message)

    def on_error(self, error_message):
        """Handle error from API"""
        self.display_message("ERROR", error_message)

    def clear_chat(self):
        """Clear the chat history"""
        self.chat_display.setText("You will be speaking with an officer. Start a transmission as you would on the radio, and dispatch the officer to a location or task.\n\n")
        self.conversation_history = []

def main():
    app = QApplication(sys.argv)
    window = SecurityOfficerChatbot()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

