from bs4 import BeautifulSoup as BS
import requests
import csv

def get_game_id(game_name):
    """Get the id number on BoardGameGeek of the game 'game_name'
        currently only only works with exact matches if there are
        multiple results or close matches with only one result.
    Args:
        game_name (str): The name of the game you want the id of.

    Returns:
        int: ID number on BoardGameGeek of the game.

    """
    soup = get_search_game_page(game_name)
    game_elts = soup.find_all("boardgame")
    id = None

    if not game_elts:
        print(game_name + " is either the wrong name or it is not on Board Game Geek. \
                         Make sure it exactly matches the BGG name")

    elif len(game_elts) == 1:
        id = game_elts[0]["objectid"]

    elif len(game_elts) > 1:
        found = False
        for elt in game_elts:
            title = elt.find("name").string
            if title == game_name:
                found = True
                id = elt["objectid"]
                break

        if not found:
            print(game_name + " is either the wrong name or it is not on Board Game Geek. \
                                         Make sure it exactly matches the BGG name")

    return id

def get_search_game_page(game_name):
    """Request the xml page from BGG for game 'game_name'.
    Args:
        param game_name (str): The name of a game to search.
    Returns:
        BeautifulSoup: Returns a parser for the xml page.
    """
    name = game_name.replace(' ', '%20')
    result = requests.get("http://www.boardgamegeek.com/xmlapi/search?search="
                          + name)
    if result.status_code == 200:
        c = result.content
        soup = BS(c, 'lxml')
        return soup
    else:
        raise ConnectionError("Could not retrieve search result for " + game_name + " due to: " + result.status_code)

def get_game_stats_page(game_id):
    """Request xml page of game stats from BGG

    Args:
        game_id(int): ID of the game in the BGG database.

    Returns:
        BeautifulSoup: Returns a parser for the xml page.

    """
    result = requests.get("https://boardgamegeek.com/xmlapi/boardgame/"
                          + str(game_id)
                          + "&stats=1")

    if result.status_code == 200:
        c = result.content
        soup = BS(c, 'lxml')
        return soup
    else:
        raise ConnectionError("Could not retrieve search result for " + str(game_id) + " due to: " + result.status_code)

def get_game_stats(id):
    """Fetches data about board game with ID 'id' from BoardGameGeek
    Args:
        id (int): The ID of the game in on BoardGameGeek

    Returns:
        tuple: Tuple containing title, minimum and maximum player count and playtime, complexity and the thumbnail url.

    """
    soup = get_game_stats_page(id)
    title = soup.find("name", {"primary":"true"})
    min_players = soup.find("minplayers")
    max_players = soup.find("maxplayers")
    min_time = soup.find("minplaytime")
    max_time = soup.find("maxplaytime")
    complexity = soup.find("averageweight")
    thumbnail = soup.find("thumbnail")
    info = [title.string, int(min_players.string), int(max_players.string), int(min_time.string), int(max_time.string), float(complexity.string), str(thumbnail.string)]
    info.insert(1, id)
    return info


def process_csv(csv_file):
    """Take a csv file with the first column as board game names, with the first cell titled 'Board Games' and return
        a list of lists of the games data.
    Args:
        csv_file (str): The string name of the .csv file to process.

    Returns:
        list: List containing a list of data for each game.

    """
    games_data = []
    with open(csv_file, 'r') as data:
        reader = csv.DictReader(data)
        for row in reader:
            game = row['Board Games']
            id = get_game_id(game)
            if id:
                game_data = get_game_stats(id)
                if game_data:
                    games_data.append(game_data)
                    continue
        print("Could not add game:" + game)
    return games_data

