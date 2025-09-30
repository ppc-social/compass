#import datetime
#
#def current_us_week_dates():
#    today = datetime.date.today()
#    # weekday(): Monday=0 ... Sunday=6
#    weekday = today.weekday()
#    
#    # Find Sunday (start of week in US style)
#    sunday = today - datetime.timedelta(days=(weekday + 1) % 7)
#    # Saturday is 6 days after Sunday
#    saturday = sunday + datetime.timedelta(days=6)
#    
#    # Get US-style week number (%U: weeks start on Sunday)
#    week_number = int(today.strftime("%U"))
#    year = today.year
#    
#    return year, week_number, sunday, saturday
#
#if __name__ == "__main__":
#    year, week, start, end = current_us_week_dates()
#    print(f"Current US-style week: {week} of {year}")
#    print(f"Start (Sunday): {start}")
#    print(f"End   (Saturday): {end}")

from datetime import datetime, timedelta, date

def get_us_week_dates(year, week):
    """
    Given a year and a US-style week number, returns the start (Sunday) and end (Saturday) dates.
    Week 1 is the week containing January 1, starting on Sunday.
    """
    #
    jan1 = datetime(year, 1, 1)
    # Find the Sunday on or before Jan 1
    days_to_sunday = jan1.weekday() + 1  # weekday(): Mon=0, Sun=6
    first_sunday = jan1 - timedelta(days=days_to_sunday % 7)
    
    # Calculate start and end dates of the requested week
    start_date = first_sunday + timedelta(weeks=week)
    end_date = start_date + timedelta(days=6)
    
    return start_date.date(), end_date.date()


# Example:
if __name__ == "__main__":
    year = 2026
    week = 1
    start, end = get_us_week_dates(year, week)
    print(f"Week {week} of {year} starts on {start} and ends on {end}")
    #print(date(2025, 9, 29).strftime("%U"))
    #print(datetime.strptime("2025-39", "%Y-%U"))
