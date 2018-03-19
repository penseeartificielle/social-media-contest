import random as rd
import requests, json
from apikeys import *
import oauth2 as oauth
from selenium import webdriver
import time

### FACEBOOK ###
#https://developers.facebook.com/tools/explorer/145634995501895/

TOKEN_FB = "?summary=true&access_token="
FB_RACINE = "https://graph.facebook.com/v2.12/"
FB_ID_PENSEE_ARTIFICIELLE = "113483579338897"
FB_ID_CONCOURS = "158412888179299"

FB_ACCOUNTS = "/me/accounts"
FB_COMMENTS = "/comments"
FB_REACTIONS = "/reactions"
FB_SHARES = "&fields=shares"
FB_CONCOURS = FB_RACINE + FB_ID_PENSEE_ARTIFICIELLE + "_" + FB_ID_CONCOURS

def generate_fb_token():
    r = requests.get(FB_RACINE + FB_ACCOUNTS + "?access_token="+TOKEN_USER_FB_SECRET)
    token = json.loads(r.text)['data'][0]['access_token']
    return token

def get_wanted_post_fb():
    r = requests.get(FB_CONCOURS + TOKEN_FB)
    post_fb = json.loads(r.text)
    return post_fb

def get_comments_fb():
    r = requests.get(FB_CONCOURS + FB_COMMENTS + TOKEN_FB)
    comments_fb = json.loads(r.text)
    nb_comments = comments_fb['summary']['total_count']
    return comments_fb, nb_comments

def get_reactions_fb():
    r = requests.get(FB_CONCOURS + FB_REACTIONS + TOKEN_FB)
    reactions_fb = json.loads(r.text)
    nb_reactions = reactions_fb['summary']['total_count']
    return reactions_fb, nb_reactions

def get_shares_fb():
    r = requests.get(FB_CONCOURS + TOKEN_FB + FB_SHARES)
    shares_fb = json.loads(r.text)
    nb_shares = shares_fb['shares']['count']
    return shares_fb, nb_shares

#
TOKEN_FB += generate_fb_token()
post_fb = get_wanted_post_fb()
comments_fb, nb_comments = get_comments_fb()
reactions_fb, nb_reactions = get_reactions_fb()
shares_fb, nb_shares = get_shares_fb()

### TWITTER ###
#https://apigee.com/console/twitter

TW_RACINE = "https://api.twitter.com/1.1/statuses"
TW_URL_PENSEEARTIF = "https://twitter.com/PenseeArtif/status"
TW_ID_CONCOURS = "/975328231208509440"
TW_ID_CONCOURS_JSON = TW_ID_CONCOURS+".json"
TW_RETWEETS = "/retweets"
TW_SHOW = "/show"

def generate_tw_token():
    consumer = oauth.Consumer(key=TW_CONSUMER_KEY, secret=TW_CONSUMER_SECRET)
    access_token = oauth.Token(key=TW_ACCESS_KEY, secret=TW_ACCESS_SECRET)
    client = oauth.Client(consumer, access_token)
    return client

def get_wanted_tweet_tw(client):
    response, data = client.request(TW_RACINE + TW_SHOW + TW_ID_CONCOURS_JSON)
    tweet_tw = json.loads(data)
    nb_favorites = tweet_tw['favorite_count']
    nb_retweets = tweet_tw['retweet_count']
    return tweet_tw, nb_favorites, nb_retweets

def get_retweets_tw(client):
    response, data = client.request(TW_RACINE + TW_RETWEETS + TW_ID_CONCOURS_JSON)
    retweets_tw = json.loads(data)
    return retweets_tw

#
client = generate_tw_token()
tweet_tw, nb_favorites, nb_retweets = get_wanted_tweet_tw(client)
retweets_tw = get_retweets_tw(client)

#######################################
# Tirage du gagnant

def print_statistiques():
    print('Statistiques :')
    print('*** Facebook')
    print('      Likes =',nb_reactions)
    print('      Commentaires =',nb_comments)
    print('      Partages =',nb_shares)
    print('*** Twitter')
    print('      Likes =',nb_favorites)
    print('      Retweets =',nb_retweets)

def generate_liste_resultats():
    total = nb_reactions + nb_comments + nb_shares + nb_favorites + nb_retweets
    resultats = ['Facebook like']*nb_reactions + ['Facebook commentaire']*nb_comments + ['Facebook partage']*nb_shares 
    resultats += ['Twitter likes']*nb_favorites + ['Twitter retweet']*nb_retweets
    return total, resultats

def tirage_media_gagnant(resultats):
    tirage = rd.randint(0, total-1)
    print("Tirage aléatoire :",tirage)
    print("Le gagnant fait partie de :",resultats[tirage])
    return tirage

def tirer_reaction_fb(reactions_fb):
    tirage = rd.randint(0, len(reactions_fb['data'])-1)
    print("... Le gagnant du concours est :",
          reactions_fb['data'][tirage]['name'],
          '(id :',
          reactions_fb['data'][tirage]['id'],
          ', type :',
          reactions_fb['data'][tirage]['type']+")")

def tirer_commentaire_fb(comments_fb):
    tirage = rd.randint(0, len(comments_fb['data'])-1)
    print("... Le gagnant du concours est :",
          comments_fb['data'][tirage]['from']['name'],
          '(id :',
          comments_fb['data'][tirage]['from']['id'],
          ', le :',
          comments_fb['data'][tirage]['created_time']+")")
    
def recuperer_partages_fb():
    url = "https://www.facebook.com/login"
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(1)
    USERNAME = "#email"
    PASSWORD = "#pass"
    LOGIN = "#loginbutton"
    username = driver.find_element_by_css_selector(USERNAME)
    password = driver.find_element_by_css_selector(PASSWORD)
    username.send_keys(FB_USERNAME)
    password.send_keys(FB_PASSWORD)
    time.sleep(1)
    submit = driver.find_element_by_css_selector(LOGIN)
    submit.click()
    time.sleep(1)
    url = "https://www.facebook.com/penseeartificielle/posts/158412888179299"
    driver.get(url)
    time.sleep(1)
    SHARES = 'UFIShareLink'
    shares = driver.find_elements_by_class_name(SHARES)
    shares[0].click()
    time.sleep(1)
    for __ in range(10):
        # multiple scrolls needed to show all 400 images
        driver.execute_script("window.scrollBy(0, 1000000)")
        time.sleep(0.2)
    time.sleep(1)
    liste = driver.find_elements_by_tag_name("h5")
    liste = liste[1:] #Remove 1st element which is original publication
    
    liste_partages = []
    for w in liste:
        w = w.find_element_by_xpath(".//span/span").text
        liste_partages.append(w)
    return liste_partages

def tirer_partage_fb():
    liste_partages = recuperer_partages_fb()
    tirage = rd.randint(1, len(liste_partages))
    print("... Le gagnant du concours est : le partage n°"+str(tirage)+" intitulé "+liste_partages[tirage-1])

def recuperer_favorites_tw(url):
    liste_favorites = []
    driver = webdriver.Firefox()
    driver.get(url)
    
    FAVORITES = ".request-favorited-popup"
    CONNEXION = ".SignupDialog-signinLink"
    USERNAME = ".js-username-field"
    PASSWORD = ".js-password-field"
    LISTE = '.activity-popup-users'
    
    time.sleep(1)
    lien_favoris = driver.find_element_by_css_selector(FAVORITES)
    lien_favoris.click()
    time.sleep(1)
    lien_connecter = driver.find_element_by_css_selector(CONNEXION)
    lien_connecter.click()
    time.sleep(1)
    username = driver.find_element_by_css_selector(USERNAME)
    password = driver.find_element_by_css_selector(PASSWORD)
    username.send_keys(TW_USERNAME)
    password.send_keys(TW_PASSWORD)
    time.sleep(1)
    
    lien_favoris = driver.find_element_by_css_selector(FAVORITES)
    lien_favoris.click()
    time.sleep(3)
    ol = driver.find_element_by_css_selector(LISTE)
    for li in ol.find_elements_by_tag_name("li"):
        div = li.find_elements_by_tag_name("div")
        if div is not None and len(div) > 0:
            div = div[0]
            name = div.get_attribute('data-screen-name')
            if name is not None:
                liste_favorites.append(name)
    driver.quit()
    return liste_favorites

def tirer_favorite_tw():
    liste_favorites = recuperer_favorites_tw(TW_URL_PENSEEARTIF+TW_ID_CONCOURS)
    tirage = rd.randint(1, len(liste_favorites))
    print("... Le gagnant du concours est : le like n°"+str(tirage)+" de @"+liste_favorites[tirage-1])

def tirer_retweet_tw(retweets_tw):
    tirage = rd.randint(0, len(retweets_tw)-1)
    print("... Le gagnant du concours est : @"+retweets_tw[tirage]['user']['screen_name'])

def grand_gagnant(resultats, tirage, reactions_fb, comments_fb, nb_shares, nb_favorites, retweets_tw):
    if resultats[tirage] == 'Facebook like':
        tirer_reaction_fb(reactions_fb)
    elif resultats[tirage] == 'Facebook commentaire':
        tirer_commentaire_fb(comments_fb)
    elif resultats[tirage] == 'Facebook partage':
        tirer_partage_fb(nb_shares)
    elif resultats[tirage] == 'Twitter likes':
        tirer_favorite_tw()
    elif resultats[tirage] == 'Twitter retweet':
        tirer_retweet_tw(retweets_tw)

def print_merci():
    print("Merci à tous pour votre participation ! N'hésitez pas à vous abonner à notre page Facebook / Twitter pour les prochaines fois :)")
            
print_statistiques()
total, resultats = generate_liste_resultats()
tirage = tirage_media_gagnant(resultats)
grand_gagnant(resultats, tirage, reactions_fb, comments_fb, nb_shares, nb_favorites, retweets_tw)
print_merci()
