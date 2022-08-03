from InstaScraper import InstaScraper
from media_mapper import media_mapper


def get_media_captions(media_list):
        for media in media_list:
            media_item = media_mapper(media)
            print(media_item.caption)
             

def caption_scraper(username):

    #initialsie the scraper
    insta_scraper=InstaScraper()

    #retrieves the account data from the landing page
    data = insta_scraper.get_first_page_data(username)

    media_list = (
        data.get("graphql").get("user").get("edge_owner_to_timeline_media").get("edges")
    )
    #extracts the captions for the media present on the landing page
    for media in media_list:
        try:
            caption = (
                media.get("node")
                .get("edge_media_to_caption")
                .get("edges")[0]
                .get("node")
                .get("text")
            )

            print(caption)
        except:
            print("no caption")
    
    next_page= insta_scraper.get_first_page_id(data)

    #checks if the landing page has a next page
    if next_page!=None:

        #exracts the user id from the first media item on the account
        user_id=insta_scraper.get_account_id(data)

        #iterates till no more pages left to scrape
        while next_page != None:

            #genrates new url using the user id and page id to send the get requests to
            new_url = insta_scraper.url_genrator(user_id,next_page)

            data=insta_scraper.get_account_data(new_url)
            
            #returns a list of media items from the cureent page
            media_list = insta_scraper.get_account_media(data)
            
            #extracting media captions to test against menu item names
            get_media_captions(media_list)

            #gets the page id of the next page or returns None if no more pages exist
            next_page=insta_scraper.get_page_id(data)


def main():
    #example input:"therock"
    username = input("Enter the username to be scraped: ")
    caption_scraper(str(username))

main()