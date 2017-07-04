import random
import math
import operator as op
from functools import reduce
import copy

class Judge():

    MAX_POSTERS = 5
    MAX_DETAILED_POSTERS = 2

    def __init__(self, identifier, lab, poster_number=None):
        self.identifier = identifier
        self.lab = lab
        self.poster_number = poster_number
        self._posters = set()
        self._detailed_posters = set()

    def __repr__(self):
        return '{} {} of lab {}'.format(type(self).__name__, self.identifier, self.lab)

    def __eq__(self, other):
        return self.lab == other.lab

    def __ne__(self, other):
        return not self == other

    @property
    def posters(self):
        return self._posters

    def add_poster(self, poster):
        if self.num_posters > self.MAX_POSTERS:
            raise ValueError('Already at max posters')
        self._posters.add(poster)

    @property
    def num_posters(self):
        return len(self.posters)

    @property
    def detailed_posters(self):
        return self._detailed_posters

    def add_detailed_poster(self, poster):
        if self.num_detailed_posters > self.MAX_DETAILED_POSTERS:
            raise ValueError('Already at max detailed posters')
        self._detailed_posters.add(poster)

    @property
    def num_detailed_posters(self):
        return len(self.detailed_posters)



class Presenter(Judge):

    MAX_POSTERS = math.inf  # no hard limit on number of people judging each person
    MAX_DETAILED_POSTERS = math.inf

    def __init__(self, identifier, lab, poster_number=None):

        """Presenter class.
        :identifier:    unique representation for that presenter
        :lab:           what lab group the presenter belongs to
                        (to ensure no presenter is a judge for another of the same lab)
        :poster_number: Poster number

        """
        super().__init__(identifier, lab, poster_number)



def get_people(people: list):
    """
    :people: list of dicts with keys identifier, lab, poster_number (optional, can be None)
    """
    judges, presenters = list(), list()
    for p in people:
        if p.get('poster_number') is not None:
            presenter = Presenter(**p)
            presenters.append(presenter)
        judge = Judge(**p)
        judges.append(judge)

    return judges, presenters


def mean(sequence):
    return reduce(op.add, sequence) / len(sequence)

def range_(sequence):
    return max(sequence) - min(sequence)

def std(sequence):
    xbar = mean(sequence)
    var  = ((x-xbar)**2 for x in sequence)
    return (reduce(op.add, var) / len(sequence))**(1/2)


def stat_presenters(presenters):

    num_posters, num_detailed_posters = list(), list()
    for presenter in presenters:
        num_posters.append(presenter.num_posters)
        num_detailed_posters.append(presenter.num_detailed_posters)

    stats = dict(ranking  = {'mean'  : mean(num_posters),
                             'std'   : std(num_posters),
                             'range' : range_(num_posters),
                             'min'   : min(num_posters),
                             'max'   : max(num_posters),
    },
                 detailed = {'mean'  : mean(num_detailed_posters),
                             'std'   : std(num_detailed_posters),
                             'range' : range_(num_detailed_posters),
                             'min'   : min(num_detailed_posters),
                             'max'   : max(num_detailed_posters),
                 }

    )
    return stats

def get_presenter(judge, presenters):

    failcount = 0  # just in case
    while True:
        presenter = random.choice(presenters)
        if judge != presenter:  # check if from same lab
            return presenter
        else:
            failcount += 1
        if failcount > 1000:  # probably stuck
            raise ValueError("Couldn't find a presenter for {!r}".format(judge))

def get_detailed_presenter(judge, presenters):
    """Function also ensures poster numbers are not on the same day
    """
    failcount = 0  # just in case
    while True:
        presenter = get_presenter(judge, presenters)
        if judge.poster_number is None or (judge.poster_number % 2 != presenter.poster_number % 2):
            return presenter
        else:
            failcount += 1
        if failcount > 1000:  # probably stuck
            raise ValueError("Couldn't find a presenter for {!r}".format(judge))

def filter_presenters(presenters, poster_numbers=None):
    """Filter presenters by excluding those with a given poster number"""
    if poster_numbers is None:
        poster_numbers = ()
    for presenter in presenters:
        # print(presenter.poster_number, poster_numbers)
        if presenter.poster_number not in poster_numbers:
            yield presenter
        else:
            pass


def assign_judges(judges, presenters):

    for _ in range(5):  # assign 5 presenters to each judge
        for judge in judges:

            sub_presenters = list(filter_presenters(presenters, judge.posters))

            presenter = get_presenter(judge, sub_presenters)
            judge.add_poster(presenter.poster_number)
            presenter.add_poster(judge.identifier)


    for _ in range(2):  # assign 2 detailed posters to each judge
        for judge in judges:
            sub_presenters = list(filter_presenters(presenters, judge.detailed_posters))
            presenter = get_detailed_presenter(judge, sub_presenters)
            judge.add_detailed_poster(presenter.poster_number)
            presenter.add_detailed_poster(judge.identifier)

    return judges, presenters

def clear_assignments(sequence):
    """sequence can be of judges or posters"""
    for s in sequence:
        s._posters.clear()
        s._detailed_posters.clear()


def gen_people(num_judges=120, num_labs=20, num_presenters=40):
    """Generate people for testing"""

    people = list()
    tot_presenters = 0
    labs = ['Lab'+str(x) for x in range(num_labs)]
    for i in range(100):
        person = dict(identifier='Person'+str(i),
                      lab=random.choice(labs),
                      poster_number = i if i < num_presenters else None
        )
        people.append(person)
    return people

def check_best_result(presenters, last=None):

    if last is None:
        last = [0, 0]
    lowest_rankings = min([x.num_posters for x in presenters])
    lowest_detailed = min([x.num_detailed_posters for x in presenters])

    if lowest_detailed > last[0] and lowest_rankings > last[1]:
        return [True, lowest_rankings, lowest_detailed]
    else:
        return [False, *last]

def main(people: list, n_iterations=100):
    """
    :people: list of dicts with keys identifier, lab, poster_number (optional, can be None)
    """

    judges, presenters = get_people(people)

    judges_best, presenters_best = None, None

    last_min_scores = None
    all_min_scores = list()
    all_stats = list()
    for i in range(n_iterations):
        judges, presenters = assign_judges(judges, presenters)
        is_best, *last_min_scores = check_best_result(presenters, last_min_scores)
        if is_best:
            judges_best = copy.deepcopy(judges)
            presenters_best = copy.deepcopy(presenters)
        clear_assignments(judges)
        clear_assignments(presenters)
    return judges_best, presenters_best


if __name__ == '__main__':

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sb
    rc = {'font.family': 'serif',
          'font.serif': ['Times', 'Palatino', 'serif']
    }
    sb.set_context('paper', font_scale=1.4)
    sb.set_style('white', rc)


    # people = [dict(identifier='Bob', lab='Lab1', poster_number=1),
    #           dict(identifier='Sam', lab='Lab1', poster_number=2),
    #           dict(identifier='Sue', lab='Lab2', poster_number=3),
    #           dict(identifier='Sally', lab='Lab3', poster_number=None),
    # ]
    n_judges       = 120
    n_labs         = 20
    n_presenters = 40
    n_iterations = 10

    people = gen_people(n_judges, n_labs, n_presenters)
    judges, presenters = get_people( people )
    # judges, presenters = assign_judges(judges, presenters)

    print('Running with {} judges, {} labs, {} presenters, {} iterations'.format(n_judges,
                                                                                n_labs,
                                                                                n_presenters,
                                                                                n_iterations))

    last_min_scores = None
    all_min_scores = list()
    all_stats = list()
    for i in range(n_iterations):
        judges, presenters = assign_judges(judges, presenters)
        is_best, *last_min_scores = check_best_result(presenters, last_min_scores)
        all_min_scores.append(last_min_scores)

        # stats = stat_presenters(presenters)
        stats = {'ranking'  : [x.num_posters for x in presenters],
                 'detailed' : [x.num_detailed_posters for x in presenters]
        }
        # df = pd.DataFrame(stats).T
        df = pd.DataFrame(stats)
        df['rep'] = i
        clear_assignments(judges)
        clear_assignments(presenters)
        all_stats.append(df)

    min_scores = pd.DataFrame(all_min_scores, columns=['Min Ranking', 'Min Detailed'])
    fig, ax = plt.subplots()
    fig.set_size_inches(6,3)
    min_scores.plot(ax=ax)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Highest Min Value')
    ax.set_ylim(bottom=-1, top=min_scores.max().max()+2)
    fig.tight_layout()
    fig.savefig('poster_matching_best_scores.png', dpi=150)

    dfs = (pd.concat(all_stats).reset_index(drop=True)
           .melt(id_vars='rep')
    )
    gp = dfs.groupby(['rep', 'variable'])

    g = sb.factorplot(x='variable', y='value', data=dfs, kind='bar')
    g.ax.set_xlabel('Judging')
    g.ax.set_ylabel('Number of Judges')
    g.savefig('poster_matching_bar.png', dpi=150)

    blue, green, *rest = sb.color_palette()

    # fig, axs = plt.subplots(nrows=1, ncols=2, sharey=True)
    fig, ax = plt.subplots(nrows=1, ncols=1, sharey=True)
    fig.set_size_inches(6, 3)
    # ax0, ax1 = axs
    for name, grp in dfs.groupby('rep'):
        detailed = grp.query('variable=="detailed"')['value']
        ranking  = grp.query('variable=="ranking"')['value']
        sb.kdeplot(ranking, label='__nolabel__', ax=ax, color=blue, alpha=.1)
        sb.kdeplot(detailed, label='__nolabel__', ax=ax, color=green, alpha=.1)
    sb.kdeplot(dfs.query('variable=="ranking"')['value'], ax=ax, color=blue, linewidth=2,
               marker='x', alpha=.8, label='Poster Ranking Judges')
    sb.kdeplot(dfs.query('variable=="detailed"')['value'], ax=ax, color=green, linewidth=2,
               markeredgecolor='k', alpha=.8, label='Detailed Poster Judges')
    ax.set_xlabel('Number of Judges per Poster')
    ax.set_ylabel('Density')
    fig.tight_layout()
    fig.savefig('poster_matching_distributions.png', dpi=150)
