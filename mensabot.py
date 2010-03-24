#!/usr/bin/env python

#
#  mensabot
#
#  Copyright (c) 2010, Daniel Gasienica <daniel@gasienica.ch>
#  All rights reserved.
#

from google.appengine.ext import webapp

from waveapi import events
from waveapi import robot
from waveapi import appengine_robot_runner

import credentials
import feedparser
import logging
import feeds



class CronHandler(webapp.RequestHandler):
    robot = None


    # override the constructor
    def __init__(self, robot):
        self.robot = robot
        webapp.RequestHandler.__init__(self)

    def get(self):
        wave = self.robot.new_wave(domain="googlewave.com", participants=["mklausmann5@googlewave.com"])
        d = feedparser.parse(feeds.MENSAS['poly'])
        wave.title = d.channel.description
        
        for entry in d.entries:
            wave.reply(entry.title + "\n" + entry.description + "\n\n")
        
        self.robot.submit(wave)


def OnWaveletSelfAdded(event, wavelet):
  """Invoked when the robot has been added."""
  logging.info("OnWaveletSelfAdded called")
  wavelet.reply("\nHi I'm the mensa robot!")

def OnBlipSubmitted(event, wavelet):
  logging.info("OnBlipSubmitted called")
  command = str(event.blip.text).split(None, 2)

  if "mensa" == command[0]:
      
      d = getMensaFeedOf(command[1])
      if len(d) > 0:
          for entry in d.entries:
              if len(command) < 3 or command[2].isspace() or command[2] == entry.title: 
                  wavelet.reply(entry.title + "\n" + entry.description + "\n\n")
      else:
          wavelet.reply("ERROR NO FEED FOUND!")
      
  else:
      wavelet.reply("ERROR COMMAND NOT FOUND!")



def getMensaFeedOf(location):
    return feedparser.parse(feeds.MENSAS[location])
    
    

    

if __name__ == "__main__":
    mensabot = robot.Robot("ETH Mensa Bot",
                           image_url="http://www.seoish.com/wp-content/uploads/2009/04/wrench.png",
                           profile_url="")
    
    mensabot.register_handler(events.WaveletSelfAdded, OnWaveletSelfAdded)
    mensabot.register_handler(events.BlipSubmitted, OnBlipSubmitted)
    
    mensabot.set_verification_token_info(credentials.VERIFICATION_TOKEN, credentials.SECURITY_TOKEN)
    mensabot.setup_oauth(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET, server_rpc_base=credentials.RPC_BASE)
    appengine_robot_runner.run(mensabot, debug=True, extra_handlers=[("/web/cron",
                                                                     lambda: CronHandler(mensabot))])
