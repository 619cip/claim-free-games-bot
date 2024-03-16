# Claim Free Games Bot
**Disclaimer:** This script does not actually CONFIRM the purchase, instead it adds the game to your cart and requires you to finish the transaction. This script utilizes seleniumbase, undetected_chromedriver, and downloads/replace chrome drivers to suit all versions of chrome browser. **For educational purposes only, use at your discretion.**

Automates finding daily free games on the Epic Games Store, adds them to the shopping cart, and prompts the final transaction to the user to complete on the Epic Games Store.

![image](https://github.com/619cip/Claim-Free-Games-Bot/assets/78285511/b7d8add1-b4c3-4ae9-9a7d-8ce1530afa37)
***
## Requirements
- Windows OS
- Gmail account (preferably a spare one)
- Chromium based browser
***
## Getting Started
The first step to getting started is to download the zip file, **[cfgb-launcher-v1-3-9-24.zip](https://github.com/619cip/Claim-Free-Games-Grabber/releases/download/v1.0/cfgb-launcher-v1-3-9-24.zip)**

Once downloaded, unzip the file. (this might take a while so follow the step below)

While you wait for the file to unzip or have already unzipped the file, link your google account to Epic Games by following [Linking your Google account to Epic Games](#Linking-your-Google-account-to-Epic-Games) below

Once you've linked your Google account and unzipped the file, navigate through the unzipped file and find the file: **settings.cfg**

Edit and save your google account credentials to **settings.cfg**. (See image below)

![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/9326761a-6a73-4018-8aa5-50311d9272c7)

Run **ClaimFreeGamesBot Launcher.exe**
[virustotallink](https://www.virustotal.com/gui/file/5837077604173ad4fa0237dfeeb360c8a9b3b43e9876dd04e8dfa914dcbd2e3c?nocache=1)

Be wary of having to check for Google login verification, virus protection prompts, and other permissions for the first time it runs.
It is recommended to keep test mode setting on when running to check if Google login requires some sort of confirmation.

Follow [Launch exe upon startup](#Launch-exe-upon-startup) to "automate" the process upon system startup.
***
## Linking your Google account to Epic Games
#### Step 1: Open up [Epic Games Login](https://www.epicgames.com/id/login?lang=en-US) and click on the Google logo
![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/37db7974-be00-49cf-89f8-13959bab60d4)

#### Step 2: Login to your Google account in the popup.
Fillout and finish the criterias logging into your Google Account.

#### Step 3: Confirm and finish the prompts on the site to sign up and link to Epic Games.
You may have to provide your birthday, come up with a name, and verify email address (same as creating a new account)

##### Once you're logged in, you've successfully linked your Google account to Epic Games.

## Launch executable upon startup
To automatically launch **ClaimFreeGamesBot Launcher.exe** upon booting up your computer, do the following steps:
#### Step 1: Create a shortcut of the executable.
Right click on **ClaimFreeGamesBot Launcher.exe** and click **Show more options**

![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/52717f43-fa2d-49b0-b104-c2741627f25f)

Click on **Create Shortcut**

![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/5b468cdb-35bf-4045-96f8-4da2a1ac82d6)

#### Step 2: Open up your Startup folder
Open up Run command box by pressing Windows logo key + R (or search for "run" in windows search bar) and type in **shell:startup**, then select OK

![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/d52039b0-4845-4763-ac9c-74def8b74c09)

#### Step 3: Drag and drop the shortcut exe to Startup folder
![image](https://github.com/619cip/Claim-Free-Games-Grabber/assets/78285511/81976070-0453-462a-8055-ff9a6013483b)

##### Upon system boot up now, it will launch the executable.
***
## Settings
- test_mode : True = headless mode is off | False = headless mode is on (headless mode on hides the whole process of adding to cart etc) **headless mode on is detected as of 3/16/24, do not use**
- timeout : default time in seconds to find a web element before throwing an exception (recommended to have a higher number for slower computers min: 1 max: 60)

## Issues
Make sure to always test run the exe (including the shortcut) before actually relying on it upon system bootup. Some issues can occur like anti virus protection blocking the exe or Google security verification.
If there's a game that is written in the **game_log.txt** file but have not claimed it, then deleting the id content can help.
