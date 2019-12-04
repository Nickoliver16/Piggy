from teacher import PiggyParent
import sys
import time
class Piggy(PiggyParent):

    '''
    *************
    SYSTEM SETUP
    *************
    '''

    def __init__(self, addr=8, detect=True):
        PiggyParent.__init__(self) # run the parent constructor

        ''' 
        MAGIC NUMBERS <-- where we hard-code our settings
        '''
        self.LEFT_DEFAULT = 80
        self.RIGHT_DEFAULT = 70
        self.exit_heading = 0
        self.SAFE_DISTANCE = 250
        self.MIDPOINT = 1225  # what servo command (1000-2000) is straight forward for your bot?
        self.load_defaults()
        

    def load_defaults(self):
        """Implements the magic numbers defined in constructor"""
        self.set_motor_limits(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_limits(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.set_servo(self.SERVO_1, self.MIDPOINT)
        

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values. Python is cool.
        # Please feel free to change the menu and add options.
        print("\n *** MENU ***") 
        menu = {"n": ("Navigate", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "h": ("Hold position", self.hold_position),
                "c": ("Calibrate", self.calibrate),
                "q": ("Quit", self.quit)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = str.lower(input("Your selection: "))
        # activate the item selected
        menu.get(ans, [None, self.quit])[1]()

    '''
    ****************
    STUDENT PROJECTS
    ****************
    '''

    def dance(self):
        #print("I don't know how to dance. \nPlease give my programmer a zero.")
        # check to see its safe to dance
        if not self.safe_to_dance():
            print ("Not safe to dance")
            return #return closes method
        else:
            print("It's safe to dance")

        for x in range(3):
            self.dab()
            self.move()
            self.move2()
            self.newmove()
            self.move3()
            self.circle()
        

    def safe_to_dance(self):
        #Does 360 distance check and returns true if safe
        for x in range(4):
            for ang in range(1000, 2001, 100):
                self.servo(ang)
                time.sleep(.1)
                if self.read_distance() < 250:
                    return False
            self.turn_by_deg(90)
        return True
            

    def scan(self):
        """Sweep the servo and populate the scan_data dictionary"""
        for angle in range(self.MIDPOINT-350, self.MIDPOINT+350, 100):
            self.servo(angle)
            self.scan_data[angle] = self.read_distance()

    
    def obstacle_count(self):
        """does a 360 scan and returns the number of obstacles that it sees"""
        found_something = False # Trigger
        trigger_distance = 250
        count = 0
        starting_position = self.get_heading() #Write down starting position
        self.right(primary=60, counter=-60)
        while self.get_heading() != starting_position:
            if self.read_distance() < trigger_distance and not found_something:
                found_something = True
                count += 1
                print("\n  Found Something!! \n")
            elif self.read_distance() > trigger_distance and found_something:
                found_something = False
                print("Seems I have a clear view. Resetting my counter")
        self.stop
        print("I found this many things: %d" % count)
        return count
    
    #Scan while moving
    def quick_check(self):
        # three quick checks
        for ang in range(self.MIDPOINT-150, self.MIDPOINT+151, 150):
            self.servo(ang)
            if self.read_distance() < self.SAFE_DISTANCE:
                return False
        #If I get to the end that means I didn't find anything
        return True
    
    # Robot saves where it is facing and if moved goes back to that degree
    def hold_position(self):
        start_angle = self.get_heading()
        while True:
            time.sleep(.1)
            current_angle = self.get_heading()
            if abs(current_angle - start_angle) > 12:
                self.turn_to_deg(start_angle)


    def nav(self):

        # Assuming facing exit at the start of the maze
        self.exit_heading = self.get_heading()
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
            
        


        while True:
            self.servo(self.MIDPOINT) 
            while self.quick_check():
                corner_count = 0
                self.fwd()
                time.sleep(0.01)
            self.stop()
            self.scan()
            # traversal
            # if the robot gets stuck in a corner for more than 5 checks it does a 180
            corner_count += 1
            if corner_count > 3:
                self.escape()
            if not self.path_exit():
                self.robot_turning()


    def path_exit(self):
        where_started = self.get_heading()
        self.turn_to_deg(self.exit_heading)
        if self.quick_check():
            return True
        else:
            self.turn_to_deg(where_started)
        return False


    def robot_turning(self):
        # Robot checks left and right and chooses the better way to turn
        left_total = 0
        left_count = 0
        right_total = 0
        right_count = 0            
        for ang, distance in self.scan_data.items():
            if ang < self.MIDPOINT:
                right_total += distance
                right_count += 1
            else:
                left_total += distance
                left_count += 1
        # Finds left and right average and turns to whichever is greater
        left_avg = left_total / left_count
        right_avg = right_total / right_count
        if left_avg > right_avg:
            self.turn_by_deg(-45)
        else:
            self.turn_by_deg(45)

    def escape(self):
        # Turns robot out of a corner and then faces the exit
        self.turn_by_deg(180)
        self.deg_fwd(720)
        self.turn_to_deg(self.exit_heading)
            

    def dab(self): 
        """ Turn right then quickly look left"""
        self.turn_by_deg(60)
        self.servo(2000)
        self.stop()


    def move(self):
        """ Look left got foward and turn left then look right and move right then go back. At the end turn left, right, left, and right"""
        self.servo(2000)
        self.fwd()
        time.sleep(0.2)
        self.turn_by_deg(-90)
        self.servo(1000)
        self.turn_by_deg(90)
        self.back()
        time.sleep(0.25)
        self.servo(1000)
        time.sleep(0.20)
        self.servo(2000)
        time.sleep(0.20)
        self.servo(1000)
        time.sleep(0.20)
        self.servo(2000)
        self.stop()

         

    def move2(self):
        """Turn right and look left then sleep. Turn left and then look right"""
        self.turn_by_deg(80)
        self.servo(1900)
        time.sleep(0.2)
        self.turn_by_deg(-80)
        self.servo(1100)
        self.stop()

    
    def newmove(self):
        """Turn right in a half circle and look left then sleep and turn right. Then go back and sleep and finally make a half circle left and go forward"""
        self.turn_by_deg(180)
        self.servo(1700)
        time.sleep(.1)
        self.servo(1100)
        self.back
        time.sleep(0.20)
        self.turn_by_deg(-180)
        self.fwd
        self.stop()


    def move3(self):
        """Move foward and turn left then look left then right. Finally go back and sleep then turn right"""
        self.fwd()
        self.turn_by_deg(-90)
        self.servo(1900)
        self.servo(1100)
        self.back()
        time.sleep(.25)
        self.turn_by_deg(90)
        self.stop()



    def circle(self):
        """Turn in a circle right and then turn in a circle left. End with lookin left then right"""
        for x in range(4):
            self.turn_by_deg(90)
        for x in range(4):
            self.turn_by_deg(-90)
        self.servo(2000)
        self.servo(1500)
        self.stop()
        



###########
## MAIN APP
if __name__ == "__main__":  # only run this loop if this is the main file

    p = Piggy()

    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x\n")
        p.quit()

    try:
        while True:  # app loop
            p.menu()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        p.quit()  
