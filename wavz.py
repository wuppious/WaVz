import time
import pygame

WIDTH = 1200
HEIGHT = 500
SCALE = HEIGHT / 2.5 / 32768

DATA_SIZE = 2048

filename = 'data/dustsucker.wav'

goneTime = 0
startTime = 0
offset = 0

pygame.init()
pygame.display.set_caption('WaVz - WAVE format audio visualizer')
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True


with open(filename, 'rb') as f:

    RIFF_chunkID        = int.from_bytes(f.read(4), byteorder='big')
    RIFF_chunkSize      = int.from_bytes(f.read(4), byteorder='little')
    RIFF_format         = int.from_bytes(f.read(4), byteorder='big')

    fmt_subchunk1ID     = int.from_bytes(f.read(4), byteorder='big')
    fmt_subchunk1Size   = int.from_bytes(f.read(4), byteorder='little')
    fmt_audioFormat     = int.from_bytes(f.read(2), byteorder='little')
    fmt_numChannels     = int.from_bytes(f.read(2), byteorder='little')
    fmt_sampleRate      = int.from_bytes(f.read(4), byteorder='little')
    fmt_byteRate        = int.from_bytes(f.read(4), byteorder='little')
    fmt_blockAlign      = int.from_bytes(f.read(2), byteorder='little')
    fmt_bitsPerSample   = int.from_bytes(f.read(2), byteorder='little')

    data_subchunk2ID    = int.from_bytes(f.read(4), byteorder='big')
    data_subchunk2Size  = int.from_bytes(f.read(4), byteorder='little')



    if not fmt_audioFormat == 1:
    	print('Compression format not supported')
    	f.close()
    	running = False

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    startTime = time.perf_counter()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    DATA_SIZE = min(16384, DATA_SIZE * 2)
                elif event.key == pygame.K_DOWN:
                    DATA_SIZE = max(128, DATA_SIZE // 2)
                elif event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    startTime = time.perf_counter()

        goneTime = time.perf_counter() - startTime
        offset = 44 + int(fmt_byteRate * goneTime)
        f.seek(offset + (offset & 1))

        points = []
        for i in range(DATA_SIZE):

            data = int.from_bytes(f.read(fmt_bitsPerSample // 8), byteorder='little')

            if data < 32768:
                data += 32768
            elif data > 32768:
                data -= 32768

            x = (i / DATA_SIZE) * WIDTH
            y = (data + 32768/2) * SCALE  
            points.append((int(x),int(y)))

        lines = []
        for x in range(WIDTH):
            lines.append(points[DATA_SIZE * x // WIDTH])

        screen.fill((0,0,0))
        pygame.draw.lines(screen, (255,255,255), False, lines)

        pygame.display.flip()
        clock.tick(60)

    f.close()
