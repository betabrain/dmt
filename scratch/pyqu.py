import apsw
import nacl
import nnpy
import persisitqueue

# <resources> i.e. message receiver, i.e. kjcs8au4ijrucs9uijch8ijnsswi48sjic
#  - specified signature
#  - has description
#  - cryptographically secured
#  - send message to <resource>
#  - sending a callable creates a <resource> and sends it instead
#  - aka. capability
#  - building block used to implement promises
#  - distributed blocks, aka. preserve and replicate callable before reply
#  - ACID state of callable

# publish / subscribe system
#  - announce publicly accessible <resources>, i.e. publish('name', 'sjkca8dsf...')
#  - private, capability channels "web of trust", i.e. publish('sds9csle...', 'data')
#  - capability to publish
#  - capability to receive
#  - capabilities may be restricted
#  - built using <resources> as building blocks?

# queuing and persistency
#  - rollback on error
#  - including code installation / callable instatiation
