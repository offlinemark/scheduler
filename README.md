# scheduler

A python library for automatically generating a schedule assigning
hosts for a repeating sequence of events.

## example

Example use case: planning a month's schedule for a weekly meetup group, where
the schedule is subject to a number of constraints.

- each meetup requires two moderators
- moderators should not moderate more than twice per month

```
In [13]: s = scheduler.Scheduler(num_events=4, num_hosts_per_event=2)

In [14]: s.register('mark', availability=[1, 2, 3, 4], max_assigned=2)

In [15]: s.register('bradley', availability=[1, 4], max_assigned=2)

In [16]: s.register('max', availability=[2, 3, 4], max_assigned=2)

In [17]: s.register('nikolai', availability=[1, 2], max_assigned=2)

In [18]: s.schedule()
Out[18]:
[['bradley', 'nikolai'],
['max', 'nikolai'],
['mark', 'max'],
['mark', 'bradley']]

In [19]: s.register('nikolai', availability=[1], max_assigned=2)

In [20]: s.schedule()

In [21]: # there was no possible schedule
```