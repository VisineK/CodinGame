import sys
import random
from pprint import pprint
import time


# I replaced "action_?" with "a?" for readability issues
#            "delta_?" with "d?"
#            "inv_?" with "i?"

random.seed(1337)

# freq learn
LEARN_RATE = [
    1.0,
    1.0,
    1.0,
    1.0,
    0.4,
    0.1,
    0.05,
    0.025,
    0.00125,
    0.0001,
    0,
]


class Inventory:
    inventory = None

    def __init__(self):
        self.inventory = [0, 0, 0, 0]

    def load(self):
        self.inventory = list(map(int, input().split()))[:-1]

    def give(self, delta):
        print(self.inventory, file=sys.stderr)
        for i in range(4):
            if delta[i] < 0 and self.inventory[i] < -delta[i]:
                return False
        if sum(delta) + sum(self.inventory) > 10:
            return False
        return True

    def copy(self):
        other = Inventory()
        other.inventory = self.inventory[:]
        return other


class ActionList:
    actions = None

    def __init__(self):
        self.actions = []

    def append(self, item):
        self.actions.append(item)

    def copy(self):
        other = ActionList()
        for action in self.actions:
            new_action = {}
            for key, value in action.items():
                if type(value) == list:
                    new_action[key] = value[:]
                else:
                    new_action[key] = value
            other.append(new_action)
        return other

    def __getitem__(self, index):
        return self.actions[index]

    def __len__(self):
        return len(self.actions)


class InvalidMoveError(Exception):
    pass


class Witch:
    inv = None
    casts = None
    brews = None
    learns = None

    def __init__(self):
        pass

    def load(self):
        acount = int(input())  # the number of spells and recipes in play
        self.brews = ActionList()
        self.casts = ActionList()
        self.learns = ActionList()
        for i in range(acount):
            (
                aid,
                atype,
                d0,
                d1,
                d2,
                d3,
                price,
                tome_index,
                tax_count,
                castable,
                repeatable,
            ) = input().split()
            d0 = int(d0)
            d1 = int(d1)
            d2 = int(d2)
            d3 = int(d3)
            price = int(price)
            tome_index = int(tome_index)
            tax_count = int(tax_count)
            castable = castable != "0"
            repeatable = repeatable != "0"
            event = []
            if atype == "BREW":
                event = self.brews
            elif atype == "CAST":
                event = self.casts
            elif atype == "LEARN":
                event = self.learns
            event.append(
                {
                    'id': aid,
                    'type': atype,
                    'delta': (d0, d1, d2, d3),
                    'price': price,
                    'tome_index': tome_index,
                    'tax_count': tax_count,
                    'castable': castable,
                    'repeatable': repeatable,
                }
            )
        self.inv = Inventory()
        self.inv.load()

    def get_move(self):
        max_inventory = []
        for i in range(4):
            max_inventory.append(max(-brew['delta'][i] for brew in self.brews))
            if max_inventory[-1] == 0:
                max_inventory[-1] = 1
        max_inventory[0] = 6

        for brew in self.brews:
            brew['give'] = self.inv.give(brew['delta'])

        for cast in self.casts:
            give = True
            for i in range(4):
                if not self.inv.give(cast['delta']):
                    give = False
                if self.inv.inventory[i] + cast['delta'][i] > max_inventory[i]:
                    give = False
            if sum(cast['delta']) + sum(self.inv.inventory) > 10:
                give = False
            cast['give'] = give
            cast['sum_delta'] = sum(cast['delta'])

        for learn in self.learns:
            learn['give'] = learn['tome_index'] <= self.inv.inventory[0]
            learn['sum_delta'] = sum(learn['delta'])

        self.brews.actions.sort(key=lambda x: (x['give'], x['price']), reverse=True)
        self.casts.actions.sort(key=lambda x: (x['give'], x['castable'], -x['sum_delta']), reverse=True)
        self.learns.actions.sort(key=lambda x: (x['give'], -x['sum_delta']), reverse=True)

        try:
            return "BREW " + random.choice(
                [brew['id'] for brew in self.brews if brew['give']])
        except IndexError:
            if random.random() < LEARN_RATE[len(self.casts)] and self.learns[0]['give']:
                return "LEARN " + self.learns[0]['id']
            else:
                try:
                    return "CAST " + random.choice(
                        [
                            cast['id']
                            for cast in self.casts
                            if cast['give'] and cast['castable']
                        ]
                    )
                except IndexError:
                    return "REST"

    def __copy(self):
            other = Witch()
            other.brews = self.brews.copy()
            other.casts = self.casts.copy()
            other.learns = self.learns.copy()
            other.inv = self.inv.copy()
            return other

    def can_brew(self):
        brewable = [brew for brew in self.brews if self.inv.give(brew['delta'])]
        if brewable:
            return random.choice([brew['id'] for brew in brewable])
        else:
            return False


    def do_rest(self):
        other = self.__copy()
        valid = False
        for spell in other.casts.actions:
            if not spell['castable']:
                valid = True
                spell['castable'] = True
        if valid:
            return other
        else:
            raise InvalidMoveError('REST move invalid')


    def do_cast(self, idx):
        other = self.__copy()
        cast = other.casts[idx]
        if not cast['castable']:
            raise InvalidMoveError('Non-castable spell')
        if not self.inv.give(cast['delta']):
            raise InvalidMoveError('Can\'t give spell')
        for i in range (4):
            other.inv.inventory[i] += cast['delta'][i]
        cast['castable']  = False
        return other

    def do_learn(self, idx):
        other = self.__copy
        return other

    def get_successors(self):
        """ Return a pair : (move, state) """
        res = []
        try:
            res.append(("REST", self.do_rest()))
        except InvalidMoveError:
            pass
        for i in range(len(self.casts)):
            try:
                res.append(("CAST " + self.casts[i]['id'], self.do_cast(i)))
            except InvalidMoveError:
                pass
        '''
        for i in len(self.learns):
            try:
                res.append(self.do_learn(i))
            except InvalidMoveError:
                pass
        '''
        return res
    
class BreathWitch(Witch):
    def get_move(self, end):
        if self.can_brew():
            return "BREW " + self.can_brew()
        q = [([], self)]
        while time.time() < end:
            moves, state = q.pop(0)
            if state.can_brew():
                print(moves, file=sys.stderr)
                return moves[0] + " AhAh!"
            for move, succ in state.get_successors():
                q.append((moves + [move], succ))
        return super().get_move()


##########################################  GAME LOOP  ######################################
while True:
    end = time.time() + 0.040
    state = BreathWitch()
    state.load()

    enemy_inventory = list(map(int, input().split()))[:-1]
    
    print(state.get_move(end=end))



# aid: the unique ID of this spell or recipe
# atype: in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
# d0: tier-0 ingredient change
# d1: tier-1 ingredient change
# d2: tier-2 ingredient change
# d3: tier-3 ingredient change
# price: the price in rupees if this is a potion
# tome_index: in the first two leagues: always 0; later: the index in the tome if this is a tome spell, equal to the read-ahead tax; For brews, this is the value of the current urgency bonus
# tax_count: in the first two leagues: always 0; later: the amount of taxed tier-0 ingredients you gain from learning this spell; For brews, this is how many times you can still gain an urgency bonus
# castable: in the first league: always 0; later: 1 if this is a castable player spell
# repeatable: for the first two leagues: always 0; later: 1 if this is a repeatable player spell
