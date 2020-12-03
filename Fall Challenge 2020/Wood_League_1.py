import sys
import random
from pprint import pprint

# I replaced "action_?" with "a?" for readability issues
#            "delta_?" with "d?"
#            "inv_?" with "i?"


# game loop
while True:
    acount = int(input())  # the number of spells and recipes in play
    brews = []
    casts = []
    other = []
    for i in range(acount):
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
        aid, atype, d0, d1, d2, d3, price, tome_index, tax_count, castable, repeatable = input().split()
        d0 = int(d0)
        d1 = int(d1)
        d2 = int(d2)
        d3 = int(d3)
        price = int(price)
        tome_index = int(tome_index)
        tax_count = int(tax_count)
        castable = castable != "0"
        repeatable = repeatable != "0"

        if atype == "BREW":
            event = brews
        elif atype == "CAST":
            event = casts
        else:
            event = other

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

    inventory = []
    for i in range(2):
        # i0: tier-0 ingredients in inventory
        # score: amount of rupees
        # i0, i1, i2, i3, score = [int(j) for j in input().split()]
        inventory.append(list(map(int, input().split())))

    # Write an at using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    for brew in brews:
        give = True
        for i in range(4):
            if -brew['delta'][i] > inventory[0][i]:
                give = False
        brew['give'] = give


    for cast in casts:
        give = True
        for i in range(4):
            if cast['delta'][i] < 0 and -cast['delta'][i] > inventory[0][i]:
                give = False
            if inventory[0][i] + cast['delta'][i] > 4:
                give = False
        if sum(cast['delta']) + sum(inventory[0]) > 10:
            print("Full up with", sum(inventory[0]), file=sys.stderr)
            give = False
        cast['give'] = give
        cast['sum_delta'] = sum(cast['delta'])


    brews.sort(key=lambda x:(x['give'], x['price']), reverse=True)
    casts.sort(key=lambda x:(x['give'], x['castable'], -x['sum_delta']), reverse=True)

    pprint(brews, stream=sys.stderr)
    pprint(casts, stream=sys.stderr)
    pprint(inventory, stream=sys.stderr)

    try:
        print("BREW " + random.choice([brew['id'] for brew in brews if brew['give']]))
    except IndexError:
        try:
            print("CAST  " + random.choice([cast['id'] for cast in casts if cast['give'] and cast['castable']]))
        except IndexError:
            print("REST") 
