# Training Chatbot

A Python-based training chatbot application designed to simulate radio communications between a security officer (Test8) and the Global Security Operations Center (GSOC). This tool is designed for training purposes to help users practice professional radio communication protocols.

## Features

- **Interactive GUI**: Built with PySide6 for a user-friendly interface
- **AI-Powered Responses**: Uses OpenAI's API to generate realistic security officer responses
- **Radio Protocol Training**: Simulates real-world security radio communications
- **Performance Evaluation**: Provides scoring based on communication standards
- **Professional Standards**: Enforces proper radio etiquette and protocols

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Training-Chatbot.git
   cd Training-Chatbot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

Run the application:
```bash
python chatbot.py
```

### Training Protocol

1. The chatbot assumes the role of "Test8" (security officer)
2. You play the role of GSOC (Global Security Operations Center)
3. Initiate communication with standard radio protocols
4. The chatbot will respond according to security communication standards
5. End the session by typing "Done" to receive your performance score

### Communication Standards

The training evaluates users on:

- **Professionalism**: Polite and respectful communication
- **Clear Language**: Plain language, avoiding slang or jargon
- **Concise Traffic**: Brief and essential communications only
- **Call Signs**: Proper identification protocols
- **Confidentiality**: Appropriate handling of sensitive information
- **Radio Security**: Following equipment security protocols

## Project Structure

```
Training-Chatbot/
├── chatbot.py          # Main application file
├── learner.py          # Additional learning components
├── Instructions.md     # Detailed project instructions
├── .env               # Environment variables (not tracked)
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Dependencies

- Python 3.7+
- PySide6 (GUI framework)
- OpenAI Python library
- python-dotenv (environment variable management)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is designed for training purposes only. It simulates radio communication protocols for educational use in security training environments.