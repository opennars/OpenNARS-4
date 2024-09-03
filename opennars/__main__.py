from opennars.NARS.Control.Reasoner import Reasoner
from opennars.NARS.Channels.UserChannel import UserChannel

nars = Reasoner(100, 100)
user_channel1 = UserChannel(nars, 1000)
user_channel2 = UserChannel(nars, 1000)
nars.add_channel(user_channel1)
nars.add_channel(user_channel2)
nars.run(True)