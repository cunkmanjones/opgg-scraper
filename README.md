> [!CAUTION]
> July 12th, 2025: Scraper no longer functions properly.
> The endpoint the program used no longer returns player data. 
> I'm archiving this repository until a new endpoint with a similar data structure is discovered.

<h3 align="center">
  <img src="https://github.com/cunkmanjones/opgg-scraper/blob/main/.github/opgg-scraper-logo-bluecircle.png">
</h3>

# General Info
**OP.GG Scraper** is a small, portable scraper written in Python & Lua.
> [!IMPORTANT]
> Returned data will be associated with *League of Legends* and currently has no functionality with other games that OP.GG may collect, store, & present data from. 

# Installation
## Windows
### Method 1: Releases Tab
Download the [Current Release](https://github.com/cunkmanjones/opgg-scraper/releases) from the Releases Tab.
### Method 2: Local Build
Download [Python Version 3.11.0](https://www.python.org/downloads/release/python-3110/) and the [Project Source](https://github.com/cunkmanjones/opgg-scraper/archive/refs/heads/main.zip) as a ZIP (or your preferred method of downloading the source code).<br/>
#### Dependencies:
Once the source is downloaded/extracted, open the folder containing `requirements.txt` using File Explorer, type `cmd` into the address bar, and paste the following command:<br/>
```
pip install -r requirements.txt
```
If you'd prefer to download the dependencies yourself:
- [fakeuseragent](https://pypi.org/project/fake-useragent/)
- [lupa](https://pypi.org/project/lupa/)
- [pandas](https://pypi.org/project/pandas/)
- [PySide6](https://pypi.org/project/PySide6/)
- [PyQtDarkTheme](https://pypi.org/project/pyqtdarktheme/)
- [requests](https://pypi.org/project/requests/)

## MacOS & Linux
> [!WARNING]
> No Current Release Executable for either MacOS or Linux.<br/>
> Untested using MacOS or Linux and may not run or compile as intended!

After installing Python Version 3.11.0 and downloading/extracting the project source, open a terminal to the folder containing `requirements.txt` and paste the following command:<br/>
```
pip install -r requirements.txt
```

# Why
*This project isn't to be taken seriously; I just made it for fun.*<br/>
I wanted to make a small application in Python with a nice-looking GUI. I also wanted to create a GitHub repository and see how difficult it would be to maintain it. The coding isn't clean or well documented, there's a massive gap in between commits due to overhauling the entire backend, and I learned more and more as the project went on, so a lot of the formatting evolved over time. The project itself isn't technically a scraper anymore, but I'm committed to the name. 

# License
- [**LGPLv3.0 License**](https://github.com/cunkmanjones/opgg-scraper/blob/main/LICENSE)
