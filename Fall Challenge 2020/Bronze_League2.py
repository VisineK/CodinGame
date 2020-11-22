import sys
import random
from pprint import pprint

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

    def afford(self, delta):
        for i in range(4):
            if delta[i] < 0 and self.inventory[i] < -delta[i]:
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
        for action in actions:
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

    def get_successors(self):
        pass

    def can_brew(self):
        return any(inv.afford(brew) for brew in brews)

    def get_move(self):
        max_inventory = []
        for i in range(4):
            max_inventory.append(max(-brew['delta'][i] for brew in self.brews))
            if max_inventory[-1] == 0:
                max_inventory[-1] = 1
        max_inventory[0] = 6

        for brew in self.brews:
            brew['afford'] = self.inv.afford(brew['delta'])

        for cast in self.casts:
            afford = True
            for i in range(4):
                if not self.inv.afford(cast['delta']):
                    afford = False
                if self.inv.inventory[i] + cast['delta'][i] > max_inventory[i]:
                    afford = False
            if sum(cast['delta']) + sum(self.inv.inventory) > 10:
                afford = False
            cast['afford'] = afford
            cast['sum_delta'] = sum(cast['delta'])

        for learn in self.learns:
            learn['afford'] = learn['tome_index'] <= self.inv.inventory[0]
            learn['sum_delta'] = sum(learn['delta'])

        self.brews.actions.sort(key=lambda x: (x['afford'], x['price']), reverse=True)
        self.casts.actions.sort(key=lambda x: (x['afford'], x['castable'], -x['sum_delta']), reverse=True)
        self.learns.actions.sort(key=lambda x: (x['afford'], -x['sum_delta']), reverse=True)

        try:
            return "BREW " + random.choice(
                [brew['id'] for brew in self.brews if brew['afford']])
        except IndexError:
            if random.random() < LEARN_RATE[len(self.casts)] and self.learns[0]['afford']:
                return "LEARN " + self.learns[0]['id']
            else:
                try:
                    return "CAST " + random.choice(
                        [
                            cast['id']
                            for cast in self.casts
                            if cast['afford'] and cast['castable']
                        ]
                    )
                except IndexError:
                    return "REST"


##########################################  GAME LOOP  ######################################
while True:
    state = Witch()
    state.load()

    enemy_inventory = list(map(int, input().split()))[:-1]
    
    print(state.get_move())



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
