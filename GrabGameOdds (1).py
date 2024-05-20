from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import pandas as pd
pd.set_option('display.max_rows', None)

# Returns the list of games posted on the page
def getGamesGrid(browser, sport):
    try:
        WebDriverWait(browser, timeout=20).until(EC.presence_of_element_located((By.XPATH, f"//h1[contains(text(),'{sport} Betting News')]")))
        grid = browser.find_element(By.XPATH, "//div[@class='grid gap-6 grid-cols-1 2xl:grid-cols-2 mb-6']")
    except:
        return []
    else:
        return grid

# Fills the two players/teams and odds for the given matchup
def fillTeams(game, team_names, team_odds):
    wait = WebDriverWait(game, 10)
    teams = wait.until(EC.presence_of_all_elements_located((By.XPATH, ".//p[@class='text-base text-brand-gray-1 __className_43b3b8 group-hover:text-brand-gray-5 font-semibold overflow-hidden truncate']")))
    try:
        odds = game.find_elements(By.XPATH, ".//p[@class='text-brand-gray-1 __className_43b3b8 font-bold text-sm']")
    except:
        return 1
    else:
        bookies = game.find_elements(By.XPATH, ".//img[@class='object-center object-cover rounded']")
        for i in range(2):
            try:
                book = bookies[i].get_attribute("alt")
            except:
                return 1
            else: 
                team_name = teams[i].text
                odd = f"{odds[i].text} ({book})"
                team_names.append(team_name)
                team_odds.append(odd)
        return 0

# Grabs the games listed on the sports page and returns a dictionary containing the matches and odds for keys
def generateOdds(browser, sport):
    games_grid = getGamesGrid(browser, sport)
    if games_grid == []:
        return []
    games = games_grid.find_elements(By.XPATH, "//div[@class='group bg-white rounded-xl flex justify-between h-[120px] shadow']")

    team_names = []
    team_odds = []

    for game in games:
        matchup = []
        matchup_odds = []
        if (fillTeams(game, matchup, matchup_odds) == 0):
            team_names.append(matchup)
            team_odds.append(matchup_odds)
    teams_odds = {"Matchups": team_names, "Odds": team_odds}

    return teams_odds

# Opens nba odds page and returs a dictionary made by generateOdds
def NBAOdds(browser):
    browser.get('https://oddsjam.com/nba')
    
    # Closes popup login option
    WebDriverWait(browser,timeout=20).until(EC.presence_of_element_located((By.XPATH,'//button[@class="h-6 w-6 hover:text-brand-gray-5 absolute right-8 top-0"]')))
    browser.find_element(By.XPATH, '//button[@class="h-6 w-6 hover:text-brand-gray-5 absolute right-8 top-0"]').click() 
    time.sleep(1)
    return generateOdds(browser, "NBA")

# Opens page for the given sport and returns a dictionary made by genearteOdds
def oddsFinder(browser, sport):
    browser.find_element(By.XPATH, f"//a[@href='/{sport}']").click() #Clicks link to page to scrape from
    time.sleep(1)
    if sport == "boxing":
        return generateOdds(browser, sport.capitalize())
    return generateOdds(browser, sport.upper())

# Similar to oddsFinder but is for pages that have their games in nested divs
def oddsFinderExpand(browser, sport, first_open):
    browser.find_element(By.XPATH, f"//a[@href='/{sport}']").click() #Clicks link to page to scrape from
    time.sleep(1)
    expand_btns = browser.find_elements(By.XPATH, "//button[@class='bg-brand-gray-1 hover:bg-brand-gray-3 p-1 rounded-full border border-brand-gray-4']")

    if first_open: #checks if the first div is already opened
        expand_btns[0].click()
    for button in expand_btns:
        button.click()
        time.sleep(1)

    return generateOdds(browser, sport.capitalize())

# Makes the dataframe and prints it to the screen
def printOdds(sport, odds):
    if odds != []:
        df = pd.DataFrame(odds)
        if not df.empty:
            print(f"Odds for upcoming {sport} matches: ")
            print(df)

# Takes a list of sports and gets the odds for each sport
def getOdds(browser, sports):
    for sport in sports:
        odds = []
        if sport == "soccer":
            odds = oddsFinderExpand(browser, sport, True)
        elif sport == "tennis":
            odds = oddsFinderExpand(browser, sport, False)
        else:
            odds = oddsFinder(browser, sport)
        printOdds(sport, odds)

def main():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removes a CSRF error message because there is no login required
    
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) 

    # This is called separately because upon opening there is a pop-up that has to be closed
    nba_odds = NBAOdds(browser)
    if nba_odds != []:
        print("Odds for the upcoming NBA games are:")
        nba_df = pd.DataFrame(nba_odds)
        print(nba_df)

    start = time.time()
 
    sports = ["ncaab", "nhl", "nfl", "ncaaf", "mlb", "soccer", "tennis", "mma", "boxing"]
    getOdds(browser, sports)

    end = time.time()
    total = end - start
    print(f"Execution time: {(total)} seconds or {total/60} minutes")

    browser.quit()

if __name__ == '__main__':
    main()