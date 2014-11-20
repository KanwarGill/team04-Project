
"""
This script retrieves monitoring site, foreign sites,
and keywords from Mongo database and looks into the monitoring
sites to find matching foreign sites or keywords.
newspaper package is mainly used to extract useful data.
If any keyword (of text) or foreign sites (of links) matched,
all the relevant data will be stored at another Mongo database for Articles
"""

__author__ = "ACME: CSCC01F14 Team 4"
__authors__ = "Yuya Iwabuchi, Jai Sughand, Xiang Wang, Kyle Bridgemohansingh, Ryan Pan"

import sys
import os

# Add Django directories in the Python paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Frontend')))

# Append local python lib to the front to assure locallibrary to be used
sys.path.insert(0, os.path.join(os.environ['HOME'], '.local/lib/python2.7/site-packages'))

# newspaper, for populating articles of each site
# and parsing most of the data.
import newspaper
# Used for newspaper's keep_article_html as it was causing error without it
import lxml.html.clean

# Regex, for parsing keywords and sources
import re

# For counting seconds
import time
import timeit
# For getting today's date
import datetime
# For extracting 'pub_date's
from dateutil import parser

# To connect and modify the database of django
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Frontend.settings'
        
# For Models connecting with the Django Database
from articles.models import*
from articles.models import Keyword as A_keyword
from explorer.models import*
from explorer.models import Keyword as E_keyword

import threading

# Settings that will be kept in database later on
#STORE_ALL_SOURCES = False       # False             - Stores all links within articles which matched with the keywords
FROM_START = True               # True              - True: Populate all articles from start
#DATE_FORMAT = "%Y-%m-%dT%H:%M"  # "%Y-%m-%dT%H:%M"  - Universal date format for consistency

MIN_ITERATION_TIME = 600

# Used for communicating stream
#COMM_FILE = '_comm.stream'
#RETRY_COUNT = 10
#RETRY_DELTA = 1
#SLEEP_TIME = 5

def configuration():
    """ (None) -> dict
    Returns a dictionary containing the micro settings from the
    config.yaml file located in the directory containing this file
    """
    config_yaml = open("../config.yaml", 'r')
    config = yaml.load(config_yaml)
    config_yaml.close()
    return config

def populate_sites(sites, is_from_start):
    """ (list of str) -> list of [str, newspaper.source.Source]
    Searches through the sites using newspaper library and
    returns list of sites with available articles populated

    Keyword arguments:
    sites         -- List of [name, url] of each site
    """
    new_sites = []
    
    # Populate each Sites, then print the amount of articles and time it took
    # print "\n\t%-25s%10s%10s" % ("Site", "Articles", "Time")
    for s in range(len(sites)):
        # print("\t%-24s" % (sites[s][0])),
        # To count the time
        start_t = time.time()
        # Duplicate the name of the sites
        new_sites.append([sites[s][0]])

        # Use the url and populate the site with articles
        new_sites[s].append((newspaper.build(sites[s][1],
                                             memoize_articles=not is_from_start,
                                             keep_article_html=True,
                                             fetch_images=False,
                                             language='en',
                                             number_thread=1)))
        new_sites[s].append(sites[s][2])
        end_t = time.time()
        # report back the amount of articles found, and time it took
        # print("%6i pgs%9is" % (new_sites[s][1].size(), end_t - start_t))
    # return the list
    return new_sites


def parse_articles(populated_sites, db_keywords, foreign_sites):
    """ (list of [str, newspaper.source.Source], list of str, list of str, str) -> None
    Download all articles from built sites and stores information to the database

    Keyword arguments:
    populated_sites     -- List of [name, 'built_article'] of each site
    total_threads       -- Number of threads to use for downloading per sites.
                           This can greatly increase the speed of download
    """
    config = configuration()['storage']
    added, updated, failed, no_match, processed = 0, 0, 0, 0, 0
    start_t = time.time()

    # Collect today's date and time
    today = datetime.datetime.now().strftime(config['date_format'])

    # print("\nStore All Sources: %s" % str(config['store_all_sources']))
    # for each article in each sites, download and parse important data
    for site in populated_sites:
        # print "\n%s" % site[0]
        article_count = site[1].size()
        for art in site[1].articles:

            # Stop any print statements, even newspaper's warning messages
            sys.stdout = open(os.devnull, "w")

            # Check for any new command on communication stream
            check_command()

            url = art.url
            # print "\n\tURL:      ", url
            # print "\tEvaluating ...\r",
            
            # Try to download and extract the useful data
            try:
                art.download()
                art.parse()
                title = art.title
            except:
                title = ""
            # If downloading/parsing the page fails, stop here and move on to next article
            if not ((title == "") or (title == "Page not found")):
                # Regex the keyword from the article's text
                keywords = get_keywords(art, db_keywords)
                # Regex the links within article's html
                sources = get_sources(art.article_html, foreign_sites)
                # Store parsed author
                authors = art.authors
                # Try to parse the published date
                pub_date = get_pub_date(art)

                # Print all data accordingly
                # print "\tTitle:    ", title
                # print "\tAuthor:   ", authors
                # print "\tDate:     ", pub_date
                # print "\tKeywords: ", keywords
                # print "\tSources:  ", sources

                # If neither of keyword nor sources matched, then stop here and move on to next article
                if not (keywords == [] and (sources == [] or config['store_all_sources'])):
                    # Try to add all the data to the Article Database

                    article_list = Article.objects.filter(url=url)
                    if not article_list:

                        article = Article(title=title, url=url, date_added=today,
                                          date_published=pub_date, influence=site[2])
                        article.save()

                        article = Article.objects.get(url=url)
                        
                        for key in keywords:
                            article.keyword_set.create(keyword=key)

                        for author in authors:
                            article.author_set.create(author=author)

                        for source in sources:
                            article.source_set.create(source=source)

                        added += 1

                        # print "\tResult:    Match detected! Added to the database."

                    else:
                        
                        article = article_list[0]
                        article.title = title
                        article.url = url 
                        article.date_added = today
                        article.date_published = pub_date
                        article.influence = site[2]
                        article.save()

                        for key in keywords:
                            if not A_keyword.objects.filter(keyword=key):
                                article.keyword_set.create(keyword=key)

                        for author in authors:
                            if not Author.objects.filter(author=author):
                                article.author_set.create(author=author)

                        for source in sources:
                            if not Source.objects.filter(source=source):
                                article.source_set.create(source=source)

                        # print "\tResult:    Match detected! Article already in database. Updating."
                        updated += 1

                else:
                    no_match += 1
                    # print "\tResult:    No Match Detected."
            else:
                # print "\tResult:    Failed to download!"
                failed += 1
            processed += 1

            # Let the output print back to normal for minimal ui
            sys.stdout = sys.__stdout__

            sys.stdout.write("(%s) %i/%i\r" % (site[0], processed, article_count))
            sys.stdout.flush()
            # Some stats to look at while running the script
        print("(%s) %i/%i\r" % (site[0], processed, article_count))
    #         print("\n\tStatistics\n\tAdded: %i | Updated: %i | No Match: %i | Failed: %i | Time Elapsed: %is" %
    #               (added, updated, no_match, failed, time.time() - start_t))
    #         print "+--------------------------------------------------------------------+"
    # print("Finished parsing all sites!")


def get_sources(html, sites):
    """ (str, list of str) -> list of str
    Searches and returns links redirected to sites within the html
    Returns empty list if none found

    Keyword arguments:
    html                -- string of html
    sites               -- list of site urls to look for
    """
    matched_urls = []
    config = configuration()['storage']

    # for each site, check if it exists within the html given
    for site in sites:
        if config['store_all_sources']:
            for url in re.findall("href=[\"\'][^\"\']*?.*?[^\"\']*?[\"\']", html, re.IGNORECASE):
                # If it matches even once, append the site to the list
                matched_urls.append(url[6:-1])
        else:
            for url in re.findall("href=[\"\'][^\"\']*?.*?[^\"\']*?[\"\']", html, re.IGNORECASE):
                # Format the site to use only the domain name for searching
                formatted_site = re.search("([a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,6}",
                                           site, re.IGNORECASE).group(0)
                if formatted_site in url:
                    # If it matches even once, append the site to the list
                    matched_urls.append(url[6:-1])
    # Return the list
    return matched_urls


def get_pub_date(article):
    """ (newspaper.article.Article) -> str
    Searches and returns date of which the article was published
    Returns 'N/A' otherwise

    Keyword arguments:
    article         -- 'Newspaper.Article' object of article
    """
    date_format = configuration()['storage']['date_format']
    dates = []

    # For each metadata stored by newspaper's parsing ability, check if any of the key contains 'date'
    for key, value in article.meta_data.iteritems():
        if re.search("date", key, re.IGNORECASE):
            # If the key contains 'date', try to parse the value as date
            try:
                dt = parser.parse(str(value)).date().strftime(date_format)
                # If parsing succeeded, then append it to the list
                dates.append(dt)
            except:
                pass
    # If one of more dates were found,
    # return the oldest date as new ones can be updated dates instead of published dates
    if dates:
        return min(dates)
    return None


def get_keywords(article, keywords):
    """ (newspaper.article.Article, list of str) -> list of str
    Searches and returns keywords which the article's title or text contains
    Returns empty list otherwise

    Keyword arguments:
    article         -- 'Newspaper.Article' object of article
    keywords        -- List of keywords
    """
    matched_keywords = []

    # For each keyword, check if article's text contains it
    for key in keywords:
        if re.search(key, article.title + article.text, re.IGNORECASE):
            # If the article's text contains the key, append it to the list
            matched_keywords.append(key)
    # Return the list
    return matched_keywords


def explore(is_from_start):
    """ () -> None
    Connects to keyword and site tables in database, crawls within monitoring sites,
    then pushes articles which matches the keywords or foreign sites to the article database

  
    """

    # print "+----------------------------------------------------------+"
    # print "| Retrieving data from Database ...                        |"
    # print "+----------------------------------------------------------+"

    monitoring_sites = []
    # Retrieve, store, and print monitoring site information
    # print "\nMonitoring Sites\n\t%-25s%-25s%-10s" % ("Name", "URL", "Influence")

    msites = Msite.objects.all()

    for site in msites:
        # monitoring_sites is now in form [['Name', 'URL'], ...]
        monitoring_sites.append([site.name, site.url, site.influence])
        # print("\t%-25s%-25s%-10i" % (site.name, site.url, site.influence))

    foreign_sites = []
    # Retrieve, store, and print foreign site information
    # print "\nForeign Sites\n\t%-40s%-25s" % ("Name", "URL")

    fsites = Fsite.objects.all()
    for site in fsites:
        # foreign_sites is now in form ['URL', ...]
        foreign_sites.append(site.url)
        # print("\t%-25s%-40s" % (site.name, site.url))

    # Retrieve all stored keywords
    keywords = E_keyword.objects.all()
    keyword_list = []
    # Print all the keywords

    # print "\nKeywords:"
    for key in keywords:
        keyword_list.append(str(key.keyword))
        # print "\t%s" % key.keyword

    # print "\n"

    # print "+----------------------------------------------------------+"
    # print "| Populating sites ...                                     |"
    # print "+----------------------------------------------------------+"
    # Populate the monitoring sites with articles
    populated_sites = populate_sites(monitoring_sites, is_from_start)

    # print "\n"

    # print "+----------------------------------------------------------+"
    # print "| Evaluating Articles ...                                  |"
    # print "+----------------------------------------------------------+"
    # Parse the articles in all sites
    parse_articles(populated_sites, keyword_list, foreign_sites)


def comm_write(text):
    config = configuration()['communication']
    for i in range(RETRY_COUNT):
        try:
            comm = open('article' + config['comm_file'], 'w')
            comm.write(text)
            comm.close()
            return None
        except:
            time.sleep(RETRY_DELTA)


def comm_read():
    config = configuration()['communication']
    for i in range(config['retry_count']):
        try:
            comm = open('article' + config['comm_file'], 'r')
            msg = comm.read()
            comm.close()
            return msg
        except:
            time.sleep(config['retry_delta'])


def comm_init():
    """ (None) -> None
    Initialize The communication file
    """
    comm_write('RR')


def check_command():
    """ (None) -> None
    Check the communication file for any commands given.
    Execute according to the commands.
    """
    config = configuration()['communication']
    msg = comm_read()

    if msg[0] == 'W':
        command = msg[1]
        if command == 'S':
            print('Stopping Explorer...')
            comm_write('SS')
            sys.exit(0)
        elif command == 'P':
            print('Pausing ...')
            comm_write('PP')
            while comm_read()[1] == 'P':
                print('Waiting %i seconds ...' % config['sleep_time'])
                time.sleep(config['sleep_time'])
            check_command()
        elif command == 'R':
            print('Resuming ...')
            comm_write('RR')


if __name__ == '__main__':
    # Connects to Site Database
    django.setup()

    # Initialize Communication Stream
    comm_init()

    fs = FROM_START

    # Check for any new command on communication stream
    check_command()

    start = timeit.default_timer()
    
    if fs:
        explore(fs)
        fs = False
    else:
        explore(fs)

    end = timeit.default_timer()
    delta_time = end - start
    sleep_time = max(MIN_ITERATION_TIME-delta_time, 0)
    for i in range(int(sleep_time//5)):
        time.sleep(5)

    # Re run the program to avoid thread to increase
    os.chmod('article_explorer_run.sh', 0700)
    os.execl('article_explorer_run.sh', '')
