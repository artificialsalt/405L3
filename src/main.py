"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import utime
import cotask
import task_share
import motor_driver
import encoder_reader
import closedloopcontrol


def task1_fun(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share, my_queue = shares

    counter = 0
    while True:
        my_share.put(counter)
        my_queue.put(counter)
        counter += 1

        yield 0


def task2_fun(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    the_share, the_queue = shares

    while True:
        # Show everything currently in the queue and the value in the share
        print(f"Share: {the_share.get ()}, Queue: ", end='')
        while q0.any():
            print(f"{the_queue.get ()} ", end='')
        print('')

        yield 0

def task_mc1(motor, encoder, controller):
    # Adjust motor power
    while True:
        a = controller.run(encoder.read())
        yield
        motor.set_duty_cycle(a)
        yield
    #time_diff = utime.ticks_diff(utime.ticks_ms(), start_time)

def task_mc2(motor, encoder, controller):
    # Adjust motor power
    while True:
        a = controller.run(encoder.read())
        yield
        motor.set_duty_cycle(a)
        yield
    #time_diff = utime.ticks_diff(utime.ticks_ms(), start_time)

# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    #share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    #q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          #name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    #task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=400,
                        #profile=True, trace=False, shares=(share0, q0))
    #task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=1500,
                        #profile=True, trace=False, shares=(share0, q0))
    
    u2 = pyb.UART(2, baudrate=115200)
    
    M1 = motor_driver.MotorDriver('A10', 'B4', 'B5', 3, 1, 2)
    E1 = encoder_reader.EncoderReader('C6', 'C7', 8, 1, 2)
    C1 = closedloopcontrol.cl_loop(0.015, 5000)
    M1.enable_motor()
    
    
    M2 = motor_driver.MotorDriver('C1', 'A0', 'A1', 5, 1, 2)
    E2 = encoder_reader.EncoderReader('B6', 'B7', 4, 1, 2)
    C2 = closedloopcontrol.cl_loop(0.05, 10000)
    #M2.enable_motor()
    
    task1 = cotask.Task(task_mc1, name='Motor_1', priority=1, period=50,
                        profile=True, trace=False, mec=(M1, E1, C1))
    task2 = cotask.Task(task_mc2, name='Motor_2', priority=2, period=50,
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
    
    pos_1 = C1.get_pos_data()
    pos_1str = [str(i) for i in pos_1]
    pos_2 = C2.get_pos_data()
    pos_2str = [str(i) for i in pos_2]
    tx1 = ','.join(pos_1str)
    tx2 = ','.join(pos_2str)
    u2.write(tx1+'\n')
    utime.sleep_ms(1000)
    u2.write(tx2+'\n')
