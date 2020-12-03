import sys
import random
import time
from collections import deque


DEBUG = True
random.seed(1337)

# learning frequency
LEARN_FREQ = [
    1.0,
    1.0,
    1.0,
    1.0,
    1.0,
    0.5,
    0.1,
    0.05,
    0.025,
    0.00125,
    0.0001,
    0,
]
LEARN_FREQ = [0.0] * 60


# Inventory management
class Inventory:
    inventory = None

    def __init__(self):
        self.inventory = [0, 0, 0, 0]

    def load(self):
        self.inventory = list(map(int, input().split()))[:-1]

    def give(self, delta):
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


# Management the actions that the witch can carry out 
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


# Initializes the different possible actions for the witch
class Witch:
    inv = None
    casts = None
    brews = None
    learns = None
    levelup = False
    compulsory_casts = None

    def __init__(self):
        pass

    def load(self):
        acount = int(input())  # the number of spells and recipes in play
        self.brews = ActionList()
        self.casts = ActionList()
        self.learns = ActionList()
        self.levelup = True
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
                    "id": aid,
                    "type": atype,
                    "delta": (d0, d1, d2, d3),
                    "price": price,
                    "tome_index": tome_index,
                    "tax_count": tax_count,
                    "castable": castable,
                    "repeatable": repeatable,
                }
            )
        self.inv = Inventory()
        self.inv.load()


    def get_move(self):
        max_inventory = []
        for i in range(4):
            max_inventory.append(max(-brew["delta"][i] for brew in self.brews))
            if max_inventory[-1] == 0:
                max_inventory[-1] = 1
        max_inventory[0] = 6

        for brew in self.brews:
            brew["give"] = self.inv.give(brew["delta"])
        for cast in self.casts:
            give = True
            for i in range(4):
                if not self.inv.give(cast["delta"]):
                    give = False
                if self.inv.inventory[i] + cast["delta"][i] > max_inventory[i]:
                    give = False
            if sum(cast["delta"]) + sum(self.inv.inventory) > 10:
                give = False
            cast["give"] = give
            cast["sum_delta"] = sum(cast["delta"])
        for learn in self.learns:
            learn["give"] = learn["tome_index"] <= self.inv.inventory[0]
            learn["sum_delta"] = sum(learn["delta"])
        self.brews.actions.sort(key=lambda x: (x["give"], x["price"]), reverse=True)
        self.casts.actions.sort(
            key=lambda x: (x["give"], x["castable"], -x["sum_delta"]), reverse=True
        )
        self.learns.actions.sort(
            key=lambda x: (x["give"], -x["sum_delta"]), reverse=True
        )

        try:
            return "BREW " + random.choice(
                [brew["id"] for brew in self.brews if brew["give"]]
            )
        except IndexError:
            if (
                random.random() < LEARN_FREQ[len(self.casts)]
                and self.learns[0]["give"]
            ):
                return "LEARN " + self.learns[0]["id"]
            else:
                try:
                    return "CAST " + random.choice(
                        [
                            cast["id"]
                            for cast in self.casts
                            if cast["give"] and cast["castable"]
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
        brewable = [brew for brew in self.brews if self.inv.give(brew["delta"])]
        if brewable:
            return random.choice([brew["id"] for brew in brewable])
        else:
            return False

    def do_rest(self):
        other = self.__copy()
        valid = False
        other.compulsory_casts = []
        for idx, spell in enumerate(other.casts.actions):
            if not spell["castable"]:
                valid = True
                spell["castable"] = True
                other.compulsory_casts.append(idx)
        if valid:
            return other
        else:
            return None  # REST move invalid

    def do_cast(self, idx):
        if self.compulsory_casts:
            if idx not in self.compulsory_casts:
                return []  # Compulsory spell exists
        other = self.__copy()
        cast = other.casts[idx]
        if not cast["castable"]:
            return []  #  Non castable spell
        if not self.inv.give(cast["delta"]):
            return []  # Can't give spell
        for i in range(4):
            other.inv.inventory[i] += cast["delta"][i]
        cast["castable"] = False
        return [(f"CAST {cast['id']}", other)]

    def do_learn(self, idx):
        learn = self.learns[idx]
        tome_index = learn["tome_index"]
        if self.inv.inventory[0] < self.learns[idx]["tome_index"]:
            return None  # Can't give tax
        other = self.__copy()
        new_spell = learn  
        new_spell["castable"] = True
        other.casts.append(new_spell)
        other.inv.inventory[0] += learn["tax_count"]
        return other

    def get_successors(self):
        """ Return a pair : (move, state) """
        res = []
        succ = self.do_rest()
        if succ is not None:
            res.append(("REST", succ))
        for i, cast in enumerate(self.casts):
            if cast["castable"]:
                try:
                    res.extend(self.do_cast(i))
                except InvalidMoveError:
                    pass
        if self.levelup:
            for i, learn in enumerate(self.learns):
                succ = self.do_learn(i)
                if succ is not None:
                    res.append(("LEARN " + learn["id"], succ))
        return res


class BreathWitch(Witch):
    def get_move(self, end):
        random_move = super().get_move()
        if self.can_brew():
            return "BREW " + self.can_brew()
        q = deque()
        q.append(([], self))
        num_explored = 0
        while q and time.process_time() < end:
            moves, state = q.popleft()
            num_explored += 1
            brew_id = state.can_brew()
            if brew_id:
                brew_id = [
                    idx for idx, brew in enumerate(self.brews) if brew["id"] == brew_id
                ][0]
                print(moves, file=sys.stderr)
                return moves[0] + " B" + str(brew_id) + "-" + str(len(moves))
            for move, succ in state.get_successors():
                if time.process_time() >= end:
                    break
                q.append((moves + [move], succ))
        if not q:
            return random_move + (" Q" + str(num_explored) if DEBUG else "")
        else:
            return random_move + (" N" + str(num_explored) if DEBUG else "")


##########################################  GAME LOOP  ######################################
while True:
    end = time.process_time() + 0.045
    state = BreathWitch()
    state.load()

    enemy_inventory = list(map(int, input().split()))[:-1]

    print(state.get_move(end=end)) 
