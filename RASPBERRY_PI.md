# Raspberry Pi Deployment Guide

Run the Kramer Bot in the background using `systemd` and a virtual environment.

## Prerequisites

1.  Clone the repository to your Pi:
    ```bash
    cd /home/cauchon
    git clone https://github.com/Cauchon/Kramer-Bot.git
    cd Kramer-Bot
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Set up your `.env` file:
    ```bash
    cp env.example .env
    nano .env
    # Add your API keys
    ```

## Setup Service

1.  **Edit the service file** (if your path or user is different):
    The included `kramer_bot.service` assumes the code is in `/home/cauchon/Kramer-Bot` and the user is `cauchon`.

2.  **Copy the service file**:
    ```bash
    sudo cp kramer_bot.service /etc/systemd/system/
    ```

3.  **Reload systemd**:
    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Enable and start the service**:
    ```bash
    sudo systemctl enable --now kramer_bot
    ```

## Manage Service

- **Check status**:
    ```bash
    sudo systemctl status kramer_bot
    ```

- **View logs**:
    ```bash
    journalctl -u kramer_bot -f
    ```

- **Stop bot**:
    ```bash
    sudo systemctl stop kramer_bot
    ```
