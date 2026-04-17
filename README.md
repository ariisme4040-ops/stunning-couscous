# Discord Bot Documentation

## Features
- **Manage Your Server**: Control server settings like roles and channels.
- **Moderation Tools**: Kick, ban, and mute users with ease.
- **Custom Commands**: Create commands tailored to your server needs.
- **Interactive Games**: Play games like trivia and hangman within your server.
- **Music Playback**: Listen to music directly in voice channels.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ariisme4040-ops/stunning-couscous.git
   cd stunning-couscous
   ```
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Create a .env File**:
   - Copy the `.env.example` to `.env` and fill in the required values:
   ```bash
   cp .env.example .env
   ```
4. **Start the Bot**:
   ```bash
   npm start
   ```

## Commands
- **!help**: Displays a list of all commands.
- **!kick [user]**: Kicks a specified user from the server.
- **!ban [user]**: Bans a specified user from the server.
- **!mute [user]**: Mutes a specified user.
- **!play [song name]**: Plays the specified song in a voice channel.

## Requirements
- Node.js (version 14 or higher)
- A Discord bot token (set in the .env file)
- Permissions to manage roles and channels in the server

For further assistance, please refer to the project's wiki or open an issue on GitHub!