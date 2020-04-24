import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
counter_boost = 1
counter_checkpoint = 0

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]
    
    # Distance between opposing pod and mine
    dx_shield = (x - opponent_x)
    dy_shield = (y - opponent_y)
    d_shield = math.sqrt((dx_shield * dx_shield)+(dy_shield * dy_shield))
    
    # For the boost counter
    #upper_radius_x = (x > next_checkpoint_x - 600)
    #lower_radius_x = (x < next_checkpoint_x + 600)
    #upper_radius_y = (y > next_checkpoint_y - 600)
    #lower_radius_y = (y < next_checkpoint_y + 600)
    
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    
    if (upper_radius_x or lower_radius_x) and (upper_radius_y or lower_radius_y):
        counter_checkpoint += 1
        
    if next_checkpoint_angle == 0 and counter_checkpoint == 5 and counter_boost == 1:
        thrust = "BOOST"
        counter_boost = 0
    elif d_shield < 1100:
        thrust = "SHIELD"
    elif next_checkpoint_angle > 90 or next_checkpoint_angle < -90 or next_checkpoint_dist < 1200:
        thrust = 30
    else:
        thrust = 100
        
    # You have to output the target position
    # followed by the power (0 <= thrust <= 100) or "BOOST"
    # i.e.: "x y thrust"
    print(str(next_checkpoint_x) + " " + str(next_checkpoint_y) + " " + str(thrust))