from pygame import*

#button class
class Button():
    #(top left corner of the image, image, scale for scaling)
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = transform.scale(image, (int(width * scale), int(height * scale)))
		self.outlineRect = self.image.get_rect()
		self.outlineRect.topleft = (x, y)
		self.clicked = False

        #needs a sureface
	def drawButton(self, display):
		user_input = False
		#get mouse position
		pos = mouse.get_pos()

		#check for collision
		if self.outlineRect.collidepoint(pos):
                     #when click, the mb variable from the graphics template becomes 1
			if not self.clicked and mouse.get_pressed()[0] == 1:  
				self.clicked = True
				user_input = True
				
                    #otherwise is 0(unclicked)
		if mouse.get_pressed()[0] == 0:
			self.clicked=False

		#draw button on screen the argument coordinates are the top left coordinates
		display.blit(self.image, self.outlineRect)      

                #returns a boolean for checking the mouse action
		return user_input
