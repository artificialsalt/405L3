"""!
@file main.py
    This file contains a task scheduling program that performs two step response tests on two different motors simultaneously.

@author Richard Kwan, Chayton Ritter, Jackie Chen, JR Ridgely
@date   2023-Feb-7 Created by modifying existing task sharing example by JR Ridgely
"""

import gc
import pyb
import utime
import cotask
import motor_driver
import encoder_reader
import closedloopcontrol

def task_mc(motor, encoder, controller):
    '''!
    Task which proportionally controls a motor.
    @param motor A motor object
    @param encoder An encoder object
    @param controller A controller object
    '''
    # Adjust motor power
    while True:
        a = controller.run(encoder.read())
        yield
        motor.set_duty_cycle(a)
        yield


if __name__ == "__main__":
    
    # Initialize UART
    u2 = pyb.UART(2, baudrate=115200)
    
    # Initialize motor/encoder/controller 1
    M1 = motor_driver.MotorDriver('A10', 'B4', 'B5', 3, 1, 2)
    E1 = encoder_reader.EncoderReader('C6', 'C7', 8, 1, 2)
    C1 = closedloopcontrol.cl_loop(0.015, 5000)
    M1.enable_motor()
    
    # Initialize motor/encoder/controller 2
    M2 = motor_driver.MotorDriver('C1', 'A0', 'A1', 5, 1, 2)
    E2 = encoder_reader.EncoderReader('B6', 'B7', 4, 1, 2)
    C2 = closedloopcontrol.cl_loop(0.015, 10000)
    M2.enable_motor()
    
    # Create tasks
    task1 = cotask.Task(task_mc, name='Motor_1', priority=1, period=10,
                        profile=True, trace=False, mec=(M1, E1, C1))
    task2 = cotask.Task(task_mc, name='Motor_2', priority=2, period=10,
                        profile=True, trace=False, mec=(M2, E2, C2))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Start timer
    start_time = utime.ticks_ms()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
            
            time_diff = utime.ticks_diff(utime.ticks_ms(), start_time)
            if time_diff > 3000:
                break
        except KeyboardInterrupt:
            break

    # Turn off motors
    M1.set_duty_cycle(0)
    M2.set_duty_cycle(0)
    M1.disable_motor()
    M2.disable_motor()
    
    # Transmit data back
    pos_1 = C1.get_pos_data()
    pos_1str = [str(i) for i in pos_1]
    pos_2 = C2.get_pos_data()
    pos_2str = [str(i) for i in pos_2]
    tx1 = ','.join(pos_1str)
    tx2 = ','.join(pos_2str)
    u2.write(tx1+'\n')
    utime.sleep_ms(1000)
    u2.write(tx2+'\n')
