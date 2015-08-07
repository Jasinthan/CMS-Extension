# CMS-Extension

This tool written in JavaScript and Python facilitates content migration. Feedbacks are welcome. 

## Features
1. Reads HTML source code from the editor, checks links, downloads files and uploads them to the right place.
2. Provides an editable list of links.

## Installation
1. Install <a href="https://addons.mozilla.org/en-us/firefox/addon/greasemonkey/">Greasemonkey</a> if you are using Firefox or <a href=
            "https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=en">
                Tampermonkey</a> if you are using Chrome.
2. Install user script from <a href="https://greasyfork.org/en/scripts/11533-cms-extension">Greasy Fork<a>.

## Configuration
1. Open`/json/ftp.json` with a plain-text editor.
2. You will see something like the following, fill the information and save the file. 
```javascript
{

    "server": "ftp.example.com",
    "username": "your_username",
    "password": "your_password"

} 
```

## Basic Usage
### Content Space Page
1. Run `run.bat`.
2. Go to content space page editor.
3. Paste content to the editor.
4. Switch to HTML mode.
5. Click on <b>Load</b>.
6. Click on <b>Strip</b> if you want to remove formatting. 
7. Click on <b>Start</b>.
8. Errors may occur, double-check whether some links redirect to files. 
9. Save your page. 

### External Link Page
1. Run `run.bat`.
2. Go to external link page editor. 
3. Fill the form. 
4. Click on <b>Check</b>.
5. Save your page. 

## Advanced Usage
### Sites that Require Login
1. Go to your browser and press <kbd>F12</kbd>.
2. Click on <b>Network</b>.
3. Go to the site from which you want to copy content and log in. 
4. Find the relevant row in the network panel by checking the <b>Domain</b>.
5. Locate the <b>Cookie</b> string under <b>Request Headers</b>.
6. Add a attribute-value pair to '/json/headers.json' like the following and save the file.
```javascript
{

    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Cookie": "fill the cookie string here"
    
}
```
### Mirrors
Follow the above instruction. You just need to include the <b>Authorization</b> string instead. 

## Q&A
##### Can I automate several pages at the same time? 
No, 'server.exe' can only check URLs for a single page at a time. 

##### Can I open several pages at the same time? 
Yes, just make sure you don't start the automation. 

##### What is "User-Agent" in headers.json?
Some websites cannot be accessed by non-browser clients. It is recommended to keep this in 'headers.json'.

##### What if I got "Session Expired"?
In this case, you need to re-login to the CMS site and refresh the editor page. 

##### Why do I get empty URLs, but their anchor texts are not empty?
This is because some sites use JavaScript codes in their anchor tags (ex. to pop-up windows). When you paste links to the editor, the <b>href</b> attributes are lost because JavaScript codes are not recognized by the HTML editor. In this case, you have to edit the URLs manually. You can directly edit the URLs in the link list. 

## Status Reference
* Ready: the URL has not been checked yet. 
* Checking: the program is checking if the URL redirects to a file. 
* Downloading: the program is downloading the file to '/temp'.
* Uploading: the program is uploading the file.
* Skipped: the URL does not redirect to a file.
* Done: the URL redirects to a file and has been replaced by the new URL. 
* Error 4XX: HTTP errors. The target is not accessible or does not exist. 
* Error: other errors. 
* Session Expired: The user script cannot retrieve the information of the page you are editing. You need to re-login to the CMS site and refresh the page. 
