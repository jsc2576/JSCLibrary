import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

"""
############################################################
		SMTP setting and function (not decorator)
############################################################
"""
SMTP_server 	= None
SMTP_port 		= None
sender_email	= None
sender_pwd		= None

#set SMTP parameters settting (use before used 'to mail' decorators)
def SMTP_setting(_SMTP_server:str, _STMP_port:int, _sender_email:str, _sender_pwd:str):
	global SMTP_server
	global SMTP_port
	global sender_email
	global sender_pwd

	SMTP_server 		= _SMTP_server
	SMTP_port 			= _STMP_port
	sender_email 		= _sender_email
	sender_pwd 			= _sender_pwd


# set smtp function (private)
def _set_smtp(encryption:str):
	smtp = None
	if encryption.lower() == "tls":
		smtp = smtplib.SMTP()
	elif encryption.lower() == "ssl":
		smtp = smtplib.SMTP_SSL()
	else:
		return result

	smtp.connect(SMTP_server, SMTP_port)
	if encryption.lower() == "tls":
		smtp.starttls()

	smtp.login(sender_email, sender_pwd)
	smtp.ehlo()

	return smtp


#set mail message function (private)
def _set_msg(smtp, title:str, result:str, receiver:list):
	msg = MIMEText(str(result))
	msg['Subject'] = title
	msg['From'] = sender_email
	for receiver_one in receiver:
		msg['To'] = receiver_one
		smtp.sendmail(sender_email, receiver_one, msg.as_string())

	smtp.quit()


#set mail message with images function (private)
def _set_msg_images(smtp, title:str, text:str, images:dict, receiver:list):
	msg = MIMEMultipart()
	msg['From'] = sender_email
	msg['Subject'] = title

	for filename, image in images.items():
		img = MIMEImage(image)
		img.add_header('Content-Disposition', 'attachment', filename=filename)  
		msg.attach(img)

	for receiver_one in receiver:
		msg['To'] = receiver_one
		smtp.sendmail(sender_email, receiver_one, msg.as_string())

	smtp.quit()

"""
############################################################
					time check decorator
############################################################
"""

def time_check(func):
	def wrapper_time_check(*args, **kwargs):
		start_time = time.time()
		result = func(*args, **kwargs)
		end_time = time.time()

		print(func.__name__ + ": " + str(end_time-start_time) + "seconds")

	return wrapper_time_check


"""
############################################################
				result to mail decorator

This decorator means Send result of function to mail.
Encryption set TLS or SSL.
If set other encryption, don't send result to mail.
And, position of this function is last in all decorators.
############################################################
"""

def result_to_mail(receiver:list, title:str, encryption:str="TLS"):
	def decorator(func):
		def wrapper_result_to_mail(*args, **kwargs):
			result = func(*args, **kwargs)
			print(result)
			smtp = _set_smtp(encryption)
			_set_msg(smtp, title, result, receiver)

			return result
		return wrapper_result_to_mail
	return decorator


"""
This decorator is determined return shape.

return: str, dict{filename: image binary}
"""
def result_to_mail_with_images(receiver:list, title:str, encryption:str="TLS"):
	def decorator(func):
		def wrapper_result_to_mail_with_image(*args, **kwargs):
			text, images = func(*args, **kwargs)
			smtp = _set_smtp(encryption)
			_set_msg_images(smtp, title, text, images, receiver)

			return text, images

		return wrapper_result_to_mail_with_image
	return decorator


