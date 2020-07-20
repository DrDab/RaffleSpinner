import pygame
import pygame.freetype
pygame.init()
import csv
import random
import sys

# begin constants
CSV_FILENAME            = "raffle.csv"
SCREEN_HEIGHT           = 100     # pixels
SCREEN_LENGTH           = 600     # pixels
MAX_FPS                 = 60      # frames/sec
MIN_SPIN_VELOCITY       = 3000    # pixels/sec
MAX_SPIN_VELOCITY       = 7000    # pixels/sec
SPIN_ACCELERATION       = -500    # pixels/sec^2
VELOCITY_ZERO_DEADBAND  = 10      # pixels/sec
TICKET_SPACING          = 80     # pixels
FONT_SIZE               = 100     # pixels
# end constants

font = pygame.freetype.Font("courierprimecode-regular.ttf")
font.fgcolor = (0, 0, 0)
font.size = FONT_SIZE

longestTicket = 0

def get_raffle_tickets():
    global longestTicket
    with open(CSV_FILENAME, newline='') as csvfile:
        toReturn = []
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['Name']
            numTicketsStr = row['Number of Tickets']
            if numTicketsStr.strip() == "":
                continue
            longestTicket = max(longestTicket, len(name))
            numTickets = int(numTicketsStr)
            for i in range(0, numTickets):
                toReturn.append(name)
        return toReturn

def clear():
    w.fill((255, 255, 255))


minDistFromCentre = sys.float_info.max - 1
minDistEntry = None
minDistEntryCameraPos = None

def render_tickets(tickets, cameraPos, draw):
    global minDistFromCentre, minDistEntry, minDistEntryCameraPos
    minDistFromCentre = sys.float_info.max - 1
    minDistEntry = None
    minDistEntryCameraPos = None
    ticketPosCur = 0.0
    for ticket in tickets:
        cameraPosFixed = cameraPos % (TICKET_SPACING * len(tickets))
        relativePos = ticketPosCur - cameraPosFixed
        curDistFromCentre = abs((SCREEN_HEIGHT/2) - (relativePos + (FONT_SIZE / 2)))
        if curDistFromCentre < minDistFromCentre:
            minDistFromCentre = curDistFromCentre
            minDistEntry = ticket
            minDistEntryCameraPos = cameraPosFixed
        if (relativePos <= -FONT_SIZE + 40 or relativePos >= SCREEN_LENGTH + FONT_SIZE) == False:
            if draw:
                font.render_to(w, (0, int(relativePos)), str(ticket))
        ticketPosCur += TICKET_SPACING

tickets = get_raffle_tickets()
random.shuffle(tickets)
#print(tickets)
running = True

width = longestTicket * FONT_SIZE * 0.65
if width < SCREEN_LENGTH:
    width = SCREEN_LENGTH

w = pygame.display.set_mode([int(width), SCREEN_HEIGHT])
c = pygame.time.Clock()

velocityPrev = 0.0
velocity = 0.0
position = random.random() * len(tickets) * TICKET_SPACING

#print(len(tickets))

awaitingFirstSpin = True

while running:
    if abs(velocity) > 0.0 or awaitingFirstSpin:
        clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                awaitingFirstSpin = False
                velocity = MIN_SPIN_VELOCITY + (random.random() * (MAX_SPIN_VELOCITY - MIN_SPIN_VELOCITY))

    dt = c.get_time() / 1000.0
    # integrate kinematics.
    velocityPrev = velocity
    if (abs(velocity) > VELOCITY_ZERO_DEADBAND):
        velocity += SPIN_ACCELERATION * dt
    else:
        velocity = 0.0
        if abs(velocityPrev) > 0.0 and (minDistEntry == None) == False:
            render_tickets(tickets, position, False)
            position = minDistEntryCameraPos
            render_tickets(tickets, position, True)
            print("%s wins!" % minDistEntry)
            tickets.remove(minDistEntry)
            print(len(tickets))
    position += velocity * dt

    if abs(velocity) > 0.0 or awaitingFirstSpin:
        render_tickets(tickets, position, True)

    pygame.draw.line(w, (0, 0, 0), (0, SCREEN_HEIGHT / 2), (width, SCREEN_HEIGHT / 2), 3)

    c.tick(MAX_FPS)
    pygame.display.flip()  