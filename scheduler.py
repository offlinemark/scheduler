from z3 import *


class SchedulerError(Exception):
    pass


def _sum_bits(bitvec):
    """

    :param BitVec bitvec:
    :return: symbolic sum of bits in bitvec
    """
    nbits = bitvec.size()
    bits = [Extract(i, i, bitvec) for i in range(nbits)]
    bvs = [Concat(BitVecVal(0, nbits - 1), b) for b in bits]
    sumbits = reduce(lambda a, b: a + b, bvs)
    return sumbits


def _vertical_concat_at(events, idx):
    """

    :param events: list of bitvecs
    :param idx:
    :return:
    """

    bits = [Extract(idx, idx, e) for e in events][::-1]
    return Concat(*bits)


class Host(object):
    def __init__(self, name, id, availability, max_assigned):
        self.name = name
        self.id = id
        self.availability = availability
        self.max_assigned = max_assigned


class Scheduler(object):
    def __init__(self, num_events, num_hosts_per_event=3, max_hosts=32):
        if num_events <= 0:
            raise SchedulerError('number of events must be > 0')

        self.num_events = num_events
        self.num_hosts_per_event = num_hosts_per_event
        self.max_hosts = max_hosts

        # each event is a bitmask. each person is a bit
        self._events = [BitVec('event{}'.format(i + 1), max_hosts) for i in range(num_events)]
        self._id_to_host = {}
        self._name_to_host = {}
        self._num_hosts = 0
        self._solver = Solver()

    def register(self, name, availability, max_assigned=None):
        """

        :param name:
        :param availability:  list of ints, each int is the number of the event that can be made ( 1 indexed)
        :type availability: list[int]
        :param int max_assigned: max number of times they would like to be assigned
        :return:
        """

        # TODO availability must be valid

        if name in self._name_to_host:
            host = self._name_to_host[name]
            host.availability = availability
            host.max_assigned = max_assigned
        else:
            host = Host(name, self._num_hosts, availability, max_assigned)
            self._id_to_host[host.id] = host
            self._name_to_host[host.name] = host

            self._num_hosts += 1

    def schedule(self):
        """
        generate a schedule or return None if impossible

        a schedule is a list of assignments. a single assignment specifies the hosts assigned
        for a specific event

        :return: example schedule
        :rtype: list[list[str]] or None
        """
        self._solver.push()
        self._apply_constraints()

        if self._solver.check() != sat:
            self._solver.pop()
            return None

        model = self._solver.model()
        assignments = []
        for event in self._events:
            assignments.append(model[event].as_long())

        return self._translate_schedule(assignments)

    def _translate_assignment(self, assignment):
        """

        :param int assignment: numeric representation of a single event's schedule
        :return:
        """
        # each 1 bit in assignment is an assigned host. get all the assigned hosts' names
        return [self._id_to_host[idx].name for idx in range(self.max_hosts) if assignment & (1 << idx)]

    def _translate_schedule(self, schedule):
        """
        translate numeric schedule representation (list of ints) into one using names

        :param schedule:
        :type schedule: list[int]
        :return: list[list[name]]
        """
        return [self._translate_assignment(assignment) for assignment in schedule]

    def _constrain_num_hosts_per_event(self):
        for event in self._events:
            event_required_hosts = _sum_bits(event)
            self._solver.add(
                event_required_hosts == self.num_hosts_per_event)  # each event must have num_hosts_per_event people

    def _constrain_host_availability(self):
        for host in self._name_to_host.values():
            for idx, event in enumerate(self._events):
                bit = Extract(host.id, host.id, event)  # symbolic bit represents whether can host
                if idx + 1 in host.availability:
                    self._solver.add(Or(bit == 0, bit == 1))
                else:
                    self._solver.add(bit == 0)

            if host.max_assigned is not None:
                times_assigned = _sum_bits(_vertical_concat_at(self._events, host.id))
                self._solver.add(times_assigned <= host.max_assigned)

    def _constrain_unassigned_bits(self):
        for event in self._events:
            unassigned_bits = Extract(self.max_hosts - 1, self._num_hosts, event)
            self._solver.add(unassigned_bits == 0)

    def _apply_constraints(self):
        self._constrain_num_hosts_per_event()
        self._constrain_host_availability()
        self._constrain_unassigned_bits()
