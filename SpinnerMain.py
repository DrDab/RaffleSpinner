import pygame
import pygame.freetype
pygame.init()
import csv
import random
import sys

# begin constants
CSV_FILENAME            = "raffle.csv"
SCREEN_HEIGHT           = 500     # pixels
SCREEN_LENGTH           = 600     # pixels
MAX_FPS                 = 60      # frames/sec
MIN_SPIN_VELOCITY       = 2100    # pixels/sec
MAX_SPIN_VELOCITY       = 2100    # pixels/sec
SPIN_ACCELERATION       = -150    # pixels/sec^2
VELOCITY_ZERO_DEADBAND  = 10      # pixels/sec
TICKET_SPACING          = 100     # pixels
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
            longestTicket = max(longestTicket, len(name))
            if numTicketsStr.strip() == "":
                continue
            numTickets = int(numTicketsStr)
            for i in range(0, numTickets):
                toReturn.append(name)
        return toReturn

def clear():
    w.fill((255, 255, 255))

def render_tickets(tickets, cameraPos):
    ticketPosCur = 0.0
    for ticket in tickets:
        relativePos = ticketPosCur - cameraPos
        if (relativePos <= -FONT_SIZE + 40 or relativePos >= SCREEN_LENGTH + FONT_SIZE) == False:
            font.render_to(w, (0, int(relativePos)), str(ticket))
        ticketPosCur += TICKET_SPACING

def getClosestToCenter(tickets, cameraPos):
    minDistFromCentre = sys.float_info.max - 1
    minDistEntry = None
    minDistEntryCameraPos = None
    ticketPosCur = 0.0
    for ticket in tickets:
        relativePos = ticketPosCur - cameraPos
        ticketCenterRelativePos = relativePos + (FONT_SIZE / 2)
        distanceFromCenter = abs((SCREEN_HEIGHT / 2) - ticketCenterRelativePos)
        if distanceFromCenter < minDistFromCentre:
            minDistFromCentre = distanceFromCenter
            minDistEntry = ticket
            minDistEntryCameraPos = ticketPosCur - (2 * TICKET_SPACING)
        ticketPosCur += TICKET_SPACING
    return [minDistEntry, minDistFromCentre, minDistEntryCameraPos]

tickets = get_raffle_tickets()
random.shuffle(tickets)

ticketsAugmented = tickets * 200

#print(tickets)
running = True

width = longestTicket * FONT_SIZE * 0.65
if width < SCREEN_LENGTH:
    width = SCREEN_LENGTH

w = pygame.display.set_mode([int(width), SCREEN_HEIGHT])
c = pygame.time.Clock()

velocityPrev = 0.0
velocity = 0.0
position = 0.0

awaitingFirstSpin = True
justFinished = False

print("%d %d" % (width, SCREEN_HEIGHT))

while running:
    if abs(velocity) > 0.0 or awaitingFirstSpin:
        clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                #position = -TICKET_SPACING * 2
                awaitingFirstSpin = False
                velocity = MIN_SPIN_VELOCITY + (random.random() * (MAX_SPIN_VELOCITY - MIN_SPIN_VELOCITY))
            if event.key == pygame.K_e:
                print("position=%.6f velocity=%.6f" % (position, velocity))

    if position > (len(ticketsAugmented) - 2) * TICKET_SPACING :
        position = -2 * TICKET_SPACING - (FONT_SIZE / 4)

    dt = c.get_time() / 1000.0
    # integrate kinematics.
    velocityPrev = velocity
    if (abs(velocity) > VELOCITY_ZERO_DEADBAND):
        velocity += SPIN_ACCELERATION * dt
    else:
        velocity = 0.0
        if abs(velocityPrev) > 0.0:
            closestToCenterList = getClosestToCenter(ticketsAugmented, position)
            if (closestToCenterList[2] == None) == False:
                toRemove = closestToCenterList[0]
                position = closestToCenterList[2]
                render_tickets(ticketsAugmented, position)
                justFinished = True
                removeArr = []
                for curTicket in tickets:
                    if curTicket == toRemove:
                        removeArr.append(toRemove)
                for removeTicket in removeArr:
                    tickets.remove(removeTicket) 
                ticketsAugmented = tickets * 200

                        
    position += velocity * dt

    if abs(velocity) > 0.0 or awaitingFirstSpin:
        render_tickets(ticketsAugmented, position)

    pygame.draw.line(w, (255, 0, 0), (0, int((SCREEN_HEIGHT / 2) - (FONT_SIZE / 2))), (int(width), int((SCREEN_HEIGHT / 2) - (FONT_SIZE / 2))), 3)
    pygame.draw.line(w, (255, 0, 0), (0, int((SCREEN_HEIGHT / 2) + (FONT_SIZE / 2))), (int(width), int((SCREEN_HEIGHT / 2) + (FONT_SIZE / 2))), 3)

    c.tick(MAX_FPS)
    if abs(velocity) > 0.0 or awaitingFirstSpin or justFinished:
        pygame.display.flip()  
        justFinished = False
