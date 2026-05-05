import math
import array
import pygame


def _make_tone(freq, duration_ms, volume=0.3, sample_rate=22050,
               decay=True, waveform='sine'):
    n = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    amp = int(32767 * volume)
    for i in range(n):
        t = i / sample_rate
        env = math.exp(-3 * i / n) if decay else 1.0
        if waveform == 'square':
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        s = int(amp * env * v)
        samples.append(s)
        samples.append(s)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _make_chord(freqs, duration_ms, volume=0.3, sample_rate=22050):
    n = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    amp = int(32767 * volume / len(freqs))
    for i in range(n):
        t = i / sample_rate
        env = math.exp(-2.5 * i / n)
        v = sum(math.sin(2 * math.pi * f * t) for f in freqs)
        s = int(amp * env * v)
        s = max(-32767, min(32767, s))
        samples.append(s)
        samples.append(s)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _make_sweep(f_start, f_end, duration_ms, volume=0.2, sample_rate=22050):
    n = int(sample_rate * duration_ms / 1000)
    samples = array.array('h')
    amp = int(32767 * volume)
    phase = 0.0
    for i in range(n):
        t = i / sample_rate
        f = f_start + (f_end - f_start) * (i / n)
        phase += 2 * math.pi * f / sample_rate
        env = math.sin(math.pi * i / n)
        s = int(amp * env * math.sin(phase))
        samples.append(s)
        samples.append(s)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class Audio:
    def __init__(self):
        self.enabled = False
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(22050, -16, 2, 512)
            self.slide_snd = _make_sweep(700, 400, 140, 0.18)
            self.thunk_snd = _make_tone(110, 110, 0.28, decay=True, waveform='square')
            self.win_snd = _make_chord([523, 659, 784], 380, 0.32)
            self.select_snd = _make_tone(880, 45, 0.10)
            self.enabled = True
        except Exception as e:
            print(f"音效初始化失敗（將以靜音執行）: {e}")

    def slide(self):
        if self.enabled: self.slide_snd.play()

    def thunk(self):
        if self.enabled: self.thunk_snd.play()

    def win(self):
        if self.enabled: self.win_snd.play()

    def select(self):
        if self.enabled: self.select_snd.play()
