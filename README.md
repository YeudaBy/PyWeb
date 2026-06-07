```
 _______  __   __  _     _  _______  _______ 
|       ||  | |  || | _ | ||       ||  _    |
|    _  ||  |_|  || || || ||    ___|| |_|   |
|   |_| ||       ||       ||   |___ |       |
|    ___||_     _||       ||    ___||  _   | 
|   |      |   |  |   _   ||   |___ | |_|   |
|___|      |___|  |__| |__||_______||_______|
▄▖▖▖▄▖  ▄▖▖▖▄▖▖▖▄▖▖ ▖  ▄▖▖ ▖  ▄▖▖▖▄▖  ▖  ▖▄▖▄ 
▐ ▙▌▙▖  ▙▌▌▌▐ ▙▌▌▌▛▖▌  ▐ ▛▖▌  ▐ ▙▌▙▖  ▌▞▖▌▙▖▙▘
▐ ▌▌▙▖  ▌ ▐ ▐ ▌▌▙▌▌▝▌  ▟▖▌▝▌  ▐ ▌▌▙▖  ▛ ▝▌▙▖▙▘
```

## What is `pyweb`?
`pyweb` is a [POC](https://en.wikipedia.org/wiki/Proof_of_concept) project to try to build the web world from scratch, with Python.
Yes, I know, it's a bit delusional.

### So, why?
Honestly, I do not know why. I just don't like the current situation, where if you want to build for the web, you have to do it with JavaScript, which, honestly, pretty much sucks.

So yes, I do not think that in one day the whole world will switch to Python.

Yes, I do not think that Python is the best way of doing that.

Yes, they probably have a strong reason why the web is built that way.

But it's just to prove to the world that I can do it.

I know that I have limits that I cannot escape from:

- I don't see a situation where the entire internet world will be rewritten in Python.
- Python does not have an actual sandbox, and that would be serious trouble when it comes to security issues.
- Python is slow, especially not as fast as C++.


But I told you - I DO NOT CARE!!

I want a Python browser and I'll build it!

### What's the plan?
Oh, I'm so glad you asked!

I want to rewrite a whole browser and ecosystem; that is, if I want to, I can build a website with nothing but Python code (and, of course, some HTML and CSS).

Also, maybe one day I will build a translator that will help me render actual websites written with JavaScript, so I would be able to browse the real internet with pyweb.

### How would you do that?
Very slow, step by step, component after another.

First I want to have a working POC that can render an interactive HTML page with some scripting, that I will dig into the heavy stuff, such as security, network, performance, UI and the whole package.


## Use `pyweb`

> Please note that this version (and probably all the versions) of `pyweb` have a lot of security problems! 
>
> Make sure to not browse any website you don't fully trust.
> 
> Basically, **You should NOT use this program on your computer.**

You can download the `.pyz` file from the releases page, or built it yourself from source:
- make sure you have `python3` and `git` installed
- run the following commands:
```commandline
git clone https://github.com/YeudaBy/PyWeb          // clone the repo
python -m zipapp pyweb -p "/usr/bin/env python3"   // build a `.pyz` file
chmod u+x pyweb.pyz                               // give the file execution permissions
./pyweb.pyz                                      // run the program
```

## `pyweb` Philosophy

I want this project to be decent and truly worth the time invested in it, so I’ve set a few rules for myself to guide me throughout development:

- Use JavaScript naming convencions, and Python PEP 8 style, for example: `document.get_element_by_id`
- Type everything you can type, with [Python hint typing](https://docs.python.org/3/library/typing.html)
- Use [OOP paradigm](https://en.wikipedia.org/wiki/Object-oriented_programming)
- Do not use AI tools for writing code
- Write clean and self-explaining code

## Road map

> This is not a proper documentation / index for the codebase.

### Pyweb client
the browser client

- [ ] browser UI
- [ ] Network model
  - [ ] Socket handling
  - [ ] TLS/SSL communications
  - [ ] DNS
  - [ ] Resources (binaries) fetching
  - [ ] Debug middleware
- [ ] Render engine
  - [ ] Render UI elements
  - [ ] Handle interactive elements
  - [ ] Run script tags
  - [ ] Render CSS styles
  - [ ] Handle media rendering


### Pyweb api 
the api library that developers can use to write their own websites, and the client will implement.


- [ ] Document
  - [ ] DOM module
- [ ] Location
- [ ] History
- [ ] Navigator
- [ ] Console
- [ ] Event
- [ ] Network
  - [ ] fetch
  - [ ] Request
  - [ ] Response
  - [ ] Header
  - [ ] WebSocker
- [ ] Storage
  - [ ] Cookies
  - [ ] Local storage
- [ ] Media
- [ ] Worker


### `pycakge` - Pyweb package manager

### Pyweb hub
a whole website writen with pyweb

- [ ] `pyweb` documentation
- [ ] an example websites
- [ ] `pycakge` website