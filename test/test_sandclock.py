import pytest
import time
from datetime import datetime
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__),'..','sandclock'))


from sandclock import Sandclock

STD_TS_FMT   = '%Y-%m-%d %H:%M:%S Z'
THREE_DAYS   =  3 * 86400

sandclock = Sandclock()
offset = sandclock.getOffset()

def test_structFromSeconds():
    secs_now = time.time()
    utc_struct   = sandclock.structFromSeconds(secs_now)
    local_struct = sandclock.structFromSeconds(secs_now, 'local')
    print (utc_struct)
    print(local_struct)
    tz = time.tzname
    print (tz)
    assert local_struct.tm_hour - utc_struct.tm_hour == offset

    daylight = time.daylight # 1
    print (daylight)

    if offset == -6:
        assert sandclock.getTimeZone() == 'MDT'
        assert daylight == 1
    elif offset == -7:
        assert sandclock.getTimeZone() == 'MST'
        assert daylight != 1

def test_stardard_vs_daylight_saving_time():
    iso_str_feb    = "2017-02-01T12:00:00Z"
    secs_feb       = sandclock.secondsFromString(iso_str_feb)
    utc_struct_feb = sandclock.structFromSeconds(secs_feb)

    iso_str_may    = "2017-05-01T12:00:00Z"
    secs_may       = sandclock.secondsFromString(iso_str_may)
    utc_struct_may = sandclock.structFromSeconds(secs_may)

    assert utc_struct_feb.tm_hour - utc_struct_may.tm_hour == 1


def test_secondsFromStruct():
    tup_with_dst = (2017, 6, 27, 10, 4, 48, 1, 178, 1)
    struct = time.struct_time(tup_with_dst)
    secs   = sandclock.secondsFromStruct(struct)
    assert secs.__class__.__name__ == 'int'

def test_secondsFromString():
    iso_str = "2017-06-26T12:26:08Z"
    secs = sandclock.secondsFromString(iso_str)
    assert secs.__class__.__name__ == 'int'

    iso_str_with_ms = "2017-06-26T12:26:08.222Z"
    secs2 = sandclock.secondsFromString(iso_str_with_ms)
    assert secs2.__class__.__name__ == 'int'

def test_conversions():
    secs_this_run     = 1498623705
    struct_this_run   = sandclock.structFromSeconds(secs_this_run)
    zulu_str_this_run = sandclock.stringFromStruct(struct_this_run, STD_TS_FMT)
    assert zulu_str_this_run == '2017-06-28 04:21:45 Z'

    secs_ref_time     = secs_this_run - THREE_DAYS # 1498364505
    struct_ref_time   = sandclock.structFromSeconds(secs_ref_time)
    zulu_str_ref_time = sandclock.stringFromStruct(struct_ref_time, STD_TS_FMT)
    assert zulu_str_ref_time == '2017-06-25 04:21:45 Z'
    assert secs_ref_time == sandclock.secondsFromStruct(struct_ref_time)

def test_roundTripSecsToStruckAndBack():
    secs_3_days_ago   = int(time.time() - THREE_DAYS)
    struct_3_days_ago = sandclock.structFromSeconds(secs_3_days_ago)
    secs   = int(sandclock.secondsFromStruct(struct_3_days_ago))
    struct_utc   = sandclock.structFromSeconds(secs)
    struct_local = sandclock.structFromSeconds(secs, 'local')

    assert struct_3_days_ago == struct_utc
    assert struct_local.tm_hour - struct_utc.tm_hour == offset
    assert struct_local.tm_hour - struct_3_days_ago.tm_hour == offset
    assert secs_3_days_ago == secs

def test_two_packs_same_result():
    secs = 1498695518
    dt = datetime.utcfromtimestamp(1498695518)
    #datetime.datetime(2017, 6, 29, 0, 18, 38)
    format = '%Y-%m-%dT%H:%M:%SZ'
    zulu_str1 = dt.strftime(format)
    #'2017-06-29T00:18:38Z'
    zulu_str2 = sandclock.stringFromSeconds(secs, format)
    assert zulu_str1 == zulu_str2

def test_pop_offset_colon():
    bamboo_str = '2017-06-12T13:55:39.712-06:00'
    str1 = sandclock.popLastColon(bamboo_str)
    assert str1 == '2017-06-12T13:55:39.712-0600'

