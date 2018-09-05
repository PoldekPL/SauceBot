## SauceBot
### A rudimentary Discord bot utilizing SauceNAO and Google Reverse Image Search to make looking for source easier.

---

SauceBot is a single-purpose Discord bot written in Python 3 with discord.py (v0.16.12) library, meant to make reverse image search easier.

While it is a functional bot, it's published here mostly to be more of a reference for people wanting to write their first bot.

#### Running it yourself

To see the bot in action, first make sure you've got `Python 3` (3.5+), `pip3` and `discord.py` (and all of its dependencies) installed. You also need to provide bot token (which you obtain from Discord Developer portal after creating your "application") in a `token` file, and your user ID in `my_id` file (which you can get after enabling Developer Mode in Discord, right-clicking on yourself and copying your ID).

If you're on Linux or similar OS, you should be able to `cd` into the directory with bot source files and run it using `./bot.py`. Optionally, you might have to make the file executable with `sudo chmod u+x bot.py`. On Windows, you might have to point the python3 to location of `bot.py` file.

To invite the bot to your server, copy this link:

`https://discordapp.com/oauth2/authorize?&client_id=CLIENT_ID&scope=bot&permissions=0`

to your browser, change `CLIENT_ID` to one shown for your "application" in Discord Developer portal, and `permissions=` value to one you can get in BOT PERMISSIONS calculator, also in the Developer portal. Once you're done, press enter and go through the invitation process on the page this link will lead to.

If all goes well and you see the bot online in your server, send a message with `!sauce` or `!google` and bot will answer with usage instructions.