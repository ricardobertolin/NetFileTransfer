import time

try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ImportError:
    class _Noop:
        def __getattr__(self, _): return ''
    Fore = Style = _Noop()

# Column positions for the two protocol participants
_C = 8    # CLIENT pipe column
_S = 66   # SERVER pipe column
_W = _S - _C - 1  # inner arrow width = 57

# ──────────────────────────────────────────────────────────────
# Low-level line builders

def _pipe():
    return ' ' * _C + '|' + ' ' * _W + '|'

def _fmt(msg, width):
    """Truncate or left-pad msg to exactly width chars."""
    return msg[:width] if len(msg) > width else msg.ljust(width)

def _send_arrow(msg):
    """CLIENT ──────────────────────────────────────────> SERVER"""
    inner = _W - 6          # subtract '---' prefix and '-->' suffix
    return ' ' * _C + '|---' + _fmt(msg, inner) + '-->|'

def _recv_arrow(msg):
    """CLIENT <────────────────────────────────────────── SERVER"""
    inner = _W - 6
    return ' ' * _C + '|<--' + _fmt(msg, inner) + '---|'

def _tcp_connect_arrow(port):
    """Double-line arrow for TCP connection establishment."""
    msg = f'[ TCP CONNECT :{port} ]'
    inner = _W - 6
    pad = '=' * max(0, inner - len(msg))
    return ' ' * _C + '|===' + msg + pad + '==>|'

def _data_channel_arrow(port):
    """Double-line arrow for the reverse data channel."""
    msg = f'[ DATA CHANNEL :{port} ]'
    inner = _W - 6
    pad = '=' * max(0, inner - len(msg))
    return ' ' * _C + '|<==' + msg + pad + '===|'

# ──────────────────────────────────────────────────────────────
# Public header printer

def print_header(mode, local_ip, remote_host, remote_port):
    """Print the diagram banner and participant labels."""
    width = _S + 2
    client_lbl = f'CLIENT ({local_ip})'
    server_lbl = f'SERVER ({remote_host}:{remote_port})'
    gap = _S - _C - len(client_lbl) - len(server_lbl)
    labels = ' ' * (_C + 1) + client_lbl + ' ' * max(2, gap) + server_lbl

    print()
    print(Fore.CYAN + Style.BRIGHT + '=' * width)
    print(Fore.CYAN + Style.BRIGHT + f'NetFileTransfer  —  Protocol Visualizer  [{mode}]'.center(width))
    print(Fore.CYAN + Style.BRIGHT + '=' * width)
    print()
    print(Fore.WHITE + Style.BRIGHT + labels)
    print(Fore.WHITE + _pipe())


# ──────────────────────────────────────────────────────────────
# Protocol logger — wraps a control-channel socket

class ProtocolLogger:
    """
    Drop-in wrapper around a TCP socket.
    Every send/recv prints a sequence-diagram arrow to stdout.
    All other socket methods are transparently proxied.
    """

    def __init__(self, sock):
        self._sock = sock
        self._t0 = time.time()

    # ── helpers ──────────────────────────────────────────────

    def _ts(self):
        return f'+{time.time() - self._t0:.3f}s'

    # ── named events ─────────────────────────────────────────

    def event(self, msg, color=None):
        """Print a free-form phase annotation (no arrow)."""
        c = color or Fore.MAGENTA
        print(c + f'  [{self._ts()}]  *** {msg} ***')
        print(_pipe())

    def connect_event(self, host, port):
        """Print the control-channel TCP connect arrow."""
        print(Fore.CYAN + f'  [{self._ts()}]  Connecting to {host}:{port} ...')
        print(Fore.CYAN + Style.BRIGHT + _tcp_connect_arrow(port))
        print(_pipe())

    def data_channel_event(self, port):
        """Print the reverse data-channel accept arrow."""
        print(Fore.BLUE + Style.BRIGHT + f'  [{self._ts()}]  Server connected on data channel :{port}')
        print(Fore.BLUE + Style.BRIGHT + _data_channel_arrow(port))
        print(_pipe())

    # ── socket interface ─────────────────────────────────────

    def send(self, data):
        msg = data.decode('utf-8', errors='replace').strip()
        print(Fore.YELLOW + f'  [{self._ts()}]  SEND {len(data):>5}B  →  {msg!r}')
        print(Fore.YELLOW + _send_arrow(msg))
        print(_pipe())
        return self._sock.send(data)

    def recv(self, size):
        data = self._sock.recv(size)
        msg = data.decode('utf-8', errors='replace').strip()
        print(Fore.GREEN + f'  [{self._ts()}]  RECV {len(data):>5}B  ←  {msg!r}')
        print(Fore.GREEN + _recv_arrow(msg))
        print(_pipe())
        return data

    def close(self):
        self._sock.close()

    def __getattr__(self, name):
        """Proxy any other socket method (bind, listen, accept, …) transparently."""
        return getattr(self._sock, name)
