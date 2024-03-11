import sys
import json
import urllib.request

import os.path
import pytest
import requests
import configparser

from selenium.webdriver.chrome.service import Service
from seleniumbase import BaseCase, Driver
from seleniumbase.common.exceptions import NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# In case of any sort of update to Chrome, downloading chrome drivers is handled here.
# Chrome Drivers from https://chromedriver.storage.googleapis.com/LATEST_RELEASE
driver_exe_path = None
try:
    service = Service(ChromeDriverManager().install())
    driver_exe_path = service.path
except ValueError:
    latest_chromedriver_version_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    latest_chromedriver_version = urllib.request.urlopen(latest_chromedriver_version_url).read().decode('utf-8')
    service = Service(ChromeDriverManager(driver_version=latest_chromedriver_version).install())
    driver_exe_path = service.path

# Set the directory to wherever the user's executable is
os.chdir(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__))

main_directory = os.path.dirname(os.path.abspath(__file__))
cfg_directory = os.path.join(main_directory, "settings.cfg")
game_log_directory = os.path.join(main_directory, "game_log.txt")
config = configparser.ConfigParser()

# Validate files used in program ( settings.cfg, game_log.txt )
print("Checking for config file...")
if not os.path.exists(cfg_directory):
    config["Settings"] = {
        "test_mode": 'True',
        "timeout": 10,
        "$gmail": "",
        "$pass": ""
    }
    with open(cfg_directory, "w") as cfg_file:
        config.write(cfg_file)
    raise Exception("Created a config file. Add gmail credentials to settings.cfg.")

print("Checking for game log file...")
if not os.path.exists(game_log_directory):
    with open(game_log_directory, "w") as game_log_file:
        json.dump([], game_log_file)

BaseCase.main(__name__, __file__)

def search_free_games():
    """
    Searches for all free games on the game store

    :return: a list of games that are free { game_id=URL, ... }
    :rtype: dict
    """

    URL = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions'
    response = requests.get(URL)

    if response.status_code == 404:
        raise Exception("Status 404")

    data = response.json()

    # Search for games with 'discountPrice' = 0 (free)
    # Return a list of games with their ID and URL (if there's any free games).
    free_games = {}
    for game in data['data']['Catalog']['searchStore']['elements']:
        if game['price']['totalPrice']['discountPrice'] == 0:
            if len(game['catalogNs']['mappings']) > 0:
                for mappings in game['catalogNs']['mappings']:
                    free_games[game['id']] = f"https://store.epicgames.com/p/{mappings['pageSlug']}"
            elif not ("[]" in game['productSlug']):
                free_games[game['id']] = f"https://store.epicgames.com/p/{game['productSlug']}"

    game_log = []
    with open(game_log_directory, "r") as game_log_file:
        try:
            game_log = json.load(game_log_file)
        except json.JSONDecodeError:
            print("Game log file is not valid.")

    game_url_list = []
    for gameId, url in free_games.items():
        if gameId not in game_log:
            game_log.append(gameId)
            game_url_list.append(url)

    with open(game_log_directory, "w") as game_log_file:
        game_log_file.seek(0)
        json.dump(game_log, game_log_file, indent=4)

    return game_url_list


class claim_free_games(BaseCase):

    def get_new_driver(self, *args, **kwargs):
        # uc mode for undetected, headless2 for no window showing
        # uc subprocess for subprocesses detection, incognito for no saved site data
        options = {'uc': True, 'headless2': True, 'uc_subprocess': True, 'incognito': True}

        # turn on headless mode if test_mode = 'True'
        with open(cfg_directory, "r") as cfg_file:
            config.read_file(cfg_file)
            self.no_screenshot_after_test = True
            self.set_default_timeout(int(config.get("Settings", "timeout")))
            if config.get("Settings", 'test_mode') == 'True':
                options['headless2'] = False

        return Driver(uc=options['uc'], headless2=options['headless2'],
                      uc_subprocess=options['uc_subprocess'], incognito=options['incognito'])

    def login_to_egs(self):
        """
        Login to epic games store using Google account

        might come across issues initially here with logging in.
        credentials must be stored in settings.cfg to login.

        :return: None
        """
        # Driver goes to EOS login page, and clicks login with Google account
        self.open("https://www.epicgames.com/id/login")
        self.click("#login-with-google")
        self.switch_to_newest_window()

        # login with Google account, might face problems with Google initially
        with open(cfg_directory, "r") as cfg_file:
            config.read_file(cfg_file)
            self.type("#identifierId", config.get('Settings', '$gmail'))
            self.click("#identifierNext")
            self.type("input[type='password']", config.get('Settings', '$pass'))
            self.click("#passwordNext")
            print("Successful login.")

        # switch to our old window (after google login popup)
        self.switch_to_default_window()

        # check changes in URL for authentication
        old_url = self.get_current_url()
        while self.get_current_url() == old_url:
            print("Waiting for site to close out.")
            self.sleep(1)

    def add_game_to_cart(self, url):
        """
        Add the new founded free games to user's cart

        NoSuchElementException can be raised if user has
        a slow computer.

        :return:
            True if successful add to cart, False otherwise.
        :parameter:
            url : str, required
                The game URL to visit.
        :raise:
            NoSuchElementException
                If the element is not found in the game URL site.
        """

        # visit our targeted game url
        print(f"Visiting {url}...")
        self.get(url)

        # check for age restriction constraint
        try:
            self.click("button:contains('Continue')")
        except NoSuchElementException:
            print("Did not find age restriction constraint from the given game.")

        # check for add to cart button (if added or not)
        try:
            self.click("button[data-testid='add-to-cart-cta-button']")
        except NoSuchElementException:
            print("Game has already been bought or added to cart.")
            return False

        print("Successfully added game to cart.")
        return True

    def verify_cart(self):
        """
        Verify our cart for free games only, if not, remove priced games.

        a lot of specific elements is in use when verifying.
        website can change these element positions and would need
        updating to the element selectors if such thing were to happen.

        :return: None
        :raise:
            NoSuchElementException
                If the element is not found on the cart site.
        """
        detected_cost_games = False
        subtotal_display = None

        # check for subtotal (holds pricing total for the cart)
        try:
            subtotal_display = self.find_element(by="css selector", selector='[data-testid="cart-summary-subtotal"]')
        except NoSuchElementException:
            print("Unable to find subtotal display in the cart.")

        # check if subtotal is not $0.00 (free), if so, change detected_cost_games to True
        try:
            total = subtotal_display.find_element(by="xpath", value='./div/span')
            if total.text != "$0.00":
                detected_cost_games = True
        except NoSuchElementException:
            print("Could not find the total price cost element.")

        if detected_cost_games:
            # get the list of games in the cart.
            list_of_games = self.find_elements(by="css selector", selector='[data-testid="offer-card-layout-wrapper"]')

            # iterate through all game info
            for game_info in list_of_games:
                # find 'remove' button
                remove_button = None
                try:
                    remove_button = game_info.find_element(by="css selector", value='.css-vfnr45')
                except NoSuchElementException:
                    print("Couldn't find remove button element.")

                # check if pricing does not say 'Free', remove if it doesn't.
                try:
                    pricing = game_info.find_element(by="css selector", value='.css-l24hbj .css-119zqif')
                    if pricing.text != "Free":
                        remove_button.click()
                except NoSuchElementException:
                    print("Couldn't find pricing information")

    def go_to_cart(self):
        """
        Visit our cart and prompt cart for user's interaction

        it is important to note that undetected_chromedriver is
        used for the prompt portion as it handles purchases
        more securely than seleniumbase.

        :return: None
        """
        print("Visiting your cart.")
        self.open("https://store.epicgames.com/cart")

        self.wait_for_ready_state_complete()

        if self.is_text_visible("Your cart is empty."):
            self.driver.quit()
            pytest.exit("Unsuccessful game add to cart.")

        self.verify_cart()

        self.save_cookies("cookies")
        self.driver.quit()

        # initialize undetected_chromedriver, prompts user the cart page
        print("Preparing to prompt cart to user...")
        options = uc.ChromeOptions()
        options.headless = False
        self.driver = uc.Chrome(driver_executable_path=driver_exe_path, options=options, use_subprocess=True)

        self.driver.get("https://store.epicgames.com")
        self.load_cookies()
        self.driver.get("https://store.epicgames.com/cart")
        self.delete_saved_cookies()

    # Main Handler #
    def test_initiator(self):
        """
        Main handler of the program, handles the order in what
        is to be executed (go to cart, logging in, verifying cart)

        Mostly verifies if there's any valid games available and
        the ending of the program.

        :return: None
        """
        print("\n")
        print(f"Directory: {main_directory}")
        print(f"Config File Dir: {cfg_directory}")
        print(f"Game Log Dir: {game_log_directory}")

        print("Searching for available free games...")
        free_games = search_free_games()

        if len(free_games) < 1:
            self.driver.quit()
            pytest.exit("No new free games on Epic Games.")

        print("Found free games. Logging into EGS.")
        self.login_to_egs()

        for url in free_games:
            self.add_game_to_cart(url)

        self.go_to_cart()

        # Stall web driver until user exits or purchases order.
        try:
            while not self._check_browser():
                if self.is_text_visible("Thanks for your order!"):
                    break
                self.sleep(1)
        except NoSuchWindowException:
            print("User exited the window")

        self.driver.quit()
