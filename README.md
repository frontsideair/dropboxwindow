Dropbox Window
=============

Scan a QR code on your phone to upload files on an untrusted PC.

Note: This software is in alpha state. I know some things are broken, I'll fix them eventually.

Usage
-----

If you're in an internet cafe or library, you can backup your files to your
Dropbox easily, without entering your credentials on an untrusted computer.

Point the browser to [Dropbox Window](https://db.6nok.org) and scan the QR code with your
phone. Grant access on your phone, and voila! You can upload files by simply
dragging and dropping. Deauthorize using either the browser or your phone. 
Your password is safe with you.

Read more about it on my [Medium](https://medium.com/@frontsideair/a-summer-spent-studying-part-ii-c038f87e60de).

Running
-------

Clone this repository and push to Heroku. (Don't forget to set environment
variables.) If you want to run on local machine, you need [Python 2.7](https://www.python.org/downloads/),
[pip](https://www.python.org/downloads/) and [foreman](https://www.python.org/downloads/) (optional).
If you have them all, run this in the project directory:

```pip install -r requirements.txt
foreman run web```

and check [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

License
-------

[GNU GPLv3](http://www.gnu.org/copyleft/gpl.html)
