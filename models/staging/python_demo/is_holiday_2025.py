import holidays
import pandas

def model(dbt, session):

    dbt.config(
        materialized="table",
        packages=['pandas', 'holidays']
    )

    us_holidays = holidays.US(years=[2025])

    df = dbt.ref("date_spine").to_pandas()

    df['is_holiday_2025'] = df['date'].apply(lambda x: x in us_holidays)

    return df