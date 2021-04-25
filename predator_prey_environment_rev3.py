#Goal1에 대한 Predator Heuristic Action 적용
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import itertools as it
import random
import time
import csv
from datetime import datetime
import winsound


PhotoImage = ImageTk.PhotoImage

row = 10
col = 10
unit = 50

prey_num = 1
predator_num = 4

window = Tk()
window.geometry('{0}x{1}'.format(row*unit, col*unit))
window.title('Prey-Predator Environment Rev3 by LoneAI Gym')
canvas = Canvas(window, background = 'white', width = col*unit, height = row*unit)

agent_image_size = int(unit * 0.9)
prey_ = PhotoImage(Image.open('prey.png').resize((agent_image_size, agent_image_size)))
predator_ = PhotoImage(Image.open('predator.png').resize((agent_image_size, agent_image_size)))

state_coordinates = [(np.array(i)*unit+unit/2).astype('int').tolist() for i in it.product(range(row), range(col))]
available_actions = [[0,0],[0,-unit],[0,+unit],[-unit,0],[+unit,0]]

for i in range(row):
	alpha = (0,i*unit)
	omega = (col*unit,i*unit)
	canvas.create_line(alpha,omega)
for i in range(col):
	alpha = (i*unit,0)
	omega = (i*unit,row*unit)
	canvas.create_line(alpha,omega)

def state_constraint(current_state):
	result = current_state in state_coordinates
	return result

def prey_motivation(current_state):
	greedy_rate = 0.99 #0.8 is best
	possibility = False
	predator_states = [globals()['predator_state_'+str(i)] for i in range(predator_num)]
	while possibility == False:
		if random.random() < greedy_rate:
			possible_states = [(np.array(current_state) + i).tolist() for i in available_actions]
			heuristic_values = []
			for i in possible_states:
				temp = []
				for j in predator_states:
					heuristic_value = np.sqrt((j[0] - i[0]) ** 2 + (j[1] - i[1]) ** 2)
					temp.append(heuristic_value)
				heuristic_values.append(np.sum(temp))
			result = possible_states[heuristic_values.index(np.max(heuristic_values))]
			print(heuristic_values)
			print(heuristic_values.index(np.max(heuristic_values)))
		else:
			result = (np.array(current_state) + random.sample(available_actions,1)[0]).tolist()
		possibility = state_constraint(result)
	return result

def predator_motivation(current_state):
	greedy_rate = 0.99 #0.9 is best
	possibility = False
	surround_states = [(np.array(prey_state_0) + i).tolist() for i in available_actions[1:]]
	while possibility == False:
		if random.random() < greedy_rate:
			possible_states = [(np.array(current_state) + i).tolist() for i in available_actions]
			heuristic_values = []
			for i in possible_states:
				temp = []
				for j in surround_states:
					heuristic_value = np.sqrt((j[0] - i[0]) ** 2 + (j[1] - i[1]) ** 2).tolist()
					temp.append(heuristic_value)
				heuristic_values.append(temp)
			heuristic_values = np.array(heuristic_values)
			result = possible_states[np.where(heuristic_values == np.min(heuristic_values))[0][0]]
			print(heuristic_values)
			print(np.where(heuristic_values == np.min(heuristic_values))[1][0])
		else:
			result = (np.array(current_state) + random.sample(available_actions,1)[0]).tolist()
		possibility = state_constraint(result)
	return result

def overlap_check():
	predator_states = []
	for i in range(predator_num):
		predator_states.append(globals()['predator_state_'+str(i)])
	for i in predator_states:
		if predator_states.count(i) > 1:
			return False
	return True

def goal_check_1():
	surround_states = sorted([(np.array(prey_state_0) + i).tolist() for i in available_actions[1:]])
	predator_states = sorted([globals()['predator_state_'+str(i)] for i in range(predator_num)])
	result = surround_states == predator_states
	return result

def goal_check_2():
	predator_states = [globals()['predator_state_'+str(i)] for i in range(predator_num)]
	result = prey_state_0 in predator_states
	return result

def state_status():
	for_write = [datetime.now(), goal_check_1(), goal_check_2()]
	for i in range(prey_num):
		temp = globals()['prey_state_'+str(i)]
		print('prey_state_'+str(i), temp)
		for_write.append(temp)
	for i in range(predator_num):
		temp = globals()['predator_state_'+str(i)]
		print('predator_state_'+str(i), temp)
		for_write.append(temp)
	with open('history_rev3.csv', 'a', newline = '\n') as write_obj:
		writer_obj = csv.writer(write_obj)
		writer_obj.writerow(for_write)

while True:
	initial_states = random.sample(state_coordinates, prey_num+predator_num)

	for i in range(prey_num):
		globals()['prey_state_'+str(i)] = initial_states.pop(0)
	for i in range(predator_num):
		globals()['predator_state_'+str(i)] = initial_states.pop(0)

	for i in range(prey_num):
		globals()['prey_vision_'+str(i)] = canvas.create_image(globals()['prey_state_'+str(i)], image = prey_) 
	for i in range(predator_num):
		globals()['predator_vision_'+str(i)] = canvas.create_image(globals()['predator_state_'+str(i)], image = predator_) 

	state_status()

	canvas.pack()
	window.update()

	gameover = False
	time.sleep(0)
	while gameover == False:
		time.sleep(0.1)
		
		for i in range(prey_num):
			canvas.delete(globals()['prey_vision_'+str(i)])
		for i in range(predator_num):
			canvas.delete(globals()['predator_vision_'+str(i)])
		
		for i in range(prey_num):
			globals()['prey_state_'+str(i)] = prey_motivation(globals()['prey_state_'+str(i)])
			globals()['prey_vision_'+str(i)] = canvas.create_image((globals()['prey_state_'+str(i)]), image = prey_)
		
		overlap = False
		while overlap == False:
			for i in range(predator_num):
				globals()['predator_state_'+str(i)] = predator_motivation(globals()['predator_state_'+str(i)])
			overlap = overlap_check()
		
		for i in range(predator_num):
			globals()['predator_vision_'+str(i)] = canvas.create_image((globals()['predator_state_'+str(i)]), image = predator_)

		window.update()

		state_status()

		if goal_check_1():
			gameover = True
			print('Game Over with Goal 1 Satisfied')
			winsound.Beep(1046,1000)
			time.sleep(5)
			for i in range(prey_num):
				canvas.delete(globals()['prey_vision_'+str(i)])
			for i in range(predator_num):
				canvas.delete(globals()['predator_vision_'+str(i)])
		if goal_check_2():
			gameover = True
			print('Game Over with Goal 2 Satisfied')
			time.sleep(0.5)
			for i in range(prey_num):
				canvas.delete(globals()['prey_vision_'+str(i)])
			for i in range(predator_num):
				canvas.delete(globals()['predator_vision_'+str(i)])