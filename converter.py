import json

def selenium_cookies_to_netscape_format(cookies, domain):
    """
    Convert Selenium Chrome cookies to Netscape format.
    """
    netscape_cookie = ''
    for cookie in cookies:
        expiry = cookie.get('expiry', 0)  # Default to 0 if expiry is not present
        cookie_line = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(
            cookie['domain'], 
            'TRUE' if cookie['domain'].startswith('.') else 'FALSE', 
            cookie['path'], 
            'TRUE' if cookie['secure'] else 'FALSE',
            str(int(expiry)),
            cookie['name'],
            cookie['value']
        )
        netscape_cookie += cookie_line

    with open("netscape_cookies.txt", "w") as f:
        f.write(netscape_cookie)

    return "netscape_cookies.txt"

if __name__ == '__main__':

    cookies = None
    
    with open("cookies.json", 'r') as f:
        cookies = json.load(f)

    selenium_cookies_to_netscape_format(cookies, ".twitter.com")
