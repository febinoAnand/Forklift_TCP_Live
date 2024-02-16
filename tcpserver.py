import socket
import json
import os
import datetime
import struct
import decimal
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ForkliftWeb.settings')
django.setup()

from forklift.models import tracker_device
from deviceData.models import RAWData, GPSData, EXTData

HOST = "0.0.0.0"
PORT = 9090  #change this to your port

####################################################
###############__CRC16/ARC Checker__################
####################################################

def crc16_arc(data):    
	data_part_length_crc = int(data[8:16], 16)
	data_part_for_crc = bytes.fromhex(data[16:16+2*data_part_length_crc])
	crc16_arc_from_record = data[16+len(data_part_for_crc.hex()):24+len(data_part_for_crc.hex())]  
	
	crc = 0
	
	for byte in data_part_for_crc:
		crc ^= byte
		for _ in range(8):
			if crc & 1:
				crc = (crc >> 1) ^ 0xA001
			else:
				crc >>= 1
	
	if crc16_arc_from_record.upper() == crc.to_bytes(4, byteorder='big').hex().upper():
		print ("CRC check passed!")
		print (f"Record length: {len(data)} characters // {int(len(data)/2)} bytes")
		return True
	else:
		print("CRC check Failed!")
		return False

####################################################

def codec_8e_checker(codec8_packet):
	if str(codec8_packet[16:16+2]).upper() != "8E" and str(codec8_packet[16:16+2]).upper() != "08":	
		print()	
		print(f"Not a Codec 8 or Codec 8E packet....")		
		return False
	else:
		return crc16_arc(codec8_packet)
	

def codec_12_checker(codec12_packet):
	if str(codec12_packet[16:16+2]).upper() != "0C":	
		print()	
		print(f"Invalid packet!!!!!!!!!!!!!!!!!!!")		
		return False
	else:
		return crc16_arc(codec12_packet)


def codec_parser_trigger(codec8_packet, device_imei, props):
		try:			
			return codec_8e_parser(codec8_packet.replace(" ",""), device_imei, props)
		except Exception as e:
			print(f"Error occured: {e}")
			start_server_tigger()


def codec12_parser_trigger(codec12_packet, device_imei, props):
		try:			
			return codec_12_parser(codec12_packet.replace(" ",""), device_imei, props)
		except Exception as e:
			print(f"Error occured: {e}")
			start_server_tigger()

def imei_checker(hex_imei): #IMEI checker function
	imei_length = int(hex_imei[:4], 16)
#	print(f"IMEI length = {imei_length}")
	if imei_length != len(hex_imei[4:]) / 2:
#		print(f"Not an IMEI - length is not correct!")
		return False
	else:
		pass

	ascii_imei = ascii_imei_converter(hex_imei)
	print(f"IMEI received = {ascii_imei}")
	if not ascii_imei.isnumeric() or len(ascii_imei) != 15:
		print(f"Not an IMEI - is not numeric or wrong length!")
		return False
	else:
		return True

def ascii_imei_converter(hex_imei):
	return bytes.fromhex(hex_imei[4:]).decode()

def start_server_tigger():
	print("Starting server!")

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, PORT))
		while True:
			s.listen()
			print(f"// {time_stamper()} // listening port: {PORT} // IP: {HOST}")
			conn, addr = s.accept()
			conn.settimeout(20) #connection timeout, change this value to close the socket if no DATA is received for X amount of seconds
			with conn:
				print(f"// {time_stamper()} // Connected by {addr}")
				device_imei = "default_IMEI"
				while True:
					try:
						data = conn.recv(1280)
						print(f"// {time_stamper()} // data received = {data.hex()}")
						if not data:
							break
						elif imei_checker(data.hex()) != False:
							device_imei = ascii_imei_converter(data.hex())
							imei_reply = (1).to_bytes(1, byteorder="big")
							conn.sendall(imei_reply)
							print(f"-- {time_stamper()} sending reply = {imei_reply}")
						elif codec_8e_checker(data.hex().replace(" ","")) != False:
							record_number = codec_parser_trigger(data.hex(), device_imei, "SERVER")
							print(f"received records {record_number}")
							print(f"from device IMEI = {device_imei}")
							print()
							record_response = (record_number).to_bytes(4, byteorder="big")
							conn.sendall(record_response)
							print(f"// {time_stamper()} // response sent = {record_response.hex()}")

						elif codec_12_checker(data.hex().replace(" ","")) != False:
							returnData = codec12_parser_trigger(data.hex(), device_imei, "SERVER")
							print(f"received records --> {returnData}")
							print(f"from device IMEI = {device_imei}")
							print()
							# record_response = (returnData).to_bytes(4, byteorder="big")
							returnData = "OK"
							record_response = str.encode(returnData)
							conn.sendall(record_response)
							print(f"// {time_stamper()} // response sent = {record_response.hex()}")
						else:
							print(f"// {time_stamper()} // no expected DATA received - dropping connection")
							break
					except socket.timeout:
						print(f"// {time_stamper()} // Socket timed out. Closing connection with {addr}")
						break
							
####################################################
###############_Codec8E_parser_code_################
####################################################

def codec_8e_parser(codec_8E_packet, device_imei, props): #think a lot before modifying  this function
	print()
#	print (str("codec 8 string entered - " + codec_8E_packet))

	rawDataObject = RAWData()
	# tracker_deviceObject = tracker_device()
	

	io_dict_raw = {}
#	timestamp = codec_8E_packet[20:36]	
	io_dict_raw["device_IMEI"] = device_imei
	io_dict_raw["server_time"] = time_stamper_for_json()
#	io_dict_raw["_timestamp_"] = device_time_stamper(timestamp)
#	io_dict_raw["_rec_delay_"] = record_delay_counter(timestamp)
	io_dict_raw["data_length"] = "Record length: " + str(int(len(codec_8E_packet))) + " characters" + " // " + str(int(len(codec_8E_packet) // 2)) + " bytes"
	io_dict_raw["_raw_data__"] = codec_8E_packet

	try:
		rawDataObject.device_id = device_imei
		rawDataObject.received_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		rawDataObject.data_length = len(codec_8E_packet)
		rawDataObject.data = codec_8E_packet
		rawDataObject.save()
	except Exception as e:
		print ("Data cant be save in raw table ", e)

	try: #writing raw DATA dictionary to ./data/data.json
		json_printer_rawDATA(io_dict_raw, device_imei)
	except Exception as e:
		print(f"JSON raw data writing error occured = {e}")

	zero_bytes = codec_8E_packet[:8]
	print()
	print (str("zero bytes = " + zero_bytes))

	data_field_length = int(codec_8E_packet[8:8+8], 16)
	print (f"data field lenght = {data_field_length} bytes")
	codec_type = str(codec_8E_packet[16:16+2])
	print (f"codec type = {codec_type}")

	data_step = 4
	if codec_type == "08":
		data_step = 2
	else:
		pass

	number_of_records = int(codec_8E_packet[18:18+2], 16)
	print (f"number of records = {number_of_records}")

	record_number = 1
	avl_data_start = codec_8E_packet[20:]
	data_field_position = 0
	while data_field_position < (2*data_field_length-6):				
		io_dict = {}
		io_dict["device_IMEI"] = device_imei		
		io_dict["server_time"] = time_stamper_for_json()
		print()
		print (f"data from record {record_number}")	
		print (f"########################################")

		timestamp = avl_data_start[data_field_position:data_field_position+16]
		io_dict["_timestamp_"] = device_time_stamper(timestamp)		
		print (f"timestamp = {device_time_stamper(timestamp)}")	
		io_dict["_rec_delay_"] = record_delay_counter(timestamp)		
		data_field_position += len(timestamp)
		
		


		priority = avl_data_start[data_field_position:data_field_position+2]
		io_dict["priority"] = int(priority, 16)
		print (f"record priority = {int(priority, 16)}")
		data_field_position += len(priority)

		longtitude = avl_data_start[data_field_position:data_field_position+8]
		print ("Long--->",longtitude)
		io_dict["longtitude"] = struct.unpack('>i', bytes.fromhex(longtitude))[0]
		print (f"longtitude = {struct.unpack('>i', bytes.fromhex(longtitude))[0]}")
		data_field_position += len(longtitude)
		


		latitude = avl_data_start[data_field_position:data_field_position+8]
		print ("Lat--->",latitude)
		print (f"latitude = {struct.unpack('>i', bytes.fromhex(latitude))[0]}")
		io_dict["latitude"] = struct.unpack('>i', bytes.fromhex(latitude))[0]
		data_field_position += len(latitude)
		

		altitude = avl_data_start[data_field_position:data_field_position+4]
		print(f"altitude = {int(altitude, 16)}")
		io_dict["altitude"] = int(altitude, 16)
		data_field_position += len(altitude)

		angle = avl_data_start[data_field_position:data_field_position+4]
		print(f"angle = {int(angle, 16)}")
		io_dict["angle"] = int(angle, 16)
		data_field_position += len(angle)

		satelites = avl_data_start[data_field_position:data_field_position+2]
		print(f"satelites = {int(satelites, 16)}")
		io_dict["satelites"] = int(satelites, 16)
		data_field_position += len(satelites)

		speed = avl_data_start[data_field_position:data_field_position+4]
		io_dict["speed"] = int(speed, 16)
		print(f"speed = {int(speed, 16)}")
		data_field_position += len(speed)

		event_io_id = avl_data_start[data_field_position:data_field_position+data_step]
		io_dict["eventID"] = int(event_io_id, 16)		
		print(f"event ID = {int(event_io_id, 16)}")
		data_field_position += len(event_io_id)

		total_io_elements = avl_data_start[data_field_position:data_field_position+data_step]
		total_io_elements_parsed = int(total_io_elements, 16)
		print(f"total I/O elements in record {record_number} = {total_io_elements_parsed}")
		data_field_position += len(total_io_elements)

		byte1_io_number = avl_data_start[data_field_position:data_field_position+data_step]
		byte1_io_number_parsed = int(byte1_io_number, 16)
		print(f"1 byte io count = {byte1_io_number_parsed}")
		data_field_position += len(byte1_io_number)	

		try:
			currentDevice = tracker_device.objects.get(device_id=device_imei)
			# print ("current Device -->",currentDevice)
			if currentDevice != None:
				GPSDataObject = GPSData()
				GPSDataObject.date = extract_device_date(timestamp)
				GPSDataObject.time = extract_device_time(timestamp)
				GPSDataObject.device_id = currentDevice
				GPSDataObject.longitude = io_dict["longtitude"]
				GPSDataObject.latitude = io_dict["latitude"]
				GPSDataObject.speed = io_dict["speed"]	
				GPSDataObject.distance = 0.0
				GPSDataObject.state = 3
				GPSDataObject.save()
		except Exception as e:
			print ("GPSData was not added because--> ",e)

		if byte1_io_number_parsed > 0:
			i = 1				
			while i <= byte1_io_number_parsed:
				key = avl_data_start[data_field_position:data_field_position+data_step]
				data_field_position += len(key)
				value = avl_data_start[data_field_position:data_field_position+2]

				io_dict[int(key, 16)] = sorting_hat(int(key, 16), value)
				data_field_position += len(value)
				print (f"avl_ID: {int(key, 16)} : {io_dict[int(key, 16)]}")
				i += 1
		else:
			pass

		byte2_io_number = avl_data_start[data_field_position:data_field_position+data_step]
		byte2_io_number_parsed = int(byte2_io_number, 16)
		print(f"2 byte io count = {byte2_io_number_parsed}")
		data_field_position += len(byte2_io_number)

		if byte2_io_number_parsed > 0:
			i = 1
			while i <= byte2_io_number_parsed:
				key = avl_data_start[data_field_position:data_field_position+data_step]
				data_field_position += len(key)

				value = avl_data_start[data_field_position:data_field_position+4]
				io_dict[int(key, 16)] = sorting_hat(int(key, 16), value)
				data_field_position += len(value)
				print (f"avl_ID: {int(key, 16)} : {io_dict[int(key, 16)]}")
				i += 1
		else:
			pass

		byte4_io_number = avl_data_start[data_field_position:data_field_position+data_step]
		byte4_io_number_parsed = int(byte4_io_number, 16)
		print(f"4 byte io count = {byte4_io_number_parsed}")
		data_field_position += len(byte4_io_number)

		if byte4_io_number_parsed > 0:
			i = 1
			while i <= byte4_io_number_parsed:
				key = avl_data_start[data_field_position:data_field_position+data_step]
				data_field_position += len(key)

				value = avl_data_start[data_field_position:data_field_position+8]
				io_dict[int(key, 16)] = sorting_hat(int(key, 16), value)
				data_field_position += len(value)
				print(f"avl_ID: {int(key, 16)} : {io_dict[int(key, 16)]}")
				i += 1
		else:
			pass

		byte8_io_number = avl_data_start[data_field_position:data_field_position+data_step]
		byte8_io_number_parsed = int(byte8_io_number, 16)
		print(f"8 byte io count = {byte8_io_number_parsed}")
		data_field_position += len(byte8_io_number)

		if byte8_io_number_parsed > 0:
			i = 1
			while i <= byte8_io_number_parsed:
				key = avl_data_start[data_field_position:data_field_position+data_step]
				data_field_position += len(key)

				value = avl_data_start[data_field_position:data_field_position+16]
				io_dict[int(key, 16)] = sorting_hat(int(key, 16), value)
				data_field_position += len(value)
				print(f"avl_ID: {int(key, 16)} : {io_dict[int(key, 16)]}")
				i += 1
		else:
			pass

		if codec_type.upper() == "8E":

			byteX_io_number = avl_data_start[data_field_position:data_field_position+4]
			byteX_io_number_parsed = int(byteX_io_number, 16)
			print(f"X byte io count = {byteX_io_number_parsed}")
			data_field_position += len(byteX_io_number)

			if byteX_io_number_parsed > 0:
				i = 1
				while i <= byteX_io_number_parsed:
					key = avl_data_start[data_field_position:data_field_position+4]
					data_field_position += len(key)

					value_length = avl_data_start[data_field_position:data_field_position+4]
					data_field_position += 4
					value = avl_data_start[data_field_position:data_field_position+(2*(int(value_length, 16)))]
					io_dict[int(key, 16)] = sorting_hat(int(key, 16), value)		
					data_field_position += len(value)
					print(f"avl_ID: {int(key, 16)} : {io_dict[int(key, 16)]}")
				#	print (f"data field postition = {data_field_position}")
				#	print (f"data_field_length = {2*data_field_length}")
					i += 1
			else:
				pass
		else:
			pass

		record_number += 1
		
		# try: #writing dictionary to ./data/data.json
		# 	json_printer(io_dict, device_imei)
		# except Exception as e:
		# 	print(f"JSON writing error occured = {e}")

	if props == "SERVER":	

		total_records_parsed = int(avl_data_start[data_field_position:data_field_position+2], 16)
		print()
		print(f"total parsed records = {total_records_parsed}")
		print()
		return int(number_of_records)
	
	else:
		total_records_parsed = int(avl_data_start[data_field_position:data_field_position+2], 16)
		print()
		print(f"total parsed records = {total_records_parsed}")
		print()
		start_server_tigger()

####################################################
		
####################################################
###############_Codec12_parser_code_################
####################################################

def codec_12_parser(codec_12_packet, device_imei, props): #think a lot before modifying  this function
	print()
#	print (str("codec 12 string entered - " + codec_12_packet))
	rawDataObject = RAWData()
	io_dict_raw = {}
#	timestamp = codec_12_packet[20:36]	
	io_dict_raw["device_IMEI"] = device_imei
	io_dict_raw["server_time"] = time_stamper_for_json()
#	io_dict_raw["_timestamp_"] = device_time_stamper(timestamp)
#	io_dict_raw["_rec_delay_"] = record_delay_counter(timestamp)
	io_dict_raw["data_length"] = "Record length: " + str(int(len(codec_12_packet))) + " characters" + " // " + str(int(len(codec_12_packet) // 2)) + " bytes"
	io_dict_raw["_raw_data__"] = codec_12_packet

	try:
		rawDataObject.device_id = device_imei
		rawDataObject.received_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		rawDataObject.data_length = len(codec_12_packet)
		rawDataObject.data = codec_12_packet
		rawDataObject.save()
	except Exception as e:
		print ("Data cant be save in raw table ", e)

	try: #writing raw DATA dictionary to ./data/data.json
		json_printer_rawDATA(io_dict_raw, device_imei)
	except Exception as e:
		print(f"JSON raw data writing error occured = {e}")

	zero_bytes = codec_12_packet[:8]
	print()
	print (str("zero bytes = " + zero_bytes))

	data_field_length = int(codec_12_packet[8:8+8], 16)
	print (f"data field length = {data_field_length} bytes")

	codec_type = str(codec_12_packet[16:16+2])
	print (f"codec type = {codec_type}")

	command_quantity = int(codec_12_packet[18:18+2], 16)
	print (f"command Quantity = {command_quantity}")

	command_type = int(codec_12_packet[20:20+2], 16)
	print (f"command Type = {command_type}")

	data_length = int(codec_12_packet[22:22+8], 16)
	print (f"data length = {data_length}")

	external_uart_data = bytearray.fromhex(codec_12_packet[30:30+data_length*2]).decode()
	print (f"Uart data = {external_uart_data}")

	


	try:
		extDistance = 0.0
		extBatPower = 0.0
		extBatVolt = 0.0
		extBatAmp = 0.0
		extWattHr = 0.0
		extSpeed = 0.0
		extBatCapacity = 0.0

		ext_data = external_uart_data[external_uart_data.index("EXT&&")+5:external_uart_data.index("??")].split("&")

		
		for data in ext_data:
			print (data)
			if data.find("DIS") > -1:
				extDistance = eval(data[3:])
				print ("External distance -->",extDistance)
			if data.find("BTP") > -1:
				extBatPower = eval(data[3:])
				print ("External battery power -->",extBatPower)
			if data.find("BTV") > -1:
				extBatVolt = eval(data[3:])
				print ("External battery volt -->",extBatVolt)
			if data.find("BTA") > -1:
				extBatAmp = eval(data[3:])
				print ("External battery amp -->",extBatAmp)
			if data.find("WHR") > -1:
				extWattHr = eval(data[3:])
				print ("External watt hr -->",extWattHr)
			if data.find("SPD") > -1:
				extSpeed = eval(data[3:])
				print ("External speed -->",extSpeed)
			if data.find("BTC") > -1:
				extBatCapacity = eval(data[3:])
				print ("External battery capacity -->",extBatCapacity)
		print(ext_data)

		
	
	except Exception as e:
		print ("Not an expected Data-->",e)

	try:
		EXTDataObject = EXTData()
		EXTDataObject.date = datetime.datetime.now().strftime("%Y-%m-%d")
		EXTDataObject.time = datetime.datetime.now().strftime("%H:%M:%S")
		EXTDataObject.device_id = tracker_device.objects.get(device_id = device_imei)
		EXTDataObject.distance = extDistance
		EXTDataObject.batt_amp = extBatAmp
		EXTDataObject.batt_voltage = extBatVolt
		EXTDataObject.batt_capacity = extBatCapacity
		EXTDataObject.batt_power = extBatPower
		EXTDataObject.watt_hr = extWattHr
		EXTDataObject.speed = extSpeed
		EXTDataObject.save()

	except Exception as e:
		print ("Data was not saved ---> ", e)
	

	return external_uart_data

def json_printer(io_dict, device_imei): #function to write JSON file with data
	json_data = json.dumps(io_dict, indent=4)
	data_path = "./data/" + str(device_imei)
	json_file = str(device_imei) + "_data.json"

	if not os.path.exists(data_path):
		os.makedirs(data_path)
	else:
		pass

	if not os.path.exists(os.path.join(data_path, json_file)):
		with open(os.path.join(data_path, json_file), "w") as file:
			file.write(json_data)
	else:
		with open(os.path.join(data_path, json_file), "a") as file:
			file.write(json_data)
	return

def json_printer_rawDATA(io_dict_raw, device_imei): #function to write JSON file with data
#	print (io_dict_raw)
	json_data = json.dumps(io_dict_raw, indent=4)
	data_path = "./data/" + str(device_imei)
	json_file = str(device_imei) + "_RAWdata.json"

	# if not os.path.exists(data_path):
	# 	os.makedirs(data_path)
	# else:
	# 	pass

	# if not os.path.exists(os.path.join(data_path, json_file)):
	# 	with open(os.path.join(data_path, json_file), "w") as file:
	# 		file.write(json_data)
	# else:
	# 	with open(os.path.join(data_path, json_file), "a") as file:
	# 		file.write(json_data)
	return
####################################################
###############____TIME_FUNCTIONS____###############
####################################################

def time_stamper():
	current_server_time = datetime.datetime.now()	
	server_time_stamp = current_server_time.strftime('%H:%M:%S %d-%m-%Y')
	return server_time_stamp

def time_stamper_for_json():
	current_server_time = datetime.datetime.now()
	timestamp_utc = datetime.datetime.utcnow()
	server_time_stamp = f"{current_server_time.strftime('%H:%M:%S %d-%m-%Y')} (local) / {timestamp_utc.strftime('%H:%M:%S %d-%m-%Y')} (utc)"
	return server_time_stamp

def device_time_stamper(timestamp):
	timestamp_ms = int(timestamp, 16) / 1000
	timestamp_utc = datetime.datetime.utcfromtimestamp(timestamp_ms)
	utc_offset = datetime.datetime.fromtimestamp(timestamp_ms) - datetime.datetime.utcfromtimestamp(timestamp_ms)
	timestamp_local = timestamp_utc + utc_offset
	formatted_timestamp_local = timestamp_local.strftime("%H:%M:%S %d-%m-%Y")
	formatted_timestamp_utc = timestamp_utc.strftime("%H:%M:%S %d-%m-%Y")
	formatted_timestamp = f"{formatted_timestamp_local} (local) / {formatted_timestamp_utc} (utc)"

	return formatted_timestamp

def extract_device_date(timestamp):
	timestamp_ms = int(timestamp, 16) / 1000
	timestamp_utc = datetime.datetime.utcfromtimestamp(timestamp_ms)
	utc_offset = datetime.datetime.fromtimestamp(timestamp_ms) - datetime.datetime.utcfromtimestamp(timestamp_ms)
	timestamp_local = timestamp_utc + utc_offset
	formatted_timestamp_local = timestamp_local.strftime("%Y-%m-%d")
	
	return formatted_timestamp_local

def extract_device_time(timestamp):
	timestamp_ms = int(timestamp, 16) / 1000
	timestamp_utc = datetime.datetime.utcfromtimestamp(timestamp_ms)
	utc_offset = datetime.datetime.fromtimestamp(timestamp_ms) - datetime.datetime.utcfromtimestamp(timestamp_ms)
	timestamp_local = timestamp_utc + utc_offset
	formatted_timestamp_local = timestamp_local.strftime("%H:%M:%S")
	
	return formatted_timestamp_local

def record_delay_counter(timestamp):
	timestamp_ms = int(timestamp, 16) / 1000
	current_server_time = datetime.datetime.now().timestamp()
	return f"{int(current_server_time - timestamp_ms)} seconds"

####################################################
###############_PARSE_FUNCTIONS_CODE_###############
####################################################

def parse_data_integer(data):
	return int(data, 16)

def int_multiply_01(data):
	return float(decimal.Decimal(int(data, 16)) * decimal.Decimal('0.1'))

def int_multiply_001(data):
	return float(decimal.Decimal(int(data, 16)) * decimal.Decimal('0.01')) 

def int_multiply_0001(data):
	return float(decimal.Decimal(int(data, 16)) * decimal.Decimal('0.001'))

def signed_no_multiply(data): #need more testing of this function
	try:
		binary = bytes.fromhex(data.zfill(8))
		value = struct.unpack(">i", binary)[0]
		return value
	except Exception as e:
		print(f"unexpected value received in function '{data}' error: '{e}' will leave unparsed value!")
		return f"0x{data}"

parse_functions_dictionary = { #this must simply be updated with new AVL IDs and their functions
	
	240: parse_data_integer,
	239: parse_data_integer,
	80: parse_data_integer,
	21: parse_data_integer,
	200: parse_data_integer,
	69: parse_data_integer,
	181: int_multiply_01,
	182: int_multiply_01,
	66: int_multiply_0001,
	24: parse_data_integer,
	205: parse_data_integer,
	206: parse_data_integer,
	67: int_multiply_0001,
	68: int_multiply_0001,
	241: parse_data_integer,
	299: parse_data_integer,
	16: parse_data_integer,
	1: parse_data_integer,
	9: parse_data_integer,
	179: parse_data_integer,
	12: int_multiply_0001,
	13: int_multiply_001,
	17: signed_no_multiply,
	18: signed_no_multiply,
	19: signed_no_multiply,
	11: parse_data_integer,
	10: parse_data_integer,
	2: parse_data_integer,
	3: parse_data_integer,
	6: int_multiply_0001,
	180: parse_data_integer

}

def sorting_hat(key, value):
	if key in parse_functions_dictionary:
		parse_function = parse_functions_dictionary[key]
		return parse_function(value)
	else:
		return f"0x{value}"

####################################################

def main():
	start_server_tigger()

if __name__ == "__main__":
	main()