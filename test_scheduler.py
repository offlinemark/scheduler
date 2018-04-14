import unittest

from scheduler import Scheduler, SchedulerError

class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.s = Scheduler(4, 3)

    def test_zero_events(self):
        with self.assertRaises(SchedulerError):
            self.s = Scheduler(0)

    def test_unsat(self):
        self.s.register('mark', [1, 2, 3, 4])
        self.s.register('nark', [1, 2, 3, 4])

        s = self.s.schedule()
        self.assertIs(s, None)

    def test_unsat2(self):
        self.s.register('mark', [1, 2, 3, 4])
        self.s.register('nark', [1, 2, 3, 4])
        self.s.register('b', [2, 3, 4])

        s = self.s.schedule()
        self.assertIs(s, None)

    def test_works_trivial(self):
        self.s.register('mark', [1, 2, 3, 4])
        self.s.register('nark', [1, 2, 3, 4])
        self.s.register('bark', [1, 2, 3, 4])

        # sat, we all go every week
        sched = self.s.schedule()
        print sched
        for week in sched:
            self.assertIn('mark', week)
            self.assertIn('nark', week)
            self.assertIn('bark', week)

    def test_works_single_sol(self):
        self.s.register('mark', [1, 2, 4])
        self.s.register('nark', [2, 3, 4])
        self.s.register('bark', [1, 3, 4])
        self.s.register('lark', [1, 2, 3])

        # sat, we all go every week
        sched = self.s.schedule()
        self.assertItemsEqual(sched[0], ['mark', 'bark', 'lark'])
        self.assertItemsEqual(sched[1], ['mark', 'nark', 'lark'])
        self.assertItemsEqual(sched[2], ['nark', 'bark', 'lark'])
        self.assertItemsEqual(sched[3], ['mark', 'bark', 'nark'])

    def test_push_pop(self):
        self.s.register('mark', [1, 2, 4])
        self.s.register('nark', [2, 3, 4])

        s = self.s.schedule()
        self.assertIs(s, None)

        self.s.register('zark', [1, 2, 3, 4])
        self.s.register('aark', [1, 2, 3, 4])

        sched = self.s.schedule()

    def test_null(self):
        self.s = Scheduler(num_events=1)
        self.assertIs(self.s.schedule(), None)

    def test_no_hosts_needed(self):
        self.s = Scheduler(num_events=1, num_hosts_per_event=0)
        self.assertEqual(self.s.schedule(), [[]])

    def test_reg_but_nothing(self):
        self.s = Scheduler(num_events=1, num_hosts_per_event=1)
        self.s.register('mark', [])
        self.assertIs(self.s.schedule(), None)

    def test_single(self):
        self.s = Scheduler(num_events=1, num_hosts_per_event=1)
        self.s.register('mark', [1])
        self.assertEqual(self.s.schedule(), [['mark']])

    def test_unsat_5(self):
        self.s = Scheduler(num_events=5, num_hosts_per_event=2)
        self.s.register('mark', [1, 2, 3, 4, 5])
        self.s.register('n', [2, 3, 4, 5])
        self.assertIs(self.s.schedule(), None)

    def test_detailed(self):
        self.s = Scheduler(num_events=5, num_hosts_per_event=2)
        self.s.register('mark', [1, 5])
        self.s.register('n', [3, 4,])
        self.s.register('nzz', [2, 4])
        self.s.register('nzzq', [1, 2, 3, 5])
        self.assertEqual(self.s.schedule(), [
            ['mark', 'nzzq'],
            ['nzz',  'nzzq'],
            ['n',    'nzzq'],
            ['n',    'nzz'],
            ['mark', 'nzzq'],

        ])

    def test_update_person(self):
        self.s = Scheduler(num_events=1, num_hosts_per_event=1)
        self.s.register('mark', [1])
        self.assertEqual(self.s.schedule(), [['mark']])
        self.s.register('mark', [])
        self.assertEqual(self.s.schedule(), None)

    def test_unsat_twice(self):
        self.s = Scheduler(num_events=4, num_hosts_per_event=1)
        self.s.register('mark', [1, 2, 3, 4], 2)
        self.assertEqual(self.s.schedule(), None)
        self.s.register('lark', [3, 4])
        self.s.schedule()




