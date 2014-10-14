
# newspaper
import newspaper
from newspaper import news_pool
from newspaper import Article

#regex
import re

#Times
import timeit
import time
#dateutil
from dateutil import parser

#db_manager
import db_manager as db



def populate_sites(sites, from_start):
    ''' Searches through the sites using newspaper library and
        returns list of sites with available articles populated

    Keyword arguments:
    sites         -- List of [name, url] of each site
    from_start    -- Boolean to search sites from scratch
    '''

    new_sites = []
    for s in range(len(sites)):
        start = time.time()
        # Duplicate the name of the sites
        new_sites.append([sites[s][0]])

        # Use the url and build the metadata of the sites
        new_sites[s].append((newspaper.build(sites[s][1],
                                             memoize_articles=not from_start)))
        end = time.time()
        print ("Populated: %-5s Found: %5i pages in %is"%(sites[s][0], new_sites[s][1].size(), end - start))

    return new_sites

def download_articles(populated_sites):
    ''' Download all articles from built sites and stores the metadata
        to the database

    Keyword arguments:
    populated_sites -- List of [name, 'built_article'] of each site
    total_threads   -- Number of threads to use for downloading per sites.
                       This can greatly increase the speed of download
    '''
    added, failed,no_match = 0,0,0
    start = time.time()

    for site in populated_sites:
        for art in site[1].articles:
            try:
                art.download()
                art.parse()
                title = art.title                                 # title     Done
            except:
                title == ""


            print "Title:    ", title

            if not ((title == "") or (title == "Page not found")):
                keywords = get_keywords(art, ['Israel', 'Soccer', 'Doctor', 'fail', 'FaIL', 'kiLLED', 'name', 'ebola'])      # keyword   Done
                #print get_keywords(art, db.get_keywords())
                matched_sources = get_sources(art, ["cnn.com", "nytimes.com", 'go.com', 'bulls.com'])                          # sources   Done
                if not (keywords == [] and matched_sources == []):


                    url =  art.url                                   # url       Done
                    authors = art.authors                               # author    Done
                    date = get_date(art)                             # date      Done

                    print "Site:     ", site[0]
                    print "URL:      ", url
                    print "Author:   ", authors
                    print "Date:     ", date
                    print "Metadata: ", art.meta_data
                    print "Keywords: ", keywords
                    print "Sources:  ", matched_sources
                    added += 1
                else:
                    print "URL:      ", art.url
                    print "\nFailed: No Site nor Keyword matched."
                    no_match += 1
            else:
                print "URL:      ", art.url
                print "\nFailed: Page was not able to download"
                failed += 1

            print ("\nAdded: %8i\nFailed: %7i\nNo Match; %5i"%(added,failed,no_match))
            print ("%is"%(time.time() - start))
            print ("\n=============================================================================================\n")


# def get_sources(article):
#     sc, sp, ep = 20, 0, 0
#     html = re.sub('<[^((a|link).*?href)].*?>', ".", article.html)
#
#     start = article.text[:sc]
#     end = article.text[-sc:]
#     start = re.sub("[^0-9a-zA-Z ]+", ".", start)
#     end = re.sub("[^0-9a-zA-Z ]+", ".", end)
#
#     while ("." in start and sp < len(article.text)):
#         start = article.text[sp:sc+sp]
#         start = re.sub("[^0-9a-zA-Z ]+", ".", start)
#         sp+=1
#
#     while ("." in end and ep < len(article.text)):
#         end = article.text[min(-ep, -1)-sc:min(-ep, -1)]
#         end = re.sub("[^0-9a-zA-Z ]+", ".", end)
#         ep+=1
#
#     # print "FS: %2i - '%s'\n" \
#     #       "ES: %2i - '%s'"%(sp, start, ep, end)
#     regex = "(?=(" + start + ".*?" + end + "))"
#     try:
#         text_html =  min(re.findall(regex, html, re.DOTALL), key=len)
#         urls = re.findall("href=[\"\'].*?[\"\']", text_html)
#         for i in range(len(urls) - 1):
#             urls[i] = urls[i][6:-1]
#     except:
#         urls = 'Failed'
#     return urls
#
# def match_sources(urls, sites):
#     matched_sources = []
#     for url in urls:
#         for site in sites:
#             if site not in matched_sources:
#                 if re.search(site, url, re.IGNORECASE):
#                     matched_sources.append(url)
#     return matched_sources

def get_sources(article, sites):
    ''' Searches and returns links redirected to sites within the article
        Returns empty list if none found

    Keyword arguments:
    article         -- 'Newspaper.Article' object of article
    sites           -- List of site urls to look for
    '''
    matched_urls = []

    for site in sites:
        for url in re.findall("href=[\"\'][^\"\']*?" + re.escape(site) + "[^\"\']*?[\"\']", article.html, re.IGNORECASE):
            matched_urls.append(url[6:-1])
    return matched_urls



def get_date(article):
    ''' Searches and returns date of which the article was published
    Returns 'Failed' otherwise

    Keyword arguments:
    article         -- 'Newspaper.Article' object of article
    '''
    dates = []
    for key, value in article.meta_data.iteritems():
        if re.search("date", key, re.IGNORECASE):
            try:
                dt = parser.parse(str(value)).date().strftime("%Y-%m-%d")
                dates.append(dt)
            except:
                pass
    if dates:
        return min(dates)
    return 'Failed'

def get_keywords(article, keywords):
    matched_keywords = []
    for key in keywords:
        if re.search(key, article.title + article.text, re.IGNORECASE):
            matched_keywords.append(key)
    return matched_keywords



# def find_artciles(allMonitoredSites):
#     pass
#     #forloop(monitored sites):
#         #SitesToArticles(Name, foreignSites):
#             #article tp ward
#             #war to db
#     #return None

if __name__ == '__main__':
    a = [['cnn', 'http://cnn.com'], ['nyt', 'http://nytimes.com'],['Yahoo news','http://news.yahoo.com'], ['Google News','http://news.google.com']]
    a = [a[3]]
    b = populate_sites(a, True)
    download_articles(b)



    # from newspaper import Article
    # urls = ["http://www.cnn.com/2014/10/12/living/columbus-day-indigenous-people-day/index.html?hpt=hp_t2",
    #         "http://www.cnn.com/2014/10/12/health/ebola/index.html?hpt=hp_t1",
    #         "http://www.cnn.com/2014/10/10/health/sperm-donor-qa/index.html?hpt=hp_c2",
    #         "http://www.nytimes.com/2014/10/13/world/asia/once-a-symbol-of-power-farming-now-an-economic-drag-in-china.html?hp&action=click&pgtype=Homepage&version=LargeMediaHeadlineSum&module=photo-spot-region&region=top-news&WT.nav=top-news&_r=0",
    #         "http://www.cbc.ca/news/canada/calgary/downtown-calgary-electrical-fire-damage-will-take-days-to-rebuild-1.2796497"]
    # for url in urls:
    #     start = timeit.default_timer()
    #     first_article = Article(url)
    #     first_article.download()
    #     first_article.parse()
    #
    #     print first_article.source_url    # can be used for site i.e. cnn.com
    #     print first_article.authors       # author    Done
    #     print first_article.title         # title     Done
    #     print get_date(first_article)     # date      IP
    #     print first_article.url           # url       Done
    #     #print first_article.text          # keyword   IP
    #
    #     print len(match_sources(get_sources(first_article), ['oregonlive.com', 'nytimes.com']) )              # sources   Done
    #     print ""
    #
    # pass