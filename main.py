
import configparser
import datetime
import uuid
import json
from io import BytesIO
from openpyxl import load_workbook
from icalendar import Calendar, Event, Timezone, vDDDTypes

VTIMEZONE = Timezone.from_ical("""BEGIN:VTIMEZONE
TZID:Asia/Shanghai
X-LIC-LOCATION:Asia/Shanghai
BEGIN:STANDARD
TZNAME:CST
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE""")

TIMEZONE = VTIMEZONE.to_tz()


def load_from_json(file):
    f = open(file, 'r', encoding='utf8')
    timetable = json.load(f)["studentTableVm"]["activities"]
    # print(timetable)
    d = [(cour["courseName"],
          cour["courseCode"],
          (cour["weeksStr"],
           cour["weekday"], cour["startUnit"], cour["endUnit"]),
          cour["room"],
          ','.join(i for i in cour['teachers']),
          cour["weekIndexes"])
         for cour in timetable]
    # print(d)
    return d


def mkevent(data, cal, dt):
    weeks, week_day, all_week, classes = get_schedule(
        data)
    event_class = Event()
    event_class.add('SUMMARY', data[0])
    if data[3] is not None:
        event_class.add('LOCATION', data[3])
    if data[4] is not None:
        event_class.add('DESCRIPTION', "教师:" + data[4] + "\n教学班号:" + data[1])
    else:
        event_class.add('DESCRIPTION', "教学班号:" + data[1])
    for start_class, end_class in classes:
        start_week = weeks[0]
        end_week = weeks[1]
        event = event_class.copy()
        if all_week is False:
            count = int(end_week) - int(start_week) + 1
            event.add("RRULE", {"freq": "weekly", "count": count})
            class_start_date = dt + \
                datetime.timedelta(weeks=int(start_week) - 1,
                                   days=week_day - 1)
            class_start_time = datetime.timedelta(hours=time_dict[int(start_class)][0][0],
                                                  minutes=time_dict[int(start_class)][0][1])
            class_end_time = datetime.timedelta(hours=time_dict[int(end_class)][1][0],
                                                minutes=time_dict[int(end_class)][1][1])
            dtstart = class_start_date + class_start_time
            dtend = class_start_date + class_end_time
            namespace = uuid.UUID(
                bytes=int(dtstart.timestamp()).to_bytes(length=8, byteorder='big') +
                int(dtend.timestamp()).to_bytes(length=8, byteorder='big')
            )
        else:
            dtstart = (dt +
                       datetime.timedelta(weeks=int(start_week) - 1)).date()
            dtend = (dt +
                     datetime.timedelta(weeks=int(end_week))).date()
            namespace = uuid.UUID(
                bytes=int(dtstart.toordinal()).to_bytes(length=8, byteorder='big') +
                int(dtend.toordinal()).to_bytes(length=8, byteorder='big')
            )

        add_datetime(event, 'DTEND', dtend)
        add_datetime(event, 'DTSTART', dtstart)
        event.add('UID', uuid.uuid3(namespace, data[0] + "-" + data[1]))

        event.add('DTSTAMP', datetime.datetime.now())
        cal.add_component(event)


def add_datetime(component, name, time):
    """一个跳过带时区的时间中 VALUE 属性的 workaround

    某些日历软件无法正常解析同时带 TZID 和 VALUE 属性的时间。
    详见 https://github.com/collective/icalendar/issues/75 。
    """
    vdatetime = vDDDTypes(time)
    if 'VALUE' in vdatetime.params and 'TZID' in vdatetime.params:
        vdatetime.params.pop('VALUE')
    component.add(name, vdatetime)


def get_schedule(data):
    # 返回值说明： [[开始周次，结束周次], ...]，星期几，是否整周，[[开始节数，结束节数]...]
    return [min(data[5]), max(data[5])], data[2][1], False, [[data[2][2], data[2][3]]]


def get_timetable_layout(file):
    f = open(file, 'r', encoding='utf8')
    data = json.load(f)["studentTableVm"]["timeTableLayout"]["courseUnitList"]
    time_dict = {}
    for d in data:
        str_st = str(d['startTime'])
        str_ed = str(d['endTime'])
        time_dict[d['indexNo']] = [
            (int(str_st[0:-2]), int(str_st[-2:])), (int(str_ed[0:-2]), int(str_ed[-2:]))]

    return time_dict


def mkical(data, start_date, time_dict):
    cal = Calendar()
    cal.add('prodid', '-//DLUT//DLUT Calendar//')
    cal.add('version', '2.0')
    cal.add_component(VTIMEZONE)
    dt = datetime.datetime.combine(
        start_date, datetime.time(), tzinfo=TIMEZONE)
    for items in data:
        mkevent(items, cal, dt)
    return cal


if __name__ == '__main__':
    data = load_from_json('./data.json')
    time_dict = get_timetable_layout('./data.json')
    start_date = datetime.date(2021, 3, 8)
    cal = mkical(data, start_date, time_dict)

    f = open("timetable.ics", 'wb')
    f.write(cal.to_ical())
    f.close()
