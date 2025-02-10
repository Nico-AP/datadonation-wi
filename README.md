# datadonation-wi

This repository contains the codebase for data donation collection tool used in the project "BTW25".




## Scraper Options

- Scrape the day from 4 days ago (hashtags and accounts): python manage.py scrape_and_save --mode=past_day
- Scrape the current day (hashtags and accounts, and update all accounts since 01.01.2025): python manage.py scrape_and_save --mode=all
- Rescrape specific day (hashtags and accounts): python manage.py scrape_and_save --mode=day --date=20240101
- Update accounts (update all accounts since 01.01.Jan only): python manage.py scrape_and_save --mode=accounts
