import RPi.GPIO as GPIO
import time 
import random

#Setting board to BOARD mode for the pin out rather than BCM
#With servo connected to pin 11 on the board and on a raspberry pi 4B modual BCM pin GPIO 17
#The sg90 micro servo oscilates with a duty cycle ia 1-2ms out of a 20ms cycle rotating 180 deg..
#That means 1ms is 1/20 or 5% PWM for -90 deg, and 2ms is 2/20 or 10% PWM for 90 deg.

class set_pins:

    def __init__(self,servo1_pin, servo2_pin, movdetect_pin):
        self.servo1_pin = servo1_pin
        self.servo2_pin = servo2_pin
        self.movdetect_pin = movdetect_pin
        setup_servo(servo1_pin)
        setup_servo(servo2_pin)
        setup_motion_detector(movdetect_pin)

    def setup_servo(servo_pin):
        GPIO.setmode (GPIO.BOARD)
        GPIO.setup (servo1_pin,GPIO.OUT)
        #Setting to 50 Hz PWM 20ms
        pwm1=GPIO.PWM(servo1_pin, 50)
        pwm1.start(0)

    def setup_motion_detector(movdetect_pin):        
        #Motion sensor input:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(movdetect_pin, GPIO.IN)

class movement_gen:

    def __init__(self):
        self.prob_list = [1,1,1,1,1]
        self.movements = movement_gen.generate_movements(5)

    #Function to generate 5 random movements to start
    def generate_movements(numb_of_movements):
        movements = list(range(numb_of_movements))
        for i in range(len(movements)):
            movements[i] = list(range(numb_of_movements))
            for j in range(len(movements[i])):
                movements[i][j] = (random.randint(-90,90),random.randint(-90,90),random.randint(1,4))  
        return movements


    #Recalculates the weighted list for probabilities of movement selction
    def prob_list_recal(prob_list,trial_success):
        for i in range(len(prob_list)):
            if trial_success[1] == 1:
                if i != trial_success[0]:
                    prob_list[i] = prob_list[i]+1
                else:
                    pass
            else:
                prob_list[i] = prob_list[i] +1
        return prob_list


    def gen_new_actions(movement):
        a = random.choices(range(1, 5, 1), weights = [4,3,2,1])[0]
        b = random.sample(range(0, 5, 1), k =a)
        print(b)
        for j in b:
            movement[j] = (random.randint(-90,90),random.randint(-90,90),random.randint(1,4))  
        return movement

    #Function for one of the angles setting
    def setAngle(angle1,pin1,angle2, pin2, time):
        duty1 = angle1 / 18 + 3
        GPIO.output(pin1, True)
        pwm.ChangeDutyCycle(duty1)
        duty2 = angle2 / 18 + 3
        GPIO.output(pin2, True)
        pwm.ChangeDutyCycle(duty2)
        time.sleep(time)
        GPIO.output(pin1, False)
        pwm.ChangeDutyCycle(duty1)
        GPIO.output(pin2, False)
        pwm.ChangeDutyCycle(duty2)



    #Runs all the movements with the time tuple
    def run_move(movements):
        for i in range(len(movements)):
            angle1 = movements[i][0]
            angle2 = movements[i][1]
            time = movements[i][2]
            print(f'x: {movements[i][0]} deg, y: {movements[i][1]} deg, time: {movements[i][2]} seconds')
            time.sleep(movements[i][2])
            setAngle(angle1,pin1,angle2,pin2,time)


    def motion_detect(counter, move_choice, move_prob_list, move_movements, setup_movdetect_pin):
        #Next bit to detect movements, change probabilities, and actions, and then run movements in loop

        if (GPIO.input(setup_movdetect_pin) == 0):
            print("No motion detected")
            counter = counter + 1
            trial_success = [move_choice,0]
            move_prob_list = movement_gen.prob_list_recal(move_prob_list,trial_success)
            move_movements[move_choice] = movement_gen.gen_new_actions(move_movements[move_choice])
            print("weigted probabilities")
            print(move_prob_list)
            move_choice = movement_gen.action_choice(move_prob_list)
            movement_gen.run_move(move_movements[move_choice])
            print("To exit program press ctrl + C")
            time.sleep(16)
            movement_gen.motion_detect(counter, move_choice, move_prob_list, move_movements)

        else (GPIO.input(setup_movdetect_pin) == 1):
            print("Motion_detected")
            counter = counter + 1
            trial_success = [move_choice, 1]
            move_prob_list = movement_gen.prob_list_recal(move_prob_list,trial_success)
            print(move_prob_list)
            move_choice = movement_gen.action_choice(move_prob_list)
            movement_gen.run_move(move_movements[move_choice])
            time.sleep(16)
            movement_gen.motion_detect(counter, move_choice, move_prob_list, move_movements)


    #choose which set of 5 movements (action) to take
    def action_choice(prob_list):   
        a = random.choices(range(0, 5, 1), weights=prob_list, k =1)
        return a[0]



def run_laser():
    setup = set_pins(11,12,17) 
    move = movement_gen()
    try:
        while True:
            move_choice = movement_gen.action_choice(move.prob_list)
            print(f'a:{move.prob_list[0]},b:{move.prob_list[1]},c:{move.prob_list[2]},d:{move.prob_list[3]},e:{move.prob_list[4]}')
            print(f'move_choice: {move_choice}')
            movement_gen.run_move(move.movements[move_choice])
            time.sleep(16)
            movement_gen.motion_detect(counter, move_choice, move.prob_list, move.movements,setup.movdetect_pin)
    except KeyboardInterrupt:
        print("interupt")
        GPIO.cleanup()

run_laser()
