from numpy import fft
from statistics import mean
import math
import pygame
import time


class Visualizer():
    def __init__(self, bands, freq_high, freq_low):
        self.bands = bands
        self.freq_high = freq_high
        self.freq_low = freq_low
        self.points = []

    def update(self, data, rate):
        self.points = []
        size = len(data) / 2
        container_size = rate / size 
        limit_high = math.floor(self.freq_high / container_size)
        limit_low = math.ceil(self.freq_low / container_size)
        limited_size = limit_high - limit_low

        for b in range(self.bands+1):
            y = 1
            start = int(self.scale(b, self.bands, limited_size))
            if not b == self.bands:
                end = int(self.scale(b+1, self.bands, limited_size))
            else:
                end = start
            if data[start:end]:
                y = mean(data[math.floor(start):math.ceil(end)])
            else:
                y = data[end]
            self.points.append(y)

    def scale(self, x, b, s):
        return math.exp((math.log(s) / b) * x)

WIDTH = 1200
HEIGHT = 300

SAMPLE_SIZE = 4096
FREQ_LOW = 20
FREQ_HIGH = 22000
BANDS = WIDTH



goneTime = 0
startTime = 0
offset = 0


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True

filename = 'data/easy.wav' 


with open(filename, 'rb') as f:

    RIFF_chunkID = int.from_bytes(f.read(4), byteorder='little')
    RIFF_chunkSize = int.from_bytes(f.read(4), byteorder='little')
    RIFF_format = int.from_bytes(f.read(4), byteorder='big')

    fmt_subchunk1ID = int.from_bytes(f.read(4), byteorder='big')
    fmt_subchunk1Size = int.from_bytes(f.read(4), byteorder='little')
    fmt_audioFormat = int.from_bytes(f.read(2), byteorder='little')
    fmt_numChannels = int.from_bytes(f.read(2), byteorder='little')
    fmt_sampleRate = int.from_bytes(f.read(4), byteorder='little')
    fmt_byteRate = int.from_bytes(f.read(4), byteorder='little')
    fmt_blockAlign = int.from_bytes(f.read(2), byteorder='little')
    fmt_bitsPerSample = int.from_bytes(f.read(2), byteorder='little')

    data_subchunk2ID = int.from_bytes(f.read(4), byteorder='big')
    data_subchunk2Size = int.from_bytes(f.read(4), byteorder='little')

    if not fmt_audioFormat:
        print('Compression format not supported')
        f.close()
        running = False

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    visualizer = Visualizer(BANDS, FREQ_HIGH, FREQ_LOW) 

    startTime = time.perf_counter()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0,0,0))
        goneTime = time.perf_counter() - startTime
        offset = 44 + int(fmt_byteRate * goneTime)
        if offset & 1:
            offset += 1

        f.seek(offset)

        
        points = []
        data = []
        for i in range(SAMPLE_SIZE):
            point = int.from_bytes(f.read(fmt_bitsPerSample // 8), byteorder='little')
            point = point / 65536
            data.append(point)
                
        data = fft.rfft(data)
        for p in data[1:]:
            magnitude = abs(math.pow(p.real,2) + math.pow(p.imag,2))
            points.append(magnitude)

        visualizer.update(points, fmt_sampleRate)

        for b in range(visualizer.bands):
            bands = visualizer.bands
            pygame.draw.line(screen, (255,255,255), (b * WIDTH / bands + (WIDTH / bands / 2), HEIGHT),
                                                    (b * WIDTH / bands + (WIDTH / bands / 2), HEIGHT - math.pow(math.log1p(visualizer.points[b]),2) * HEIGHT / 200))

        # for x in range(SAMPLE_SIZE//4):
        #     if x/(SAMPLE_SIZE // 4) // WIDTH == 0:
        #         pygame.draw.line(screen, (255,255,255), ((x/(SAMPLE_SIZE//4)) * WIDTH, HEIGHT), 
        #                                                 ((x/(SAMPLE_SIZE//4)) * WIDTH, HEIGHT - math.log1p(points[x] / max_mag)*HEIGHT))

        pygame.display.flip()
        clock.tick(60)
    f.close()



