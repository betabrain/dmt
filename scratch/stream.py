import window


class DMT:
    def __init__(self):
        self._receive_window = window.Window()
        self._send_pos = 0
        self._sent = {}

    def send(self, item: object):
        self._send_pos += 1
        self._sent[self._send_pos] = item
        return [
            self._send_pos,
            self._receive_window.min,
            self._receive_window.max,
            self._receive_window.window,
            item,
        ]

    def receive(self, packet):
        pos, w_min, w_max, w_flags = packet


if __name__ == "__main__":
    d = DMT()
    print(d.send("Hello"))
    print(d.send(", "))
    print(d.send("World"))
    print(d.send("!"))
