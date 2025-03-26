# Telegram Video Bot

This is a Telegram bot designed to handle video processing tasks. This bot is built using Python and leverages the Telegram Bot API to interact with users.

## Features

- **Video Upload:** Users can upload videos directly to the bot.
- **Video Processing:** The bot processes videos to perform tasks such as format conversion, compression, and more.
- **Notifications:** Users receive notifications once their videos are processed.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/intensealchemist/telegramvideobot.git
    ```

2. Navigate to the project directory:
    ```sh
    cd telegramvideobot
    ```

3. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Obtain a Telegram bot token by creating a new bot through the [BotFather](https://core.telegram.org/bots#botfather).

2. Set the bot token as an environment variable:
    ```sh
    export TELEGRAM_BOT_TOKEN=your-telegram-bot-token
    ```

3. Run the bot:
    ```sh
    python bot.py
    ```

## Contributing

Contributions are welcome! Please create a fork of the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python Telegram Bot Library](https://python-telegram-bot.readthedocs.io/)
