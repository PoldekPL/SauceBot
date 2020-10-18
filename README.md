## SauceBot
### A simple Discord bot utilizing multiple reverse search engines to make looking for ~~sauce~~ source easier.

---

SauceBot is a single-purpose Discord bot written in Python 3 with the latest (v1.5.0 at the time of writing this) discord.py library, meant to fulfill one goal - make reverse image search easier.

It is a functional bot and can be easily used as a reference for people wanting to write their own Discord bots in Python.

#### Running it yourself

Easiest way to replicate the environment in which the bot was created and is used is to clone the repository to a local directory on your PC and create a virtual Python environment right next to it. Make sure you've got `Python 3` (3.5+) and`pip3` installed first. After creating the virtual environment and activating it, run `pip3 install -r requirements.txt`.

Next you'll need to provide bot token (which you obtain from Discord Developer portal after creating your "application") in a `token` file in the same directory as `bot.py`.

Once all that is done, you've got the virtual environment activated and you navigated in the console/terminal to the main directory of the bot, launch it using `python .\bot.py` or `python3 .\bot.py`, depending on what's your OS and how you installed Python.

To invite the bot to your server, copy this link:

```
https://discordapp.com/oauth2/authorize?&client_id=CLIENT_ID&scope=bot&permissions=VALUE
```

to your browser, change `CLIENT_ID` to one shown for your "application" in Discord Developer portal, and `VALUE` to one you can get in *Bot Permissions* calculator, also in the Developer portal. Once you're done, press enter and go through the invitation process on the page this link will lead to.

Only permissions that SauceBot currently needs are:

* Send Messages
* Manage Messages
* Add Reactions

Additionally, since the addition of Privileged Gateway Intents to Discord API, the bot also requires both intents, that is:

* Presence
* Server Members

If all goes well and you see the bot online in your server, send a message with `sauce.help` and bot will answer with usage instructions.