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
        set_pins.setup_servo(servo1_pin)
        set_pins.setup_servo(servo2_pin)
        set_pins.setup_motion_detector(movdetect_pin)

    def setup_servo(servo_pin):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(servo_pin,GPIO.OUT)
        #Setting to 50 Hz PWM 20ms

    def setup_motion_detector(movdetect_pin):
        #Motion sensor input:
        GPIO.setmode(GPIO.BOARD)
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
                movements[i][j] = (random.randint(70,110),random.randint(0,45),(random.randint(1,4))/2)
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
            movement[j] = (random.randint(70,110),random.randint(0,45),(random.randint(1,4))/2)
        return movement

    #Function for one of the angles setting

    def setAngle(angle1,pin1,angle2, pin2, sec):
        pwm1 = GPIO.PWM(pin1,50)
        pwm1.start(0)
        pwm2 = GPIO.PWM(pin2, 50)
        pwm2.start(0)
        duty1 = angle1 / 18 + 3
        GPIO.output(pin1, True)
        pwm1.ChangeDutyCycle(duty1)
        duty2 = angle2 / 18 + 3
        GPIO.output(pin2, True)
        pwm2.ChangeDutyCycle(duty2)
        time.sleep(.1)
        pwm1.stop()
        pwm2.stop()
        #run move detection here until sec is reached
        mov = movement_gen.check_mov(7, sec)
        time.sleep(sec)
        GPIO.output(pin1, False)
        pwm1.ChangeDutyCycle(duty1)
        GPIO.output(pin2, False)
        pwm2.ChangeDutyCycle(duty2)
        print(f'move detected {mov}')
        return mov

    def check_mov(pin,sec):
        t = 0
        thisposition = GPIO.input(pin)
        while thisposition == True:
            if t < sec:
                time.sleep(0.01)
                thisposition = GPIO.input(pin)
                t = t + 0.01
            else:
                mov = 0
                return mov
        mov = 1
        return mov


    #Runs all the movements with the time tuple
    def run_move(movements):
        mov = 0
        for i in range(len(movements)):
            angle1 = movements[i][0]
            angle2 = movements[i][1]
            seconds = movements[i][2]
            print(f'x: {movements[i][0]} deg, y: {movements[i][1]} deg, time: {movements[i][2]} seconds')
            time.sleep(movements[i][2])
            mov_of_act = movement_gen.setAngle(movements[i][0],11,movements[i][1],13,movements[i][2])
            mov = mov + mov_of_act
        print(mov)
        return mov
    def clock():
        counter = 1
        while counter >= 10:
            time.sleep(1)
            counter = counter +1



    def watchopen(thiscontact):
        thisposition = GPIO.input(thiscontact)
        t = 0
        if t <=20:
    #    if thisposition == True:
            while thisposition == True:
                time.sleep(0.1)
                thisposition = GPIO.input(thiscontact)
                t = t + 0.1
                if t>=20:
                    print("No Movement Detected in Last 20 second")
                    t = 0
                    movement_gen.watchopen(thiscontact)
                else:
                    pass
            print(f'Move Detected. Last move {t} seconds')
            time.sleep(0.1)
            t = 0
            movement_gen.watchopen(thiscontact)
        else:
            print("No move detected")

#           watchclose(thiscontact)
#        watchclose(thiscontact)

    def watchclose(thiscontact):
        thisposition = GPIO.input(thiscontact)
        if thisposition == False:
            counter = 1
            while thisposition == False:
                time.sleep(0.1)
                thisposition = GPIO.input(thiscontact)
            watchopen(thiscontact)
        watchopen(thiscontact)

    def motion_detect(counter, move_choice, move_prob_list, move_movements, setup_movdetect_pin, mov1):
        #Next bit to detect movements, change probabilities, and actions, and then run movements in loop
        mov = GPIO.input(setup_movdetect_pin)
        if mov1 == 0:
            print("No motion detected")
            counter = counter + 1
            trial_success = [move_choice,0]
            move_prob_list = movement_gen.prob_list_recal(move_prob_list,trial_success)
            move_movements[move_choice] = movement_gen.gen_new_actions(move_movements[move_choice])
            print("weigted probabilities")
            print(move_prob_list)
            move_choice = movement_gen.action_choice(move_prob_list)
            mov = movement_gen.run_move(move_movements[move_choice])
            print(f'mov{mov}')
            print("To exit program press ctrl + C")
            mov1 = 0
            mov2 = movement_gen.check_mov(setup_movdetect_pin, 5)
            mov1 = mov + mov2
            movement_gen.motion_detect(counter, move_choice, move_prob_list, move_movements, setup_movdetect_pin, mov1)

        else:
            print("Motion_detected")
            print(GPIO.input(setup_movdetect_pin))
            counter = counter + 1
            trial_success = [move_choice, 1]
            move_prob_list = movement_gen.prob_list_recal(move_prob_list,trial_success)
            print(move_prob_list)
            move_choice = movement_gen.action_choice(move_prob_list)
            movement_gen.run_move(move_movements[move_choice])
            print(f'mov amount {mov}')
            print("To exit program press ctrl + C")
            mov1 = 0
            mov2 = movement_gen.check_mov(setup_movdetect_pin, 5)
            mov1 = mov + mov2
            movement_gen.motion_detect(counter, move_choice, move_prob_list, move_movements, setup_movdetect_pin, mov1)


    #choose which set of 5 movements (action) to take
    def action_choice(prob_list):
        a = random.choices(range(0, 5, 1), weights=prob_list, k =1)
        return a[0]



def run_laser():
    setup = set_pins(11,13,7)
    move = movement_gen()
    try:
        while True:
            move_choice = movement_gen.action_choice(move.prob_list)
            print(f'a:{move.prob_list[0]},b:{move.prob_list[1]},c:{move.prob_list[2]},d:{move.prob_list[3]},e:{move.prob_list[4]}')
            print(f'move_choice: {move_choice}')
#            movement_gen.watchopen(setup.movdetect_pin)
#            movement_gen.run_move(move.movements[move_choice])
#            time.sleep(16)
            movement_gen.motion_detect(0,move_choice, move.prob_list, move.movements,setup.movdetect_pin,0)
    except KeyboardInterrupt:
        print("interupt")
        GPIO.cleanup()

run_laser()