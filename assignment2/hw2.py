#!/usr/bin/env python
import json
import sys

class DictDefaultEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class PR:
    def __init__(self, p, r):
        self.p = p
        self.r = r

PR_MAT = {
    'exercise': {
        'fit':      { 'fit': PR(0.99, 8),   'unfit': PR(0.01, 8) },
        'unfit':    { 'fit': PR(0.2, 0),    'unfit': PR(0.8, 0) },
    },
    'relax': {
        'fit':      { 'fit': PR(0.7, 10),   'unfit': PR(0.3, 10) },
        'unfit':    { 'fit': PR(0, 5),      'unfit': PR(1, 5) }
    }
}

def r(cur_state, action, new_state):
    return PR_MAT[action][cur_state][new_state].r

def p(cur_state, action, new_state):
    return PR_MAT[action][cur_state][new_state].p

death_probs = {
    'exercise': 0.1,
    'relax':    0.01
}

# p -> p'
def add_death(actions):
    for action, death_probability in death_probs.items():

        actions[action]['dead'] = { 'dead': PR(1, 0) }
        for state in actions[action].keys():
            if state == 'dead':
                continue

            actions[action]['dead'][state] = PR(0, 0)

            for new_state in actions[action][state].keys():
                actions[action][state][new_state].p = (1 - death_probability)*p(state, action, new_state)

            actions[action][state]['dead'] = PR(death_probability, 0)

def q0(state, action):
    return p(state, action, 'fit')*r(state, action, 'fit') + p(state, action, 'unfit')*r(state, action, 'unfit')

def vn(n, state, disc_factor):
    return max(q(n, state, 'exercise', disc_factor), q(n, state, 'relax', disc_factor))

def q(n, state, action, disc_factor):
    if n == 0:
        return q0(state, action)

    return q0(state, action) + \
        disc_factor * (\
            p(state, action, 'fit')  * vn(n-1, 'fit', disc_factor) + \
            p(state, action, 'unfit')* vn(n-1, 'unfit', disc_factor)
        )

def main():
    add_death(PR_MAT)

    valid_states = next(iter(PR_MAT.values())).keys()
    if len(sys.argv) != 4 or sys.argv[3] not in valid_states:
        print(f'usage: {sys.argv[0]} <n> <γ> <{"|".join(valid_states)}>', file=sys.stderr)
        sys.exit(1)

    n = int(sys.argv[1])
    disc_factor = float(sys.argv[2])
    state = sys.argv[3]

    for action in PR_MAT:
        print(f'q(n={n}, s={state}, a={action}, γ={disc_factor}) = {q(n, state, action, disc_factor)}')

if __name__ == '__main__':
    main()
