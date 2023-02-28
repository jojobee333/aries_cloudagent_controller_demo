import secrets
import socket

class Utilities:
    def flatten(self, args):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                yield from self.flatten(arg)
            else:
                yield arg

    def generate_seed(self, label: str, bytestring: bool, length=32):
        if bytestring is True:
            result = secrets.token_bytes()
        else:
            result = (label + ("".join(["0" for i in range(0, length)])))[:length]
        return result

    def is_port_in_use(self, host, port):
        """# set a timeout to avoid blocking indefinitely
              # try to connect to the specified port
               # if the connection was successful, the port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            if result == 0:
                # port is in use
                return True
            else:
                # port is not in use
                return False

    def print_args(self, args):
        print(" ".join(args))
