import git
import time
import cPickle as pickle

__version__ = 0.1


class Accumulator(object):
    """
    Accumulator
    """
    def __init__(self, name):

        self.name = name
        self.reset()

    def reset(self):

        self.acc = 0
        self.count = 0

    def update(self, val, n=1):

        self.acc += val * n
        self.count += n

    def get(self):

        raise NotImplementedError("Accumulator should be subclassed")


class AvgMetric(Accumulator):

    def __init__(self, name):

        super(AvgMetric, self).__init__(name)

    def get(self):

        return self.acc * 1. / self.count


class SumMetric(Accumulator):

    def __init__(self, name):

        super(SumMetric, self).__init__(name)

    def get(self):

        return self.acc


class Experiment(object):

    def __init__(self, name, get_git_hash=True):

        super(Experiment, self).__init__()

        self.name = name
        self.config = dict()
        self.results = dict()

        self.results['time'] = []
        self.clocked = time.time()

        if get_git_hash:
            self.add_git_hash()

    def add_git_hash(self):

        try:
            repo = git.Repo(search_parent_directories=True)
            self.add_config({'git_hash': repo.head.object.hexsha})
        except:
            print("I tried to find a git repository in current "
                  "and parent directories but did not find any.")

    def add_config(self, config_dict):

        for (key, value) in config_dict.iteritems():
            self.config[key] = value

    def set_data(self, data_dict):

        for (key, value) in data_dict.iteritems():
            self.results[key] = value

    def append_data(self, data_dict, time=True):

        for (key, value) in data_dict.iteritems():
            self.results[key].append(value)

        if time:
            relative_time = time.time() - self.clocked
            self.results['time'].append(relative_time)

    def set_metrics(self, *args):

        data_dict = dict()
        for metric in args:
            data_dict[metric.name] = metric.get()

        self.set_data(data_dict)

    def append_metrics(self, time=True, *args):

        data_dict = dict()
        for metric in args:
            data_dict[metric.name] = metric.get()

        self.append_data(data_dict, time)

    def to_file(self, filename):

        var_dict = vars(self)
        pickle.dump(var_dict, open(filename, 'wb'))
        print("Experiment logged in {}".format(filename))


class NNExperiment(Experiment):

    def __init__(self, name):

        super(NNExperiment, self).__init__(name)

        self.add_data({'train_batch_time': [],
                       'train_objective': [],
                       'train_accuracy@1': [],
                       'train_accuracy@k': [],
                       'test_batch_time': [],
                       'test_objective': [],
                       'test_accuracy@1': [],
                       'test_accuracy@k': []})