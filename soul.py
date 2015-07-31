#######################################################################
# The Chroma Automation Suite was originally created back in late October
# - early November of 2014. I decided to put this comment here as a sort
# of nostalgic plaque to remember the history of this mess of code. It
# was originally a totally not-automatic deal, just a really rough python
# script integrated a bit with PRAW to literally just look through some
# comments to form a list of users, then send out a PM message. It's
# had a rocky history, but hopefully this will solidify it.
#
# Created: 11/03/2014 (first commit)
#
# Copyright: Beer License. Yall can use this how/where/when ever, but
#               you owe me a beer!
#
# Author: Eliminioa <eliminioa@gmail.com>
#
# Thanks for reading!
#######################################################################
import sqlite3
from multiprocessing import Pipe

from Body.body import Body
from Mind.mind import Mind
from Utilities import connector, configReader

CONFIG = configReader.read()
MIND_ANTENNA = connector.Connector(CONFIG)
BODY_ANTENNA = connector.Connector(CONFIG)

SENSORY_NEURON, MOTOR_NEURON = Pipe()

MIND = Mind('MIND', CONFIG, MIND_ANTENNA, SENSORY_NEURON)
BODY = Body('BODY', CONFIG, BODY_ANTENNA, MOTOR_NEURON)

def init_db():
    """Initializes the database."""
    db = sqlite3.connect(CONFIG['DATABASE'])
    with open('Mind/subconscious.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

if __name__ == "__main__":
    MIND.start()
    BODY.start()