# import pygame
import pygame
# import network module
from PodSixNet.Connection import connection, ConnectionListener

# init pygame
pygame.init()

pygame.mixer.music.load('music/guitar-electro-sport-trailer-115571.mp3')
pygame.mixer.music.play()

# class for I/O on network
# this represent the player, too
class Listener(ConnectionListener):
	# init the player
	def __init__(self, host, port):
		self.Connect((host, port))
		
		# set the window
		self.screen = pygame.display.set_mode((800, 640))
		
		# player number. this can be 0 (left player) or 1 (right player)
		self.num = None
		# players' rects
		self.players = (pygame.Rect(10, 260, 8, 80), pygame.Rect(785, 260, 8, 80))
		# players movement
		self.movement = [0, 0]

		# radius of the ball
		self.rad = 6
		# ball's rect
		self.ballrect = pygame.Rect(394, 294, 12, 12)

		# True if the server sended the ready message
		self.ready = False
		# True if the game is working
		self.start = False

		# font for writing the scores
		self.font = pygame.font.SysFont('sans,freesans,courier,arial', 18, True)
		# points of the first and second players
		self.points = [0, 0]
	
	# funtion to manage bars movement
	def Network_move(self, data):
		if data['player'] != self.num:
			self.players[data['player']].top = data['top']
	
	# get the player number
	def Network_number(self, data):
		self.num = data['num']

	# get ballpos
	def Network_ballpos(self, data):
		self.ballrect = pygame.Rect(data['pos'], data['size'])
	
	# if the game is ready
	def Network_ready(self, data):
		self.ready = not self.ready
	
	# change players' score
	def Network_points(self, data):
		self.points[0] = data[0]
		self.points[1] = data[1]
	
	# start the game
	def Network_start(self, data):
		self.ready = False
		self.start = True
	
	# mainloop
	def Loop(self):
		while True:
			# update connection
			connection.Pump()
			# update the listener
			self.Pump()
			
			# control user input
			for event in pygame.event.get():
				# end the game in necessary
				if event.type == pygame.QUIT:
					exit(0)
				
				# if the game is started
				elif self.start:
				
					# control user keyboard input
					if event.type == pygame.KEYDOWN:
					
						# if 'o' is pressed move the bar up
						if event.key == pygame.K_UP:
							self.movement[self.num] = -10
						
						# if 'k' is pressed move the bar down
						elif event.key == pygame.K_DOWN:
							self.movement[self.num] = 10
						
					elif event.type == pygame.KEYUP:
						# if key are released stop the movement
						if event.key in (pygame.K_UP, pygame.K_DOWN):
							self.movement[self.num] = 0
			
			# clear the screen
			self.screen.fill((0, 0, 0))
			
			# if game is working
			if self.start:
				n = 0
				# for each player control his movement
				for move in self.movement:
					# if the bar is at the top of the screen
					if self.players[n].top + move < 0:
						self.players[n].top = 0
						# stop the movement
						self.movement[n] = 0
					# if the bar is at the bottom of the screen
					elif self.players[n].bottom + move > 600:
						self.players[n].bottom = 600
						# stop the movement
						self.movement[n] = 0
					else:
						self.players[n].top += move
					
					n += 1
				
				# send to the server information about movement
				connection.Send({'action': 'move', 'player': self.num, 'top': self.players[self.num].top})
				
				# draw objects
				
				# ballpos
				pos = (self.ballrect.left+self.rad, self.ballrect.top+self.rad)
				# draw the ball
				pygame.draw.circle(self.screen, (255, 255, 255), pos, self.rad)
	
				# draw the line at the bottom of the screen
				pygame.draw.line(self.screen, (100, 100, 100), (0, 600), (800, 600))
				
				n = 0
				# for each player draw the bar and print the score at the bottom of the screen
				for rect in self.players:
					# draw the bar
					pygame.draw.rect(self.screen, (255, 255, 255), rect)
					
					if n == self.num:
						if n == 0:
							self.screen.blit(self.font.render(str(self.points[n]), True, (0, 255, 0)), (50, 608))
						else:
							self.screen.blit(self.font.render(str(self.points[n]), True, (0, 255, 0)), (750-self.font.size(str(self.points[n]))[0], 608))
					else:
						if n == 0:
							self.screen.blit(self.font.render(str(self.points[n]), True, (255, 0, 0)), (50, 608))
						else:
							self.screen.blit(self.font.render(str(self.points[n]), True, (255, 0, 0)), (750-self.font.size(str(self.points[n]))[0], 608))
	
					n += 1
				
				# update the screen
				pygame.display.flip()
			
			# if self.ready is True
			if self.ready:
				# write some text
				self.screen.blit(self.font.render('Ready', True, (0, 0, 255)), (400-self.font.size('Ready')[0]/2, 290))
				# update the screen
				pygame.display.flip()
			# print 'Waiting for players...'
			elif not self.start:
				# write some text
				self.screen.blit(self.font.render('Waiting for players...', True, (255, 255, 255)), (400-self.font.size('Waiting for players...')[0]/2, 290))
				# update the screen
				pygame.display.flip()
	
			# wait 25 milliseconds
			pygame.time.wait(25)
		

print('Enter the server ip adresse (pleaviously enter on the server script).')
print('Empty for localhost')
# ask the server ip adresse
server = input('server ip: ')
# control if server is empty
if server == '':
	server = 'localhost'

# init the listener
listener = Listener(server, 31500)
# start the mainloop
listener.Loop()

