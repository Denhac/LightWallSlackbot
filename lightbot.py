import os
import time
from slackclient import SlackClient
import opc

# starterbot's ID as an environment variable
#BOT_ID = os.environ.get("BOT_ID")
BOT_ID = "U1T9YNQKS"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# constants
AT_BOT = "<@" + BOT_ID + ">"

current_light_function = None
current_time_remaining = 0
    
numLEDs = 251
frequency = 1
#Connect to light controller  
client = opc.Client('10.0.100.6:80')

def red_alert():
    # [ (red, green, blue) ]
    pixels = [ (255,0,0) ] * numLEDs #creates an array of all the pixels (the whole row)
    client.put_pixels(pixels)
    time.sleep(frequency)
    pixels = [ (0,0,0) ] * numLEDs 
    client.put_pixels(pixels)
    #time.sleep(frequency)
    
def rainbow():
    pixels = [ (0,0,0) ] * numLEDs
    for i in range(numLEDs):
	pixels[i] = ((80+i+current_time_remaining*10) % 255,
		     (160+i+current_time_remaining*10) % 255,
		     (240+i+current_time_remaining*10) % 255)
    client.put_pixels(pixels)
	

def handle_command(command, channel):
    global current_light_function, current_time_remaining
    response = "Not sure what you mean. "
    if command.upper().startswith("STOP"):
	current_light_function = None
	current_time_remaining = 0
	response = "Halting Functions"
    if command.upper().startswith("RED ALERT"):
	current_light_function = red_alert
	current_time_remaining = 10
	response = "Initiating Red Alert!"
    if command.upper().startswith("RAINBOW"):
	current_light_function = rainbow
	current_time_remaining = 30
	response = "Taste the rainbow"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    print("Parsing %d messages") % len(output_list)
    if output_list and len(output_list) > 0:
        for output in output_list:
	    print (output)
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
	    if (current_time_remaining > 0):
	        current_light_function()
		current_time_remaining = current_time_remaining - 1
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
