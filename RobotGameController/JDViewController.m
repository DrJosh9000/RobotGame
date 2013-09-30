//
//  JDViewController.m
//  RobotGameController
//
//  Created by Josh Deprez on 21/09/13.
//
//  RobotGameController is licensed under the MIT license.
//
//  Copyright (c) 2013 Josh Deprez.
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is furnished
//  to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
//  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
//  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
//  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
//  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

#import "JDViewController.h"

#import <CoreMotion/CoreMotion.h>

#import <sys/types.h>
#import <sys/socket.h>
#import <netinet/in.h>
#import <arpa/inet.h>
#import <string.h>
#import <netdb.h>

struct sockaddr_in svr_addr;
int sock;

@interface JDViewController ()
@property (strong, nonatomic) CMMotionManager *motionManager;
@property (assign, nonatomic) uint counter;
@end

@implementation JDViewController

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.counter = 0;
    
    // DNS, yay
    const char* name = "seikaku.local";
    const struct hostent* hostinfo = gethostbyname2(name,AF_INET);
    const char* addr = NULL;
    if (hostinfo == NULL)
    {
        herror("could not get host info");
        return;
    }
    else
    {
        addr = inet_ntoa(*((struct in_addr *)hostinfo->h_addr));
        NSLog(@"%s = %s", hostinfo->h_name, addr);
    }
    
    // Sockets, yay
    struct sockaddr_in my_addr;
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;
    my_addr.sin_port = 0;
    bind(sock, (struct sockaddr*)&my_addr, sizeof(my_addr));
    
    svr_addr.sin_family = AF_INET;
    inet_aton(addr, &svr_addr.sin_addr);
    svr_addr.sin_port = htons(9991);

    self.motionManager = [CMMotionManager new];
    [self.motionManager startDeviceMotionUpdatesToQueue:[NSOperationQueue mainQueue]
        withHandler:^(CMDeviceMotion *motion, NSError *error) {
            // Acceleration due to user
            //NSLog(@"userAcceleration %f, %f, %f", motion.userAcceleration.x, motion.userAcceleration.y, motion.userAcceleration.z);
            
            // Acceleration due to gravity
            //NSLog(@"gravity %f, %f, %f", motion.gravity.x, motion.gravity.y, motion.gravity.z);
            
            // Attitude
            //NSLog(@"attitude %f, %f, %f", motion.attitude.roll, motion.attitude.pitch, motion.attitude.yaw);
            
            // Compass
            //NSLog(@"magneticField %f, %f, %f", motion.magneticField.field.x, motion.magneticField.field.y, motion.magneticField.field.z);
            
            /*
            // Create datagram
            NSString *datagram = [NSString stringWithFormat:@"%d,%f,%f,%f",
                                  self.counter,
                                  motion.userAcceleration.x,
                                  motion.userAcceleration.y,
                                  motion.userAcceleration.z];
            */
             
            /*
            // Create datagram
            NSString *datagram = [NSString stringWithFormat:@"%d,%f,%f,%f",
                                  self.counter,
                                  motion.gravity.x,
                                  motion.gravity.y,
                                  motion.gravity.z];
            */
            
            /*
            // Create datagram
            NSString *datagram = [NSString stringWithFormat:@"%d,%f,%f,%f",
                                  self.counter,
                                  motion.attitude.roll,
                                  motion.attitude.pitch,
                                  motion.attitude.yaw];
            */

            
            
            // Using attitude for robot control
            double x = -motion.attitude.pitch;
            double y = -motion.attitude.roll;
            
            // Rotate the pointer view on the device
            self.pointerImageView.layer.transform = CATransform3DMakeRotation(atan2(y, x) - M_PI_2, 0.0, 0.0, -1.0);
            NSString *datagram = [NSString stringWithFormat:@"%d,%f,%f",self.counter, x, y];
            
        
            const char* cdatagram = [datagram cStringUsingEncoding:NSUTF8StringEncoding];
            // send udp datagram
            sendto(sock, cdatagram, strlen(cdatagram)+1, 0, (struct sockaddr*)&svr_addr, sizeof(svr_addr));
            
            self.counter++;
    }];
}

- (void) dealloc {
    [self.motionManager stopDeviceMotionUpdates];
    self.motionManager = nil;
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)leftFireButtonTouched:(id)sender {
    //NSLog(@"leftFireButtonTouch");
    // send udp datagram
    NSString *datagram = [NSString stringWithFormat:@"%d,left", self.counter];
    const char* cdatagram = [datagram cStringUsingEncoding:NSUTF8StringEncoding];
    sendto(sock, cdatagram, strlen(cdatagram)+1, 0, (struct sockaddr*)&svr_addr, sizeof(svr_addr));
    self.counter++;
}

- (IBAction)rightFireButtonTouched:(id)sender {
    //NSLog(@"rightFireButtonTouch");
    // send udp datagram
    NSString *datagram = [NSString stringWithFormat:@"%d,right", self.counter];
    const char* cdatagram = [datagram cStringUsingEncoding:NSUTF8StringEncoding];
    sendto(sock, cdatagram, strlen(cdatagram)+1, 0, (struct sockaddr*)&svr_addr, sizeof(svr_addr));
    self.counter++;
}
@end
