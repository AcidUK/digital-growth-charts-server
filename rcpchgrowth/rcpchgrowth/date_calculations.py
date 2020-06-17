from datetime import date, datetime
from datetime import timedelta
from dateutil import relativedelta
import math
from decimal import *
from .constants import FORTY_WEEKS_GESTATION, TERM_PREGNANCY_LENGTH_DAYS, TERM_LOWER_THRESHOLD_LENGTH_DAYS, EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS

"""
5 functions to calculate age related parameters
 - decimal_age: returns a decimal age from 2 dates (birth_date and observation_date) and gestational age at delivery (gestation_weeks and gestation_days), based on 40 weeks as 0. Days/Weeks before 40 weeks are negative.
 - chronological_decimal_age: returns a decimal age from 2 dates (takes birth_date and observation_date)
 - corrected_decimal_age: returns a corrected decimal age accounting for prematurity (takes birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int, pregnancy_length_day [optional])
 - chronological_calendar_age: returns a calendar age as a string (takes birth_date or estimated_date_delivery and observation_date)
 - estimated_date_delivery: returns estimated date of delivery in a known premature infant (takes birth_date, gestation_weeks, gestation_days, pregnancy_length_days[optional])
"""

def decimal_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int):
    """
    returns decimal age relative to forty weeks expressed as 0 y
    THIS FUNCTION IS DEPRECATED
    """
    days_born_from_forty_weeks = ((gestation_weeks * 7) + gestation_days) - TERM_PREGNANCY_LENGTH_DAYS
    days_of_life_in_years = chronological_decimal_age(birth_date, observation_date)
    return  (days_born_from_forty_weeks / 365.25) + days_of_life_in_years


def chronological_decimal_age(birth_date: date, observation_date: date) -> float:

    """
    Calculates a decimal age from two dates supplied as raw dates without times.
    Returns value floating point
    :param birth_date: date of birth
    :param observation_date: date observation made
    """

    days_between = observation_date - birth_date
    chronological_decimal_age = days_between.days / 365.25
    return chronological_decimal_age
    

def corrected_decimal_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int)->float: 
    """
    Corrects for gestational age. 
    Corrects for 1 year, if gestation at birth >= 32 weeks and < 37 weeks
    Corrects for 2 years, if gestation at birth <32 weeks
    Otherwise returns decimal age without correction
    Any baby 37-42 weeks returns decimal age of 0.0
    Depends on chronological_decimal_age
    :param birth_date: date of birth
    :param observation_date: date observation made
    :param gestation_weeks: weeks of gestation up to 40
    :param gestation_days: days in excess of weeks
    """
    
    correction_days = 0
    pregnancy_length_days = TERM_PREGNANCY_LENGTH_DAYS

    if gestation_weeks > 0:
        pregnancy_length_days = (gestation_weeks * 7) + gestation_days

    try:
        uncorrected_age = chronological_decimal_age(birth_date, observation_date)
    except ValueError as err:
        return err

    prematurity = TERM_PREGNANCY_LENGTH_DAYS - pregnancy_length_days

    if pregnancy_length_days >= TERM_LOWER_THRESHOLD_LENGTH_DAYS:
        #term baby
        return uncorrected_age

    elif pregnancy_length_days < EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS and uncorrected_age <= 2:
        #correct age for 2 years
        correction_days = prematurity
        edd = birth_date + timedelta(days=correction_days)
        return chronological_decimal_age(edd, observation_date)

    elif (pregnancy_length_days >= EXTREME_PREMATURITY_THRESHOLD_LENGTH_DAYS) and (pregnancy_length_days < TERM_LOWER_THRESHOLD_LENGTH_DAYS) and uncorrected_age <=1:
        #correct age for 1 year
        correction_days = prematurity
        edd = birth_date + timedelta(days=correction_days)
        return chronological_decimal_age(edd, observation_date)
    
    else:
        return uncorrected_age


def chronological_calendar_age(birth_date: date, observation_date: date) -> str:
    """
    returns age in years, months, weeks and days: to return a corrected calendar age use passes EDD instead of birth date
    """
    difference = relativedelta.relativedelta(observation_date, birth_date)
    years = difference.years
    months = difference.months
    weeks = difference.weeks
    days = difference.days
    # hours = difference.hours
    # minutes = difference.minutes

    date_string = []

    if years == 1:
        date_string.append(str(years) + " year")
    if years > 1:
        date_string.append(str(years) + " years")
    if months > 1:
        date_string.append(str(months) + " months")
    if months == 1:
        date_string.append(str(months) + " month")
    if days == 1:
        date_string.append(str(days) + " day")
    if days > 1:
        if weeks > 0:
            remainingdays = days - (weeks*7)
            if weeks == 1:
                date_string.append(str(weeks) + " week")
            elif weeks > 1:
                date_string.append(str(weeks) + " weeks")
            if remainingdays == 1:
                date_string.append(str(remainingdays) + " day")
            if remainingdays > 1:
                date_string.append(str(remainingdays) + " days")
    if len(date_string) > 1:
        return (', '.join(date_string[:-1])) + ' and ' + date_string[-1]
    elif len(date_string) == 1:
        return date_string[0]
    elif birth_date == observation_date:
        return 'Happy Birthday'
    else:
        return ''


def estimated_date_delivery(birth_date: date, gestation_weeks: int, gestation_days: int) -> date:
    """
    Returns estimated date of delivery from gestational age and birthdate
    Will still calculate an estimated date of delivery if already term (>37 weeks)
    """
    pregnancy_length_days = TERM_PREGNANCY_LENGTH_DAYS

    if gestation_weeks > 0:
        pregnancy_length_days = (gestation_weeks * 7) + gestation_days
    
    prematurity = TERM_PREGNANCY_LENGTH_DAYS - pregnancy_length_days

    edd = birth_date + timedelta(days=prematurity)
    return edd


def corrected_gestational_age(birth_date: date, observation_date: date, gestation_weeks: int, gestation_days: int)->str:
    """
    Returns a corrected gestational age
    """
    edd = estimated_date_delivery(birth_date, gestation_weeks, gestation_days)
    forty_two_weeks_gestation_date = edd + timedelta(days=14)

    if observation_date >= forty_two_weeks_gestation_date:
        #beyond 2 weeks post term - chronological age measured in days / weeks / months years
        #no correction
        return {
            "corrected_gestation_weeks": None,
            "corrected_gestation_days": None
        }
    
    pregnancy_length_days = (gestation_weeks * 7) + gestation_days
    # time_alive = relativedelta.relativedelta(observation_date, birth_date)
    time_alive = observation_date - birth_date
    days_of_life = time_alive.days
    days_since_conception = days_of_life + pregnancy_length_days

    corrected_weeks = math.floor(days_since_conception / 7)
    corrected_supplementary_days = days_since_conception - (corrected_weeks * 7)

    # return f"{corrected_weeks}+{corrected_supplementary_days} weeks"
    return {
        'corrected_gestation_weeks': corrected_weeks,
        'corrected_gestation_days': corrected_supplementary_days
    }


def string_to_date(convert_string):
    return datetime.strptime(convert_string, '%d/%m/%Y')


# def tim_date_tests():
    # """
        # validation tests using dummy data
    # """
    # child_dobs = ["03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","09/07/2004","09/07/2004","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","03/12/2010","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","09/07/2004","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","01/04/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009","03/01/2009"]
    # child_measurement_dates = ["03/12/2010","20/12/2010","08/03/2012","22/06/2012","27/11/2014","11/10/2004","11/10/2004","01/04/2009","02/07/2009","21/07/2009","21/07/2009","28/07/2009","03/07/2011","25/01/2012","18/03/2013","05/07/2013","12/03/2014","05/06/2014","24/09/2014","21/05/2015","08/03/2012","12/03/2014","05/06/2014","24/09/2014","21/05/2015","09/07/2004","05/01/2005","30/05/2005","06/09/2005","12/12/2005","09/02/2006","20/10/2006","01/02/2007","05/01/2005","30/05/2005","06/09/2005","28/07/2009","18/08/2009","01/09/2009","04/12/2009","19/02/2010","23/02/2010","06/05/2010","16/09/2010","14/10/2010","16/12/2010","03/03/2011","18/08/2009","04/12/2009","19/02/2010","06/05/2010","16/09/2010","14/10/2010","16/12/2010","03/03/2011","03/05/2010","29/12/2010","13/09/2011","03/10/2011","02/04/2012","06/06/2012","04/03/2013","20/11/2013","18/12/2013","15/01/2014","15/04/2014","19/09/2014","11/12/2014","19/02/2015","03/06/2015","03/05/2010","13/09/2011","04/03/2013","20/11/2013","19/09/2014","11/12/2014","19/02/2015"]
    # child_gestation_months = [27,27,27,27,27,35,35,40,40,40,40,40,27,27,27,27,27,27,27,27,27,27,27,27,27,35,35,35,35,35,35,35,35,35,35,35,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
    # final_ages_list=[]
    # dob_ages_as_list = []
    # measurement_ages_as_dates = []
    # for m in range(len(child_dobs)):
        # age_as_date = string_to_date(child_dobs[m])
        # dob_ages_as_list.append(age_as_date)
    # for n in range(len(child_measurement_dates)):
        # measurement_age_as_date = string_to_date(child_measurement_dates[n])
        # measurement_ages_as_dates.append(measurement_age_as_date)
    # 
    # for i in range(len(child_dobs)):
        # child_corrected_age = corrected_decimal_age(dob_ages_as_list[i],measurement_ages_as_dates[i],child_gestation_months[i],0)
        # child_uncorrected_age = chronological_decimal_age(dob_ages_as_list[i], measurement_ages_as_dates[i])
        # final_ages_list.append(child_uncorrected_age)
    # 
    # return final_ages_list

# def simon_tests():
    # final_list=[]
    # birth_date = '11/8/2010' #Jim Tanner memorial
    # converted_birth_date=string_to_date(birth_date)
    # measurement_dates = ["11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","11/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","18/08/2010","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","10/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","11/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","12/08/2011","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","10/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012",
    # "11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","11/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","12/08/2012","11/11/2012","11/02/2013","11/05/2013","11/08/2013","11/11/2013","11/02/2014","11/05/2014","10/08/2014","11/08/2014","12/08/2014","10/08/2015","11/08/2015","12/08/2015","10/08/2016","11/08/2016","12/08/2016","10/08/2017","11/08/2017","12/08/2017","10/08/2018","11/08/2018","12/08/2018","10/08/2019","11/08/2019","12/08/2019","10/08/2020","11/08/2020","12/08/2020","10/08/2021","11/08/2021","12/08/2021","10/08/2022","11/08/2022","12/08/2022","10/08/2023","11/08/2023","12/08/2023","10/08/2024","11/08/2024","12/08/2024","10/08/2025","11/08/2025","12/08/2025","10/08/2026","11/08/2026","12/08/2026","10/08/2027","11/08/2027","12/08/2027","10/08/2028","11/08/2028","12/08/2028","10/08/2029","11/08/2029","12/08/2029","10/08/2030","11/08/2030","12/08/2030"]
    # gestation_weeks = [24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,40,40,40,40,40,40,41,41,41,41,41,41,41,42,42,42,42,42,42,42,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,40,40,40,40,40,40,41,41,41,41,41,41,41,42,42,42,42,42,42,42,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,24,24,24,24,24,24,24,25,25,25,25,25,25,25,26,26,26,26,26,26,26,27,27,27,27,27,27,27,28,28,28,28,28,28,28,29,29,29,29,29,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,32,32,32,32,32,32,32,33,33,33,33,33,33,33,34,34,34,34,34,34,34,35,35,35,35,35,35,35,36,36,36,36,36,36,36,37,37,37,37,37,37,37,38,38,38,38,38,38,38,39,39,39,39,39,39,39,40,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # gestation_days = [0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,1,2,3,4,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # for m in range(len(measurement_dates)):
        # converted_measurement_date = string_to_date(measurement_dates[m])
        # final_list.append(converted_measurement_date)
        # final_list.append(chronological_decimal_age(converted_birth_date, converted_measurement_date))
        # final_list.append(corrected_decimal_age(converted_birth_date, converted_measurement_date, gestation_weeks[m], gestation_days[m]))
    # return final_list
