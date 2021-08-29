# Olympics Scraper - Tokyo 2020

## Summary

This project is mainly a scraper to archive complete results from the Tokyo 2020 Olympics. It also provides some basic information about how to use the semi-official API yourself to make something

The scraper implemented in this repository was written to download **complete data**. If you only want limited data such as schedules or medal counts, you would probably find it easier to read [the API documentation](API.md) and implement your own query (I'm happy to help with this - just open an issue).

**If you want to use this data for analysis, you're probably best off using the dataset [uploaded on Kaggle](https://www.kaggle.com/llui85/tokyo-2021-olympics-complete-grouped-by-type) (see below for more information).**

## How do I use this?

1. Clone the repository.

```bash
git clone https://github.com/llui85/olympics-tokyo2020.git
```

2. Start the scraper - and wait a while. Modify the tasks in `scraper.py` if you wish. This script simply requests the data from the API and stores each request.

```bash
python3 scraper.py
```

3. Merge the requests together (as most of them are paginated). If you edited the tasks in `scraper.py` then you should modify `merge-requests.py` accordingly. Make sure the pagination matches `scraper.py`.

```bash
python3 merge-requests.py
```

At this point you are finished, and find your scraped data in `./docs/data/raw/merged_requests`. If you like, you can generate an extremely large JSON file that contains all of the data, organised by type, with:

```bash
python3 generate_data.py
```

___

As this is a large download which can take over half an hour if scraping completely, I have uploaded the combined JSON file to [ Kaggle](https://www.kaggle.com/llui85/tokyo-2021-olympics-complete-grouped-by-type) and [Dropbox](https://www.dropbox.com/s/jmcdvwqkb6hcxks?dl=1).

## Attribution
Data should always be attributed to the [Olympic Channel Services](https://olympicchannelservices.com/), and the [Olympic Broadcasting Services](https://www.obs.tv/home). It's probably also a good idea to attribute the IOC as well.

If you use this data, I'd appreciate it very much if you attribute the scraping process to "llui85", and link to this repository. This would be appreciated, but it's not required.

Example:

```
Data source: Olympic Channel Services and Olympic Broadcasting Services. Data scraped by llui85 (https://github.com/llui85/olympics-tokyo2020)
```


## Why should I use this over any of the [other scrapers available?](https://github.com/search?o=desc&q=olympics+scraper&s=updated&type=Repositories)

Unlike the other scrapers, this project downloads complete results from a stable JSON API, and does not rely on web scraping. Data is scraped directly from Olympic servers.

This means that the data is:
* more reliable and consistant
* better structured for analysis
* complete

## Does this work for the Paralympics?

Yes it does!

You will need to change the following variables in `scraper.py` to use the paralympic servers.

```py
OVP_PREFIX = 'https://appovpparatok.ovpobs.tv'
OCSI_PREFIX = 'https://appocsiparatok.ovpobs.tv'
API_KEY = 'MTk5OTQ0Njo6b2NzaS1hcGl1c2Vy'
API_SECRET = 'ZGVkMTlmYTdhMWE5MzJlMjU1YTBmYzAwODgyMDkyZDRmNTcwYmU0ZjhmZWFiODk0OGQyODc4NjY0MjY3NWQ2YTo6M2FkYTk0NDExODNmOTgyNWMwYWFiOTE2MmIwYzQxYWM='
```

## Is this scraper endorsed by the IOC?
No.

___

If you've got any questions or need help with this project, feel free to open an issue. Please star the repo if you like this project!
