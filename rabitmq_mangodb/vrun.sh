#!/usr/bin/sh


/usr/bin/python /home/ec2-user/autoDiscovery/rabitmq_mangodb/action.py sendqueue & 


/usr/bin/python /home/ec2-user/autoDiscovery/rabitmq_mangodb/action.py progressqueue >> /dev/null 2>&1
