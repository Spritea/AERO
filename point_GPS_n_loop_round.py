#!/usr/bin/env python

from __future__ import print_function
import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative

def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5
                                                                    
# Connect to the Vehicle                                                        

vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

energy=1

def arm_and_takeoff(aTargetAltitude):                                           

    """                                                        
    Arms vehicle and fly to aTargetAltitude.                                                          
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready                                                                     
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode                                                                              
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off                                                           
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto     
    #  (otherwise the command after Vehicle.simple_takeoff will execute         
    #   immediately).                                                           
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.              
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

lat=vehicle.location.global_relative_frame.lat
lon=vehicle.location.global_relative_frame.lon
alt=5
start_point=LocationGlobalRelative(lat,lon,alt)

arm_and_takeoff(5)

T1=time.time()


def fly_to_GPS(aLocation,groundspeed):
    """
    Fly to a specific GPS point
    """
    currentLocation = vehicle.location.global_relative_frame
    #targetLocation = LocationGlobalRelative(34.25654,146.549946,3)
    targetDistance = get_distance_metres(currentLocation, aLocation)
    vehicle.simple_goto(aLocation,groundspeed)
    
    #print "DEBUG: targetLocation: %s" % targetLocation
    #print "DEBUG: targetLocation: %s" % targetDistance

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, aLocation)
        print ("Distance to target: ", remainingDistance)
        print("hight: ",vehicle.location.global_relative_frame.alt)
        print("voltage: ",vehicle.battery.voltage)

        if remainingDistance<=1: #Just below target, in case of undershoot.
                print ("Reached target")
                break
        time.sleep(2)


print("Set default/target airspeed to 3")
vehicle.airspeed = 1

point1 = LocationGlobalRelative(30.5369655587, 114.355667303,3)
point2 = LocationGlobalRelative(30.5367841753, 114.355639243,3)
point3 = LocationGlobalRelative(30.5368700787, 114.355510008,3)
point4 = LocationGlobalRelative(30.5369672367, 114.355540424,3)

i=0
N=1

while i<N:

    print("Going towards P1")
    fly_to_GPS(point1,2)
    time.sleep(2)
    print("Going towards P2")
    fly_to_GPS(point2,3)
    time.sleep(3)
    print("Going towards P3")
    fly_to_GPS(point3,3)
    time.sleep(2)
    print("Going towards P4")
    fly_to_GPS(point4,2)
    time.sleep(2)
    i=i+1
    
print("fly to start point !!")
fly_to_GPS(start_point,2)    
vehicle.mode = VehicleMode("LAND")

time.sleep(25)
arm_and_takeoff(6)
time.sleep(2)
vehicle.mode = VehicleMode("LAND")

# Close vehicle object before exiting script                                      
print("Close vehicle object")
vehicle.close()



