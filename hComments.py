def hubski_comments(
        users,
        config,
        max_depth=100,
        comments_dict=None,
):
    """
   Downloads all recent comments made by users on Hubski.
 
   Parameters
   ----------
   users : list of str
   max_depth : int, optional
   comments_dict : dict of str, list of str
       Re-use comments from this dictionary, if possible.
 
   Returns
   -------
   dict of str, list of str

   WRITTEN BY thundara
   """
    if comments_dict is None:
        comments_dict = defaultdict(list)
 
    comments_xpath = (
        "//div[div[@class='subhead']//text()='{}']"       # Enclosing div
        "/div[@id='comtext']/p/span[@class='quotelink']"  # Comment content
    )
    next_url_xpath = "//div[@class='morelink']/@title"
    sess = requests.Session()
    logger = logging.getLogger("zombots.comments.hubski")
    no_user_text = (
        '<a href="/">You are in a maze of twisty little passages, '
        'all alike.</a>'
    )
 
    for user in users:
        if len(comments_dict.get(user, [])) > 0:
            continue
 
        url = "https://hubski.com/comments?id={}".format(user)
        comments = []
 
        logger.info("Getting comments for %s", user)
 
        for depth in range(max_depth):
            # Get the content of the page
            r = sess.get(url)
 
            if r.status_code != 200 or r.text == no_user_text:
                raise Exception("Unable to get comments from {}".format(url))
 
            # Build the HTML tree
            root = lxml.html.soupparser.fromstring(_fix_content(r.content))
 
            # Extract comments
            logger.debug("Extracting comments from %s", url)
 
            matches = root.xpath(comments_xpath.format(user))
 
            for match in matches:
                # Use .text_content() instead of .text to include strings that
                # may be within links
                #
                # XXX: This also includes quoted text
                comment = match.text_content()
 
                if comment:
                    comments.append(comment)
 
            # Get the next page of comments
            next_url = root.xpath(next_url_xpath)
 
            if next_url:
                url = "https://hubski.com{}".format(next_url[0])
            else:
                break
 
        comments_dict[user] = comments
 
    return comments_dict