import copy
import posixpath
import argparse
import asyncio
from datetime import datetime
import logging

from asyncua import ua, uamethod, Server
from random import random


logger = logging.getLogger()


# method to be exposed through server
def is_even(parent, variant):
    ret = False
    if variant.Value % 2 == 0:
        ret = True
    return [ua.Variant(ret, ua.VariantType.Boolean)]


# method to be exposed through server
# uses a decorator to automatically convert to and from variants
@uamethod
def multiply(parent, x, y):
    return x * y


async def main(host="0.0.0.0", port="4840", path="freeopcua/server/"):
    server = Server()
    await server.init()

    server_endpoint = posixpath.join(f"opc.tcp://{host}:{port}", path)
    server.set_endpoint(server_endpoint)
    server.set_server_name("OpcUa Simulator Server")
    # set all possible endpoint policies for clients to connect through
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )

    uri = "http://opcua-splight.io"
    idx = await server.register_namespace(uri)

    # create a new node type we can instantiate in our address space
    dev = await server.nodes.base_object_type.add_object_type(idx, "MyDevice")
    await (await dev.add_variable(idx, "sensor1", 1.0)).set_modelling_rule(True)
    await (await dev.add_property(idx, "device_id", "0340")).set_modelling_rule(True)
    ctrl = await dev.add_object(idx, "controller")
    await ctrl.set_modelling_rule(True)
    await (await ctrl.add_property(idx, "state", "Idle")).set_modelling_rule(True)

    # populating our address space

    # First a folder to organise our nodes
    await server.nodes.objects.add_folder(idx, "NodeFolder")
    # instanciate one instance of our device
    mydevice = await server.nodes.objects.add_object(idx, "Device0001", dev)
    mydevice_var = await mydevice.get_child(
        [f"{idx}:controller", f"{idx}:state"]
    )  # get proxy to our device state variable
    # create directly some objects and variables
    myobj = await server.nodes.objects.add_object(idx, "MyObject")
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
    await myvar.set_writable()  # Set MyVariable to be writable by clients
    mystringvar = await myobj.add_variable(idx, "MyStringVariable", "Really nice string")
    await mystringvar.set_writable()  # Set MyVariable to be writable by clients
    mydtvar = await myobj.add_variable(idx, "MyDateTimeVar", datetime.utcnow())
    await mydtvar.set_writable()  # Set MyVariable to be writable by clients
    myarrayvar = await myobj.add_variable(idx, "myarrayvar", [6.7, 7.9])
    await myobj.add_variable(idx, "myuintvar", ua.UInt16(4))
    await myobj.add_variable(idx, "myStronglytTypedVariable", ua.Variant([], ua.VariantType.UInt32))
    await myarrayvar.set_writable(True)
    await myobj.add_method(
        idx, "is_even", is_even, [ua.VariantType.Int64], [ua.VariantType.Boolean]
    )
    await myobj.add_method(
        idx,
        "multiply",
        multiply,
        [ua.VariantType.Int64, ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )

    # creating a default event object
    # The event object automatically will have members for all events properties
    # you probably want to create a custom event type, see other examples
    myevgen = await server.get_event_generator()
    myevgen.event.Severity = 300

    async with server:
        var = await myarrayvar.read_value()  # return a ref to value in db server side! not a copy!
        var = copy.copy(
            var
        )  # WARNING: we need to copy before writting again otherwise no data change event will be generated
        var.append(9.3)
        await myarrayvar.write_value(var)
        await mydevice_var.write_value("Running")
        await myevgen.trigger(message="This is BaseEvent")
        # write_attribute_value is a server side method which is faster than using write_value
        # but than methods has less checks
        await server.write_attribute_value(myvar.nodeid, ua.DataValue(0.9))

        while True:
            await asyncio.sleep(0.1)
            await server.write_attribute_value(myvar.nodeid, ua.DataValue(random()))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a simulated server with OPCUA protocol.')
    parser.add_argument('--host', dest='host', type=str, default='0.0.0.0',
                        help='OPCUA host')
    parser.add_argument('--port', dest='port', type=int, default=4840,
                        help='OPCUA port')
    parser.add_argument('--path', dest='path', type=str, default="freeopcua/server/",
                        help='The server endpoint')

    args = parser.parse_args()
    asyncio.run(main(host=args.host, port=args.port, path=args.path))
